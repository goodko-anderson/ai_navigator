from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q 
from .models import Tool, Comment

# ==========================================
# 1. 收藏切換功能 (保留原樣)
# ==========================================
@login_required
def tool_favorite(request, slug):
    tool = get_object_or_404(Tool, slug=slug)
    
    if tool.favorites.filter(id=request.user.id).exists():
        tool.favorites.remove(request.user)
    else:
        tool.favorites.add(request.user)
        
    return redirect(request.META.get('HTTP_REFERER', 'tool_list'))

# (備用版，可保留或刪除)
@login_required
def toggle_favorite(request, slug):
    tool = get_object_or_404(Tool, slug=slug)
    
    if request.user in tool.favorites.all():
        tool.favorites.remove(request.user)
    else:
        tool.favorites.add(request.user)
        
    next_url = request.META.get('HTTP_REFERER')
    if next_url:
        return redirect(next_url)
    
    return redirect('tool_detail', slug=slug)

# ==========================================
# 2. 顯示工具詳情 (保留原樣)
# ==========================================
def tool_detail(request, slug):
    tool = get_object_or_404(Tool, slug=slug)
    
    # 計數器 +1
    tool.views += 1
    tool.save()

    # 檢查是否已收藏
    is_favorited = False
    if request.user.is_authenticated:
        if request.user in tool.favorites.all():
            is_favorited = True

    # 找出相關文章
    related_articles = tool.articles.filter(is_published=True)

    context = {
        'tool': tool,
        'is_favorited': is_favorited,
        'related_articles': related_articles,
    }
    return render(request, 'tools/tool_detail.html', context)

# ==========================================
# 3. 處理留言 (保留原樣)
# ==========================================
@login_required
@require_POST
def add_comment(request, slug):
    tool = get_object_or_404(Tool, slug=slug)
    content = request.POST.get('content')
    
    if content:
        Comment.objects.create(
            tool=tool,
            user=request.user,
            content=content
        )
    
    return redirect('tool_detail', slug=slug)

# ==========================================
# 4. 軍火庫總清單 (🔥 核心升級區)
# ==========================================
def tool_list(request):
    # 1. 取得所有工具
    tools_all = Tool.objects.all().order_by('-created_at')
    
    # 2. 搜尋邏輯 (Search)
    query = request.GET.get('q')
    if query:
        tools_all = tools_all.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )

    # 3. 👇 新增：分類篩選邏輯 (Category)
    category = request.GET.get('category')
    if category:
        tools_all = tools_all.filter(category=category)

    # 4. 👇 新增：抓出所有不重複的分類 (給前端生成按鈕用)
    # values_list(flat=True) 會回傳 ['繪圖', '寫作', ...] 的清單，而不是 [('繪圖',), ...]
    categories = Tool.objects.values_list('category', flat=True).distinct()

    # 5. 設定分頁：改為 12 個 (適合 3欄或4欄排版)
    paginator = Paginator(tools_all, 12) 
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 6. 打包資料
    context = {
        'tools': page_obj,
        'query': query,           # 搜尋關鍵字
        'categories': categories, # 👇 傳送分類清單給前端
        'active_category': category, # 👇 傳送目前選中的分類(讓按鈕變色)
    }
    
    return render(request, 'tools/tool_list.html', context)