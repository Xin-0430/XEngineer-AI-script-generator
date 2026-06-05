# script_generator.py
import yaml

def chapter_to_script(chapter):
    """
    可以在这里做更多处理
    目前直接返回章节内容字典
    """
    return chapter

def save_yaml(scripts, filename="output.yaml"):
    """
    保存生成的剧本为 YAML 文件
    """
    with open(filename, "w", encoding="utf-8") as f:
        yaml.dump(scripts, f, allow_unicode=True)