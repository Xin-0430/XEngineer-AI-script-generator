# script_generator.py
import yaml
from templates import get_template

def generate_title(chapter):
    content = chapter.get("content", [])
    for line in content:
        line = line.strip()
        if line:
            return line[:20]
    return "无标题"

def extract_characters(content_lines):
    """
    简单角色提取
    """
    names = []
    keywords = ["林夜", "系统", "张三", "李四"]
    for line in content_lines:
        for name in keywords:
            if name in line and name not in names:
                names.append(name)
    return names

def chapter_to_script(chapter, template_type="网剧", location="未知地点", time_val="未知时间", characters=None):
    """
    将章节转换为完整剧本结构
    """
    content = chapter.get("content", [])
    title = generate_title(chapter)
    chapter["title"] = title

    if characters is None:
        characters = []

    template_fields = get_template(template_type)

    script = {
        "chapter": chapter.get("chapter", ""),
        "title": chapter["title"],
        "location": location,
        "time": time_val,
        "characters": characters,
        "content": content
    }

    # 合并模板特定字段
    script.update(template_fields)

    return script

def save_yaml(scripts, filename="output.yaml"):
    with open(filename, "w", encoding="utf-8") as f:
        yaml.dump(scripts, f, allow_unicode=True)