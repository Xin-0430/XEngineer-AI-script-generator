# script_generator.py

import yaml
import re
import json

from templates import get_template
from config import USE_AI

# ---------------- AI模块 ----------------

if USE_AI:
    try:
        from ai.deepseek_client import chat
        from ai.prompt_builder import (
            build_character_prompt
        )
    except Exception:
        USE_AI = False


# ==================================================
# 标题生成
# ==================================================

def generate_title(chapter):

    content = chapter.get("content", [])

    for line in content:

        line = line.strip()

        if line:
            return line[:20]

    return "无标题"


# ==================================================
# 规则版角色提取
# ==================================================

def extract_characters(content_lines):

    names = set()

    blacklist = {
        "第一章",
        "第二章",
        "第三章",
        "系统",
        "声音",
        "脑海",
        "任务",
        "异世界",
        "小说",
        "世界"
    }

    pattern = r'[\u4e00-\u9fa5]{2,3}'

    for line in content_lines:

        matches = re.findall(pattern, line)

        for item in matches:

            if item not in blacklist:
                names.add(item)

    return list(names)


# ==================================================
# AI版角色提取
# ==================================================

def extract_characters_ai(content_lines):

    content = "\n".join(content_lines)

    prompt = build_character_prompt(content)

    try:

        result = chat(prompt)

        names = json.loads(result)

        return names

    except Exception:

        return extract_characters(content_lines)


# ==================================================
# 台词提取
# ==================================================

def extract_dialogues(content_lines, characters):
    """增强版台词提取 - 支持多种格式"""
    dialogues = []
    seen = set()

    full_text = "\n".join(content_lines)

    # 匹配模式1："角色名：台词"
    pattern1 = r'([\u4e00-\u9fa5]{2,4})[:：]([^:：\n]+)'
    matches1 = re.findall(pattern1, full_text)
    for speaker, text in matches1:
        text = text.strip()
        if text and len(text) > 0 and text not in ["", "。", "？", "！"]:
            key = f"{speaker}:{text}"
            if key not in seen:
                seen.add(key)
                dialogues.append({"speaker": speaker, "text": text})

    # 匹配模式2："说：台词" 或 "道：台词"（尝试从上下文找角色名）
    pattern2 = r'(?:说|道|问|答)[：:]\s*["“]?([^"“\n]+)["”]?'
    matches2 = re.findall(pattern2, full_text)
    for text in matches2:
        text = text.strip()
        if text and len(text) > 0 and text not in ["", "。", "？", "！"]:
            # 尝试找角色名
            speaker = "未知"
            for char in characters:
                if char in full_text:
                    speaker = char
                    break
            key = f"{speaker}:{text}"
            if key not in seen:
                seen.add(key)
                dialogues.append({"speaker": speaker, "text": text})

    return dialogues

# ==================================================
# 场景识别
# ==================================================

def detect_location(content_lines):

    locations = [
        "教室",
        "森林",
        "医院",
        "天台",
        "地铁",
        "咖啡馆",
        "办公室",
        "宿舍",
        "操场",
        "实验室"
    ]

    text = "".join(content_lines)

    for location in locations:

        if location in text:
            return location

    return "未知地点"


# ==================================================
# 情绪分析
# ==================================================

def detect_emotion(content_lines):

    emotion_map = {
        "震惊": ["震惊", "惊讶"],
        "愤怒": ["愤怒", "暴怒"],
        "悲伤": ["悲伤", "哭泣"],
        "开心": ["开心", "大笑"],
        "紧张": ["紧张", "忐忑"],
        "恐惧": ["恐惧", "害怕"]
    }

    text = "".join(content_lines)

    for emotion, keywords in emotion_map.items():

        for keyword in keywords:

            if keyword in text:
                return emotion

    return "平静"


# ==================================================
# 镜头推荐
# ==================================================

def recommend_camera(content_lines):

    text = "".join(content_lines)

    camera = []

    if "睁开眼" in text:
        camera.append("特写")

    if "发现" in text:
        camera.append("推镜")

    if "奔跑" in text:
        camera.append("跟拍")

    if "战斗" in text:
        camera.append("全景")

    if "高空" in text:
        camera.append("远景")

    if not camera:
        camera.append("中景")

    return camera


# ==================================================
# AI镜头推荐
# ==================================================

def recommend_camera_ai(content_lines):

    if not USE_AI:
        return recommend_camera(content_lines)

    try:

        content = "\n".join(content_lines)

        prompt = f"""
你是影视导演。

根据下面内容推荐镜头。

只返回JSON数组。

例如：

["特写","推镜"]

内容：

{content}
"""

        result = chat(prompt)

        return json.loads(result)

    except Exception:

        return recommend_camera(content_lines)


# ==================================================
# 核心转换
# ==================================================

def chapter_to_script(
    chapter,
    template_type="网剧"
):

    content = chapter.get(
        "content",
        []
    )

    title = generate_title(
        chapter
    )

    if USE_AI:

        characters = extract_characters_ai(
            content
        )

        camera = recommend_camera_ai(
            content
        )

    else:

        characters = extract_characters(
            content
        )

        camera = recommend_camera(
            content
        )

    dialogues = extract_dialogues(
        content,
        characters
    )

    emotion = detect_emotion(
        content
    )

    location = detect_location(
        content
    )

    template_fields = get_template(
        template_type
    )

    script = {
        "chapter": chapter.get(
            "chapter",
            ""
        ),

        "title": title,

        "scene_type": template_type,

        "location": location,

        "time": "未知时间",

        "characters": characters,

        "dialogues": dialogues,

        "emotion": emotion,

        "camera": camera,

        "content": content
    }

    script.update(
        template_fields
    )

    return script


# ==================================================
# YAML保存
# ==================================================

def save_yaml(
    scripts,
    filename="output.yaml"
):

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:

        yaml.dump(
            scripts,
            f,
            allow_unicode=True,
            sort_keys=False
        )