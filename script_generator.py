# script_generator.py
import yaml
import re
import json
from templates import get_template
from config import USE_AI, DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, MODEL_NAME

# ----------------- 标题生成 -----------------
def generate_title(chapter):
    content = chapter.get("content", [])
    for line in content:
        line = line.strip()
        if line:
            return line[:20]
    return "无标题"

# ----------------- 角色提取 -----------------
def extract_characters(content_lines):
    """
    智能角色提取，匹配2~3个汉字的名字
    如果 USE_AI=True，可接入 DeepSeek API
    """
    names = set()
    pattern = r'[\u4e00-\u9fa5]{2,3}'
    for line in content_lines:
        matches = re.findall(pattern, line)
        for name in matches:
            names.add(name)
    return list(names)

# ----------------- 对话提取 -----------------
def extract_dialogues(content_lines):
    """
    提取台词
    输出列表 [{'speaker': '角色名', 'text': '台词'}]
    """
    dialogues = []
    speaker = None
    for line in content_lines:
        line = line.strip()
        if not line:
            continue
        # 检测角色台词格式
        match = re.match(r'([\u4e00-\u9fa5]{2,3})说道[:：]', line)
        if match:
            speaker = match.group(1)
        else:
            if line.startswith("“") and line.endswith("”") and speaker:
                dialogues.append({
                    "speaker": speaker,
                    "text": line.strip("“”")
                })
                speaker = None
    return dialogues

# ----------------- 情绪分析 -----------------
def analyze_emotion(content_lines):
    """
    简单情绪识别
    """
    emotions = ["愤怒","悲伤","开心","紧张","恐惧","震惊"]
    detected = set()
    for line in content_lines:
        for emo in emotions:
            if emo in line:
                detected.add(emo)
    return list(detected)

# ----------------- 场景识别 -----------------
def detect_scene(content_lines):
    """
    简单场景识别
    """
    locations = ["教室","森林","医院","天台","地铁","咖啡馆"]
    for line in content_lines:
        for loc in locations:
            if loc in line:
                return loc
    return "未知地点"

# ----------------- 镜头推荐 -----------------
def recommend_camera(content_lines):
    """
    根据关键词推荐镜头
    """
    keywords = {
        "特写":["盯","紧张","惊讶","恐惧"],
        "中景":["走","跑","谈话"],
        "推镜":["追","移动","冲","追逐"]
    }
    shots = set()
    for line in content_lines:
        for shot, kws in keywords.items():
            for kw in kws:
                if kw in line:
                    shots.add(shot)
    return list(shots)

# ----------------- 章节转换 -----------------
def chapter_to_script(chapter, template_type="网剧"):
    """
    将章节转换为完整剧本结构
    """
    content = chapter.get("content", [])
    title = generate_title(chapter)
    chapter["title"] = title

    # 角色
    characters = extract_characters(content)

    # 对话
    dialogues = extract_dialogues(content)

    # 场景
    location = detect_scene(content)

    # 镜头
    camera = recommend_camera(content)

    # 情绪
    emotion = analyze_emotion(content)

    # 模板字段
    template_fields = get_template(template_type)

    script = {
        "chapter": chapter.get("chapter",""),
        "title": title,
        "location": location,
        "characters": characters,
        "content": content,
        "dialogues": dialogues,
        "emotion": emotion,
    }

    if "camera" in template_fields:
        script["camera"] = camera + template_fields.get("camera",[])
    if "bgm" in template_fields:
        script["bgm"] = template_fields.get("bgm",[])
    if "scene_type" in template_fields:
        script["scene_type"] = template_fields.get("scene_type")
    if "narrator" in template_fields:
        script["narrator"] = "，".join(content)

    return script

# ----------------- YAML 保存 -----------------
def save_yaml(scripts, filename="output.yaml"):
    with open(filename, "w", encoding="utf-8") as f:
        yaml.dump(scripts, f, allow_unicode=True)
