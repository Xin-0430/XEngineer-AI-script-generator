import yaml
import re

from templates import get_template


# =====================
# 标题生成
# =====================

def generate_title(chapter):

    content = chapter.get("content", [])

    for line in content:
        line = line.strip()

        if line:
            return line[:20]

    return "无标题"


# =====================
# 角色识别
# =====================

def extract_characters(content_lines):

    names = []

    keywords = [
        "林夜",
        "系统",
        "张三",
        "李四"
    ]

    for line in content_lines:

        for name in keywords:

            if name in line and name not in names:
                names.append(name)

    return names


# =====================
# 台词提取
# =====================

def extract_dialogues(content_lines):

    dialogues = []

    speaker = None

    for line in content_lines:

        line = line.strip()

        if line.endswith("说道："):

            speaker = line.replace("说道：", "")

        elif line.endswith("回答："):

            speaker = line.replace("回答：", "")

        elif line.startswith("“") and speaker:

            dialogues.append({
                "speaker": speaker,
                "text": line.strip("“”")
            })

            speaker = None

    return dialogues


# =====================
# 场景识别
# =====================

def detect_location(content_lines):

    locations = [
        "教室",
        "森林",
        "医院",
        "天台",
        "地铁",
        "咖啡馆",
        "宫殿",
        "学校"
    ]

    text = "".join(content_lines)

    for loc in locations:

        if loc in text:
            return loc

    return "未知地点"


# =====================
# 情绪分析
# =====================

def detect_emotion(content_lines):

    text = "".join(content_lines)

    emotions = {

        "愤怒": [
            "愤怒",
            "生气",
            "暴怒"
        ],

        "开心": [
            "开心",
            "高兴",
            "兴奋"
        ],

        "悲伤": [
            "伤心",
            "难过",
            "流泪"
        ],

        "紧张": [
            "紧张",
            "害怕"
        ],

        "震惊": [
            "震惊",
            "惊讶"
        ]
    }

    for emotion, words in emotions.items():

        for word in words:

            if word in text:
                return emotion

    return "平静"


# =====================
# 镜头推荐
# =====================

def recommend_camera(content_lines):
    """
    智能镜头推荐系统
    """

    text = "".join(content_lines)

    cameras = []

    # ==================
    # 情绪镜头
    # ==================

    if any(word in text for word in [
        "愤怒",
        "暴怒",
        "生气",
        "震惊",
        "惊讶",
        "害怕",
        "紧张",
        "恐惧"
    ]):
        cameras.append("特写")

    # ==================
    # 发现类镜头
    # ==================

    if any(word in text for word in [
        "发现",
        "看到",
        "看见",
        "出现",
        "映入眼帘"
    ]):
        cameras.append("推镜")

    # ==================
    # 动作镜头
    # ==================

    if any(word in text for word in [
        "奔跑",
        "狂奔",
        "逃跑",
        "追赶",
        "冲出"
    ]):
        cameras.append("跟拍")

    # ==================
    # 战斗镜头
    # ==================

    if any(word in text for word in [
        "战斗",
        "交手",
        "厮杀",
        "挥剑",
        "攻击",
        "对决"
    ]):
        cameras.append("快速切换")

    # ==================
    # 回忆镜头
    # ==================

    if any(word in text for word in [
        "回忆",
        "往事",
        "曾经",
        "小时候"
    ]):
        cameras.append("慢推")

    # ==================
    # 大场景镜头
    # ==================

    if any(word in text for word in [
        "森林",
        "城市",
        "广场",
        "学校",
        "宫殿",
        "高楼",
        "山脉",
        "大海",
        "天空"
    ]):
        cameras.append("远景")

    # ==================
    # 对话镜头
    # ==================

    dialogue_count = 0

    for line in content_lines:

        if (
            "说道" in line
            or "回答" in line
            or "问道" in line
            or "喊道" in line
        ):
            dialogue_count += 1

    if dialogue_count >= 2:
        cameras.append("双人对话镜头")

    # ==================
    # 默认镜头
    # ==================

    if not cameras:
        cameras.append("中景")

    # 去重
    cameras = list(dict.fromkeys(cameras))

    return cameras


# =====================
# 主转换函数
# =====================

def chapter_to_script(

        chapter,
        template_type="动漫",
        location=None,
        time_val="未知时间"
):

    content = chapter.get("content", [])

    title = generate_title(chapter)

    characters = extract_characters(content)

    dialogues = extract_dialogues(content)

    if location is None:
        location = detect_location(content)

    emotion = detect_emotion(content)

    camera = recommend_camera(content)

    template_fields = get_template(
        template_type
    )

    script = {

        "chapter":
            chapter.get("chapter", ""),

        "title":
            title,

        "location":
            location,

        "time":
            time_val,

        "characters":
            characters,

        "emotion":
            emotion,

        "camera":
            camera,

        "dialogues":
            dialogues,

        "content":
            content
    }

    script.update(template_fields)

    return script


# =====================
# 保存YAML
# =====================

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