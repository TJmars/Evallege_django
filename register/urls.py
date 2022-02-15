from django.urls import path
from . import views
from projectB import settings
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import url
from django.views.static import serve

app_name = 'register'

urlpatterns = [

    path('top/', views.Top.as_view(), name='top'),
    path('', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('user_create/', views.UserCreate.as_view(), name='user_create'),
    path('user_create/done/', views.UserCreateDone.as_view(), name='user_create_done'),
    path('user_create/complete/<token>/', views.UserCreateComplete.as_view(), name='user_create_complete'),
    #ユーザー詳画面
    path('user_detail/<int:pk>/', views.UserDetail.as_view(), name='user_detail'),
    path('user_circle_search/', views.UserCircleSearch.as_view(), name='user_circle_search'),
    path('user_circle_add/<int:pk>/', views.UserCircleAdd.as_view(), name='user_circle_add'),

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
    path('lecture_top/<int:pk>/<int:place>/', views.LectureTop.as_view(), name='lecture_top'),
    path('lecture_edit/<int:pk>/', views.LectureEdit.as_view(), name='lecture_edit'),
    path('projectB/register/gakunen_chart/<int:pk>/<int:place>', views.gakunen_chart,name="gakunen_chart"),
    path('projectB/register/grade_chart/<int:pk>/<int:place>', views.grade_chart,name="grade_chart"),
    path('projectB/register/eva_chart/<int:pk>/<int:place>', views.eva_chart,name="eva_chart"),
    path('projectB/register/dif_chart/<int:pk>/<int:place>', views.dif_chart,name="dif_chart"),
    path('projectB/register/time_week_chart/<int:pk>/<int:place>', views.time_week_chart,name="time_week_chart"),
    path('projectB/register/time_last_chart/<int:pk>/<int:place>', views.time_last_chart,name="time_last_chart"),
    #授業評価投稿画面
    path('evaluate/', views.Evaluate.as_view(), name='evaluate'),
    #ヘルプ画面
    path('help/top/',views.Help_top.as_view(), name='help_top'),
    path('help/contents/<int:pk>/',views.Help_contents.as_view(), name='help_contents'),

    #サークル掲示板
    path('circle_list/', views.CircleList.as_view(), name='circle_list'),
    path('circle_create/<int:pk>/', views.CircleCreate.as_view(), name='circle_create'),
    path('circle_detail/<int:pk>/',views.CircleDetail.as_view(),name='circle_detail'),
    path('board_create/<int:pk>/',views.BoardCreate.as_view(),name='board_create'),
    path('board_create_indi/',views.BoardCreateIndi.as_view(),name='board_create_indi'),

    #ボード
    path('board_list/',views.BoardList.as_view(),name='board_list'),
    #利用規約
    path('terms/',views.Terms.as_view(),name='terms'),

    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
