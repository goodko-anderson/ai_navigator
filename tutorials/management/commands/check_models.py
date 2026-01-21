import google.generativeai as genai
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = '查詢目前 API Key 可用的所有 Gemini 模型'

    def handle(self, *args, **kwargs):
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            self.stdout.write(self.style.ERROR("❌ 錯誤：settings.py 中未設定 GEMINI_API_KEY"))
            return

        # 顯示鑰匙前幾碼以確認身份
        self.stdout.write(f"🔑 使用鑰匙：{api_key[:10]}...")

        try:
            genai.configure(api_key=api_key)
            
            self.stdout.write("📡 正在連線 Google 查詢可用模型清單...\n")
            
            # 列出所有模型
            found_any = False
            for m in genai.list_models():
                # 我們只關心能生成內容 (generateContent) 的模型
                if 'generateContent' in m.supported_generation_methods:
                    found_any = True
                    self.stdout.write(self.style.SUCCESS(f"✅ 發現模型: {m.name}"))
                    self.stdout.write(f"   👉 說明: {m.description}")
                    self.stdout.write(f"   👉 版本: {m.version}")
                    self.stdout.write("-" * 40)

            if not found_any:
                self.stdout.write(self.style.WARNING("⚠️ 連線成功，但沒有發現任何支援 generateContent 的模型。這可能是 API Key 權限受限。"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ 查詢失敗: {e}"))