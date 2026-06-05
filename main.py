from utils.parser import split_chapters
from script_generator import chapter_to_script, save_yaml

with open("data/example.txt", "r", encoding="utf-8") as f:
    text = f.read()

chapters = split_chapters(text)

# 示例：给每章指定默认地点、时间、角色
scripts = []
for ch in chapters:
    script = chapter_to_script(
        ch,
        location="咖啡厅",
        time_val="夜晚",
        characters=["李明", "张晓"]
    )
    scripts.append(script)

save_yaml(scripts)
print("增强剧本已生成：output.yaml")