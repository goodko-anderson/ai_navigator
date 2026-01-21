from django.contrib import admin
from .models import UserProfile

# 讓後台可以管理 UserProfile
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'avatar')