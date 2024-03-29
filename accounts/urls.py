from django.urls import path
from . import views

urlpatterns = [
    path('login',views.Login.as_view(),name='login'),
    path('logout',views.Logout.as_view(),name='logout'),
    path('newaccount',views.UserCreate.as_view(),name='newaccount'),
    path('timeline',views.TimeLine,name='timeline'),
    #↓もういらないかも
    path('usercreate_done',views.UserCreateDone,name='usercreate_done'),
    path('mypage',views.Mypage,name='mypage'),
    path('mypage/edit',views.Edit,name='edit'),
    path('mypage/passwordchange',views.PasswordChange.as_view(),name='passwordchange'),
    path('passwordchange/done',views.PasswordChangeDone.as_view(),name='passwordchange_done'),
    #フォローしている人一覧ページ
    path('<str:user_id>/following',views.FollowPage,name='following'),
    path('<str:user_id>/followers',views.FollowersPage,name='followers'),
    #一時的に追加
    path('allusers',views.AllUsers,name='allusers'),
    path('allposts',views.AllPosts,name='allposts'),
    path('create',views.Post,name='create'),
    path('create/detail',views.PostDetail,name='detail'),
    path('postcancel/<int:myid>',views.PostCancel,name='postcancel'),
    path('good/<int:myid>',views.good,name='good'),
    #goodのもう一つ試し
    path('goodtry',views.goodtry,name='goodtry'),
    #フォロー処理のトライ
    path('followingtry',views.Followadd,name='followtry'),
    path('<str:user_id>',views.UserPage,name='userpage'),
]
