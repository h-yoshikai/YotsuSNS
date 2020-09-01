from django.contrib.auth.forms import AuthenticationForm,UserCreationForm,PasswordChangeForm,PasswordResetForm,SetPasswordForm

from django.contrib.auth import get_user_model
from .models import AuthUser,Profile,Message
from django import forms
import re
from django.contrib.auth import authenticate
from file_resubmit.admin import AdminResubmitImageWidget

User=get_user_model()

class LoginForm(AuthenticationForm):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['username'].label='ユーザID'
        self.fields['password'].label='パスワード'
        ###フィールドのクラスとラベルを設定###
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

class UserCreateForm(UserCreationForm,forms.ModelForm):
    class Meta:
        model = User
        fields = ('username','email')

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

        self.fields['password1'].label='パスワード'
        self.fields['password1'].help_text='8文字以上の英数字を設定してください'
        self.fields['password2'].label='パスワード（確認）'
        self.fields['password2'].help_text='確認のためもう一度パスワードを入力'
        #self.fields['username'].widget.attrs['placeholder']='例：'
        self.fields['username'].label='ユーザID'
        self.fields['username'].help_text='6文字以上の英数字を設定してください'
        self.fields['email'].label='メールアドレス'

    def clean_username(self):
        name=self.cleaned_data.get('username')
        alnumReg = re.compile(r'^[a-zA-Z0-9]+$')
        if not alnumReg.match(name):
            self.add_error('username','半角英数字で入力してください')
        if name is None:
            self.add_error('username','ユーザIDを設定してください')
        if len(name)<6:
            self.add_error('username','ユーザIDは6文字以上で設定してください')
        if AuthUser.objects.filter(username=name).exists():
            self.add_error('username','そのユーザIDは既に使われています')

        return name

    def clean_password1(self):
        password1=self.cleaned_data.get('password1')
        if len(password1)<8:
            self.add_error('password1','パスワードは8文字以上で設定してください')
        return password1

    def clean_password2(self):
        password1=self.cleaned_data.get('password1')
        password2=self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            self.add_error('password2','パスワードが一致しません')
        return password2

    def clean_email(self):
        email=self.cleaned_data.get('email')
        print(email)
        if AuthUser.objects.filter(email=email).exists():
            self.add_error('email','そのメールアドレスは既に使われています')
        return email

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username','email')

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

        self.fields['username'].label='ユーザID'
        self.fields['username'].help_text='6文字以上の英数字を設定してください'
        self.fields['email'].label='メールアドレス'

    def clean_username(self):
        name=self.cleaned_data.get('username')
        alnumReg = re.compile(r'^[a-zA-Z0-9]+$')
        if not alnumReg.match(name):
            self.add_error('username','半角英数字で入力してください')
        if name is None:
            self.add_error('username','ユーザIDを設定してください')
        if len(name)<6:
            self.add_error('username','ユーザIDは6文字以上で設定してください')
        #if AuthUser.objects.filter(username=name).exists():
        #    self.add_error('username','そのユーザIDは既に使われています')

        return name

    #def clean_email(self):
    #    email=self.cleaned_data.get('email')
    #    print(email)
    #    if AuthUser.objects.filter(email=email).exists():
    #        self.add_error('email','そのメールアドレスは既に使われています')
    #    return email

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('pro_image','name','profile_text')

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class MyPasswordChangeForm(PasswordChangeForm):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['image','content']

class MessageContentForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content':forms.Textarea(
                attrs={'placeholder':'キャプションを書く','rows':'5'}
            )
        }

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

        self.fields['content'].label='キャプション'

class MessageImageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['image']
        widgets = {
            'image':AdminResubmitImageWidget(),
        }
