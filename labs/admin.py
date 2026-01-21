from django.contrib import admin
from django.utils.html import format_html # 👈 用來產生 HTML圖片標籤
from .models import LabProject

@admin.register(LabProject)
class LabProjectAdmin(admin.ModelAdmin):
    # === 1. 列表頁設定 ===
    # 顯示的欄位：ID、標題、相關工具、(縮圖)、建立時間、瀏覽數
    list_display = ('id', 'title', 'related_tool', 'cover_preview', 'created_at', 'views')
    
    # 點擊哪些欄位可以進入編輯
    list_display_links = ('id', 'title')
    
    # 右側篩選器：依照 工具、建立時間 篩選
    list_filter = ('related_tool', 'created_at')
    
    # 上方搜尋框：可搜尋 標題、描述、Prompt
    search_fields = ('title', 'description', 'prompt_text')
    
    # 每頁顯示幾筆
    list_per_page = 20

    # === 2. 編輯頁設定 ===
    # 使用 fieldsets 將欄位分組，讓版面更整潔
    fieldsets = (
        ('基本資訊', {
            'fields': ('title', 'description', 'related_tool')
        }),
        ('媒體素材', {
            # 👇 修改處：加入了 before_image 和它的預覽
            'fields': ('cover_image', 'cover_preview_large', 'before_image', 'before_preview_large', 'video'),
            'description': '上傳圖片或影片，下方會顯示預覽。若要啟用「Before/After 滑桿」，請同時上傳成果圖與 Before 對比圖。'
        }),
        ('AI 參數 (Prompt)', {
            # 👇 修改處：加入了 negative_prompt
            'fields': ('prompt_text', 'negative_prompt'),
            'classes': ('collapse',), # 預設摺疊起來
        }),
        ('數據統計', {
            'fields': ('views', 'created_at'),
            'classes': ('collapse',),
        }),
    )
    
    # 設定唯讀欄位 (預覽圖、建立時間不能手動改)
    # 👇 修改處：記得把新的 before_preview_large 加進來
    readonly_fields = ('cover_preview_large', 'before_preview_large', 'created_at')

    # === 3. 自定義方法：產生列表小縮圖 ===
    def cover_preview(self, obj):
        if obj.cover_image:
            # 顯示 50px 高的縮圖
            return format_html('<img src="{}" style="height: 50px; border-radius: 5px;" />', obj.cover_image.url)
        return "無圖片"
    cover_preview.short_description = "封面縮圖"

    # === 4. 自定義方法：產生編輯頁大預覽圖 (After) ===
    def cover_preview_large(self, obj):
        if obj.cover_image:
            # 顯示最大寬度 300px 的預覽圖
            return format_html('<img src="{}" style="max-width: 300px; border-radius: 10px; margin-top: 10px;" />', obj.cover_image.url)
        return "尚未上傳圖片"
    cover_preview_large.short_description = "成果圖預覽 (After)"

    # === 5. 👇 新增方法：產生編輯頁大預覽圖 (Before) ===
    def before_preview_large(self, obj):
        if obj.before_image:
            return format_html('<img src="{}" style="max-width: 300px; border-radius: 10px; margin-top: 10px;" />', obj.before_image.url)
        return "尚未上傳 Before 對比圖"
    before_preview_large.short_description = "對比圖預覽 (Before)"