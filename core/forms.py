from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

# 1. 修改基本資料的表單
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(label="電子郵件", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

# 2. 上傳大頭貼的表單
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        # 👇 修正：對應 Model，改回 'avatar'
        fields = ['avatar']
        labels = {'avatar': '上傳大頭貼'}
        widgets = {
            # 👇 Widget key 也是 'avatar'
            'avatar': forms.FileInput(attrs={
                'class': 'form-control', 
                'accept': 'image/*' 
            }),
        }