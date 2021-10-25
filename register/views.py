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
    MyPasswordResetForm, MySetPasswordForm, EmailChangeForm, CreateLectureForm, EvaForm,ChatForm,TextSaleForm, TextChatForm
)
from .models import Lecture, LectureEva,UserLectureList, LectureChat, Text_product, Text_chat
import base64
import datetime
from django.contrib import messages
import random, string
import re
from django.shortcuts import render
from django.views.generic import View
import stripe
from PIL import Image
import qrcode
from io import BytesIO
import pathlib
import shutil
import os

stripe.api_key = settings.STRIPE_SECRET_KEY


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
        context['user_name'] = self.request.user.user_name
        context['user_lecture_list'] = self.request.user.lecture_list.all()
        context['user_lecture_eva_list'] = []
        #評価した講義以外は「評価回答ボタン」を表示
        user_lecture_eva_list = LectureEva.objects.filter(user=self.request.user)
        for i in user_lecture_eva_list:
            context['user_lecture_eva_list'].append(i.lecture)

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
    paginate_by = 10

    def get_queryset(self):
        college = self.request.user.college_name.id
        keyword = self.request.GET.get('keyword')
        keyword2 = self.request.GET.get('keyword2')
        queryset = Lecture.objects.filter(college_name=college)
        if keyword:
            queryset = queryset.filter(
            Q(lecture_name__icontains=keyword) | Q(teacher_name__icontains=keyword)
            ).filter(college_name=college)

        if keyword2:
            keyword2=re.sub(r'開講曜日[\s　]+授業コード[\s　]+科目名[\s　]+教員氏名[\s　]+教室[\r\n]+','',keyword2)
            keyword2=re.sub(r'開講区分[\s　]+授業コード[\s　]+科目名[\s　]+教員氏名[\s　]+教室[\s　]+単位[\s　]+エラー[\r\n]+','',keyword2)
            keyword2=re.sub(r'開講曜日[\s　]+授業コード[\s　]+科目名[\s　]+教員氏名[\s　]+教室[\s　]+単位[\s　]+エラー[\r\n]+','',keyword2)
            keyword2=keyword2.replace('集中講義／実習\r','')

            #統一のため単位数を削除
            keyword2=re.sub(r'\t\d\t+','',keyword2)
            #改行&タブで分ける。
            split_list = re.split('[\r\n\t]',keyword2)
            data_split_list = []
            result_lecture_list = []
            result_teacher_list = []
            count=0

            #空白の要素を削除
            for word in split_list:
                if word != '':
                    data_split_list.append(word)
            for word in data_split_list:
                if count%5==2:
                    lecture = word
                    # 「 [ 」の最初の位置を取得し、それ以前の文字情報を取得。かつ文字列前後の空白を削除 # マクロ経済学
                    lecture = lecture[:lecture.find('[')].strip(' ')
                    result_lecture_list.append(lecture)
                elif count%5==3:
                    teacher = word
                    teacher=teacher.replace('\u3000', ' ') # 全角空白を半角空白へ変換
                    result_teacher_list.append(teacher)
                count+=1

            queryset=Lecture.objects.filter(lecture_name__in=result_lecture_list).filter(teacher_name__in=result_teacher_list)
            a=Lecture.objects.all()[3]
            print("テストデータ：{0}です".format(a))

        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_lecture_list'] = self.request.user.lecture_list.all()
        context['user_lecture_eva_list'] = []
        #評価した講義以外は「評価回答ボタン」を表示
        user_lecture_eva_list = LectureEva.objects.filter(user=self.request.user)
        for i in user_lecture_eva_list:
            context['user_lecture_eva_list'].append(i.lecture)
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
        context['gakunen_chart'] = gakunen_chart(self.kwargs['pk'],self.kwargs['place'])
        context['grade_chart'] = grade_chart(self.kwargs['pk'],self.kwargs['place'])
        context['eva_chart'] = eva_chart(self.kwargs['pk'],self.kwargs['place'])
        context['dif_chart'] = dif_chart(self.kwargs['pk'],self.kwargs['place'])
        lecture = Lecture.objects.get(id=self.kwargs['pk'])
        eva_comment=''
        if self.kwargs['place'] == 0:
            eva_list = LectureEva.objects.filter(lecture=lecture).exclude(eva_comment__exact="")
        elif self.kwargs['place'] == 1:
            eva_list = LectureEva.objects.filter(lecture=lecture).filter(place=1).exclude(eva_comment__exact="")
        else:
            eva_list = LectureEva.objects.filter(lecture=lecture).filter(place=2).exclude(eva_comment__exact="")

        if eva_list.count() > 11:
            context['eva_list'] = eva_list.order_by('-created_at')[:9]
        else:
            context['eva_list'] = eva_list


        context['eva_count'] = LectureEva.objects.filter(user=self.request.user).filter(lecture=lecture).count()
        return context

def gakunen_chart(pk,place):
    import matplotlib
    #バックエンドを指定
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import io
    from django.http import HttpResponse

    lecture = Lecture.objects.get(id=pk)

    if place == 0:
        dif_A = LectureEva.objects.filter(lecture=lecture).filter(gakunen_lank=1).count()
        dif_B = LectureEva.objects.filter(lecture=lecture).filter(gakunen_lank=2).count()
        dif_C = LectureEva.objects.filter(lecture=lecture).filter(gakunen_lank=3).count()
        dif_D = LectureEva.objects.filter(lecture=lecture).filter(gakunen_lank=4).count()
    elif place == 1:
        dif_A = LectureEva.objects.filter(lecture=lecture).filter(gakunen_lank=1).filter(place=1).count()
        dif_B = LectureEva.objects.filter(lecture=lecture).filter(gakunen_lank=2).filter(place=1).count()
        dif_C = LectureEva.objects.filter(lecture=lecture).filter(gakunen_lank=3).filter(place=1).count()
        dif_D = LectureEva.objects.filter(lecture=lecture).filter(gakunen_lank=4).filter(place=1).count()
    else:
        dif_A = LectureEva.objects.filter(lecture=lecture).filter(gakunen_lank=1).filter(place=2).count()
        dif_B = LectureEva.objects.filter(lecture=lecture).filter(gakunen_lank=2).filter(place=2).count()
        dif_C = LectureEva.objects.filter(lecture=lecture).filter(gakunen_lank=3).filter(place=2).count()
        dif_D = LectureEva.objects.filter(lecture=lecture).filter(gakunen_lank=4).filter(place=2).count()

    datas = [dif_A, dif_B, dif_C, dif_D]
    label3 = ['freshman', 'sophomore', 'junior', 'senior']
    colors = ['magenta', 'skyblue', 'aqua', 'lime']
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



#グラフ
def grade_chart(pk,place):
    import matplotlib
    #バックエンドを指定
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import io
    from django.http import HttpResponse

    lecture = Lecture.objects.get(id=pk)

    if place == 0:
        grade_S = LectureEva.objects.filter(lecture=lecture).filter(grade_lank=5).count()
        grade_A = LectureEva.objects.filter(lecture=lecture).filter(grade_lank=4).count()
        grade_B = LectureEva.objects.filter(lecture=lecture).filter(grade_lank=3).count()
        grade_C = LectureEva.objects.filter(lecture=lecture).filter(grade_lank=2).count()
        grade_D = LectureEva.objects.filter(lecture=lecture).filter(grade_lank=1).count()
    elif place == 1:
        grade_S = LectureEva.objects.filter(lecture=lecture).filter(grade_lank=5).filter(place=1).count()
        grade_A = LectureEva.objects.filter(lecture=lecture).filter(grade_lank=4).filter(place=1).count()
        grade_B = LectureEva.objects.filter(lecture=lecture).filter(grade_lank=3).filter(place=1).count()
        grade_C = LectureEva.objects.filter(lecture=lecture).filter(grade_lank=2).filter(place=1).count()
        grade_D = LectureEva.objects.filter(lecture=lecture).filter(grade_lank=1).filter(place=1).count()
    else:
        grade_S = LectureEva.objects.filter(lecture=lecture).filter(grade_lank=5).filter(place=2).count()
        grade_A = LectureEva.objects.filter(lecture=lecture).filter(grade_lank=4).filter(place=2).count()
        grade_B = LectureEva.objects.filter(lecture=lecture).filter(grade_lank=3).filter(place=2).count()
        grade_C = LectureEva.objects.filter(lecture=lecture).filter(grade_lank=2).filter(place=2).count()
        grade_D = LectureEva.objects.filter(lecture=lecture).filter(grade_lank=1).filter(place=2).count()

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


def eva_chart(pk,place):
    import matplotlib
    #バックエンドを指定
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import io
    from django.http import HttpResponse

    lecture = Lecture.objects.get(id=pk)

    if place == 0:
        eva_S = LectureEva.objects.filter(lecture=lecture).filter(eva_lank=5).count()
        eva_A = LectureEva.objects.filter(lecture=lecture).filter(eva_lank=4).count()
        eva_B = LectureEva.objects.filter(lecture=lecture).filter(eva_lank=3).count()
        eva_C = LectureEva.objects.filter(lecture=lecture).filter(eva_lank=2).count()
        eva_D = LectureEva.objects.filter(lecture=lecture).filter(eva_lank=1).count()
    elif place == 1:
        eva_S = LectureEva.objects.filter(lecture=lecture).filter(eva_lank=5).filter(place=1).count()
        eva_A = LectureEva.objects.filter(lecture=lecture).filter(eva_lank=4).filter(place=1).count()
        eva_B = LectureEva.objects.filter(lecture=lecture).filter(eva_lank=3).filter(place=1).count()
        eva_C = LectureEva.objects.filter(lecture=lecture).filter(eva_lank=2).filter(place=1).count()
        eva_D = LectureEva.objects.filter(lecture=lecture).filter(eva_lank=1).filter(place=1).count()
    else:
        eva_S = LectureEva.objects.filter(lecture=lecture).filter(eva_lank=5).filter(place=2).count()
        eva_A = LectureEva.objects.filter(lecture=lecture).filter(eva_lank=4).filter(place=2).count()
        eva_B = LectureEva.objects.filter(lecture=lecture).filter(eva_lank=3).filter(place=2).count()
        eva_C = LectureEva.objects.filter(lecture=lecture).filter(eva_lank=2).filter(place=2).count()
        eva_D = LectureEva.objects.filter(lecture=lecture).filter(eva_lank=1).filter(place=2).count()

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


def dif_chart(pk,place):
    import matplotlib
    #バックエンドを指定
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import io
    from django.http import HttpResponse

    lecture = Lecture.objects.get(id=pk)
    if place == 0:
        dif_S = LectureEva.objects.filter(lecture=lecture).filter(dif_lank=5).count()
        dif_A = LectureEva.objects.filter(lecture=lecture).filter(dif_lank=4).count()
        dif_B = LectureEva.objects.filter(lecture=lecture).filter(dif_lank=3).count()
        dif_C = LectureEva.objects.filter(lecture=lecture).filter(dif_lank=2).count()
        dif_D = LectureEva.objects.filter(lecture=lecture).filter(dif_lank=1).count()
    elif place == 1:
        dif_S = LectureEva.objects.filter(lecture=lecture).filter(dif_lank=5).filter(place=1).count()
        dif_A = LectureEva.objects.filter(lecture=lecture).filter(dif_lank=4).filter(place=1).count()
        dif_B = LectureEva.objects.filter(lecture=lecture).filter(dif_lank=3).filter(place=1).count()
        dif_C = LectureEva.objects.filter(lecture=lecture).filter(dif_lank=2).filter(place=1).count()
        dif_D = LectureEva.objects.filter(lecture=lecture).filter(dif_lank=1).filter(place=1).count()
    else:
        dif_S = LectureEva.objects.filter(lecture=lecture).filter(dif_lank=5).filter(place=2).count()
        dif_A = LectureEva.objects.filter(lecture=lecture).filter(dif_lank=4).filter(place=2).count()
        dif_B = LectureEva.objects.filter(lecture=lecture).filter(dif_lank=3).filter(place=2).count()
        dif_C = LectureEva.objects.filter(lecture=lecture).filter(dif_lank=2).filter(place=2).count()
        dif_D = LectureEva.objects.filter(lecture=lecture).filter(dif_lank=1).filter(place=2).count()

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

class Help_top(generic.TemplateView):
    template_name = 'register/help_top.html'

class Help_contents(generic.TemplateView):
    template_name = 'register/help_contents.html'

    def get_context_data(self, **kwargs,):
        context = super().get_context_data(**kwargs)
        context['help_pk'] = self.kwargs['pk']
        return context


class Text_product_list(generic.ListView):
    model = Text_product
    template_name = 'register/text_product_list.html'
    def get_context_data(self, **kwargs,):
        context = super().get_context_data(**kwargs)

        keyword = self.request.GET.get('keyword')
        queryset = Text_product.objects.all()
        if keyword:
            queryset = queryset.filter(product_name__icontains=keyword)

        context['text_product_list'] = queryset

        image_url_list = []
        for product in queryset:
            image_filepath = product.image
            image_url = f"{settings.MEDIA_URL}/{image_filepath}"
            target = '/'
            idx = image_url.rfind(target)
            image_url_list.append(image_url[idx+1:])

        context['image_url'] = image_url_list
        return context


class Text_product_detail(generic.DetailView):
    template_name = 'register/text_product_detail.html'
    model = Text_product

    def post(self, request, *args, **kwargs):
        """購入時の処理"""
        text_product = self.get_object()
        token = request.POST['stripeToken']  # フォームでのサブミット後に自動で作られる
        try:
            # 購入処理
            charge = stripe.Charge.create(
                amount=text_product.price,
                currency='jpy',
                source=token,
                description='メール:{} 書籍名:{}'.format(request.user.email, text_product.product_name),
            )
        except stripe.error.CardError as e:
            # カード決済が上手く行かなかった(限度額超えとか)ので、メッセージと一緒に再度ページ表示
            context = self.get_context_data()
            context['message'] = 'このクレジットカードはご利用できません。限度額等をご確認ください。'
            return render(request, 'register/text_product_detail.html', context)
        else:
            text_product.on_sale = False
            text_product.buy_user = self.request.user
            text_product.save()
            return redirect('register:text_product_list')

    def get_context_data(self, **kwargs):
        """STRIPE_PUBLIC_KEYを渡したいだけ"""
        context = super().get_context_data(**kwargs)
        context['publick_key'] = settings.STRIPE_PUBLIC_KEY
        product = Text_product.objects.get(id=self.kwargs['pk'])
        context['on_sale'] = product.on_sale
        text_product = self.get_object()
        return context

class Text_chat_page(generic.ListView,generic.edit.ModelFormMixin):
    """教科書チャット"""
    model = Text_chat
    form_class = TextChatForm
    template_name = 'register/text_chat.html'

    def get(self, request, *args, **kwargs):
        self.object = None
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']
        product = Text_product.objects.get(id=self.kwargs['pk'])
        context['chat_list'] = Text_chat.objects.filter(product=product).order_by('-created_at')

        return context


    def post(self, request, *args, **kwargs):
        self.object = None
        self.object_list = self.get_queryset()
        form = self.get_form()
        if form.is_valid():
            user = self.request.user
            product = Text_product.objects.get(id=self.kwargs['pk'])
            chat = form.save(commit=False)
            chat.user = user
            chat.product = product
            chat.save()
            return self.form_invalid(form)
        else:
            return self.form_invalid(form)


def change_suffix(file_name, from_suffix, to_suffix):
    # ファイルの拡張子を得る
    sf = pathlib.PurePath(file_name).suffix
    # 変更対象かどうか判定する
    if sf == from_suffix:
        # ファイル名(拡張子除く)を得る
        st = pathlib.PurePath(file_name).stem
        # 変更後のファイル名を得る
        to_name = st + to_suffix
        # ファイル名を変更する
        shutil.move(file_name, to_name)


class Text_sale(generic.CreateView):
    model = Text_product
    template_name = 'register/text_sale.html'
    form_class = TextSaleForm


    def form_valid(self, form):
        user = self.request.user
        text_product = form.save(commit=False)
        text_product.sale_user = user
        text_product.save()
        """image_filepath = text_product.image
        print("一番{}".format(image_filepath))
        image_url = f"{settings.MEDIA_URL}{image_filepath}"
        print("二番{}".format(image_url))
        sf = pathlib.PurePath(image_url).suffix
        print("三番{}".format(sf))
        st = "{}".format(text_product.pk)
        print("四番{}".format(st))

        to_suffix = ".jpeg"
        to_name = st + to_suffix
        print("五番{}".format(to_name))

        image_url_str = str(image_url)
        img = Image.open(image_url_str)

        shutil.move(f'{settings.MEDIA_ROOT}/{image_filepath}', f'{settings.MEDIA_ROOT}/product_image/{to_name}')
        image_url_data = f"product_image/{to_name}"
        print("六番{}".format(image_url_data))
        text_product.image = image_url_data
        text_product.save()"""


        #現在の画像のディレクトリを取得
        image_filepath = text_product.image
        image_url = f"{settings.MEDIA_URL}{image_filepath}"

        #ディレクトリから拡張子を外したものを取得
        image_url_str = str(image_url)
        target = '.'
        index = image_url_str.find(target)
        image_url_no_extension = image_url_str[:index-1]

        #jpegを定義

        #Imageでopen
        
        img = Image.open(image_url_str)
        #拡張子を変更して保存
        image_url_input_str = image_url_no_extension + ".jpeg"
        img.save(image_url_input_str, 'jpeg')
        #djangoの方のディレクト英を変更

        return redirect('register:text_product_list')


class Text_sale_buy_list(generic.ListView):
    Model = Text_product
    template_name = 'register/text_sale_buy_list.html'


    def get_queryset(self, **kwargs):
        queryset = Text_product.objects.all()
        if self.kwargs['pk'] == 0:
            queryset = Text_product.objects.filter(sale_user=self.request.user)
        else:
            queryset = Text_product.objects.filter(buy_user=self.request.user)
        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']
        return context


class Sale_buy_process(generic.DetailView):
    model = Text_product
    template_name = 'register/sale_buy_process.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['place'] = self.kwargs['place']
        return context


    def post(self, request,pk,place):
        product_id = request.POST['text_product']
        text_product = Text_product.objects.get(id=product_id)
        text_product.sale_done = True
        eva = request.POST['s2']
        if eva == 1:
            text_product.trade_eva = True
        else:
            text_product.trade_eva = False
        text_product.save()
        return redirect('register:top')

class TextSaleUser(generic.ListView):
    model = Text_product
    template_name = 'register/text_sale_user.html'

    def get_queryset(self,**kwargs):
        user = User.objects.get(pk=self.kwargs['userpk'])
        products = Text_product.objects.filter(sale_user=user)
        return products



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
        def randomname(n):
            return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

        code = ""

        while True:
            def randomname(n):
                return ''.join(random.choices(string.ascii_letters + string.digits, k=n))
            code = randomname(6)
            user = User.objects.filter(invi_code=code).count()
            if user == 0:
                break

        user = form.save(commit=False)
        user.invi_code = code
        user.is_active = False

        input_invi_code = form.cleaned_data['input_invi_code']
        if input_invi_code != "":
            invi_user=User.objects.filter(invi_code=input_invi_code)
            if invi_user:
                invi_user[0].invi_point = invi_user[0].invi_point+1
                invi_user[0].save()
                user.save()
            else:
                messages.warning(self.request, '該当する招待コードが存在しません。')
                return redirect('register:user_create')
        else:
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
