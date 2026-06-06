from openai import OpenAI

from config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    MODEL_NAME
)

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL
)


def chat(prompt, max_tokens=500):
    """
    调用 DeepSeek API
    - max_tokens: 限制输出长度，加快速度
    """
    # 限制输入长度，加快 API 响应
    if len(prompt) > 2000:
        prompt = prompt[:2000] + "\n...(内容已截断)"

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=max_tokens  # 限制输出长度
    )

    return response.choices[0].message.content