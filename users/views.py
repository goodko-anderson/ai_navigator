from django.shortcuts import render
# 👇 引入這個裝飾器，用來保護頁面 (沒登入會被踢走)
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    # 回傳 dashboard.html 頁面
    return render(request, 'dashboard.html')