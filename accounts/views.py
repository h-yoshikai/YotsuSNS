from django.shortcuts import render,redirect,resolve_url
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView,LogoutView,PasswordChangeView,PasswordChangeDoneView,
    PasswordResetConfirmView,PasswordResetCompleteView
)
from django.views import generic
from .forms import (
    LoginForm,UserCreateForm,UserUpdateForm,ProfileForm,MyPasswordChangeForm
)
from django.urls import reverse_lazy

from django.conf import settings
from django.contrib.auth import get_user_model,login,authenticate
from django.contrib.auth.mixins import UserPassesTestMixin

from .models import AuthUser,Profile,Follow
from django.conf import settings

import os

User=get_user_model()
# Create your views here.
class Login(LoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'

class Logout(LoginRequiredMixin,LogoutView):
    template_name = 'accounts/logout.html'

class UserCreate(generic.CreateView,UserPassesTestMixin):
    form_class = UserCreateForm
    template_name = 'accounts/user_create.html'
    success_url = reverse_lazy("mypage")

    #ユーザを作成すると自動的にログイン，success_urlにとぶ
    def form_valid(self,form):
        response = super().form_valid(form)
        username = form.cleaned_data.get('username')
        raw_pw = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=raw_pw)
        login(self.request, user)
        profile=Profile(owner=self.request.user)
        profile.save()
        return response

#ユーザ作成時にProfileを紐づけるために関数に変更（もういらないかも）
def UserCreateDone(request):
    user=request.user
    profile=Profile(owner=user)
    profile.save()

    return render(request,'accounts/user_create_done.html')

@login_required(login_url='accounts/login')
def Mypage(request):
    user=request.user
    #AuthUserからProfileを逆引き
    profile=user.profile_owner.get()
    params={
        'user':user,
        'profile':profile,
    }
    return render(request,'accounts/mypage.html',params)

@login_required(login_url='accounts/login')
def Edit(request):
    user=request.user
    #AuthUserからProfileを逆引き
    profile=user.profile_owner.get()
    params={
        'userform':UserUpdateForm(instance=user),
        'profileform':ProfileForm(instance=profile),
    }
    original=''
    large=''
    thumbnail=''
    medium=''
    if request.method=='POST':
        #以前のファイルがあればそのファイルのパスを取得
        previous=profile.pro_image.name
        if previous != '':
            original=os.path.join(settings.MEDIA_ROOT,profile.pro_image.name)
            print('original:'+original)
            large=os.path.join(settings.MEDIA_ROOT,profile.pro_image.large.name)
            thumbnail=os.path.join(settings.MEDIA_ROOT,profile.pro_image.thumbnail.name)
            medium=os.path.join(settings.MEDIA_ROOT,profile.pro_image.medium.name)

        userform=UserUpdateForm(request.POST,instance=user)
        profileform=ProfileForm(request.POST,request.FILES,instance=profile)
        if userform.is_valid() and profileform.is_valid():
            #以前のファイルがあれば削除
            #この時点でuserとprofileの情報変わってる
            if previous != '':
                os.remove(original)
                os.remove(large)
                os.remove(thumbnail)
                os.remove(medium)
            userform.save()
            profileform.save()
            return redirect(to='/accounts/mypage')
        else:
            params['userform']=userform
            params['profileform']=profileform

    return render(request,'accounts/accountedit.html',params)

class PasswordChange(PasswordChangeView):
    form_class = MyPasswordChangeForm
    success_url = reverse_lazy('passwordchange_done')
    template_name = 'accounts/changepass.html'

class PasswordChangeDone(PasswordChangeDoneView):
    template_name = 'accounts/passwordchange_done.html'

@login_required(login_url='/accounts/login')
def FollowPage(request,user_id):
    #リストにしたい場合はfilterもしくは，[user]にする
    #見たいユーザのオブジェクトを取得
    user=AuthUser.objects.get(username=user_id)
    #followedが，userがフォローしている人になる
    following=Follow.objects.filter(owner=user)
    counts=[]
    flag=1
    #この後に，見ているユーザ(request.user)が，followに入っているユーザをフォローしているかどうか調べる
    for i in range(len(following)):
        count=Follow.objects.filter(owner=request.user,followed=following[i].followed).count()
        if request.user == following[i].followed:
            count=-1
        counts.append(count)
    params={
        'follow':zip(following,counts),
        'flag':flag,
    }
    return render(request,'accounts/follow.html',params)

@login_required(login_url='/accounts/login')
def FollowersPage(request,user_id):
    user=AuthUser.objects.get(username=user_id)
    #ownerが，userのフォロワーになる
    followers=Follow.objects.filter(followed=user)
    counts=[]
    flag=0
    #自分がその人のフォロワーをフォローしているか調べる
    for i in range(len(followers)):
        count=Follow.objects.filter(owner=request.user,followed=followers[i].owner).count()
        if request.user == followers[i].owner:
            count=-1
        counts.append(count)
    params={
        'follow':zip(followers,counts),
        'flag':flag,
    }
    return render(request,'accounts/follow.html',params)

@login_required(login_url='/accounts/login')
def AllUsers(request):
    #adminが表示されないようにしたい
    users=AuthUser.objects.all()
    counts=[]
    #request.userがフォローしているかどうか調べる
    for i in range(len(users)):
        count=Follow.objects.filter(owner=request.user,followed=users[i]).count()
        if request.user == users[i]:
            count=-1
        counts.append(count)

    params={
        'alluser':zip(users,counts),
    }
    return render(request,'accounts/allusers.html',params)

@login_required(login_url='/accounts/login')
def Followadd(request,user_id):
    #userがfollowedをフォローする
    user=request.user
    followed=AuthUser.objects.get(username=user_id)
    #followedが本人だったとき
    #先にowner,followed両方自分のレコードを保存するのもあり？
    if followed == request.user:
        #あとで書き換える
        return redirect(to='/accounts/'+user_id+'/following')

    #followedがフォローされているか確認
    num=Follow.objects.filter(owner=request.user).filter(followed=followed).count()
    if num>0:
        #あとで書き換える
        return redirect(to='/accounts/'+user_id+'/following')

    fol=Follow()
    fol.owner=request.user
    fol.followed=followed
    fol.save()
    return redirect(to='/accounts/allusers')

@login_required(login_url='/accounts/login')
def UserPage(request,user_id):
    #表示するユーザを取得
    owner=AuthUser.objects.get(username=user_id)
    #フォロワー，フォロー中の数を調べる
    followercount=Follow.objects.filter(followed=owner).count()
    followingcount=Follow.objects.filter(owner=owner).count()
    #自分がそのユーザ(owner)をフォローしているかどうか調べる
    count=Follow.objects.filter(owner=request.user,followed=owner).count()
    if request.user == owner:
        count=-1
    params={
        'user':owner,
        'followercount':followercount,
        'followingcount':followingcount,
        'count':count,
    }
    return render(request,'accounts/userpage.html',params)
