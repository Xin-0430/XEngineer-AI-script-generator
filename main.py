from utils.parser import split_chapters
from script_generator import chapter_to_script, save_yaml

# 读取小说文本
with open("data/example.txt", "r", encoding="utf-8") as f:
    text = f.read()

# 拆分章节
chapters = split_chapters(text)

# 生成剧本
scripts = []
for chapter in chapters:
    script = chapter_to_script(chapter)
    scripts.append(script)

# 保存 YAML
save_yaml(scripts)

print("剧本已生成：output.yaml")