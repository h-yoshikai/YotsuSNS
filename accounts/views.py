from django.shortcuts import render,redirect,resolve_url
from django.http import HttpResponseRedirect
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
    LoginForm,UserCreateForm,UserUpdateForm,ProfileForm,MyPasswordChangeForm,MessageForm,MessageImageForm,MessageContentForm,TagForm
)
from django.urls import reverse_lazy

from django.conf import settings
from django.contrib.auth import get_user_model,login,authenticate
from django.contrib.auth.mixins import UserPassesTestMixin

from .models import AuthUser,Profile,Follow,Message,Tag,Good
from django.conf import settings
import re

from django.template.loader import render_to_string
from django.http import JsonResponse

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
    #自分がそのユーザ(owner)をフォローしているかどうか調べる
    isFollow=Follow.objects.filter(owner=request.user,followed=user).count()
    if request.user == user:
        isFollow=-1
    #この後に，見ているユーザ(request.user)が，followに入っているユーザをフォローしているかどうか調べる
    for i in range(len(following)):
        count=Follow.objects.filter(owner=request.user,followed=following[i].followed).count()
        if request.user == following[i].followed:
            count=-1
        counts.append(count)
    params={
        'focususer':user,
        'follow':zip(following,counts),
        'flag':flag,
        'count':isFollow,
    }
    return render(request,'accounts/follow.html',params)

@login_required(login_url='/accounts/login')
def FollowersPage(request,user_id):
    user=AuthUser.objects.get(username=user_id)
    #ownerが，userのフォロワーになる
    followers=Follow.objects.filter(followed=user)
    counts=[]
    flag=0
    #自分がそのユーザ(owner)をフォローしているかどうか調べる
    isFollow=Follow.objects.filter(owner=request.user,followed=user).count()
    if request.user == user:
        isFollow=-1

    #自分がその人のフォロワーをフォローしているか調べる
    for i in range(len(followers)):
        count=Follow.objects.filter(owner=request.user,followed=followers[i].owner).count()
        if request.user == followers[i].owner:
            count=-1
        counts.append(count)
    params={
        'focususer':user,
        'follow':zip(followers,counts),
        'flag':flag,
        'count':isFollow,
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
def Followadd(request):
    #userがfollowedをフォローする
    user=request.user
    user_id=request.POST.get('username')
    followed=AuthUser.objects.get(username=user_id)
    #followedが本人だったとき
    #先にowner,followed両方自分のレコードを保存するのもあり？
    if followed == request.user:
        #あとで書き換える
        return redirect(to='/accounts/'+user_id+'/following')

    #followedがフォローされているか確認
    num=Follow.objects.filter(owner=request.user).filter(followed=followed).count()
    if num>0:
        #あとで書き換える(解除処理？)
        data=Follow.objects.get(owner=request.user,followed=followed)
        data.delete()
        if request.is_ajax():
            return JsonResponse({'result':'OK'})

    fol=Follow()
    fol.owner=request.user
    fol.followed=followed
    fol.save()
    if request.is_ajax():
        return JsonResponse({'result':'OK'})
    #return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

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
    #表示するユーザの投稿を取得
    usermessages=Message.objects.filter(owner=owner)
    params={
        'user':owner,
        'followercount':followercount,
        'followingcount':followingcount,
        'count':count,
        'usermessages':usermessages,
    }
    return render(request,'accounts/userpage.html',params)

@login_required(login_url='/accounts/login')
def Post(request):
    imform=MessageImageForm()
    params={
        'imageform':imform,
    }
    return render(request,'accounts/postcreate.html',params)

@login_required(login_url='/accounts/login')
def PostDetail(request):
    #/createから来た場合（画像の確認）
    if request.method == 'POST' and request.POST['mode'] == '__image__':
        obj=Message(owner=request.user)
        imageform=MessageImageForm(request.POST,request.FILES,instance=obj)
        if imageform.is_valid():
            imageform.save()
            newobj=Message.objects.get(myid=obj.myid)
            params={
                'messageform':MessageContentForm(instance=newobj),
                'tagform':TagForm(),
                'mess':newobj,
            }
            return render(request,'accounts/postdetail.html',params)
    #/create/detailから来た場合（キャプション，タグの確認）
    elif request.method == 'POST' and request.POST['mode'] == '__content__':
        obj=Message.objects.get(myid=request.POST['myid'])
        contentform=MessageContentForm(request.POST,instance=obj)
        tagform=TagForm(request.POST)
        #フォーム内容が正しければ保存してマイページへ（あとからタイムラインに行くようにする）
        if contentform.is_valid() and tagform.is_valid():
            #キャプションの保存
            contentform.save()
            #タグの保存
            saveTags(request.POST['tagfield'],request.POST['myid'])
            return redirect(to='/accounts/mypage')
        #フォーム内容がよくなければ，エラーメッセージを表示（ページそのまま）
        else:
            params={
                'messageform':contentform,
                'tagform':tagform,
                'mess':obj,
            }
            return render(request,'accounts/postdetail.html',params)

    return redirect(to='/accounts/create')

@login_required(login_url='/accounts/login')
def PostCancel(request,myid):
    #編集中だったメッセージを取得
    obj=Message.objects.get(myid=myid)
    #保存した画像のパスを取得
    original=os.path.join(settings.MEDIA_ROOT,obj.image.name)
    large=os.path.join(settings.MEDIA_ROOT,obj.image.large.name)
    thumbnail=os.path.join(settings.MEDIA_ROOT,obj.image.thumbnail.name)
    medium=os.path.join(settings.MEDIA_ROOT,obj.image.medium.name)
    #画像を削除
    os.remove(original)
    os.remove(large)
    os.remove(thumbnail)
    os.remove(medium)
    #メッセージを削除
    obj.delete()

    return redirect(to='/accounts/create')

@login_required(login_url='accounts/login')
def AllPosts(request):
    messobjs=Message.objects.all()
    likelist=[]
    numlike=[]
    for mess in messobjs:
        liked=Good.objects.filter(owner=request.user,message=mess).count()
        count=Good.objects.filter(message=mess).count()
        likelist.append(liked)
        numlike.append(count)

    params={
        'allmessages':zip(messobjs,likelist,numlike),
    }
    return render(request,'accounts/allposts.html',params)

@login_required(login_url='accounts/login')
def TimeLine(request):
    #フォローしている人のメッセージを取得
    #followedが，userがフォローしている人になる
    following=Follow.objects.filter(owner=request.user)
    followlist=[]
    likelist=[]
    numlike=[]
    for i in range(len(following)):
        followlist.append(following[i].followed)

    messobjs=Message.objects.filter(owner__in=followlist)
    for mess in messobjs:
        liked=Good.objects.filter(owner=request.user,message=mess).count()
        count=Good.objects.filter(message=mess).count()
        likelist.append(liked)
        numlike.append(count)

    params={
        'allmessages':zip(messobjs,likelist,numlike),
    }
    return render(request,'accounts/timeline.html',params)

@login_required(login_url='accounts/login')
def good(request,myid):
    obj=Message.objects.get(myid=myid)
    if Good.objects.filter(owner=request.user,message=obj).exists():
        #既にいいね！をされている
        #解除
        Good.objects.get(owner=request.user,message=obj).delete()
    else:
        newgood=Good(owner=request.user,message=obj)
        newgood.save()
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

@login_required(login_url='accounts/login')
def goodtry(request):
    print(request.is_ajax())
    if 'messmyid' in request.POST:
        print("Exist")
    else:
        print("Not")
    obj=Message.objects.get(myid=request.POST.get('messmyid'))
    if Good.objects.filter(owner=request.user,message=obj).exists():
        #既にいいね！をされている
        #解除
        Good.objects.get(owner=request.user,message=obj).delete()
    else:
        newgood=Good(owner=request.user,message=obj)
        newgood.save()

    count=Good.objects.filter(message=obj).count()

    if request.is_ajax():
    #html=render_to_string('accounts/allposts.html',params,request=request)
        return JsonResponse({'result':'OK','count':count})
    #return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

def saveTags(strtags,myid):
    #タグのリストを作成
    list=[re.sub(r'\s+','',x) for x in strtags.split('#') if not x == '']
    obj=Message.objects.get(myid=myid)
    for tag in list:
        num=Tag.objects.filter(tagname=tag).count()
        if num == 0:
            tagobj=Tag.objects.create(tagname=tag)
            tagobj.relmessage.add(obj)
            tagobj.save()
        else:#既にタグが存在している場合
            tagobj=Tag.objects.get(tagname=tag)
            tagobj.relmessage.add(obj)
            tagobj.save()
