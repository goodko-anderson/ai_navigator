from django.contrib import admin
from django.urls import path, include 
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

# 1. 引入 Core views
from core import views 
from core.views import home, dashboard 

# 2. 引入 Tutorials views
from tutorials.views import (
    article_list, 
    article_detail, 
    add_article_comment, 
    article_favorite,
    article_like,
    image_analysis  # <--- ✅ 新增這裡：引入 image_analysis
)

# 3. 引入 Tools views
from tools.views import (
    tool_detail, 
    toggle_favorite, 
    add_comment, 
    tool_list, 
    tool_favorite
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- Summernote ---
    path('summernote/', include('django_summernote.urls')),

    # --- 搜尋 ---
    path('search/', views.search, name='search'),

    # --- 首頁與戰情室 ---
    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    
    # --- 文章相關 (新手村) ---
    path('tutorials/', article_list, name='article_list'),
    path('tutorial/<str:slug>/', article_detail, name='article_detail'),
    path('article_comment/<str:slug>/', add_article_comment, name='add_article_comment'),
    
    path('tutorial/<str:slug>/favorite/', article_favorite, name='article_favorite'),
    path('tutorial/<str:slug>/like/', article_like, name='article_like'),

    # --- 🛠️ 工具相關 ---
    path('tools/', tool_list, name='tool_list'),
    path('tool/<str:slug>/', tool_detail, name='tool_detail'),
    path('comment/<str:slug>/', add_comment, name='add_comment'), 
    
    path('favorite/<str:slug>/', toggle_favorite, name='toggle_favorite'),
    path('tool/<str:slug>/favorite/', tool_favorite, name='tool_favorite'),

    # --- 🧪 實驗室 ---
    # 👇 ✅ 新增這裡：註冊路徑
    path('lab/image-analysis/', image_analysis, name='image_analysis'),
    
    # (Labs app 的路徑保留)
    path('labs/', include('labs.urls')), 

    # --- 會員 ---
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('account/settings/', views.account_settings, name='account_settings'),
    path('account/password/', views.change_password, name='change_password'),
]

# ⭐ 關鍵修正：在 DEBUG 模式下，同時打通 Media (上傳檔) 與 Static (系統檔) 的路徑 ⭐
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)