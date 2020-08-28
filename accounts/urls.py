from django.urls import path
from . import views

urlpatterns = [
    path('login',views.Login.as_view(),name='login'),
    path('logout',views.Logout.as_view(),name='logout'),
    path('newaccount',views.UserCreate.as_view(),name='newaccount'),
    #↓もういらないかも
    path('usercreate_done',views.UserCreateDone,name='usercreate_done'),
    path('mypage',views.Mypage,name='mypage'),
    path('mypage/edit',views.Edit,name='edit'),
    path('mypage/passwordchange',views.PasswordChange.as_view(),name='passwordchange'),
    path('passwordchange/done',views.PasswordChangeDone.as_view(),name='passwordchange_done'),
]
