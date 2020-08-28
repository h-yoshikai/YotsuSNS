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
    LoginForm,UserCreateForm,UserUpdateForm,ProfileForm
)
from django.urls import reverse_lazy

from django.conf import settings
from django.contrib.auth import get_user_model,login,authenticate
from django.contrib.auth.mixins import UserPassesTestMixin

from .models import AuthUser,Profile
from django.conf import settings

import os

User=get_user_model()
# Create your views here.
class Login(LoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'

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
