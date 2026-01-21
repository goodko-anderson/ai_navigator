from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# 建立一個 UserProfile 模型來擴充 User
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # 👇 這是您原本的設定，我們沿用它，不要改名！
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', blank=True, null=True, verbose_name="大頭貼")

    def __str__(self):
        return f'{self.user.username} 的個人檔案'

# 👇 訊號 (Signals)：當 User 建立時，自動建立一個對應的 UserProfile
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()