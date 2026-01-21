from django.urls import path
from . import views

urlpatterns = [
    # 實驗室列表頁
    path('', views.lab_list, name='lab_list'),
    
    # 作品詳情頁
    path('project/<int:pk>/', views.lab_detail, name='lab_detail'),

    # AI 自動寫手頁面
    path('ai-writer/', views.ai_writer_view, name='ai_writer'),

    # 👇 關鍵修正：name 必須改成 'publish_lab_to_article' 才能跟 Template 對上
    path('project/<int:pk>/publish/', views.publish_lab_to_article, name='publish_lab_to_article'),
    # 👇 新增這行
    path('reverse-engineering/', views.reverse_engineering_view, name='reverse_engineering'),
    path('iso-analysis/', views.iso_analysis_view, name='iso_analysis'),
    # 👇 新增這一行：ISO 11608 分析儀的路徑
    path('iso-analysis/', views.iso_analysis_view, name='iso_analysis'),
]