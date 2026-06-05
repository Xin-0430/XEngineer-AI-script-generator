# script_generator.py
import yaml
from templates import get_template

def generate_title(chapter):
    """
    自动生成章节标题
    """
    content = chapter.get("content", [])
    for line in content:
        line = line.strip()
        if line:
            return line[:20]
    return "无标题"

# 稳定版本角色库（PR4 推荐）
CHARACTER_LIBRARY = [
    "林夜",
    "系统",
    "张三",
    "李四",
    "王强"
]

def extract_characters(content_lines):
    """
    智能角色识别
    从内容中匹配 CHARACTER_LIBRARY
    """
    names = []
    for line in content_lines:
        for character in CHARACTER_LIBRARY:
            if character in line and character not in names:
                names.append(character)
    return names

def chapter_to_script(chapter, template_type="网剧", location="未知地点", time_val="未知时间", characters=None):
    """
    将章节转换为完整剧本结构
    """
    content = chapter.get("content", [])
    title = generate_title(chapter)
    chapter["title"] = title

    # 如果没有传 characters 参数，自动识别
    if characters is None:
        characters = extract_characters(content)

    template_fields = get_template(template_type)
    dialogues = extract_dialogues(content)
    script = {
        "chapter": chapter.get("chapter", ""),
        "title": chapter["title"],
        "location": location,
        "time": time_val,
        "characters": characters,
        "dialogues": dialogues,
        "content": content
    }

    # 合并模板字段
    script.update(template_fields)
    return script
def extract_dialogues(content_lines):
    """
    简单台词提取器
    """

    dialogues = []

    current_speaker = None

    for line in content_lines:

        line = line.strip()

        if "说道" in line:
            current_speaker = line.replace("说道：", "")

        elif "回答" in line:
            current_speaker = line.replace("回答：", "")

        elif "：“" in line:
            parts = line.split("：“")

            if len(parts) == 2:

                speaker = parts[0]

                text = parts[1].replace("”", "")

                dialogues.append({
                    "speaker": speaker,
                    "text": text
                })

        elif line.startswith("“") and current_speaker:

            dialogues.append({
                "speaker": current_speaker,
                "text": line.replace("“", "").replace("”", "")
            })

    return dialogues
def save_yaml(scripts, filename="output.yaml"):
    """
    将生成的剧本列表保存为 YAML 文件
    """
    with open(filename, "w", encoding="utf-8") as f:
        yaml.dump(scripts, f, allow_unicode=True)