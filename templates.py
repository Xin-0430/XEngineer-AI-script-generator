def get_template(template_type):
    templates = {
        "网剧": {
            "scene_type": "网剧"
        },

        "动漫": {
            "scene_type": "动漫",
            "camera": ["特写"],
            "bgm": ["神秘"]
        },

        "有声书": {
            "scene_type": "有声书",
            "narrator": ""
        }
    }

    return templates.get(
        template_type,
        templates["网剧"]
    )