from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
)
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, resolve_url, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import generic
from django.db.models import Q
from .forms import (
    LoginForm, UserCreateForm, UserUpdateForm, MyPasswordChangeForm,
    MyPasswordResetForm, MySetPasswordForm, EmailChangeForm, CreateLectureForm, EvaForm,ChatForm
)
from .models import Lecture, LectureEva,UserLectureList, LectureChat
import base64
import datetime
from django.contrib import messages

User = get_user_model()

class first(generic.TemplateView):
    """最初のページ"""
    template_name = 'register/first.html'

class Top(generic.ListView):
    """履修中講義一覧ページ"""
    model = Lecture
    template_name = 'register/top.html'
    paginate_by = 10

    def get_queryset(self):
        lectures = self.request.user.lecture_list.all()
        return lectures

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_lecture_list'] = self.request.user.lecture_list.all()
        return context

    def post(self, request):
        lecture_id = request.POST['lecture']
        check_lecture = self.request.user.lecture_list.filter(id=lecture_id)
        lecture = Lecture.objects.get(id=lecture_id)
        if not check_lecture:
            self.request.user.lecture_list.add(lecture)
        else:
            user_lecture_list = UserLectureList.objects.filter(user=self.request.user).filter(lecture=lecture)
            time = user_lecture_list[0].created_at
            JST = datetime.timezone(datetime.timedelta(hours=9), "JST")
            elapsed_time = datetime.datetime.now(JST)-time
            if elapsed_time.days < 30:
                self.request.user.lecture_list.remove(lecture)
            else:
                eva = LectureEva.objects.filter(user=self.request.user).filter(lecture=lecture).count()
                if eva != 0:
                    self.request.user.lecture_list.remove(lecture)
                else:
                    messages.warning(request, 'この講義の履修を解除するには、授業評価を投稿する必要があります。')
                    return redirect('register:top')



        return redirect('register:top')



class SelectLecture(generic.ListView):
    """講義検索/登録ページ"""

    model = Lecture
    template_name = 'register/select_lecture.html'
    paginate_by = 1

    def get_queryset(self):
        college = self.request.user.college_name.id
        keyword = self.request.GET.get('keyword')
        queryset = Lecture.objects.filter(college_name=college)
        if keyword:
            queryset = queryset.filter(
            Q(lecture_name__icontains=keyword) | Q(teacher_name__icontains=keyword)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_lecture_list'] = self.request.user.lecture_list.all()
        return context

    def post(self, request):
        lecture_id = request.POST['lecture']
        check_lecture = self.request.user.lecture_list.filter(id=lecture_id)
        lecture = Lecture.objects.get(id=lecture_id)
        if not check_lecture:
            self.request.user.lecture_list.add(lecture)
        else:
            user_lecture_list = UserLectureList.objects.filter(user=self.request.user).filter(lecture=lecture)
            time = user_lecture_list[0].created_at
            JST = datetime.timezone(datetime.timedelta(hours=9), "JST")
            elapsed_time = datetime.datetime.now(JST)-time
            if elapsed_time.seconds < 10:
                self.request.user.lecture_list.remove(lecture)
            else:
                eva = LectureEva.objects.filter(user=self.request.user).filter(lecture=lecture).count()
                if eva != 0:
                    self.request.user.lecture_list.remove(lecture)
                else:
                    messages.warning(request, 'この講義の履修を解除するには、授業評価を投稿する必要があります。')
                    return redirect('register:select_lecture')

        return redirect('register:select_lecture')



class LectureCreate(generic.CreateView):
    """講義作成ページ"""
    model = Lecture
    template_name = 'register/create_lecture_form.html'
    form_class = CreateLectureForm

    def form_valid(self, form):
        college = self.request.user.college_name
        lecture = form.save(commit=False)
        lecture.college_name = college
        lecture_list = Lecture.objects.filter(college_name=college).filter(lecture_name=lecture.lecture_name).filter(teacher_name=lecture.teacher_name)
        if lecture_list.count()==0:
            lecture.save()
            return redirect('register:select_lecture')
        else:
            messages.warning(self.request, '講義名、担当教員が一致する授業が存在しています。「講義を探す」より講義名、または担当教員名で検索してください。')
            return redirect('register:create_lecture')


class DetailView(generic.DetailView):
    """講義詳細ページ(グラフなど)"""
    model = Lecture
    template_name = 'register/lecture_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']
        context['user_lecture_list'] = self.request.user.lecture_list.all()
        context['grade_chart'] = grade_chart(self.kwargs['pk'])
        context['eva_chart'] = eva_chart(self.kwargs['pk'])
        context['dif_chart'] = dif_chart(self.kwargs['pk'])
        context['gakunen_chart'] = gakunen_chart(self.kwargs['pk'])
        lecture = Lecture.objects.get(id=self.kwargs['pk'])
        eva_comment=''
        eva_list = LectureEva.objects.filter(lecture=lecture).exclude(eva_comment__exact="").count()
        if eva_list > 11:
            context['eva_list'] = LectureEva.objects.filter(lecture=lecture).exclude(eva_comment__exact="").order_by('-created_at')[:9]
        else:
            context['eva_list'] = LectureEva.objects.filter(lecture=lecture).exclude(eva_comment__exact="")


        context['eva_count'] = LectureEva.objects.filter(user=self.request.user).filter(lecture=lecture).count()
        return context


#グラフ
def grade_chart(pk):
    import matplotlib
    #バックエンドを指定
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import io
    from django.http import HttpResponse

    lecture = Lecture.objects.get(id=pk)
    grade_S = LectureEva.objects.filter(lecture=lecture).filter(grade_lank=5).count()
    grade_A = LectureEva.objects.filter(lecture=lecture).filter(grade_lank=4).count()
    grade_B = LectureEva.objects.filter(lecture=lecture).filter(grade_lank=3).count()
    grade_C = LectureEva.objects.filter(lecture=lecture).filter(grade_lank=2).count()
    grade_D = LectureEva.objects.filter(lecture=lecture).filter(grade_lank=1).count()

    datas = [grade_S, grade_A, grade_B, grade_C, grade_D]
    label1 = ['S', 'A', 'B', 'C', 'D']
    colors = ['lime', 'aqua', 'skyblue', 'magenta', 'yellow']
    ax = plt.subplot()
    ax.axis("equal")
    pie = ax.pie(datas, #データ
                 startangle=90, #円グラフ開始軸を指定
                 labels=label1, #ラベル
                 colors=colors, #色指定
                 counterclock=False, #逆時計回り
                 labeldistance=None,
                 )
    buf = io.BytesIO()
    plt.legend()
    plt.savefig(buf, format='png', dpi=200)
    plt.close()
    return base64.b64encode(buf.getvalue()).decode("utf-8").replace("\n", "")


def eva_chart(pk):
    import matplotlib
    #バックエンドを指定
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import io
    from django.http import HttpResponse

    lecture = Lecture.objects.get(id=pk)
    eva_S = LectureEva.objects.filter(lecture=lecture).filter(eva_lank=5).count()
    eva_A = LectureEva.objects.filter(lecture=lecture).filter(eva_lank=4).count()
    eva_B = LectureEva.objects.filter(lecture=lecture).filter(eva_lank=3).count()
    eva_C = LectureEva.objects.filter(lecture=lecture).filter(eva_lank=2).count()
    eva_D = LectureEva.objects.filter(lecture=lecture).filter(eva_lank=1).count()

    datas = [eva_S, eva_A, eva_B, eva_C, eva_D]
    label2 = ['Very much', 'much', 'Neutral', 'little', 'Very little']
    colors = ['lime', 'aqua', 'skyblue', 'magenta', 'yellow']
    ax = plt.subplot()
    ax.axis("equal")
    pie = ax.pie(datas, #データ
                 startangle=90, #円グラフ開始軸を指定
                 labels=label2, #ラベル
                 colors=colors, #色指定
                 counterclock=False, #逆時計回り
                 labeldistance=None,
                 )
    buf = io.BytesIO()
    plt.legend()
    plt.savefig(buf, format='png', dpi=200)
    plt.close()
    return base64.b64encode(buf.getvalue()).decode("utf-8").replace("\n", "")


def dif_chart(pk):
    import matplotlib
    #バックエンドを指定
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import io
    from django.http import HttpResponse

    lecture = Lecture.objects.get(id=pk)
    dif_S = LectureEva.objects.filter(lecture=lecture).filter(dif_lank=5).count()
    dif_A = LectureEva.objects.filter(lecture=lecture).filter(dif_lank=4).count()
    dif_B = LectureEva.objects.filter(lecture=lecture).filter(dif_lank=3).count()
    dif_C = LectureEva.objects.filter(lecture=lecture).filter(dif_lank=2).count()
    dif_D = LectureEva.objects.filter(lecture=lecture).filter(dif_lank=1).count()

    datas = [dif_S, dif_A, dif_B, dif_C, dif_D]
    label3 = ['Very easy', 'Easy', 'Normal', 'Hard', 'Very hard']
    colors = ['lime', 'aqua', 'skyblue', 'magenta', 'yellow']
    ax = plt.subplot()
    ax.axis("equal")
    pie = ax.pie(datas, #データ
                 startangle=90, #円グラフ開始軸を指定
                 labels=label3, #ラベル
                 colors=colors, #色指定
                 counterclock=False, #逆時計回り
                 labeldistance=None,
                 )
    buf = io.BytesIO()
    plt.legend()
    plt.savefig(buf, format='png', dpi=200)
    plt.close()
    return base64.b64encode(buf.getvalue()).decode("utf-8").replace("\n", "")


def gakunen_chart(pk):
    import matplotlib
    #バックエンドを指定
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import io
    from django.http import HttpResponse

    lecture = Lecture.objects.get(id=pk)
    dif_A = LectureEva.objects.filter(lecture=lecture).filter(gakunen_lank=4).count()
    dif_B = LectureEva.objects.filter(lecture=lecture).filter(gakunen_lank=3).count()
    dif_C = LectureEva.objects.filter(lecture=lecture).filter(gakunen_lank=2).count()
    dif_D = LectureEva.objects.filter(lecture=lecture).filter(gakunen_lank=1).count()

    datas = [dif_A, dif_B, dif_C, dif_D]
    label3 = ['freshman', 'sophomore', 'junior', 'senior']
    colors = ['magenta', 'skyblue', 'aqua', 'lime']
    print(datas)
    ax = plt.subplot()
    ax.axis("equal")
    pie = ax.pie(datas, #データ
                 startangle=90, #円グラフ開始軸を指定
                 labels=label3, #ラベル
                 colors=colors, #色指定
                 counterclock=False, #逆時計回り
                 labeldistance=None,
                 )
    buf = io.BytesIO()
    plt.legend()
    plt.savefig(buf, format='png', dpi=200)
    plt.close()
    return base64.b64encode(buf.getvalue()).decode("utf-8").replace("\n", "")


class Evaluate(generic.CreateView):
    """授業評価投稿ページ"""
    model = LectureEva
    template_name = 'register/eva_form.html'
    form_class = EvaForm

    def form_valid(self, form):
        user = self.request.user
        lecture = Lecture.objects.get(id=self.kwargs['pk'])
        eva = form.save(commit=False)
        eva.user = user
        eva.lecture = lecture
        eva.save()

        user.user_point = user.user_point+1
        user.save()
        return redirect('register:select_lecture')



class ChatList(generic.ListView,generic.edit.ModelFormMixin):
    """コメント一覧/投稿ページ"""
    model = LectureChat
    form_class = ChatForm
    template_name = 'register/chat.html'
    paginate_by = 15

    def get(self, request, *args, **kwargs):
        self.object = None
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']
        lecture = Lecture.objects.get(id=self.kwargs['pk'])
        chat_list = LectureChat.objects.filter(lecture=lecture)
        if chat_list.count() > 21:
            context['chat_list'] = LectureChat.objects.filter(lecture=lecture).order_by('-created_at')[:19]
        else:
            context['chat_list'] = LectureChat.objects.filter(lecture=lecture).order_by('-created_at')

        return context


    def post(self, request, *args, **kwargs):
        self.object = None
        self.object_list = self.get_queryset()
        form = self.get_form()
        if form.is_valid():
            user = self.request.user
            lecture = Lecture.objects.get(id=self.kwargs['pk'])
            chat = form.save(commit=False)
            chat.user = user
            chat.lecture = lecture
            chat.save()
            return self.form_invalid(form)
        else:
            return self.form_invalid(form)


class Login(LoginView):
    """ログインページ"""
    form_class = LoginForm
    template_name = 'register/login.html'


class Logout(LogoutView):
    """ログアウトページ"""
    template_name = 'register/login.html'


class UserCreate(generic.CreateView):
    """ユーザー仮登録"""
    template_name = 'register/user_create.html'
    form_class = UserCreateForm

    def form_valid(self, form):
        """仮登録と本登録用メールの発行."""
        # 仮登録と本登録の切り替えは、is_active属性を使うと簡単です。
        # 退会処理も、is_activeをFalseにするだけにしておくと捗ります。
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # アクティベーションURLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': domain,
            'token': dumps(user.pk),
            'user': user,
        }

        subject = render_to_string('register/mail_template/create/subject.txt', context)
        message = render_to_string('register/mail_template/create/message.txt', context)

        user.email_user(subject, message)
        return redirect('register:user_create_done')


class UserCreateDone(generic.TemplateView):
    """ユーザー仮登録したよ"""
    template_name = 'register/user_create_done.html'


class UserCreateComplete(generic.TemplateView):
    """メール内URLアクセス後のユーザー本登録"""
    template_name = 'register/user_create_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)  # デフォルトでは1日以内

    def get(self, request, **kwargs):
        """tokenが正しければ本登録."""
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()

        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()

        # tokenは問題なし
        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                return HttpResponseBadRequest()
            else:
                if not user.is_active:
                    # まだ仮登録で、他に問題なければ本登録とする
                    user.is_active = True
                    user.save()
                    return super().get(request, **kwargs)

        return HttpResponseBadRequest()


class OnlyYouMixin(UserPassesTestMixin):
    """本人か、スーパーユーザーだけユーザーページアクセスを許可する"""
    raise_exception = True

    def test_func(self):
        user = self.request.user
        return user.pk == self.kwargs['pk'] or user.is_superuser


class UserDetail(OnlyYouMixin, generic.DetailView):
    """ユーザーの詳細ページ"""
    model = User
    template_name = 'register/user_detail.html'  # デフォルトユーザーを使う場合に備え、きちんとtemplate名を書く


class UserUpdate(OnlyYouMixin, generic.UpdateView):
    """ユーザー情報更新ページ"""
    model = User
    form_class = UserUpdateForm
    template_name = 'register/user_form.html'  # デフォルトユーザーを使う場合に備え、きちんとtemplate名を書く

    def get_success_url(self):
        return resolve_url('register:user_detail', pk=self.kwargs['pk'])


class PasswordChange(PasswordChangeView):
    """パスワード変更ビュー"""
    form_class = MyPasswordChangeForm
    success_url = reverse_lazy('register:password_change_done')
    template_name = 'register/password_change.html'


class PasswordChangeDone(PasswordChangeDoneView):
    """パスワード変更しました"""
    template_name = 'register/password_change_done.html'


class PasswordReset(PasswordResetView):
    """パスワード変更用URLの送付ページ"""
    subject_template_name = 'register/mail_template/password_reset/subject.txt'
    email_template_name = 'register/mail_template/password_reset/message.txt'
    template_name = 'register/password_reset_form.html'
    form_class = MyPasswordResetForm
    success_url = reverse_lazy('register:password_reset_done')


class PasswordResetDone(PasswordResetDoneView):
    """パスワード変更用URLを送りましたページ"""
    template_name = 'register/password_reset_done.html'


class PasswordResetConfirm(PasswordResetConfirmView):
    """新パスワード入力ページ"""
    form_class = MySetPasswordForm
    success_url = reverse_lazy('register:password_reset_complete')
    template_name = 'register/password_reset_confirm.html'


class PasswordResetComplete(PasswordResetCompleteView):
    """新パスワード設定しましたページ"""
    template_name = 'register/password_reset_complete.html'


class EmailChange(LoginRequiredMixin, generic.FormView):
    """メールアドレスの変更"""
    template_name = 'register/email_change_form.html'
    form_class = EmailChangeForm

    def form_valid(self, form):
        user = self.request.user
        new_email = form.cleaned_data['email']

        # URLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': domain,
            'token': dumps(new_email),
            'user': user,
        }

        subject = render_to_string('register/mail_template/email_change/subject.txt', context)
        message = render_to_string('register/mail_template/email_change/message.txt', context)
        send_mail(subject, message, None, [new_email])

        return redirect('register:email_change_done')


class EmailChangeDone(LoginRequiredMixin, generic.TemplateView):
    """メールアドレスの変更メールを送ったよ"""
    template_name = 'register/email_change_done.html'


class EmailChangeComplete(LoginRequiredMixin, generic.TemplateView):
    """リンクを踏んだ後に呼ばれるメアド変更ビュー"""
    template_name = 'register/email_change_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)  # デフォルトでは1日以内

    def get(self, request, **kwargs):
        token = kwargs.get('token')
        try:
            new_email = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()

        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()

        # tokenは問題なし
        else:
            User.objects.filter(email=new_email, is_active=False).delete()
            request.user.email = new_email
            request.user.save()
            return super().get(request, **kwargs)
