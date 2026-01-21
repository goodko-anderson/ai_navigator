from django.contrib import admin
from .models import Article, Prompt, Comment  # 👈 修正：是用 Prompt，不是 PromptCard
# 👇 1. 引入 Summernote 的後台類別
from django_summernote.admin import SummernoteModelAdmin

# 設定 Prompt 在文章頁面中內嵌顯示
class PromptInline(admin.TabularInline):
    model = Prompt  # 👈 這裡也要改用 Prompt
    extra = 1

# 👇 2. 繼承 SummernoteModelAdmin (原本是 admin.ModelAdmin)
@admin.register(Article)
class ArticleAdmin(SummernoteModelAdmin):
    # 👇 3. 指定哪些欄位要變成富文本編輯器
    summernote_fields = ('content',)
    
    list_display = ('title', 'category', 'difficulty', 'is_published', 'created_at')
    list_filter = ('is_published', 'difficulty', 'category')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [PromptInline]  # 把 Prompt 內嵌進來

# 👇 新增：讓後台也能管理留言
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'article', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__username', 'article__title')