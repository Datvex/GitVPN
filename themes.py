from collections import OrderedDict

THEMES = OrderedDict([
    ("Claude", {"p": (217, 119, 87), "s": (217, 119, 87)}),
    ("Cyberpunk", {"p": (0, 255, 255), "s": (175, 0, 255)}),
    ("Ocean", {"p": (0, 255, 255), "s": (0, 0, 255)}),
    ("Sunset", {"p": (255, 100, 0), "s": (128, 0, 128)}),
    ("Matrix", {"p": (0, 255, 0), "s": (0, 50, 0)}),
    ("Gold", {"p": (255, 215, 0), "s": (80, 50, 0)})
])

def get_theme_list():
    return list(THEMES.keys())