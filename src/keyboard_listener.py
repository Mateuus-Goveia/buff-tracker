from pynput import keyboard


SPECIAL_KEYS = {
    "alt": "alt", "alt_l": "alt", "alt_r": "alt", "alt_gr": "alt",
    "ctrl": "ctrl", "ctrl_l": "ctrl", "ctrl_r": "ctrl",
    "shift": "shift", "shift_l": "shift", "shift_r": "shift",
    "up": "arrow_up", "down": "arrow_down", "left": "arrow_left", "right": "arrow_right",
    "delete": "del", "home": "hm", "insert": "ins", "page_up": "pup", "page_down": "pdn",
    "space": "space", "end": "end",
}
for _index in range(1, 13):
    SPECIAL_KEYS[f"f{_index}"] = f"f{_index}"

CHAR_KEYS = {
    "\\": "backslash", "|": "backslash",
    "`": "backtick", "~": "backtick",
    "[": "bracket_left", "{": "bracket_left",
    "]": "bracket_right", "}": "bracket_right",
    ",": "comma", "<": "comma",
    ".": "period", ">": "period",
    "'": "quote", '"': "quote",
    ";": "semicolon", ":": "semicolon",
    "/": "slash", "?": "slash",
    "-": "minus", "_": "minus",
    "=": "equals", "+": "equals",
}


def key_id(key):
    """Convert a pynput key event to the ID used by assets/keyboard."""
    name = getattr(key, "name", None)
    if name:
        mapped = SPECIAL_KEYS.get(name.lower())
        if mapped:
            return mapped

    char = getattr(key, "char", None)
    if not char:
        return None
    if char in CHAR_KEYS:
        return CHAR_KEYS[char]
    char = char.lower()
    return char if len(char) == 1 and char.isalnum() else None


def start_keyboard_listener(callback):
    """Start a global keyboard listener and call back once per key press."""
    pressed = set()

    def on_press(key):
        key_name = key_id(key)
        if key_name and key_name not in pressed:
            pressed.add(key_name)
            callback(key_name)

    def on_release(key):
        key_name = key_id(key)
        if key_name:
            pressed.discard(key_name)

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.daemon = True
    listener.start()
    return listener
