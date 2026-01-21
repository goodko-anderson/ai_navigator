from django.db import models
from django.contrib.auth.models import User
from tools.models import Tool

class Article(models.Model):
    title = models.CharField(max_length=200)
    # ⭐ 重點是加上 allow_unicode=True (允許萬國碼/中文)
    slug = models.SlugField(unique=True, allow_unicode=True, verbose_name="網址 Slug")
    content = models.TextField()
    
    views = models.PositiveIntegerField(default=0, verbose_name="瀏覽次數")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)

    # 👇 1. 收藏功能 (原本就有)
    favorites = models.ManyToManyField(User, related_name='saved_articles', blank=True, verbose_name="收藏用戶")
    
    # 👇 2. 新增按讚功能 (新增這個!)
    likes = models.ManyToManyField(User, related_name='liked_articles', blank=True, verbose_name="按讚用戶")

    # 分類與難度
    difficulty = models.IntegerField(default=1, choices=[
        (1, '新手'), (2, '進階'), (3, '專家')
    ])
    category = models.CharField(max_length=50, default='General')
    
    # 封面圖
    cover_image = models.ImageField(upload_to='article_covers/', blank=True, null=True)
    
    # 關聯工具
    related_tool = models.ForeignKey(Tool, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')

    def __str__(self):
        return self.title
    
    # 👇 新增這兩個小幫手函式，方便模板呼叫
    def total_likes(self):
        return self.likes.count()
        
    def total_favorites(self):
        return self.favorites.count()

class Prompt(models.Model):
    PROMPT_TYPES = [('TEXT', '文字生成'), ('IMAGE', '圖片生成')]
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='prompts')
    title = models.CharField(max_length=100)
    content = models.TextField()
    prompt_type = models.CharField(max_length=10, choices=PROMPT_TYPES, default='TEXT')

    def __str__(self):
        return self.title

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.author.username} on {self.article.title}'