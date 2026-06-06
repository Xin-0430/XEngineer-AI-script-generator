from utils.parser import split_chapters
from script_generator import chapter_to_script
# 在 main.py 或 config.py 中

def generate_scripts_from_file(
    text,
    template_type
):

    chapters = split_chapters(text)

    scripts = []

    for chapter in chapters:

        script = chapter_to_script(
            chapter,
            template_type
        )

        scripts.append(script)

    return scripts