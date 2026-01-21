from django.db import models
from django.contrib.auth.models import User

# 嘗試引入 Tool 模型，如果 tools app 還沒準備好也不會報錯
try:
    from tools.models import Tool
except ImportError:
    Tool = None

# ==========================================
# 1. 實驗專案 (保持原樣)
# ==========================================
class LabProject(models.Model):
    title = models.CharField(max_length=200, verbose_name="實驗標題")
    description = models.TextField(verbose_name="實驗心得")
    
    # === 新增功能區 (為了 AI 自動寫手) ===
    # 1. 完整內容：用來存 Gemini 寫好的 HTML 文章
    content = models.TextField(blank=True, null=True, verbose_name="完整文章內容")
    
    # 2. 建立者：記錄是誰生成的 (設為 null=True 以免舊資料報錯)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="建立者")
    
    # 3. 狀態：區分草稿或完成品
    status = models.CharField(max_length=20, default='draft', choices=[('draft', '草稿'), ('completed', '完成')], verbose_name="狀態")

    # === 圖片區 (保持您原本的設定) ===
    # 這是原本的圖 (視為 After / 最終成果)
    cover_image = models.ImageField(upload_to='lab_covers/', verbose_name="成果封面圖 (After)", blank=True, null=True)
    
    # Before 對比圖
    before_image = models.ImageField(upload_to='lab_before/', verbose_name="Before 對比圖 (線稿/原圖)", blank=True, null=True)
    
    # 影片上傳欄位
    video = models.FileField(upload_to='lab_videos/', verbose_name="成果影片", blank=True, null=True)

    # === 咒語區 (保持您原本的設定) ===
    # 正向 Prompt
    prompt_text = models.TextField(blank=True, verbose_name="使用的 Prompt 咒語")
    
    # 負向 Prompt
    negative_prompt = models.TextField(blank=True, verbose_name="負向 Prompt (Negative)", help_text="例如: low quality, blurry, nsfw")
    
    # === 數據區 (保持您原本的設定) ===
    views = models.PositiveIntegerField(default=0, verbose_name="瀏覽次數")
    
    related_tool = models.ForeignKey(
        'tools.Tool', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="使用工具",
        related_name='lab_projects' 
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "實驗專案"
        verbose_name_plural = "實驗專案"


# ==========================================
# 2. 逆向工程紀錄 (保持原樣)
# ==========================================
class ReverseImage(models.Model):
    image = models.ImageField(upload_to='reverse_engineering/', verbose_name="上傳圖片")
    prompt_result = models.TextField(blank=True, verbose_name="AI 分析出的咒語")
    analysis_report = models.TextField(blank=True, verbose_name="詳細分析報告")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="使用者")

    def __str__(self):
        return f"Reverse Analysis #{self.id} - {self.created_at.strftime('%Y/%m/%d')}"

    class Meta:
        verbose_name = "逆向工程紀錄"
        verbose_name_plural = "逆向工程紀錄"


# ==========================================
# 3. 👇 ISO 11608 分析紀錄 (整合參數版)
# ==========================================
class IsoAnalysis(models.Model):
    title = models.CharField(max_length=200, default="ISO 11608 分析報告", verbose_name="報告標題")
    
    # 上傳的原始數據檔
    data_file = models.FileField(upload_to='iso_data/', verbose_name="數據檔案")
    
    # 分析結果圖表 (由後端自動生成)
    result_plot = models.ImageField(upload_to='iso_plots/', blank=True, null=True, verbose_name="分析圖表")

    # 👇 新增：ISO 參數設定區 (對應 Tkinter 的 Input Parameters)
    density = models.FloatField(default=1.0, verbose_name="液體密度 (g/cm³)")
    param_alpha = models.FloatField(default=0.01, verbose_name="解析度 α (mL)")
    param_beta = models.FloatField(default=5.0, verbose_name="公差範圍 β (%)")
    param_k = models.FloatField(default=2.92, verbose_name="ISO K-Factor")
    
    # 👇 新增：劑量設定 (Vset)
    v_min = models.FloatField(default=0.1, verbose_name="最小劑量 Min")
    v_mid = models.FloatField(default=0.3, verbose_name="中間劑量 Mid")
    v_max = models.FloatField(default=0.5, verbose_name="最大劑量 Max")
    
    # 改用 JSONField：用來存 Min/Mid/Max 各組的詳細統計數據
    report_data = models.JSONField(default=dict, blank=True, verbose_name="詳細分析數據")
    
    # 判定結果 (Pass/Fail)
    is_pass = models.BooleanField(default=False, verbose_name="是否通過")
    
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"ISO Report - {self.created_at.strftime('%Y/%m/%d')}"
        
    class Meta:
        verbose_name = "ISO分析紀錄"
        verbose_name_plural = "ISO分析紀錄"