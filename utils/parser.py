# utils/parser.py
import re

def split_chapters(text):
    """
    按章节拆分小说文本
    返回章节列表，每个章节是字典：
    {
        "chapter": "第1章",
        "title": "系统觉醒",
        "content": [...]
    }
    """
    chapters = []

    # 匹配 "第1章 系统觉醒" 或 "第一章 系统觉醒" 的章节标题
    pattern = re.compile(r'^(第[一二三四五六七八九十0-9]+章)\s*(.*)$', re.MULTILINE)

    matches = list(pattern.finditer(text))

    for i, match in enumerate(matches):
        chapter_num = match.group(1).strip()
        chapter_title = match.group(2).strip()
        start = match.end()

        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(text)

        content_text = text[start:end].strip()
        # 按行拆分，并过滤掉空行
        content_lines = [line.strip() for line in content_text.split("\n") if line.strip()]

        chapters.append({
            "chapter": chapter_num,
            "title": chapter_title,
            "content": content_lines
        })

    return chapters