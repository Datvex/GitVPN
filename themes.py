THEMES = {
    "Cyberpunk": {
        "primary":   "#00ffff",
        "secondary": "#af00ff",
        "success":   "#00ff00",
        "error":     "#ff0000",
        "accent":    "#ffff00"
    },
    "Ocean": {
        "primary":   "#00ffff",
        "secondary": "#0000ff",
        "success":   "#00ff00",
        "error":     "#ff0000",
        "accent":    "#ffffff"
    },
    "Sunset": {
        "primary":   "#ffff00",
        "secondary": "#ff0000",
        "success":   "#00ff00",
        "error":     "#ff4500",
        "accent":    "#ffa500"
    },
    "Matrix": {
        "primary":   "#00ff00",
        "secondary": "#008000",
        "success":   "#ffffff",
        "error":     "#ff0000",
        "accent":    "#00ff00"
    }
}

def get_theme(name):
    return THEMES.get(name, THEMES["Cyberpunk"])