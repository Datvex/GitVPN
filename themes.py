from collections import OrderedDict

THEMES = OrderedDict([
    ("Claude", {"p": (205, 105, 75), "s": (236, 216, 196)}),
    ("Cyberpunk", {"p": (0, 255, 255), "s": (175, 0, 255)}),
    ("Ocean", {"p": (0, 255, 255), "s": (0, 0, 255)}),
    ("Sunset", {"p": (255, 255, 0), "s": (255, 0, 0)}),
    ("Matrix", {"p": (0, 255, 0), "s": (0, 128, 0)}),
    ("Gold", {"p": (255, 215, 0), "s": (255, 69, 0)})
])

def get_theme_list():
    return list(THEMES.keys())
