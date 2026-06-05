def get_template(template_type):

    templates = {

        "网剧": {
            "scene_type": "网剧"
        },

        "动漫": {
            "scene_type": "动漫",
            "bgm": ["神秘"]
        },

        "电影": {
            "scene_type": "电影"
        },

        "有声书": {
            "scene_type": "有声书"
        }
    }

    return templates.get(
        template_type,
        templates["网剧"]
    )