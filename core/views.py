from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

# 引入 App 模型
from tools.models import Tool
from tutorials.models import Article
from labs.models import LabProject

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
# 引入我們自定義的 Form
from .forms import UserUpdateForm, ProfileUpdateForm
from .models import UserProfile

# ==========================================
# 1. 首頁 (Home)
# ==========================================
def home(request):
    latest_projects = LabProject.objects.all().order_by('-created_at')[:3]
    popular_tools = Tool.objects.all().order_by('-views')[:4]

    context = {
        'latest_projects': latest_projects,
        'popular_tools': popular_tools,
        'tools': popular_tools, 
        'articles': [], 
    }
    return render(request, 'home.html', context)

# ==========================================
# 2. 搜尋功能 (Search)
# ==========================================
def search(request):
    query = request.GET.get('q', '')
    
    tools = []
    articles = []
    projects = []
    
    if query:
        tools = Tool.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__icontains=query)
        )
        articles = Article.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query)
        )
        # 實驗室搜尋 (只搜工具名與標題)
        projects = LabProject.objects.filter(
            Q(related_tool__name__icontains=query) | 
            Q(title__icontains=query)
        )

    return render(request, 'search_results.html', {
        'query': query, 
        'tools': tools,
        'articles': articles,
        'projects': projects
    })

# ==========================================
# 3. 戰情室 (Dashboard)
# ==========================================
@login_required
def dashboard(request):
    try:
        favorite_tools = request.user.saved_tools.all()
    except AttributeError:
        favorite_tools = []

    try:
        favorite_articles = request.user.saved_articles.all().order_by('-created_at')
    except AttributeError:
        favorite_articles = []
    
    total_tools_fav = len(favorite_tools)
    total_articles_fav = len(favorite_articles)
    
    recommended_tool = Tool.objects.exclude(favorites=request.user).order_by('-views').first()
    if not recommended_tool:
        recommended_tool = Tool.objects.first()

    context = {
        'favorite_tools': favorite_tools,
        'favorite_articles': favorite_articles,
        'total_tools_fav': total_tools_fav,
        'total_articles_fav': total_articles_fav,
        'recommended_tool': recommended_tool,
    }
    return render(request, 'dashboard.html', context)

# ==========================================
# 4. 帳號設定 (Account Settings) - 🔥 重點修復區
# ==========================================
@login_required
def account_settings(request):
    # 確保 UserProfile 存在
    UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # 更新 User 模型 (username, email)
        u_form = UserUpdateForm(request.POST, instance=request.user)
        # 🔥 關鍵修正：必須加上 request.FILES 才能接收圖片！
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, '您的帳號與大頭貼已更新成功！')
            return redirect('dashboard') # 儲存後跳轉回戰情室
        else:
            # 如果失敗，顯示錯誤訊息 (通常是檔案格式不對)
            messages.error(request, '更新失敗，請檢查欄位。')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = { 'u_form': u_form, 'p_form': p_form }
    return render(request, 'account_settings.html', context)

# ==========================================
# 5. 修改密碼
# ==========================================
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user) 
            messages.success(request, '您的密碼已成功修改！')
            return redirect('account_settings')
        else:
            messages.error(request, '請修正以下的錯誤。')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'password_change.html', {'form': form})