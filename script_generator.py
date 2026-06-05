# script_generator.py
import yaml

def generate_title(chapter):
    content = chapter.get("content", [])
    for line in content:
        line = line.strip()
        if line:
            return line[:20]
    return "无标题"

def chapter_to_script(chapter, location="未知地点", time_val="未知时间", characters=None):
    """
    将章节转换为完整剧本结构
    """
    content = chapter.get("content", [])
    title = generate_title(chapter)
    chapter["title"] = title

    if characters is None:
        characters = []

    return {
        "chapter": chapter.get("chapter", ""),
        "title": chapter["title"],
        "location": location,
        "time": time_val,
        "characters": characters,
        "content": content
    }

def save_yaml(scripts, filename="output.yaml"):
    with open(filename, "w", encoding="utf-8") as f:
        yaml.dump(scripts, f, allow_unicode=True)