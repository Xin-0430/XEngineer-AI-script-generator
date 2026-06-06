# ai/prompt_builder.py

def build_character_prompt(content):
    """构建角色提取的 prompt（精简版，加快速度）"""

    # 限制内容长度
    if len(content) > 1000:
        content = content[:1000]

    prompt = f"""从以下小说片段中提取所有人名（角色名），只返回JSON数组，不要有其他内容。

片段：
{content}

示例输出：["李明", "张晓", "王老师"]

注意：只输出JSON数组，不要有其他解释。"""

    return prompt


def build_camera_prompt(content):
    """构建镜头推荐的 prompt（精简版）"""

    if len(content) > 800:
        content = content[:800]

    prompt = f"""根据以下内容推荐镜头，只返回JSON数组。

内容：{content}

示例输出：["特写", "推镜", "中景"]"""

    return prompt