from django.urls import path
from . import views

urlpatterns = [
    path('login',views.Login.as_view(),name='login'),
    path('newaccount',views.UserCreate.as_view(),name='newaccount'),
    #↓もういらないかも
    path('usercreate_done',views.UserCreateDone,name='usercreate_done'),
    path('mypage',views.Mypage,name='mypage'),
    path('mypage/edit',views.Edit,name='edit'),
]
