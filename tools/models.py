from django.db import models
from django.contrib.auth.models import User # 👈 1. 確保有引入 User

# 1. 工具模型
class Tool(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    website_url = models.URLField(blank=True, null=True)
    
    # 工具圖片
    image = models.ImageField(upload_to='tool_images/', blank=True, null=True)
    
    # 分類與精選
    category = models.CharField(max_length=50, default='Uncategorized')
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # 👇 2. 新增這行：收藏功能
    # related_name='saved_tools' 意思是：以後可以用 user.saved_tools 查出這個人收藏了哪些工具
    favorites = models.ManyToManyField(User, related_name='saved_tools', blank=True, verbose_name="收藏的使用者")

    # 👇 新增這一行：瀏覽次數 (預設為 0)
    views = models.PositiveIntegerField(default=0, verbose_name="瀏覽次數")

    def __str__(self):
        return self.name

# 2. 留言模型
class Comment(models.Model):
    # 關聯到哪個工具
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE, related_name='comments')
    
    # 👇 關鍵修改在這裡！請確認你的檔案裡有 related_name='tool_comments'
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tool_comments')
    
    # 留言內容
    content = models.TextField()
    
    # 留言時間
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} 評論 {self.tool.name}'