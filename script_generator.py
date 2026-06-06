# script_generator.py
import yaml
import re
import json
from templates import get_template
from config import USE_AI, DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, MODEL_NAME


# ----------------- AI 角色提取 -----------------
def extract_characters_ai(content_lines):
    """使用 DeepSeek API 提取角色名"""
    try:
        from openai import OpenAI
    except ImportError:
        return extract_characters_rule(content_lines)

    content = "\n".join(content_lines)
    # 限制长度加快速度
    if len(content) > 800:
        content = content[:800]

    prompt = f"""从以下小说片段中提取所有人名（角色名），只返回JSON数组，不要有其他内容。

片段：
{content}

示例输出：["李明", "张晓", "王老师"]

注意：只输出JSON数组。"""

    try:
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=200
        )
        result = response.choices[0].message.content.strip()

        # 清理 markdown 标记
        if result.startswith("```json"):
            result = result[7:]
        if result.startswith("```"):
            result = result[3:]
        if result.endswith("```"):
            result = result[:-3]

        names = json.loads(result)
        return names if isinstance(names, list) else []
    except Exception as e:
        print(f"AI角色提取失败: {e}")
        return extract_characters_rule(content_lines)


# ----------------- 规则版角色提取（降级用）-----------------
def extract_characters_rule(content_lines):
    """规则版角色提取，匹配2~3个汉字的名字"""
    names = set()
    pattern = r'[\u4e00-\u9fa5]{2,3}'
    for line in content_lines:
        matches = re.findall(pattern, line)
        for name in matches:
            names.add(name)
    # 过滤常见非人名词
    blacklist = {"但是", "所以", "因为", "如果", "然后", "于是", "这个", "那个", "没有", "不是", "可以", "应该", "我们",
                 "你们", "他们", "这里", "那里", "怎么", "什么", "为什么"}
    result = [n for n in names if n not in blacklist]
    return result[:10]


# ----------------- 标题生成 -----------------
def generate_title(chapter):
    content = chapter.get("content", [])
    for line in content:
        line = line.strip()
        if line:
            return line[:20]
    return "无标题"


# ----------------- 对话提取（增强版，支持多种格式）-----------------
def extract_dialogues(content_lines):
    """增强版台词提取 - 支持多种格式，自动去重"""
    dialogues = []
    full_text = "\n".join(content_lines)

    # 去重用
    seen_texts = set()

    # 方法1：匹配 "角色名：台词" 或 "角色名说：台词"
    pattern1 = r'([\u4e00-\u9fa5]{2,4})(?:说|道|回|问|答|喊|叫)?[：:]\s*["“]?([^"“\n]+)["”]?'
    matches1 = re.findall(pattern1, full_text)
    for speaker, text in matches1:
        text = text.strip()
        if text and len(text) > 0 and text not in ["", "。", "？", "！", "，"]:
            if text not in seen_texts:
                seen_texts.add(text)
                dialogues.append({"speaker": speaker, "text": text})

    # 方法2：匹配纯引号内的内容
    pattern2 = r'["“]([^"“”]+)["”]'
    matches2 = re.findall(pattern2, full_text)
    for text in matches2:
        text = text.strip()
        if not text or text in seen_texts:
            continue
        seen_texts.add(text)
        # 尝试找说话人
        speaker = "未知"
        for line in content_lines:
            if text in line:
                before = line[:line.find(text)]
                name_match = re.search(r'([\u4e00-\u9fa5]{2,4})(?:说|道|回|问)?[：:]?$', before)
                if name_match:
                    speaker = name_match.group(1)
                    break
        dialogues.append({"speaker": speaker, "text": text})

    return dialogues


# ----------------- 情绪分析 -----------------
def analyze_emotion(content_lines):
    """简单情绪识别 - 返回字符串"""
    emotions = ["愤怒", "悲伤", "开心", "紧张", "恐惧", "震惊"]
    for line in content_lines:
        for emo in emotions:
            if emo in line:
                return emo
    return "平静"


# ----------------- 场景识别 -----------------
def detect_scene(content_lines):
    """简单场景识别"""
    locations = ["教室", "森林", "医院", "天台", "地铁", "咖啡馆", "街道", "家中", "办公室", "公园"]
    for line in content_lines:
        for loc in locations:
            if loc in line:
                return loc
    return "未知地点"


# ----------------- 镜头推荐 -----------------
def recommend_camera(content_lines):
    """根据关键词推荐镜头"""
    keywords = {
        "特写": ["盯", "紧张", "惊讶", "恐惧", "看", "注视"],
        "中景": ["走", "跑", "谈话", "站", "坐"],
        "推镜": ["追", "移动", "冲", "追逐", "靠近"],
        "全景": ["战斗", "打", "厮杀", "战场"],
        "跟拍": ["奔跑", "跟随", "追逐"]
    }
    shots = set()
    for line in content_lines:
        for shot, kws in keywords.items():
            for kw in kws:
                if kw in line:
                    shots.add(shot)
    if not shots:
        shots.add("中景")
    return list(shots)


# ----------------- 章节转换 -----------------
def chapter_to_script(chapter, template_type="网剧"):
    """
    将章节转换为完整剧本结构
    """
    content = chapter.get("content", [])
    title = generate_title(chapter)
    chapter["title"] = title

    # ========== 角色提取：根据 USE_AI 决定用 AI 还是规则 ==========
    if USE_AI:
        characters = extract_characters_ai(content)
    else:
        characters = extract_characters_rule(content)

    # ========== 其他全部用规则（台词、场景、镜头、情绪）==========
    dialogues = extract_dialogues(content)
    location = detect_scene(content)
    camera = recommend_camera(content)
    emotion = analyze_emotion(content)

    # 模板字段
    template_fields = get_template(template_type)

    script = {
        "chapter": chapter.get("chapter", ""),
        "title": title,
        "location": location,
        "characters": characters,
        "content": content,
        "dialogues": dialogues,
        "emotion": emotion,
    }

    if "camera" in template_fields:
        script["camera"] = camera + template_fields.get("camera", [])
    else:
        script["camera"] = camera
    if "bgm" in template_fields:
        script["bgm"] = template_fields.get("bgm", [])
    if "scene_type" in template_fields:
        script["scene_type"] = template_fields.get("scene_type")
    if "narrator" in template_fields:
        script["narrator"] = "，".join(content)

    return script


# ----------------- YAML 保存 -----------------
def save_yaml(scripts, filename="output.yaml"):
    with open(filename, "w", encoding="utf-8") as f:
        yaml.dump(scripts, f, allow_unicode=True)