from django.contrib import admin
from django.utils.html import format_html
from .models import Tool, Comment

# 註冊留言版 (簡單管理即可)
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'tool', 'content_preview', 'created_at')
    list_filter = ('created_at',)
    
    def content_preview(self, obj):
        return obj.content[:30] + '...' if len(obj.content) > 30 else obj.content
    content_preview.short_description = "留言內容"

@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    # === 1. 列表頁設定 ===
    # 顯示：Logo、名稱、分類、官網連結
    list_display = ('logo_preview', 'name', 'category', 'website_link')
    
    # 篩選器：分類
    list_filter = ('category',)
    
    # 搜尋：名稱、描述
    search_fields = ('name', 'description')
    
    # 自動填入 Slug (當您輸入名稱時，Slug 會自動產生)
    prepopulated_fields = {'slug': ('name',)}

    # === 2. 編輯頁設定 ===
    fieldsets = (
        ('工具資訊', {
            'fields': ('name', 'slug', 'category', 'website_url', 'description')
        }),
        ('視覺設定', {
            'fields': ('image', 'logo_preview_large'), # 假設您的模型欄位是 image (如果是 logo 請自行修改)
        }),
        ('數據', {
            'fields': ('views', 'created_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('logo_preview_large', 'views', 'created_at')

    # === 自定義方法 ===
    def logo_preview(self, obj):
        # ⚠️ 注意：請確認您的 Tool 模型圖片欄位是 image 還是 logo
        # 這裡假設是 image (依照昨天 tool_list.html 的設定)
        if obj.image:
            return format_html('<img src="{}" style="height: 40px; border-radius: 5px;" />', obj.image.url)
        return "-"
    logo_preview.short_description = "Logo"

    def website_link(self, obj):
        if obj.website_url:
            return format_html('<a href="{}" target="_blank">前往官網</a>', obj.website_url)
        return "-"
    website_link.short_description = "連結"

    def logo_preview_large(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 200px; border-radius: 10px;" />', obj.image.url)
        return "無圖片"
    logo_preview_large.short_description = "圖片預覽"