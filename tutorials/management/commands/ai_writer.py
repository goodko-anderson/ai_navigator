import time
import json
import urllib.request
import urllib.error
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.conf import settings
from tutorials.models import Article
from tools.models import Tool

class Command(BaseCommand):
    help = '新手村自動寫手 (CLI 直連版 - 免安裝套件)'

    def add_arguments(self, parser):
        parser.add_argument('topic', type=str, help='工具名稱 (輸入 "ALL" 跑全部)')

    # --- 🔧 核心工具：通用 API 呼叫函式 ---
    def call_gemini(self, prompt, api_key):
        # 優先使用 2.5 (最強)，備援 2.0
        matrix = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-flash-latest"]
        
        for model in matrix:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                headers = {'Content-Type': 'application/json'}
                data = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode('utf-8')
                
                req = urllib.request.Request(url, data=data, headers=headers, method='POST')
                with urllib.request.urlopen(req, timeout=30) as response:
                    if response.status == 200:
                        res_json = json.loads(response.read().decode('utf-8'))
                        try:
                            text = res_json['candidates'][0]['content']['parts'][0]['text']
                            # 清理 Markdown
                            if text.startswith("```"): 
                                text = text.replace("```json", "").replace("```html", "").replace("```", "")
                            return text.strip()
                        except KeyError:
                            print(f"⚠️ {model} 回傳內容格式錯誤 (KeyError)")
                            continue

            except urllib.error.HTTPError as e:
                # 👇 把錯誤原因印出來，方便除錯
                print(f"❌ 連線失敗 [{model}]: HTTP {e.code} - {e.reason}")
                if e.code == 400:
                    print("   (提示：可能是 API Key 無效，或 Key 沒有權限存取此模型)")
                if e.code == 429:
                    print(f"⚠️ API 塞車 (429)，休息 10 秒...")
                    time.sleep(10)
                continue 
            except Exception as e:
                print(f"❌ 未知錯誤 [{model}]: {e}")
                continue 

        return None # 全軍覆沒

    def handle(self, *args, **kwargs):
        topic_input = kwargs['topic']
        
        # =====================================================
        # 🔑 讀取 API Key
        # =====================================================
        MY_API_KEY = settings.GEMINI_API_KEY

        if not MY_API_KEY:
            self.stdout.write(self.style.ERROR("❌ 錯誤：settings.py 中未設定 GEMINI_API_KEY"))
            return

        # 顯示前幾碼確認
        print(f"🔑 目前使用的鑰匙：{MY_API_KEY[:10]}... (來自 settings.py)")

        # 1. 篩選工具
        target_tools = Tool.objects.all() if topic_input == "ALL" else Tool.objects.filter(name__icontains=topic_input)
        
        if not target_tools.exists():
            self.stdout.write(self.style.ERROR(f"❌ 找不到工具：{topic_input}"))
            return

        print(f"🚀 啟動寫手！目標：{[t.name for t in target_tools]}")

        # 2. 開始巡迴
        for tool in target_tools:
            print(f"\n🔥 正在處理：{tool.name}...")
            
            # --- 階段一：發想題目 ---
            existing = Article.objects.filter(related_tool=tool).values_list('title', flat=True)
            print(f"📊 已有文章：{len(existing)} 篇，正在發想新題目...")

            idea_prompt = f"""
            你是一個內容策略師。目標工具：{tool.name}。
            我們已有：{list(existing)}。
            請發想 3 個「完全不同」的繁體中文教學標題。
            只回傳 JSON 陣列字串，不要有其他廢話。範例：["標題A", "標題B"]
            """
            
            json_str = self.call_gemini(idea_prompt, MY_API_KEY)
            
            if not json_str:
                print("💀 發想失敗 (所有模型皆報錯)，跳過此工具。")
                continue

            try:
                # 加入 strict=False 以防發想階段也有換行符號問題
                new_topics = json.loads(json_str, strict=False)
                print(f"💡 AI 點子：{new_topics}")
            except json.JSONDecodeError:
                print(f"❌ JSON 解析失敗，AI 回傳了：{json_str[:50]}...")
                continue

            # --- 階段二：撰寫文章 ---
            for sub_topic in new_topics:
                if Article.objects.filter(title=sub_topic).exists():
                    print(f"⏭️ 跳過重複：{sub_topic}")
                    continue

                print(f"✍️ 正在撰寫：{sub_topic} ...")
                write_prompt = f"""
                請為「{tool.name}」寫一篇教學，主題：「{sub_topic}」。
                要求：繁體中文、HTML 格式 (h2, p, ul)、不含 markdown 標記。
                回傳 JSON：{{ "title": "{sub_topic}", "content": "HTML內容", "difficulty": 1 }}
                """

                article_json_str = self.call_gemini(write_prompt, MY_API_KEY)
                
                if article_json_str:
                    try:
                        # 🌟 關鍵修改：加入 strict=False 允許控制字元（如換行）
                        data = json.loads(article_json_str, strict=False)
                        
                        Article.objects.create(
                            title=data['title'],
                            slug=slugify(data['title'], allow_unicode=True),
                            content=data['content'],
                            difficulty=data.get('difficulty', 1),
                            category=tool.category,
                            related_tool=tool,
                            author_id=1,
                            is_published=True
                        )
                        print(f"✅ 存檔成功！")
                        time.sleep(3) 
                    except Exception as e:
                        print(f"💥 存檔或解析失敗：{e}")
                else:
                    print("❌ 生成內容失敗")