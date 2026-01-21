import base64
import time  # 時間控制模組
from django.core.files.storage import default_storage
from django.conf import settings
import google.generativeai as genai
from django.shortcuts import render, get_object_or_404, redirect
# 👇 確認引入 login_required
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages 

# 引入模型
from .models import Article, Comment

# ==========================================
# 1. 文章列表 (確保僅顯示已發布文章)
# ==========================================
def article_list(request):
    articles_all = Article.objects.filter(is_published=True).order_by('-created_at')
    
    query = request.GET.get('q') 
    if query:
        articles_all = articles_all.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query)
        )
    
    paginator = Paginator(articles_all, 9) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'articles': page_obj,
        'query': query, 
    }
    
    return render(request, 'tutorials/article_list.html', context)


# ==========================================
# 2. 文章詳情 (確保 HTML 渲染與計數正常)
# ==========================================
def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, is_published=True)
    
    article.views += 1
    article.save()

    prompts = article.prompts.all()
    
    related_articles = Article.objects.filter(is_published=True).exclude(id=article.id).order_by('-created_at')[:3]

    context = {
        'article': article,
        'prompts': prompts,
        'related_articles': related_articles,
    }
    
    return render(request, 'tutorials/article_detail.html', context)


# ==========================================
# 3. 新增留言
# ==========================================
@login_required
@require_POST
def add_article_comment(request, slug):
    article = get_object_or_404(Article, slug=slug)
    content = request.POST.get('content')
    
    if content:
        Comment.objects.create(
            article=article,
            author=request.user,
            content=content
        )
        messages.success(request, '您的留言已發布！') 
    
    return redirect('article_detail', slug=slug)


# ==========================================
# 4. 文章收藏功能
# ==========================================
@login_required
def article_favorite(request, slug):
    article = get_object_or_404(Article, slug=slug)
    
    if request.user in article.favorites.all():
        article.favorites.remove(request.user)
        messages.info(request, '已從收藏中移除')
    else:
        article.favorites.add(request.user)
        messages.success(request, '已加入收藏！')
        
    return redirect('article_detail', slug=slug)


# ==========================================
# 5. 文章按讚功能
# ==========================================
@login_required
def article_like(request, slug):
    article = get_object_or_404(Article, slug=slug)
    
    if request.user in article.likes.all():
        article.likes.remove(request.user)
    else:
        article.likes.add(request.user)
        messages.success(request, '感謝您的點讚！')
        
    return redirect('article_detail', slug=slug)


# ==========================================
# 6. 實驗室功能：逆向工程引擎 (Image to Prompt)
# ==========================================
# 👇 修改點：加上 @login_required，保護您的 API 額度
@login_required
def image_analysis(request):
    print("👉 [Debug] 進入 image_analysis view")

    result_prompt = None
    image_url = None

    if request.method == 'POST' and request.FILES.get('upload_image'):
        print("📸 [Debug] 偵測到 POST 請求與圖片上傳")
        
        try:
            # 1. 取得上傳的圖片
            img_file = request.FILES['upload_image']
            
            # 2. 設定 API Key
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            # 3. 讀取圖片數據
            img_data = img_file.read()

            # 4. 準備模型列表 (根據您的 check_models 結果量身打造)
            # 策略：優先使用 "Lite" (輕量版) 系列，因為它們通常擁有比標準版更高的免費額度
            candidate_models = [
                # 👇 優先嘗試 2.0 Flash Lite (最有可能有剩餘額度)
                "gemini-2.0-flash-lite-preview-02-05", 
                
                # 👇 其次嘗試 2.5 Flash Lite
                "gemini-2.5-flash-lite-preview-09-2025",
                
                # 👇 通用 Lite 指標
                "gemini-flash-lite-latest",
                
                # 👇 如果 Lite 都沒了，再試試看 2.0 Flash (雖然剛剛報錯，但值得放在後面備用)
                "gemini-2.0-flash-001",
                
                # 👇 最後一搏：最新的 3.0 Flash Preview (這可是稀有貨！)
                "gemini-3-flash-preview"
            ]

            # 5. 發送請求 (指令)
            prompt_request = """
            你是一個 AI 繪圖專家。請分析這張圖片的：
            1. 藝術風格 (如：Cyberpunk, Ukiyo-e, Oil Painting)
            2. 構圖與視角 (如：Wide angle, Macro, Isometric)
            3. 光影與色調 (如：Neon lights, Cinematic lighting)
            4. 畫面主體描述
            
            最後，請根據上述分析，寫出一短短的、適合用來讓 Midjourney 或 Stable Diffusion 生成類似圖片的英文 Prompt。
            格式要求：只給我 Prompt 本身，不要有解釋。
            """

            # 迴圈嘗試所有模型
            for model_name in candidate_models:
                print(f"🚀 [Debug] 正在嘗試模型：{model_name}...")
                try:
                    model = genai.GenerativeModel(model_name)
                    
                    response = model.generate_content([
                        {'mime_type': img_file.content_type, 'data': img_data},
                        prompt_request
                    ])
                    
                    result_prompt = response.text
                    print(f"✅ [Debug] {model_name} 分析成功！")
                    break 

                except Exception as inner_e:
                    error_msg = str(inner_e)
                    print(f"⚠️ [Debug] {model_name} 失敗: {error_msg}")
                    
                    # 如果是 429，通常代表該模型的「每日額度」滿了，直接換下一個模型，不用等待
                    # 因為如果是 Daily Limit Reached，等 30 秒也沒用
                    if "404" in error_msg:
                         print(f"ℹ️ [Info] 模型 {model_name} 找不到，可能是套件版本問題。")
                    
                    continue
            
            if not result_prompt:
                raise Exception("所有可用模型的額度皆已耗盡 (Daily Quota Exceeded)。請明天再來，或嘗試升級 API Key。")

            # 轉成 base64 以在前端顯示
            b64_img = base64.b64encode(img_data).decode('utf-8')
            image_url = f"data:{img_file.content_type};base64,{b64_img}"

        except Exception as e:
            print(f"❌ [Debug] 最終錯誤: {e}")
            result_prompt = f"分析失敗：{str(e)}"

    return render(request, 'tutorials/lab_image_analysis.html', {
        'result_prompt': result_prompt,
        'image_url': image_url
    })