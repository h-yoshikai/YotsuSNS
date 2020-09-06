from django.contrib import admin
from .models import AuthUser,Profile,Follow,Message,Tag,Good
# Register your models here.
admin.site.register(AuthUser)
admin.site.register(Profile)
admin.site.register(Follow)
admin.site.register(Message)
admin.site.register(Tag)
admin.site.register(Good)
