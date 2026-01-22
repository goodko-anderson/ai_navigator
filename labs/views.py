from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.html import strip_tags 
from django.utils.text import slugify # 👈 引入這個來做中文網址
import uuid
import json
import time
import os  # ✅ 新增：引入 OS 模組，用來自動建立資料夾
import google.generativeai as genai
import PIL.Image
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
import io
from django.core.files.base import ContentFile
import warnings

# 👇 引入所有 Model 和 Form
from .models import LabProject, ReverseImage, IsoAnalysis
from .forms import AIWriterForm, ReverseImageForm, IsoAnalysisForm
from tutorials.models import Article 

try:
    from tools.models import Tool
except ImportError:
    Tool = None

# ==========================================
# 0. 共用工具函式 (Helpers)
# ==========================================

# --- 🔐 權限檢查 ---
def is_superuser(user):
    return user.is_superuser

# --- 🔧 內容淨化 (移除 HTML 雜質) ---
def clean_ai_content(text):
    if not text: return ""
    cleaned = text
    cleaned = cleaned.replace("```html", "").replace("```", "")
    tags_to_remove = ["<!DOCTYPE html>", "<html>", "</html>", "<head>", "</head>", "<body>", "</body>"]
    for tag in tags_to_remove:
        cleaned = cleaned.replace(tag, "")
    return cleaned.strip()

# --- 🔧 文字生成函式 (Gemini 2.0) ---
def try_generate_content(prompt):
    api_key = settings.GEMINI_API_KEY
    if not api_key: raise ValueError("尚未設定 API Key")
    genai.configure(api_key=api_key)

    candidate_models = [
        "gemini-2.0-flash",           # 首選
        "gemini-2.5-flash",           # 最新
        "gemini-2.0-flash-exp",       
        "gemini-flash-latest",        
        "gemini-2.5-pro"              
    ]

    last_error = None
    for model_name in candidate_models:
        try:
            print(f"📡 AI 寫手嘗試連線: {model_name} ...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return clean_ai_content(response.text), model_name
        except Exception as e:
            print(f"⚠️ {model_name} 失敗: {str(e)}")
            last_error = e
            if "429" in str(e): time.sleep(1)
            continue
            
    raise RuntimeError(f"所有模型皆無法連線。請檢查 API Key 或網路。")

# --- 👁️ 視覺生成函式 (逆向工程) ---
def try_generate_vision(prompt, img):
    api_key = settings.GEMINI_API_KEY
    if not api_key: raise ValueError("尚未設定 API Key")
    genai.configure(api_key=api_key)

    candidate_models = [
        "gemini-2.0-flash",             
        "gemini-2.5-flash",             
        "gemini-2.0-flash-exp",         
        "gemini-flash-latest",          
        "gemini-2.0-flash-lite-preview" 
    ]

    last_error = None
    for model_name in candidate_models:
        try:
            print(f"👁️ 逆向工程嘗試連線: {model_name} ...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content([prompt, img])
            print(f"✅ 視覺分析成功！使用模型: {model_name}")
            return clean_ai_content(response.text)
        except Exception as e:
            print(f"⚠️ {model_name} 失敗: {str(e)}")
            last_error = e
            if "429" in str(e): time.sleep(1)
            continue

    raise RuntimeError(f"視覺模型全數陣亡。")


# ==========================================
# 1. 一般視圖 (Views)
# ==========================================

def lab_list(request):
    projects_all = LabProject.objects.all().order_by('-created_at')
    tool_filter = request.GET.get('tool')
    if tool_filter:
        projects_all = projects_all.filter(related_tool__name=tool_filter)
    
    tools = []
    if Tool:
        tools = Tool.objects.filter(lab_projects__isnull=False).annotate(total_projects=Count('lab_projects')).order_by('-total_projects')

    paginator = Paginator(projects_all, 6)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'labs/lab_list.html', {
        'projects': page_obj, 'tools': tools, 'current_tool': tool_filter, 'total_count': LabProject.objects.count()
    })

def lab_detail(request, pk):
    project = get_object_or_404(LabProject, pk=pk)
    project.views += 1
    project.save()
    return render(request, 'labs/lab_detail.html', {'project': project})

@user_passes_test(is_superuser)
def ai_writer_view(request):
    new_project = None
    if request.method == 'POST':
        form = AIWriterForm(request.POST)
        if form.is_valid():
            topic = form.cleaned_data['topic']
            try:
                prompt = f"""
                你現在是一位專業的科技部落客。請寫一篇關於「{topic}」的繁體中文教學文章。
                【格式嚴格要求】：
                1. 直接給我 HTML 原始碼，從 <h2> 開始寫。
                2. 絕對不要包含 <html>, <head>, <body> 標籤。
                3. 使用 <h2>, <h3>, <p>, <ul>, <li>, <strong> 標籤排版。
                【文章結構】：
                1. 引言 (用 <p> 開頭)
                2. 三個核心重點章節 (用 <h2> 標題)
                3. 總結
                """
                result_text, used_model = try_generate_content(prompt)
                
                # === ⭐ 自動關聯工具 (升級版) ===
                related_tool = None
                if Tool:
                    all_tools = Tool.objects.all()
                    topic_lower = topic.lower()
                    
                    # 1. 檢查輸入主題
                    for tool in all_tools:
                        if tool.name.lower() in topic_lower or topic_lower in tool.name.lower():
                            related_tool = tool
                            break
                    
                    # 2. 檢查 AI 生成內容 (防漏網之魚)
                    if not related_tool:
                        generated_preview = strip_tags(result_text).lower()[:500]
                        for tool in all_tools:
                            if tool.name.lower() in generated_preview:
                                related_tool = tool
                                break

                    # 3. 特殊縮寫
                    if not related_tool and ("midjourney" in topic_lower or "mj" in topic_lower):
                         related_tool = Tool.objects.filter(name__icontains="Midjourney").first()
                # ==================================
                
                clean_description = strip_tags(result_text)[:150] + "..."
                new_project = LabProject.objects.create(
                    title=f"AI 生成：{topic}", description=clean_description,
                    content=result_text, user=request.user,
                    status='completed', related_tool=related_tool
                )
                msg = f'文章生成成功！(模型：{used_model})'
                if related_tool: msg += f' 已自動關聯工具：{related_tool.name}'
                messages.success(request, msg)
            except Exception as e:
                messages.error(request, f'生成失敗：{str(e)}')
    else:
        form = AIWriterForm()
    return render(request, 'labs/ai_writer.html', {'form': form, 'new_project': new_project})

@user_passes_test(is_superuser)
def publish_lab_to_article(request, pk):
    project = get_object_or_404(LabProject, pk=pk)
    clean_title = project.title.replace("AI 生成：", "").strip()[:100]
    
    existing_article = Article.objects.filter(title=clean_title).first()
    if existing_article:
        messages.info(request, "這篇文章之前已經發布過囉！")
        return redirect('article_detail', slug=existing_article.slug)

    try:
        # === ⭐ 網址生成邏輯 (中文友善版) ===
        # 允許 Unicode (中文)
        base_slug = slugify(clean_title, allow_unicode=True) 
        
        # 萬一標題全是特殊符號，回退到隨機碼
        if not base_slug:
            base_slug = f"ai-{uuid.uuid4().hex[:8]}"
            
        new_slug = base_slug
        counter = 1
        
        # 避免網址重複 (例如：python-教學-1)
        while Article.objects.filter(slug=new_slug).exists():
            new_slug = f"{base_slug}-{counter}"
            counter += 1
        # ==================================

        Article.objects.create(
            title=clean_title, 
            content=clean_ai_content(project.content),
            author=request.user, 
            category="實戰教學",
            related_tool=project.related_tool, 
            slug=new_slug,            
            is_published=True, 
            cover_image=project.cover_image 
        )
        messages.success(request, f"已成功發布！網址：/article/{new_slug}/")
        return redirect('article_list')
    except Exception as e:
        messages.error(request, f"發布發生錯誤：{str(e)}")
        return redirect('lab_detail', pk=pk)

@login_required
def reverse_engineering_view(request):
    analysis_result = None
    if request.method == 'POST':
        form = ReverseImageForm(request.POST, request.FILES)
        if form.is_valid():
            # ✅ 新增：確保 lab_before 資料夾存在 (防止滑桿壞掉)
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'lab_before'), exist_ok=True)

            reverse_obj = form.save(commit=False)
            reverse_obj.user = request.user
            reverse_obj.save()
            try:
                img = PIL.Image.open(reverse_obj.image.path)
                prompt = """
                你是一位精通 Midjourney 的 Prompt 工程師。
                請仔細觀察這張圖片，進行「逆向工程」。
                請輸出兩部分內容：
                1. 【英文咒語 (Prompts)】：寫出能生成這張圖片風格、構圖、光影、內容的 Midjourney 英文指令。
                2. 【中文分析】：用繁體中文簡短分析這張圖的「構圖技巧」、「光影設定」和「藝術風格」。
                【格式要求 - 請直接輸出 HTML】：
                請不要給 Markdown 代碼塊。
                英文咒語部分請用 <div class="p-3 bg-black text-warning font-monospace rounded mb-3 border border-secondary"> 包裹。
                中文分析部分請用 <div class="text-light opacity-75"> 包裹。
                標題請用 <h5 class="text-white fw-bold mt-3">。
                """
                reverse_obj.prompt_result = try_generate_vision(prompt, img)
                reverse_obj.save()
                analysis_result = reverse_obj
                messages.success(request, "視覺分析完成！AI 已成功解析圖片基因。")
            except Exception as e:
                messages.error(request, f"AI 分析失敗：{str(e)}")
    else:
        form = ReverseImageForm()
    return render(request, 'labs/reverse_engineering.html', {'form': form, 'result': analysis_result})


# ==========================================
# 2. ISO 11608 核心演算法 (Anderson-Darling Minitab 版)
# ==========================================

def calculate_iso_specs(v_set, alpha, beta):
    """計算 ISO 11608 規格限值 (LSL, USL)"""
    if beta == 0: beta = 0.0001
    
    # 計算轉折點 (Transition Point)
    tp = (100 * alpha) / beta
    
    if v_set <= tp:
        # 小劑量模式：使用絕對誤差 (±alpha)
        lsl = max(0, v_set - alpha)
        usl = v_set + alpha
        mode = "Fixed (±α)"
    else:
        # 大劑量模式：使用百分比誤差 (±beta%)
        tol = (beta * v_set) / 100
        lsl = max(0, v_set - tol)
        usl = v_set + tol
        mode = f"Percent (±{beta}%)"
        
    return lsl, usl, mode

def get_ad_p_value(ad_stat, n):
    """Minitab 修正版 P-Value 計算公式 (基於 D'Agostino & Stephens)"""
    if n < 2: return 0.0
    
    # 修正統計量 A^2*
    a_sq_star = ad_stat * (1 + 0.75/n + 2.25/(n**2))
    
    # 根據 A^2* 的大小選擇不同的逼近公式
    if a_sq_star >= 0.6: 
        p = np.exp(1.2937 - 5.709 * a_sq_star + 0.0186 * (a_sq_star**2))
    elif a_sq_star >= 0.34: 
        p = np.exp(0.9177 - 4.279 * a_sq_star - 1.38 * (a_sq_star**2))
    elif a_sq_star > 0.2: 
        p = 1 - np.exp(-8.318 + 42.796 * a_sq_star - 59.938 * (a_sq_star**2))
    else: 
        p = 1 - np.exp(-13.436 + 101.14 * a_sq_star - 223.73 * (a_sq_star**2))
        
    return p

def ad_test_logic(values):
    """執行 Anderson-Darling 常態性檢定"""
    if len(values) < 3: return 0, 0, 0, False
    
    # 封印 FutureWarning (Scipy 更新提示)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=FutureWarning)
        res = stats.anderson(values, dist='norm')
        
    ad_stat = res.statistic
    p_val = get_ad_p_value(ad_stat, len(values))
    
    # 取得 Minitab 臨界值 (僅供參考)
    try:
        if hasattr(res, 'significance_level'):
            idx = list(res.significance_level).index(5.0)
            ad_crit = res.critical_values[idx]
        else:
            ad_crit = 0.752
    except:
        ad_crit = 0.752 
        
    is_norm = p_val > 0.05
    return ad_stat, ad_crit, p_val, is_norm

def compute_ad_plot_data(df_group):
    """計算 AD Plot (QQ Plot) 的座標點"""
    df_sorted = df_group.sort_values('val').reset_index(drop=True)
    v = df_sorted['val'].values
    
    # 計算理論分位數 (OSM) 與有序觀察值 (OSR)
    (osm, osr), (slope, intercept, _) = stats.probplot(v, dist="norm")
    
    # 計算殘差 (Residual) 用於找出離群值
    fitted = slope * osm + intercept
    residual = np.abs(osr - fitted)
    
    out = df_sorted.copy()
    out['osm'], out['osr'], out['residual'] = osm, osr, residual
    return out, slope, intercept

@login_required
def iso_analysis_view(request):
    analysis_result = None
    
    if request.method == 'POST':
        form = IsoAnalysisForm(request.POST, request.FILES)
        if form.is_valid():
            # ✅ 新增：自我修復機制 (自動建立消失的資料夾)
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'iso_data'), exist_ok=True)
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'iso_plots'), exist_ok=True)

            iso_obj = form.save(commit=False)
            iso_obj.user = request.user
            
            try:
                # 1. 讀取檔案
                file = request.FILES['data_file']
                if file.name.endswith('.csv'):
                    raw = pd.read_csv(file)
                else:
                    raw = pd.read_excel(file)
                
                results_json = []
                density = iso_obj.density
                iso_k = iso_obj.param_k
                alpha = iso_obj.param_alpha
                beta = iso_obj.param_beta
                
                target_map = {
                    'Min': iso_obj.v_min,
                    'Mid': iso_obj.v_mid,
                    'Max': iso_obj.v_max
                }
                
                # === ⭐ 圖表視覺優化區 (Visual Optimization) ⭐ ===
                plt.style.use('dark_background')
                plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Arial', 'DejaVu Sans']
                plt.rcParams['axes.unicode_minus'] = False # 解決負號顯示問題

                # 字體全面加大
                plt.rcParams['font.size'] = 11          
                plt.rcParams['axes.titlesize'] = 14      
                plt.rcParams['axes.labelsize'] = 12      
                plt.rcParams['xtick.labelsize'] = 10     
                plt.rcParams['ytick.labelsize'] = 10     
                plt.rcParams['legend.fontsize'] = 10    

                # 顏色高對比優化
                axis_color = '#e2e8f0' # 亮灰白色
                grid_color = '#475569' # 較淡的網格線
                
                plt.rcParams['text.color'] = axis_color
                plt.rcParams['axes.labelcolor'] = axis_color
                plt.rcParams['xtick.color'] = axis_color
                plt.rcParams['ytick.color'] = axis_color
                plt.rcParams['axes.edgecolor'] = axis_color
                plt.rcParams['axes.linewidth'] = 1.2
                plt.rcParams['grid.color'] = grid_color
                plt.rcParams['grid.alpha'] = 0.4
                plt.rcParams['grid.linestyle'] = '--'
                
                # 準備畫布
                fig, axes = plt.subplots(2, 3, figsize=(18, 12), facecolor='#0b0f19')
                plt.subplots_adjust(hspace=0.4, wspace=0.25)
                # ================================================
                
                overall_pass = True
                
                # 3. 迴圈處理 Min, Mid, Max
                for idx, (key, v_set) in enumerate(target_map.items()):
                    lsl, usl, spec_mode = calculate_iso_specs(v_set, alpha, beta)
                    
                    cols = [c for c in raw.columns if key.upper() in str(c).upper()]
                    if not cols:
                        axes[0, idx].text(0.5, 0.5, f"No {key} Data", ha='center', color='gray', fontsize=14)
                        axes[1, idx].axis('off')
                        continue
                        
                    s = pd.to_numeric(raw[cols[0]], errors='coerce').dropna()
                    vol_values = s.values / density
                    
                    current_df = pd.DataFrame({'val': vol_values, 'id': range(1, len(vol_values)+1)})
                    initial_count = len(vol_values)
                    
                    # === 自動優化 (AD Test Loop) ===
                    removed_ids = []
                    MAX_REMOVALS = 3
                    MIN_N = 15
                    
                    ad_stat, ad_crit, p_val, is_norm = 0, 0, 0, False
                    
                    for _ in range(MAX_REMOVALS + 1): 
                        v = current_df['val'].values
                        if len(v) < MIN_N: break
                        
                        ad_stat, ad_crit, p_val, is_norm = ad_test_logic(v)
                        
                        if is_norm: break
                        
                        if len(removed_ids) < MAX_REMOVALS:
                            p_df, _, _ = compute_ad_plot_data(current_df)
                            bad_row = p_df.sort_values('residual', ascending=False).iloc[0]
                            bad_id = int(bad_row['id'])
                            current_df = current_df[current_df['id'] != bad_id]
                            removed_ids.append(bad_id)
                        else: break
                    
                    # === 最終統計 ===
                    mu, sd = np.mean(v), np.std(v, ddof=1)
                    k_act = 0
                    if sd > 0:
                        k_act = min((mu - lsl) / sd, (usl - mu) / sd)
                    
                    in_range = np.all((v >= lsl) & (v <= usl))
                    ti_pass = k_act >= iso_k
                    is_group_pass = is_norm and in_range and ti_pass
                    if not is_group_pass: overall_pass = False
                    
                    results_json.append({
                        'group': key,
                        'v_set': v_set,
                        'n': len(v), 
                        'n_init': initial_count,
                        'mean': round(mu, 4),
                        'sd': round(sd, 4),
                        'lsl': round(lsl, 4),
                        'usl': round(usl, 4),
                        'k_act': round(k_act, 3),
                        'p_val': f"{p_val:.4f}" if p_val >= 0.005 else "< 0.005",
                        'verdict': "PASS" if is_group_pass else "FAIL",
                        'spec_mode': spec_mode,
                        'removed_ids': removed_ids if removed_ids else "-"
                    })
                    
                    # === 繪圖 ===
                    # 1. 上排：直方圖
                    ax_h = axes[0, idx]
                    ax_h.set_title(f"{key} (Vset={v_set})", color='white', fontweight='bold')
                    
                    # 繪製直方圖 (Histogram)
                    n_bins, bins, patches = ax_h.hist(v, bins=10, density=True, alpha=0.7, color='#0dcaf0', edgecolor='black', label='Data')
                    
                    # 繪製擬合曲線 (Fit Curve)
                    xr = np.linspace(min(v.min(), lsl)*0.98, max(v.max(), usl)*1.02, 100)
                    ax_h.plot(xr, stats.norm.pdf(xr, mu, sd), color='#ef4444', lw=2.5, label='Fit')
                    
                    # 繪製規格線
                    ax_h.axvline(lsl, color='#fbbf24', linestyle='--', linewidth=2, label='LSL')
                    ax_h.axvline(usl, color='#fbbf24', linestyle='--', linewidth=2, label='USL')
                    ax_h.axvline(v_set, color='#10b981', linestyle=':', linewidth=2, label='Vset')
                    
                    ax_h.legend(loc='upper right', frameon=True, facecolor='#1e293b', edgecolor='#475569')
                    
                    # 2. 下排：AD Plot
                    ax_p = axes[1, idx]
                    ax_p.set_title(f"AD Plot (P={p_val:.3f})", color='white', fontweight='bold')
                    
                    p_df, slp, icp = compute_ad_plot_data(current_df)
                    ax_p.scatter(p_df['osm'], p_df['osr'], color='#94a3b8', s=40, alpha=0.9, edgecolor='#cbd5e1', zorder=3)
                    ax_p.plot(p_df['osm'], slp * p_df['osm'] + icp, color='#ef4444', linestyle='--', lw=2, zorder=2)
                    ax_p.grid(True, zorder=0)

                # 4. 存檔
                buffer = io.BytesIO()
                fig.savefig(buffer, format='png', facecolor='#0b0f19', transparent=True)
                buffer.seek(0)
                plt.close(fig)
                
                file_name = f"iso_v1_{iso_obj.user.id}_{int(time.time())}.png"
                iso_obj.result_plot.save(file_name, ContentFile(buffer.read()), save=False)
                
                iso_obj.report_data = results_json
                iso_obj.is_pass = overall_pass
                iso_obj.save()
                
                analysis_result = iso_obj
                messages.success(request, "ISO 11608 劑量準確度分析完成！(Minitab Compatible)")
                
            except Exception as e:
                messages.error(request, f"分析失敗：{str(e)}")
    else:
        form = IsoAnalysisForm()

    return render(request, 'labs/iso_analysis.html', {
        'form': form, 
        'result': analysis_result
    })

    # labs/views.py 的最下面

@login_required
def chat_view(request):
    """
    自由對話實驗室 (Free Chat Lab)
    功能：提供一個類似 ChatGPT 的簡易介面，讓使用者直接測試 Gemini 模型。
    """
    response_text = None
    user_input = ""
    
    if request.method == 'POST':
        user_input = request.POST.get('user_input', '').strip()
        if user_input:
            try:
                # 這裡我們直接呼叫之前寫好的共用函式
                # 為了讓 AI 知道這是聊天，我們可以加一點點 System Prompt (可選)
                prompt = f"使用者說：{user_input}\n請以繁體中文、友善且專業的語氣回答。"
                
                result_text, used_model = try_generate_content(prompt)
                
                # 為了讓前端顯示漂亮，將換行符號轉成 HTML 的 <br> (簡易處理)
                response_text = result_text.replace('\n', '<br>')
                
            except Exception as e:
                messages.error(request, f"連線錯誤：{str(e)}")
    
    return render(request, 'labs/chat.html', {
        'response': response_text,
        'user_input': user_input
    })