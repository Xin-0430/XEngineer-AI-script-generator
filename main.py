from utils.parser import split_chapters
from script_generator import chapter_to_script, save_yaml

# 生成剧本函数，可在 Streamlit 或其他地方调用
def generate_scripts_from_file(text, template_type="动漫"):
    chapters = split_chapters(text)

    scripts = []
    for chapter in chapters:
        script = chapter_to_script(chapter, template_type)
        scripts.append(script)

    return scripts

# 如果直接运行 main.py 也能生成 YAML
if __name__ == "__main__":
    with open("data/example.txt", "r", encoding="utf-8") as f:
        text = f.read()

    scripts = generate_scripts_from_file(text, template_type="动漫")
    save_yaml(scripts)
    print("剧本已生成：output.yaml")