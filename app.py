import streamlit as st
import yaml
import re
import json
from datetime import datetime
from main import generate_scripts_from_file


# ============================================================
# 正式模式 - 按章节调用 DeepSeek API
# ============================================================

def call_deepseek_api_by_chapters(novel_text, template_type, api_key):
    """按章节分别调用 AI，确保所有章节都被处理"""

    try:
        from openai import OpenAI
    except ImportError:
        return None, "请先安装 openai 库：pip install openai"

    if not api_key:
        return None, "请输入 DeepSeek API Key"

    # 按章节分割小说
    chapter_pattern = r'(第[一二三四五六七八九十百千万0-9]+章[^\n]*[\n])'
    parts = re.split(chapter_pattern, novel_text)

    chapters = []
    for i in range(1, len(parts), 2):
        if i + 1 < len(parts):
            title = parts[i].strip()
            content = parts[i + 1].strip()
            if title and content:
                chapters.append({"title": title, "content": content})

    if len(chapters) == 0:
        chapters = [{"title": "第一章", "content": novel_text[:3000]}]

    st.info(f"📖 检测到 {len(chapters)} 个章节，将逐章调用 AI 处理...")

    template_prompts = {
        "网剧": "采用网剧剧本格式，节奏紧凑，对话简洁",
        "短剧": "采用短剧剧本格式，短小精悍",
        "动漫": "采用动漫剧本格式，二次元风格",
        "电影": "采用电影剧本格式，场景详细",
        "有声书": "采用有声书格式，对话为主"
    }

    system_prompt = f"""你是一位专业的剧本改编专家。将小说片段转换为YAML格式剧本。

{template_prompts.get(template_type, template_prompts['网剧'])}

输出格式（YAML）：
chapter: 章节名
title: 本章标题
location: 场景地点
time: 时间
characters: [角色1, 角色2]
dialogues:
  - speaker: 角色名
    text: 台词内容
emotion: 情绪
camera: ["镜头1", "镜头2"]"""

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    all_scripts = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, chapter in enumerate(chapters):
        status_text.text(f"正在处理第 {idx + 1}/{len(chapters)} 章：{chapter['title']}")
        content = chapter['content'][:2500]

        user_prompt = f"""章节名称：{chapter['title']}

章节内容：
{content}"""

        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=3000
            )

            result = response.choices[0].message.content
            if result.startswith("```yaml"):
                result = result[7:]
            if result.startswith("```"):
                result = result[3:]
            if result.endswith("```"):
                result = result[:-3]
            result = result.strip()

            try:
                script = yaml.safe_load(result)
                if isinstance(script, dict):
                    all_scripts.append(script)
                elif isinstance(script, list):
                    all_scripts.extend(script)
                else:
                    all_scripts.append({"chapter": chapter['title'], "error": "格式错误"})
            except:
                all_scripts.append({"chapter": chapter['title'], "error": "解析失败"})

        except Exception as e:
            all_scripts.append({"chapter": chapter['title'], "error": str(e)})

        progress_bar.progress((idx + 1) / len(chapters))

    status_text.text(f"✅ 处理完成，共 {len(all_scripts)} 个章节")
    progress_bar.empty()

    # 补充缺失的章节
    expected_count = len(chapters)
    if len(all_scripts) < expected_count:
        st.warning(f"⚠️ 只处理了 {len(all_scripts)}/{expected_count} 章，为缺失章节补全默认结构")
        existing_chapters = {s.get('chapter', '') for s in all_scripts}
        for ch in chapters:
            if ch['title'] not in existing_chapters:
                all_scripts.append({
                    "chapter": ch['title'],
                    "title": ch['title'].replace('章', '章').strip(),
                    "location": "未知地点",
                    "time": "白天",
                    "characters": [],
                    "dialogues": [],
                    "emotion": "平静",
                    "camera": ["中景"],
                    "note": "此章节已自动补全"
                })

    # 按章节排序
    def get_chapter_order(script):
        ch = script.get('chapter', '')
        nums = re.findall(r'(\d+)', ch)
        if nums:
            return int(nums[0])
        chinese_nums = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
        for cn, num in chinese_nums.items():
            if cn in ch:
                return num
        return 999

    all_scripts.sort(key=get_chapter_order)

    return all_scripts, None


def ai_mode_convert(text, template_type, api_key):
    scripts, error = call_deepseek_api_by_chapters(text, template_type, api_key)
    if error:
        st.error(f"❌ {error}")
        return []
    if scripts:
        valid_count = len([s for s in scripts if 'error' not in s])
        st.success(f"✅ 成功处理 {valid_count}/{len(scripts)} 个章节")
        return scripts if valid_count > 0 else []
    return []


# ============================================================
# 安全解析函数
# ============================================================

def safe_get_camera(camera_value):
    if camera_value is None:
        return ["中景"]
    if isinstance(camera_value, list):
        return [str(c) for c in camera_value if isinstance(c, str)][:4]
    if isinstance(camera_value, str):
        return [camera_value]
    return ["中景"]


def safe_get_characters(characters_value):
    if characters_value is None:
        return []
    if isinstance(characters_value, list):
        return [str(c) for c in characters_value if isinstance(c, str)][:6]
    if isinstance(characters_value, str):
        return [characters_value]
    return []


# ============================================================
# 页面配置
# ============================================================

st.set_page_config(
    page_title="AI 小说转剧本工具",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-title { font-size: 3rem; font-weight: 700; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 0.5rem; }
    .sub-title { text-align: center; color: #666; font-size: 1.1rem; margin-bottom: 2rem; }
    .feature-card { background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%); border-radius: 15px; padding: 1rem; text-align: center; transition: transform 0.3s; }
    .feature-card:hover { transform: translateY(-5px); }
    .stat-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; padding: 1.2rem; text-align: center; color: white; }
    .success-box { background: linear-gradient(135deg, #d4fc79 0%, #96e6a1 100%); border-radius: 12px; padding: 1rem; margin: 1rem 0; }
    .info-box { background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%); border-radius: 12px; padding: 1rem; margin: 1rem 0; }
    .sidebar-header { font-size: 1.2rem; font-weight: 600; margin-bottom: 1rem; color: #667eea; }
    .stButton > button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 25px; padding: 0.6rem 1.5rem; font-weight: 600; transition: all 0.3s; }
    .stButton > button:hover { transform: scale(1.02); box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4); }
    .mode-badge-demo { background: #f0ad4e; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; display: inline-block; }
    .mode-badge-ai { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; display: inline-block; }
    .custom-divider { height: 3px; background: linear-gradient(90deg, #667eea, #764ba2, #667eea); margin: 1.5rem 0; border-radius: 3px; }
    .stTabs [data-baseweb="tab-list"] { gap: 2rem; }
    .stTabs [data-baseweb="tab"] { font-size: 1rem; font-weight: 500; color: #666; }
    .stTabs [aria-selected="true"] { color: #667eea; border-bottom-color: #667eea; }
    .footer { text-align: center; padding: 2rem; color: #999; font-size: 0.85rem; border-top: 1px solid #eee; margin-top: 2rem; }
    .warning-box { background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 12px; border-radius: 8px; margin: 10px 0; }
    .info-box-blue { background-color: #d1ecf1; border-left: 4px solid #17a2b8; padding: 12px; border-radius: 8px; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎬 AI 小说转剧本工具</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">上传小说，AI 自动生成结构化剧本、角色、台词、场景、情绪和镜头建议</div>',
            unsafe_allow_html=True)
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# 功能卡片
c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(
    '<div class="feature-card"><span style="font-size:2rem;">📖</span><h4>智能解析</h4><p style="color:#666;">自动识别章节</p></div>',
    unsafe_allow_html=True)
with c2: st.markdown(
    '<div class="feature-card"><span style="font-size:2rem;">🎭</span><h4>角色提取</h4><p style="color:#666;">AI识别角色</p></div>',
    unsafe_allow_html=True)
with c3: st.markdown(
    '<div class="feature-card"><span style="font-size:2rem;">🎬</span><h4>镜头建议</h4><p style="color:#666;">专业分镜推荐</p></div>',
    unsafe_allow_html=True)
with c4: st.markdown(
    '<div class="feature-card"><span style="font-size:2rem;">📊</span><h4>情绪分析</h4><p style="color:#666;">场景情感标注</p></div>',
    unsafe_allow_html=True)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ============================================================
# 侧边栏
# ============================================================

with st.sidebar:
    st.markdown('<div class="sidebar-header">⚙️ 工具设置</div>', unsafe_allow_html=True)

    # 运行模式选择
    st.markdown("### 🎮 运行模式")
    mode = st.radio(
        "选择模式",
        ["演示模式", "正式模式 (需API Key)"],
        help="演示模式：仅角色识别使用AI，其他功能（镜头、情绪、场景）使用规则匹配"
    )

    # 演示模式说明（醒目提示）
    if mode == "演示模式":
        st.markdown("""
        <div class="warning-box">
            ⚠️ <strong>演示模式说明</strong><br>
            • ✅ 角色识别：调用 AI（准确）<br>
            • ⚡ 镜头建议：规则匹配<br>
            • ⚡ 情绪分析：规则匹配<br>
            • ⚡ 场景识别：规则匹配<br>
            • ⚡ 台词提取：规则匹配<br>
            <span style="font-size:12px; color:#856404;">💡 如需完整AI功能，请使用「正式模式」并输入API Key</span>
        </div>
        """, unsafe_allow_html=True)

    # 正式模式说明
    if mode == "正式模式 (需API Key)":
        st.markdown("""
        <div class="info-box-blue">
            🤖 <strong>正式模式说明</strong><br>
            • ✅ 角色识别：调用 AI<br>
            • ✅ 镜头建议：调用 AI<br>
            • ✅ 情绪分析：调用 AI<br>
            • ✅ 场景识别：调用 AI<br>
            • ✅ 台词提取：调用 AI<br>
            <span style="font-size:12px; color:#0c5460;">💡 需要有效的 DeepSeek API Key</span>
        </div>
        """, unsafe_allow_html=True)

    # API Key 输入（仅正式模式显示）
    api_key = None
    if mode == "正式模式 (需API Key)":
        st.markdown("---")
        api_key = st.text_input(
            "🔑 DeepSeek API Key",
            type="password",
            placeholder="请输入你的 API Key",
            help="前往 platform.deepseek.com 获取"
        )
        st.caption("💡 [获取 API Key](https://platform.deepseek.com/)")

    st.markdown("---")

    # 剧本模板
    template_type = st.selectbox("📚 剧本模板", ["网剧", "短剧", "动漫", "电影", "有声书"])

    st.markdown("---")
    template_desc = {
        "网剧": "节奏紧凑，适合网络传播",
        "短剧": "短小精悍，适合短视频",
        "动漫": "二次元风格，适合动画",
        "电影": "场景详细，适合大银幕",
        "有声书": "对话为主，适合音频"
    }
    st.info(f"📌 {template_desc.get(template_type, '通用模板')}")

    st.markdown("---")

    # 模式对比表
    with st.expander("📊 演示模式 vs 正式模式"):
        st.markdown("""
| 功能 | 演示模式 | 正式模式 |
|------|----------|----------|
| 角色识别 | ✅ AI 识别 | ✅ AI 识别 |
| 镜头建议 | ⚡ 规则匹配 | ✅ AI 生成 |
| 情绪分析 | ⚡ 规则匹配 | ✅ AI 分析 |
| 场景识别 | ⚡ 规则匹配 | ✅ AI 识别 |
| 台词提取 | ⚡ 规则匹配 | ✅ AI 提取 |
| 需要 API Key | ❌ 不需要 | ✅ 需要 |
| 处理速度 | 快速 | 较慢（逐章） |
| 效果质量 | 良好 | 专业 |
        """)

    st.markdown("---")
    st.caption("🎬 v3.0")

# ============================================================
# 主内容区域
# ============================================================

# 显示当前模式标签（带说明）
if mode == "演示模式":
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
        <span class="mode-badge-demo">🎮 演示模式</span>
        <span style="font-size: 12px; color: #856404;">⚠️ 仅角色识别使用AI，其他功能为规则匹配</span>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
        <span class="mode-badge-ai">🤖 正式模式</span>
        <span style="font-size: 12px; color: #0c5460;">✅ 全部功能使用AI增强</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")

# 上传区域
uploaded_file = st.file_uploader("📁 上传小说文件", type=["txt"])

if uploaded_file:
    text = uploaded_file.read().decode("utf-8")
    file_size = len(text)
    chapters_found = re.findall(r'第[一二三四五六七八九十百千万0-9]+章', text)
    chapter_count = len(set(chapters_found))

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f'<div class="stat-card"><div class="stat-number">📄</div><div class="stat-label">{uploaded_file.name}</div></div>',
            unsafe_allow_html=True)
    with c2:
        st.markdown(
            f'<div class="stat-card"><div class="stat-number">{file_size:,}</div><div class="stat-label">字符数</div></div>',
            unsafe_allow_html=True)
    with c3:
        st.markdown(
            f'<div class="stat-card"><div class="stat-number">{chapter_count}</div><div class="stat-label">检测到章节</div></div>',
            unsafe_allow_html=True)

    with st.expander("📖 小说预览"):
        st.text(text[:600] + ("..." if len(text) > 600 else ""))

    if st.button("🚀 开始转换", use_container_width=True):
        if mode == "正式模式 (需API Key)" and not api_key:
            st.error("❌ 请在侧边栏输入 DeepSeek API Key")
            st.stop()

        if mode == "演示模式":
            with st.spinner("📖 正在解析小说，生成剧本中...（AI识别角色）"):
                scripts = generate_scripts_from_file(text, template_type)

            # 确保演示模式输出正确的字段格式
            for script in scripts:
                if 'camera' not in script or not isinstance(script['camera'], list):
                    script['camera'] = ["中景"]
                if 'characters' not in script:
                    script['characters'] = []
                if 'dialogues' not in script:
                    script['dialogues'] = []
                if 'emotion' not in script:
                    script['emotion'] = "平静"
                if 'location' not in script:
                    script['location'] = "未知"

            total_chars = sum(len(s.get('characters', [])) for s in scripts)
            total_dialogues = sum(len(s.get('dialogues', [])) for s in scripts)

            st.markdown(f"""
            <div class="success-box">
                🎉 <strong>剧本生成完成！（演示模式）</strong><br>
                共 {len(scripts)} 章，识别 {total_chars} 个角色，{total_dialogues} 段对话<br>
                <span style="font-size:0.8rem;">⚠️ 演示模式：仅角色识别使用AI，其他功能为规则匹配</span>
            </div>
            """, unsafe_allow_html=True)

        else:
            with st.spinner("🤖 AI 正在逐章分析小说...（可能需要30-60秒）"):
                scripts = ai_mode_convert(text, template_type, api_key)
            if not scripts:
                st.stop()
            total_chars = sum(len(s.get('characters', [])) for s in scripts)
            total_dialogues = sum(len(s.get('dialogues', [])) for s in scripts)
            st.markdown(f"""
            <div class="success-box">
                🤖 <strong>剧本生成完成！（正式模式 - AI 增强）</strong><br>
                共 {len(scripts)} 章，识别 {total_chars} 个角色，{total_dialogues} 段对话
            </div>
            """, unsafe_allow_html=True)

        st.session_state['scripts'] = scripts

        # 修复字段
        for script in st.session_state['scripts']:
            if 'camera' in script:
                script['camera'] = safe_get_camera(script['camera'])
            else:
                script['camera'] = ["中景"]
            if 'characters' in script:
                script['characters'] = safe_get_characters(script['characters'])
            else:
                script['characters'] = []

        # ========== 标签页 ==========
        tab1, tab2, tab3, tab4 = st.tabs(["📜 剧本内容", "🎭 角色分析", "📊 统计分析", "📥 导出文件"])

        with tab1:
            for idx, s in enumerate(st.session_state['scripts'], 1):
                chapter_name = s.get('chapter', f'第{idx}章')
                title_name = s.get('title', '无标题')
                with st.expander(f"📖 {chapter_name}：{title_name}"):
                    ca, cb, cc, cd = st.columns(4)
                    with ca:
                        st.markdown(f"**📍 地点**<br>{s.get('location', '未知')}", unsafe_allow_html=True)
                    with cb:
                        st.markdown(f"**🎭 情绪**<br>{s.get('emotion', '平静')}", unsafe_allow_html=True)
                    with cc:
                        camera = s.get('camera', ['中景'])
                        camera_str = ', '.join([str(c) for c in camera[:3] if isinstance(c, str)]) if isinstance(camera,
                                                                                                                 list) else str(
                            camera)[:30]
                        st.markdown(f"**🎬 镜头**<br>{camera_str}", unsafe_allow_html=True)
                    with cd:
                        chars = s.get('characters', [])
                        char_str = ', '.join([str(c) for c in chars[:3] if isinstance(c, str)])
                        st.markdown(f"**👥 角色**<br>{char_str if char_str else '未知'}", unsafe_allow_html=True)
                    st.markdown("---")
                    dialogues = s.get('dialogues', [])
                    if dialogues:
                        st.markdown("**💬 对话内容**")
                        for d in dialogues[:10]:
                            if isinstance(d, dict):
                                speaker = d.get('speaker', '未知')
                                dialog_text = d.get('text', '')
                                st.markdown(f"> **{speaker}**：{dialog_text}")
                    else:
                        st.caption("暂无对话内容")
                    with st.expander("🔧 查看 YAML"):
                        st.code(yaml.dump(s, allow_unicode=True, sort_keys=False), language="yaml")

        with tab2:
            st.markdown("#### 🎭 角色分析")
            all_chars = set()
            char_dialogues = {}
            for s in st.session_state['scripts']:
                for c in s.get('characters', []):
                    if isinstance(c, str) and c:
                        all_chars.add(c)
                for d in s.get('dialogues', []):
                    if isinstance(d, dict):
                        sp = d.get('speaker', '未知')
                        if sp:
                            char_dialogues[sp] = char_dialogues.get(sp, 0) + 1
            col_l, col_r = st.columns(2)
            with col_l:
                st.markdown("**👥 角色列表**")
                if all_chars:
                    for char in sorted(all_chars)[:20]:
                        st.markdown(f"- {char}")
                else:
                    st.info("未识别到角色")
            with col_r:
                st.markdown("**🎙️ 台词统计**")
                if char_dialogues:
                    max_cnt = max(char_dialogues.values())
                    for sp, cnt in sorted(char_dialogues.items(), key=lambda x: -x[1])[:10]:
                        st.progress(cnt / max_cnt if max_cnt > 0 else 0)
                        st.markdown(f"**{sp}**：{cnt} 句")
                else:
                    st.info("暂无台词数据")

        with tab3:
            st.markdown("#### 📊 统计分析")
            all_chars_set = set()
            total_dialogues = 0
            emotions = {}
            locations = {}
            for s in st.session_state['scripts']:
                for c in s.get('characters', []):
                    if isinstance(c, str) and c:
                        all_chars_set.add(c)
                total_dialogues += len(s.get('dialogues', []))
                em = s.get('emotion', '未知')
                # 如果 em 是列表，取第一个元素
                if isinstance(em, list):
                    em = em[0] if em else '未知'
                elif not isinstance(em, str):
                    em = str(em)
                emotions[em] = emotions.get(em, 0) + 1
                loc = s.get('location', '未知')
                if isinstance(loc, list):
                    loc = loc[0] if loc else '未知'
                elif not isinstance(loc, str):
                    loc = str(loc)
                locations[loc] = locations.get(loc, 0) + 1
            sc1, sc2, sc3, sc4 = st.columns(4)
            with sc1:
                st.metric("📖 总章节数", len(st.session_state['scripts']))
            with sc2:
                st.metric("👥 总角色数", len(all_chars_set))
            with sc3:
                st.metric("💬 总对话数", total_dialogues)
            with sc4:
                avg = round(total_dialogues / len(st.session_state['scripts']), 1) if st.session_state[
                    'scripts'] else 0; st.metric("平均对话/章", avg)
            if emotions:
                st.markdown("---")
                st.markdown("**🎭 情绪分布**")
                for em, cnt in sorted(emotions.items(), key=lambda x: -x[1]):
                    st.markdown(f"- {em}: {cnt} 章")
            if locations:
                st.markdown("---")
                st.markdown("**📍 地点分布**")
                for loc, cnt in sorted(locations.items(), key=lambda x: -x[1])[:5]:
                    st.markdown(f"- {loc}: {cnt} 章")

        with tab4:
            st.markdown("#### 📥 导出文件")
            full_yaml = yaml.dump(st.session_state['scripts'], allow_unicode=True, sort_keys=False)
            col_d1, col_d2, col_d3 = st.columns(3)
            with col_d1:
                st.download_button("📄 下载 YAML", full_yaml, f"script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml")
            with col_d2:
                json_data = json.dumps(st.session_state['scripts'], ensure_ascii=False, indent=2)
                st.download_button("🔧 下载 JSON", json_data, f"script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with col_d3:
                script_text = ""
                for s in st.session_state['scripts']:
                    script_text += f"【{s.get('chapter', '')}】{s.get('title', '')}\n"
                    for d in s.get('dialogues', []):
                        if isinstance(d, dict):
                            script_text += f"{d.get('speaker', '')}：{d.get('text', '')}\n"
                    script_text += "\n"
                st.download_button("📝 下载台词本", script_text,
                                   f"script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            st.markdown("---")
            report = f"""剧本统计报告
生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
运行模式：{mode}
模板类型：{template_type}
总章节数：{len(st.session_state['scripts'])}
总角色数：{len(all_chars_set)}
总对话数：{total_dialogues}

角色台词排行：
"""
            for sp, cnt in sorted(char_dialogues.items(), key=lambda x: -x[1]):
                report += f"  {sp}: {cnt} 句\n"
            st.download_button("📊 下载统计报告", report, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

        if st.button("🔄 重新开始"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

else:
    st.markdown("""
    <div class="info-box">
        📌 <strong>开始使用</strong><br>
        1. 选择运行模式（演示模式无需 API Key）<br>
        2. 上传 TXT 小说文件<br>
        3. 点击「开始转换」
    </div>
    """, unsafe_allow_html=True)
    st.markdown("### 📖 小说格式示例")
    st.code("""
第一章 觉醒

林晨睁开眼，发现自己躺在一片陌生的森林里。
"这是哪里？"他喃喃自语。

第二章 系统

"叮！系统激活成功！"一个声音在脑海中响起。
林晨震惊地站起来："系统？"

第三章 任务

"发布新手任务：采集10个草药"
林晨无奈地叹了口气："好吧，只能接受了。"
    """, language="text")

st.markdown('<div class="footer">🎬 AI 小说转剧本工具 | 演示模式 + 正式模式 | 支持多章节处理</div>',
            unsafe_allow_html=True)