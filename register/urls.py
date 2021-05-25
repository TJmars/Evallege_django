from django.urls import path
from . import views

app_name = 'register'

urlpatterns = [
    #ログイン、ユーザー登録関係
    path('',views.first.as_view(), name='first'),
    path('top/', views.Top.as_view(), name='top'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('user_create/', views.UserCreate.as_view(), name='user_create'),
    path('user_create/done/', views.UserCreateDone.as_view(), name='user_create_done'),
    path('user_create/complete/<token>/', views.UserCreateComplete.as_view(), name='user_create_complete'),
    path('user_detail/<int:pk>/', views.UserDetail.as_view(), name='user_detail'),
    path('user_update/<int:pk>/', views.UserUpdate.as_view(), name='user_update'),
    path('password_change/', views.PasswordChange.as_view(), name='password_change'),
    path('password_change/done/', views.PasswordChangeDone.as_view(), name='password_change_done'),
    path('password_reset/', views.PasswordReset.as_view(), name='password_reset'),
    path('password_reset/done/', views.PasswordResetDone.as_view(), name='password_reset_done'),
    path('password_reset/confirm/<uidb64>/<token>/', views.PasswordResetConfirm.as_view(), name='password_reset_confirm'),
    path('password_reset/complete/', views.PasswordResetComplete.as_view(), name='password_reset_complete'),
    path('email/change/', views.EmailChange.as_view(), name='email_change'),
    path('email/change/done/', views.EmailChangeDone.as_view(), name='email_change_done'),
    path('email/change/complete/<str:token>/', views.EmailChangeComplete.as_view(), name='email_change_complete'),

    #講義登録画面
    path('select_lecture/', views.SelectLecture.as_view(), name='select_lecture'),
    #新規講義作成画面
    path('create_lecture/', views.LectureCreate.as_view(), name='create_lecture'),
    #講義詳細画面
    path('detail/<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('projectB/register/grade_chart/<int:pk>', views.grade_chart,name="grade_chart"),
    path('projectB/register/eva_chart/<int:pk>', views.eva_chart,name="eva_chart"),
    path('projectB/register/dif_chart/<int:pk>', views.dif_chart,name="dif_chart"),
    #授業評価投稿画面
    path('evaluate/<int:pk>/', views.Evaluate.as_view(), name='evaluate'),
]