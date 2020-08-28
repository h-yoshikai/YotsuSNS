from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator
from stdimage.models import StdImageField
import os

# Create your models here.
class AuthUserManager(BaseUserManager):
    def create_user(self, username, password, email):
        if not username:
            raise ValueError('Users must have an username')
        if not email:
            raise ValueError('Users must have an email')

        user = self.model(
                username=username,
                email=email
                )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, email):
        user = self.create_user(
                username=username,
                password=password,
                email=email)

        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class AuthUser(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name='ユーザ'

    #ユーザID
    username = models.CharField(
        verbose_name='ユーザID',
        unique=True,
        max_length=30,
    )
    #メールアドレス
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    objects = AuthUserManager()

    def __str__(self):
        return self.username

class Profile(models.Model):
    #AuthUserとの関連
    owner=models.ForeignKey(
        AuthUser,
        on_delete=models.CASCADE,
        related_name='profile_owner')
    #プロフィール画像（4種類の画像として保存する）
    pro_image=StdImageField(
        upload_to='images/',
        null=True,
        blank=True,
        variations={
            'large':(600,400),
            'thumbnail':(100,100,True),
            'medium':(300,200),
        })
    #ユーザの名前
    name=models.CharField(default=None,max_length=30,null=True,blank=True)
    #ユーザの自己紹介文
    profile_text=models.CharField(default=None,max_length=140,null=True,blank=True)

    def __str__(self):
        return self.owner.username
