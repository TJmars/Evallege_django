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
    MyPasswordResetForm, MySetPasswordForm, EmailChangeForm, CreateLectureForm, EvaForm,ChatForm,TextSaleForm,CircleCreateForm,LectureChatForm,BoardCreateForm,BoardCreateIndiForm,LectureEditForm
)
from .models import Lecture, LectureEva,UserLectureList, LectureChat, Text_product, Circle, Board
import base64
import datetime
from django.contrib import messages
import random, string
import re
from django.shortcuts import render
from django.views.generic import View
from PIL import Image
import qrcode
from io import BytesIO
import pathlib
import shutil
import os
import cv2
import matplotlib.pyplot as plt
import csv
import re
from csv import reader


User = get_user_model()



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
                    messages.warning(request, 'この講義の履修を解除するには、授業評価を投稿する必要があります。Lectureページのグッドボタンから授業評価画面へと進んでください。')
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

        if keyword2:
            #講義一覧読み込み
            #----------------------------------------------------
            with open('register/Lecture-2022-02-04.csv', 'r') as csv_file:
                csv_reader = reader(csv_file)
                list_all = list(csv_reader)
            #-----------------------------------------------------
            #ユーザがコピペしたやつ読み込み
            #------------------------------------------------
            input_data = keyword2
            lecture_list=[]
            teacher_list=[]

            split_data=re.split('\n',input_data)
            resub_data=[]
            for x in split_data:
                resub_data.append(re.sub('\[.*\]','',x).strip())

            for i in range(len(resub_data)):
                for x in list_all:
                    if x[1]==resub_data[i] and x[2]==resub_data[i+1]:
                        lecture_list.append(resub_data[i])
                        teacher_list.append(resub_data[i+1])
                        break;

            print(lecture_list)
            print(teacher_list)

            college = self.request.user.college_name

            queryset=Lecture.objects.filter(lecture_name__in=lecture_list).filter(teacher_name__in=teacher_list).filter(college_name=college)

        elif keyword:
            queryset = queryset.filter(
            Q(lecture_name__icontains=keyword) | Q(teacher_name__icontains=keyword)
            ).filter(college_name=college)



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
            if elapsed_time.days < 30:
                self.request.user.lecture_list.remove(lecture)
            else:
                eva = LectureEva.objects.filter(user=self.request.user).filter(lecture=lecture).count()
                if eva != 0:
                    self.request.user.lecture_list.remove(lecture)
                else:
                    messages.warning(request, 'この講義の履修を解除するには、授業評価を投稿する必要があります。Lectureページのグッドボタンから授業評価画面へと進んでください。')
                    return redirect('register:select_lecture')

        return redirect('register:select_lecture')






class LectureEdit(generic.UpdateView):
    """講義詳細編集ページ"""
    model = Lecture
    template_name = 'register/lecture_edit.html'
    form_class = LectureEditForm



    def form_valid(self, form):
        lecture = form.save(commit=False)
        lecture.save()
        return redirect('register:lecture_top',pk=self.kwargs['pk'],place=0)



class LectureTop(generic.CreateView):
    """授業詳細ページ"""
    model = LectureChat
    template_name = 'register/lecture_top.html'
    form_class = LectureChatForm


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lecture = Lecture.objects.get(id=self.kwargs['pk'])
        context['lecture'] = lecture



        """グラフ"""
        lecture_eva_list = LectureEva.objects.filter(lecture=lecture)
        eva_count = lecture_eva_list.count()
        week_time_total = 0
        last_time_total = 0
        for eva in lecture_eva_list:
            week_time_total += eva.everyweek_time
            last_time_total += eva.last_time

        if week_time_total!=0 and last_time_total!=0:
            context['average_week_time'] = week_time_total/eva_count
            context['average_last_time'] = last_time_total/eva_count
        else:
            context['average_week_time'] = 'No data'
            context['average_last_time'] = 'No data'


        context['gakunen_chart'] = gakunen_chart(self.kwargs['pk'],self.kwargs['place'])
        context['grade_chart'] = grade_chart(self.kwargs['pk'],self.kwargs['place'])
        context['eva_chart'] = eva_chart(self.kwargs['pk'],self.kwargs['place'])
        context['dif_chart'] = dif_chart(self.kwargs['pk'],self.kwargs['place'])
        context['time_week_chart'] = time_week_chart(self.kwargs['pk'],self.kwargs['place'])
        context['time_last_chart'] = time_last_chart(self.kwargs['pk'],self.kwargs['place'])
        context['eva_count'] = LectureEva.objects.filter(lecture=lecture).count()
        context['user_count'] = UserLectureList.objects.filter(lecture=lecture).count()


        age_total = 0
        grade_total = 0
        dif_total = 0
        eva_total = 0

        freshman = LectureEva.objects.filter(lecture=lecture).filter(gakunen_lank=1).count()
        sophomore = LectureEva.objects.filter(lecture=lecture).filter(gakunen_lank=2).count()
        junior = LectureEva.objects.filter(lecture=lecture).filter(gakunen_lank=3).count()
        senior = LectureEva.objects.filter(lecture=lecture).filter(gakunen_lank=4).count()

        if freshman!=0 or sophomore!=0 or junior!=0 or senior!=0:
            age_list = [freshman,sophomore,junior,senior]
            max_age = max(age_list)
            max_age_index = age_list.index(max_age)+1

            if max_age_index == 1:
                context['most_age'] = "Freshman"
            elif max_age_index == 2:
                context['most_age'] = "Sophomore"
            elif max_age_index == 3:
                context['most_age'] = "Junior"
            else:
                context['most_age'] = "Senior"
        else:
            context['most_age'] = "No data"


        for eva in lecture_eva_list:
            age_total += eva.gakunen_lank
            grade_total += eva.grade_lank
            dif_total += eva.dif_lank
            eva_total += eva.eva_lank

        if age_total!=0:
            context['age_average'] = age_total/eva_count
        else:
            context['age_average'] = 'No data'

        if grade_total!=0:
            context['grade_average'] = grade_total/eva_count-1
        else:
            context['grade_average'] = 'No data'

        if dif_total!=0:
            context['dif_average'] = dif_total/eva_count
        else:
            context['dif_average'] = 'No data'

        if eva_total!=0:
            context['eva_average'] = eva_total/eva_count
        else:
            context['eva_average'] = 'No data'


        """詳細"""


        """チャット"""
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







def gakunen_chart(pk,place):
    import matplotlib
    #バックエンドを指定
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import io
    from django.http import HttpResponse
    import japanize_matplotlib

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
    colors = ["#33D69F", "#6F52ED", "#FFB800", '#FF4C61']
    plt.figure(facecolor="#fcfcfc")
    ax = plt.subplot()
    ax.axis("equal")

    pie = ax.pie(datas, #データ
                 startangle=90, #円グラフ開始軸を指定
                 colors=colors, #色指定
                 counterclock=False, #逆時計回り
                 labeldistance=None,
                 wedgeprops={'linewidth': 4, 'edgecolor':"white"}
                 )
    buf = io.BytesIO()
    plt.subplots_adjust(left=-0.06, right=0.65, bottom=0.05, top=0.95)
    #ドーナツ型にするように白い円を上から描写
    #radies:円グラフのサイズ
    plt.pie([100],colors=['#f9f9f9'],radius=0.82)
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
    import japanize_matplotlib

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
    colors = ["#33D69F","#52C8ED", "#6F52ED", "#FFB800", '#FF4C61']
    plt.figure(facecolor="#fcfcfc")
    ax = plt.subplot()
    ax.axis("equal")
    pie = ax.pie(datas, #データ
                 startangle=90, #円グラフ開始軸を指定
                 colors=colors, #色指定
                 counterclock=False, #逆時計回り
                 labeldistance=None,
                 wedgeprops={'linewidth': 4, 'edgecolor':"white"}
                 )
    buf = io.BytesIO()
    plt.subplots_adjust(left=-0.06, right=0.65, bottom=0.05, top=0.95)
    #ドーナツ型にするように白い円を上から描写
    #radies:円グラフのサイズ
    plt.pie([100],colors=['#f9f9f9'],radius=0.82)
    plt.title('成績',x=0.5,y=0.45,size=20,color="#444444")
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
    import japanize_matplotlib

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
    colors = ["#33D69F","#52C8ED", "#6F52ED", "#FFB800", '#FF4C61']
    plt.figure(facecolor="#fcfcfc")
    ax = plt.subplot()
    ax.axis("equal")
    pie = ax.pie(datas, #データ
                 startangle=90, #円グラフ開始軸を指定
                 colors=colors, #色指定
                 counterclock=False, #逆時計回り
                 labeldistance=None,
                 wedgeprops={'linewidth': 4, 'edgecolor':"white"}
                 )
    buf = io.BytesIO()
    plt.subplots_adjust(left=-0.06, right=0.65, bottom=0.05, top=0.95)
    #ドーナツ型にするように白い円を上から描写
    #radies:円グラフのサイズ
    plt.pie([100],colors=['#f9f9f9'],radius=0.82)
    plt.title('総合評価',x=0.5,y=0.45,size=20,color="#444444")
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
    import japanize_matplotlib

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
    colors = ["#33D69F","#52C8ED", "#6F52ED", "#FFB800", '#FF4C61']
    plt.figure(facecolor="#fcfcfc")
    ax = plt.subplot()
    ax.axis("equal")
    pie = ax.pie(datas, #データ
                 startangle=90, #円グラフ開始軸を指定
                 colors=colors, #色指定
                 counterclock=False, #逆時計回り
                 labeldistance=None,
                 wedgeprops={'linewidth': 4, 'edgecolor':"white"}
                 )
    buf = io.BytesIO()
    plt.subplots_adjust(left=-0.06, right=0.65, bottom=0.05, top=0.95)
    #ドーナツ型にするように白い円を上から描写
    #radies:円グラフのサイズ
    plt.pie([100],colors=['#f9f9f9'],radius=0.82)
    plt.title('難易度',x=0.5,y=0.45,size=20,color="#444444")
    plt.savefig(buf, format='png', dpi=200)
    plt.close()
    return base64.b64encode(buf.getvalue()).decode("utf-8").replace("\n", "")



def time_week_chart(pk,place):
    import matplotlib
    #バックエンドを指定
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import io
    from django.http import HttpResponse
    import japanize_matplotlib
    import numpy as np
    from matplotlib.ticker import MaxNLocator

    lecture = Lecture.objects.get(id=pk)
    time_1 = LectureEva.objects.filter(lecture=lecture).filter(everyweek_time__lte=15).count()
    time_2 = LectureEva.objects.filter(lecture=lecture).filter(everyweek_time__gt=15).filter(everyweek_time__lte=30).count()
    time_3 = LectureEva.objects.filter(lecture=lecture).filter(everyweek_time__gt=30).filter(everyweek_time__lte=45).count()
    time_4 = LectureEva.objects.filter(lecture=lecture).filter(everyweek_time__gt=45).filter(everyweek_time__lte=60).count()
    time_5 = LectureEva.objects.filter(lecture=lecture).filter(everyweek_time__gt=60).count()



    # figureを生成する
    #fig = plt.figure(facecolor="#D6FFF1")
    #plt.figure(facecolor="#D6FFF1")

    fig = plt.figure(figsize=(7,4))

    # axをfigureに設定する
    ax = fig.add_subplot(1, 1, 1)
    plt.rcParams["axes.facecolor"] = (1,1,1,0)
    # 対象データ
    left = ['0-15', '16-30', '31-45', '46-60', '61-']  # 横軸(棒の左端の位置)
    height = [time_1, time_2, time_3, time_4, time_5]  # 値
    # 横軸のラベル
    labels = ['0~15', '16~30', '31~45', '46~60', '60~']

    plt.bar(left, height,color="#2F80EC",width=0.6)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.tick_params(bottom=False,
               left=False,
               right=False,
               top=False)
    ax.yaxis.set_major_locator(MaxNLocator(5))
    plt.xticks(fontsize=15,color="#747474")
    plt.yticks(fontsize=15,color="#747474")
    plt.grid(axis='y',color = "#e3e3e3", linewidth=1)
    plt.rcParams['axes.axisbelow'] = True
    plt.show()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=200)
    plt.close()
    return base64.b64encode(buf.getvalue()).decode("utf-8").replace("\n", "")


def time_last_chart(pk,place):
    import matplotlib
    #バックエンドを指定
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import io
    from django.http import HttpResponse
    import japanize_matplotlib
    import numpy as np
    from matplotlib.ticker import MaxNLocator

    lecture = Lecture.objects.get(id=pk)
    time_1 = LectureEva.objects.filter(lecture=lecture).filter(last_time__lte=30).count()
    time_2 = LectureEva.objects.filter(lecture=lecture).filter(last_time__gt=30).filter(last_time__lte=60).count()
    time_3 = LectureEva.objects.filter(lecture=lecture).filter(last_time__gt=60).filter(last_time__lte=90).count()
    time_4 = LectureEva.objects.filter(lecture=lecture).filter(last_time__gt=90).filter(last_time__lte=120).count()
    time_5 = LectureEva.objects.filter(lecture=lecture).filter(last_time__gt=120).count()


    # figureを生成する
    #fig = plt.figure(facecolor="#D6FFF1")
    #plt.figure(facecolor="#D6FFF1")

    fig = plt.figure(figsize=(7,4))

    # axをfigureに設定する
    ax = fig.add_subplot(1, 1, 1)
    plt.rcParams["axes.facecolor"] = (1,1,1,0)
    # 対象データ
    left = ['0-30', '30-60', '60-90', '90-120', '121-']  # 横軸(棒の左端の位置)
    height = [time_1, time_2, time_3, time_4, time_5]  # 値
    # 横軸のラベル
    labels = ['A', 'B', 'C', 'D', 'E']

    plt.bar(left, height,color="#2F80EC",width=0.6)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.tick_params(bottom=False,
               left=False,
               right=False,
               top=False)
    ax.yaxis.set_major_locator(MaxNLocator(5))
    plt.xticks(fontsize=15,color="#747474")
    plt.yticks(fontsize=15,color="#747474")
    plt.grid(axis='y',color = "#e3e3e3", linewidth=1)
    plt.rcParams['axes.axisbelow'] = True
    plt.show()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=200)
    plt.close()
    return base64.b64encode(buf.getvalue()).decode("utf-8").replace("\n", "")




class Evaluate(generic.TemplateView):
    """授業評価投稿ページ"""
    model = LectureEva
    template_name = 'register/eva_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lecture_list'] = self.request.user.lecture_list.all()#履修中の講義リスト
        eva_list = LectureEva.objects.filter(user=self.request.user)#評価済みのレコード
        lecture_list = []
        for lecture_eva in eva_list:
            lecture_list.append(lecture_eva.lecture)
        context['user_lecture_eva_list'] = lecture_list#評価済みの講義のリストを作製

        return context


    def post(self, request):
        #履修中の講義リスト
        lecture_list = self.request.user.lecture_list.all()
        #評価投稿済
        eva_list = LectureEva.objects.filter(user=self.request.user)
        #対象リストの作成
        eva_lecture_list = []
        for lecture in eva_list:
            eva_lecture_list.append(lecture.lecture)

        for lecture in lecture_list:
            if lecture not in eva_lecture_list:#評価済みの講義は処理を行わない
                gakunen = self.request.user.user_age
                grade_id = "grade{}".format(lecture.id)
                grade = request.POST[grade_id]
                eva_id = "eva{}".format(lecture.id)
                eva = request.POST[eva_id]
                dif_id = "dif{}".format(lecture.id)
                dif = request.POST[dif_id]
                week_time_id = "week{}".format(lecture.id)
                week_time = request.POST[week_time_id]
                last_time_id = "last{}".format(lecture.id)
                last_time = request.POST[last_time_id]

                #field値を指定して作成
                LectureEva.objects.create(
                gakunen_lank=gakunen,grade_lank=grade,eva_lank=eva,dif_lank=dif,everyweek_time=week_time,last_time=last_time,place=1,lecture=lecture,user=self.request.user
                )


        return redirect('register:top')




class Help_top(generic.TemplateView):
    template_name = 'register/help_top.html'

class Help_contents(generic.TemplateView):
    template_name = 'register/help_contents.html'

    def get_context_data(self, **kwargs,):
        context = super().get_context_data(**kwargs)
        context['help_pk'] = self.kwargs['pk']
        return context





class CircleList(generic.ListView):
    model = Circle
    template_name = 'register/circle_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        college = user.college_name

        keyword = self.request.GET.get('keyword')
        if keyword:
            circle_list = Circle.objects.filter(circle_name__icontains=keyword).filter(college=college)
            context['circle_list_1'] = circle_list
            context['circle_list_2'] = circle_list
            context['circle_list_3'] = circle_list
            context['circle_list_4'] = circle_list
        else:
            context['circle_list_1'] = Circle.objects.filter(college=college).filter(genre=1)
            context['circle_list_2'] = Circle.objects.filter(college=college).filter(genre=2)
            context['circle_list_3'] = Circle.objects.filter(college=college).filter(genre=3)
            context['circle_list_4'] = Circle.objects.filter(college=college).filter(genre=4)

        return context


class CircleDetail(generic.DetailView):
    model = Circle
    template_name = 'register/circle_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']
        circle = Circle.objects.get(id=self.kwargs['pk'])
        context['board_list'] = Board.objects.filter(circle=circle).order_by('-created_at')
        user = self.request.user
        context['user'] = user

        return context

    def post(self, request, pk):
         if request.method == 'POST':
             if 'circle' in request.POST:
                 circle_id = request.POST['circle']
                 circle = Circle.objects.get(id=circle_id)
                 user = self.request.user
                 if user in circle.user_list.all():
                     circle.user_list.remove(user)
                 else:
                     circle.user_list.add(user)
             elif 'board' in request.POST:
                 board_id = request.POST['board']
                 board = Board.objects.get(id=board_id)
                 user = self.request.user

                 if user in board.good_user.all():
                     board.good_user.remove(user)
                     board.good = board.good - 1
                     board.save()
                 else:
                     board.good_user.add(user)
                     board.good = board.good + 1
                     board.save()
             return redirect('register:circle_detail',pk=self.kwargs['pk'])






class CircleCreate(generic.UpdateView):
    model = Circle
    template_name = 'register/circle_create.html'
    form_class = CircleCreateForm


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        circle = Circle.objects.get(id=self.kwargs['pk'])
        user_bool = False
        if user in circle.editor_list.all():
            user_bool = True
        context['user_bool'] = user_bool
        return context

    def form_valid(self, form):
        circle = form.save(commit=False)
        image = circle.image
        print(image)
        circle.save()

        return redirect('register:circle_detail',pk=self.kwargs['pk'])


class BoardCreate(generic.CreateView):
    model = Board
    template_name = 'register/board_create.html'
    form_class = BoardCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']
        user = self.request.user
        circle = Circle.objects.get(id=self.kwargs['pk'])
        user_bool = False
        if user in circle.editor_list.all():
            user_bool = True
        context['user_bool'] = user_bool
        return context


    def form_valid(self, form):
        user = self.request.user
        college = user.college_name
        circle = Circle.objects.get(id=self.kwargs['pk'])
        board = form.save(commit=False)
        board.college = college
        board.circle = circle
        board.save()
        return redirect('register:circle_detail',pk=self.kwargs['pk'])

class BoardCreateIndi(generic.CreateView):
    model = Board
    template_name = 'register/board_create_indi.html'
    form_class = BoardCreateIndiForm

    def form_valid(self, form):
        user = self.request.user
        college = user.college_name
        board = form.save(commit=False)
        board.college = college
        board.post_user = user
        board.status_num = 1
        board.save()
        return redirect('register:board_list')



class BoardList(generic.ListView):
    model = Board
    template_name = 'register/board_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        college = user.college_name
        context['board_list'] = Board.objects.filter(college=college).order_by('-created_at')
        context['board_list_only_college'] = Board.objects.filter(college=college).filter(status_num=0).order_by('-created_at')

        return context

    def post(self, request):
        board_id = request.POST['board']
        board = Board.objects.get(id=board_id)
        user = self.request.user

        if user in board.good_user.all():
            board.good_user.remove(user)
            board.good = board.good - 1
            board.save()
        else:
            board.good_user.add(user)
            board.good = board.good + 1
            board.save()

        return redirect('register:board_list')



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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        circle_list = user.editor_list.all()
        context['circle_list'] = circle_list
        return context



class UserCircleSearch(generic.TemplateView):
    """サークルパスワード入力ページ"""
    model = Circle
    template_name = "register/user_circle_search.html"

class UserCircleAdd(generic.TemplateView):
    """編集ユーザ追加ページ"""
    models = Circle
    template_name = "register/user_circle_add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        circle = Circle.objects.get(id=self.kwargs['pk'])
        context['circle'] = circle
        context['user'] = self.request.user
        return context

    def post(self, request,**kwargs):
        circle = Circle.objects.get(id=self.kwargs['pk'])
        password = request.POST['password']
        if circle.circle_password == password:
            user = self.request.user
            if user in circle.editor_list.all():
                circle.editor_list.remove(user)
            else:
                circle.editor_list.add(user)
                circle.user_list.add(user)
            return redirect('register:circle_detail',pk=self.kwargs['pk'])
        else:
            return redirect('register:user_circle_add',pk=self.kwargs['pk'])

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


class Terms(generic.TemplateView):
    """利用規約ページ"""
    template_name = 'register/terms.html'
