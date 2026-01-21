from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        
        # 自訂表單樣式 (讓它長得像深色主題)
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '寫下你的想法或提問...',
                'style': 'background-color: #1e293b; color: #fff; border: 1px solid #334155;'
            }),
        }
        labels = {
            'content': ''  # 隱藏標籤文字，比較簡潔
        }