from django.urls import path
from . import views

urlpatterns = [
    path('login',views.Login.as_view(),name='login'),
    path('newaccount',views.UserCreate.as_view(),name='newaccount'),
    path('usercreate_done',views.UserCreateDone.as_view(),name='usercreate_done'),
    path('mypage',views.Mypage,name='mypage'),
]
