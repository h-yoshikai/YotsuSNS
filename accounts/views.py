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
    LoginForm,UserCreateForm
)
from django.urls import reverse_lazy

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin

from .models import AuthUser,Profile

User=get_user_model()
# Create your views here.
class Login(LoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'

class UserCreate(generic.CreateView,UserPassesTestMixin):
    form_class = UserCreateForm
    template_name = 'accounts/user_create.html'
    success_url = reverse_lazy("usercreate_done")

class UserCreateDone(generic.TemplateView):
    template_name = 'accounts/user_create_done.html'

@login_required(login_url='accounts/login')
def Mypage(request):
    user=request.user
    profile=Profile.objects.get(owner=user)
    params={
        'user':user,
        'profile':profile,
    }
    return render(request,'accounts/mypage.html',params)
