from utils.parser import split_chapters

from script_generator import (
    chapter_to_script,
    save_yaml
)

with open(
        "data/example.txt",
        "r",
        encoding="utf-8"
) as f:

    text = f.read()

chapters = split_chapters(text)

scripts = []

for chapter in chapters:

    script = chapter_to_script(
        chapter,
        template_type="动漫"
    )

    scripts.append(script)

save_yaml(scripts)

print("剧本已生成：output.yaml")