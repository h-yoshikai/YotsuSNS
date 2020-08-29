from django.contrib import admin
from .models import AuthUser,Profile,Follow
# Register your models here.
admin.site.register(AuthUser)
admin.site.register(Profile)
admin.site.register(Follow)
