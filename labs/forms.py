from django import forms
# 👇 1. 引入相關模型
from .models import ReverseImage, IsoAnalysis 

# ==========================================
# 1. AI 自動寫手表單 (保留原樣)
# ==========================================
class AIWriterForm(forms.Form):
    topic = forms.CharField(
        label='文章主題', 
        max_length=200, 
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg', 
            'placeholder': '例如：Midjourney V6 完整教學...'
        })
    )

# ==========================================
# 2. 逆向工程圖片上傳表單 (保留原樣)
# ==========================================
class ReverseImageForm(forms.ModelForm):
    class Meta:
        model = ReverseImage
        fields = ['image']  # 我們只需要使用者上傳圖片
        
        # 自定義樣式，讓上傳框符合深色主題
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control bg-dark text-light border-secondary',
                'style': 'padding: 15px; border-radius: 12px;',
                'accept': 'image/*'  # 限制只能選圖片
            })
        }

# ==========================================
# 3. 👇 ISO 數據分析上傳表單 (升級版)
# ==========================================
class IsoAnalysisForm(forms.ModelForm):
    class Meta:
        model = IsoAnalysis
        # 👇 包含所有設定參數
        fields = [
            'data_file', 
            'density', 'param_alpha', 'param_beta', 'param_k', 
            'v_min', 'v_mid', 'v_max'
        ] 
        
        widgets = {
            # 檔案上傳框
            'data_file': forms.FileInput(attrs={
                'class': 'form-control bg-dark text-light border-secondary',
                'style': 'padding: 15px; border-radius: 12px;',
                'accept': '.csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel' 
            }),
            
            # === 物理參數輸入框 (深色樣式) ===
            'density': forms.NumberInput(attrs={
                'class': 'form-control bg-dark text-light border-secondary', 
                'step': '0.001', 'placeholder': '1.0'
            }),
            'param_k': forms.NumberInput(attrs={
                'class': 'form-control bg-dark text-light border-secondary', 
                'step': '0.001', 'placeholder': '2.921'
            }),
            'param_alpha': forms.NumberInput(attrs={
                'class': 'form-control bg-dark text-light border-secondary', 
                'step': '0.001', 'placeholder': '0.01'
            }),
            'param_beta': forms.NumberInput(attrs={
                'class': 'form-control bg-dark text-light border-secondary', 
                'step': '0.1', 'placeholder': '5.0'
            }),
            
            # === 劑量設定輸入框 ===
            'v_min': forms.NumberInput(attrs={
                'class': 'form-control bg-dark text-light border-secondary', 
                'step': '0.01'
            }),
            'v_mid': forms.NumberInput(attrs={
                'class': 'form-control bg-dark text-light border-secondary', 
                'step': '0.01'
            }),
            'v_max': forms.NumberInput(attrs={
                'class': 'form-control bg-dark text-light border-secondary', 
                'step': '0.01'
            }),
        }