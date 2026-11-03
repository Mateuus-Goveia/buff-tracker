class BuffItem:
    def __init__(self, buff_id, name, duration, icon_file, sound_file, input_key="none", modifier="none", is_consumable=False, raw_skill_name=None, keyboard_key="none"):
        self.id = buff_id
        self.name = name
        self.duration = int(duration)
        self.icon_file = icon_file
        self.sound_file = sound_file
        self.input_key = input_key
        self.modifier = modifier
        self.is_consumable = is_consumable
        self.raw_skill_name = raw_skill_name
        self.keyboard_key = keyboard_key
        self.remaining = 0
        self.is_active = False
        self.sound_played_warning = False

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "duration": self.duration,
            "icon_file": self.icon_file,
            "sound_file": self.sound_file,
            "input_key": self.input_key,
            "modifier": self.modifier,
            "is_consumable": self.is_consumable,
            "raw_skill_name": self.raw_skill_name,
            "keyboard_key": self.keyboard_key,
        }
