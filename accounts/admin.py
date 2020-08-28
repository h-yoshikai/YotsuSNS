from django.contrib import admin
from .models import AuthUser,Profile
# Register your models here.
admin.site.register(AuthUser)
admin.site.register(Profile)
