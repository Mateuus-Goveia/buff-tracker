import os
import re
import sys
import json
import uuid

import pygame
from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from src import i18n
from src.i18n import get_setting, set_setting, tr
from src.options import INPUT_IDS, NONE, input_label, normalize_id
from src.utils import (
    DATA_DIR, ICONS_DIR, DPAD_DIR, KEYBOARD_DIR, SOUNDS_DIR, USER_BUFFS_PATH,
    load_json_data, keyboard_asset_name, shortcut_asset_name,
)
from src.models import BuffItem
from src.joystick import start_joystick_listener
from src.keyboard_listener import start_keyboard_listener
from src.ui.main_window import KeyboardPickerDialog, MainWindow, load_pixmap
from src.ui.theme import build_stylesheet, load_pixel_font, theme_asset
from src.ui.widgets import BuffCard

LEGACY_SOUND_ALIASES = {"bell1": "alert_01", "bell2": "alert_02", "hey": "alert_03"}


def branch_label(job_key):
    """Convert '2nd job - fighter' to 'Fighter' (the second-job name only)."""
    name = re.sub(r"^\s*\d+\s*(st|nd|rd|th)\s+job\s*[-:]?\s*", "", job_key, flags=re.IGNORECASE).strip()
    return name[:1].upper() + name[1:]


def is_first_job(job_key):
    return job_key.strip().lower().startswith("1st")


class JoystickBridge(QObject):
    """Forward joystick events to the UI thread through a Qt signal."""
    triggered = Signal(str, str)


class KeyboardBridge(QObject):
    triggered = Signal(str)


class _JoystickProxy:
    """Proxy exposed to the joystick listener (running_joystick + trigger_buff_by_input)."""
    running_joystick = True

    def __init__(self, bridge):
        self.trigger_buff_by_input = bridge.triggered.emit


class AppBuffTracker:
    def __init__(self):
        try:
            pygame.mixer.init()
        except Exception:
            pass

        self.qapp = QApplication.instance() or QApplication(sys.argv)
        self.qapp.setStyleSheet(build_stylesheet(load_pixel_font()))
        self.qapp.setWindowIcon(QIcon(theme_asset("app_icon.png")))
        i18n.init()

        self.classes_data = load_json_data(os.path.join(DATA_DIR, "classes.json"))
        self.consumables_data = load_json_data(os.path.join(DATA_DIR, "consumables.json"))
        self.user_buffs = []
        self.cards = {}  # Buff ID -> BuffCard.
        self.input_mode = get_setting("input_mode", "joystick")
        if self.input_mode not in ("joystick", "keyboard"):
            self.input_mode = "joystick"
        self.selected_keyboard_key = None
        self.load_user_buffs()

        self.window = MainWindow(self)
        self.sync_consumable_checkboxes()

        class_names = list(self.classes_data.keys()) if self.classes_data else ["Warrior"]
        self.update_jobs(class_names[0])
        self.refresh_input_options()
        self.render_cards_ui()

        self.timer = QTimer(self.window)
        self.timer.timeout.connect(self.update_timers)
        self.timer.start(1000)

        self.bridge = JoystickBridge()
        self.bridge.triggered.connect(self.trigger_buff_by_input)
        self.keyboard_bridge = KeyboardBridge()
        self.keyboard_bridge.triggered.connect(self.trigger_buff_by_key)
        self.joystick_proxy = None
        self.joystick_thread = None
        self.keyboard_listener = None
        self.qapp.aboutToQuit.connect(self._stop_input_listeners)
        self._start_input_listener()

    def run(self):
        self.window.show()
        return self.qapp.exec()

    def _stop_input_listeners(self):
        if self.joystick_proxy is not None:
            self.joystick_proxy.running_joystick = False
            self.joystick_proxy = None
        if self.joystick_thread is not None:
            self.joystick_thread.join(timeout=0.5)
            self.joystick_thread = None
        if self.keyboard_listener is not None:
            self.keyboard_listener.stop()
            self.keyboard_listener.join(timeout=0.5)
            self.keyboard_listener = None

    def _start_input_listener(self):
        if self.input_mode == "joystick":
            self.joystick_proxy = _JoystickProxy(self.bridge)
            self.joystick_thread = start_joystick_listener(self.joystick_proxy)
        else:
            try:
                self.keyboard_listener = start_keyboard_listener(self.keyboard_bridge.triggered.emit)
            except Exception:
                self.window.set_error(tr("err.keyboard_listener"))

    def change_input_mode(self, mode):
        if mode not in ("joystick", "keyboard") or mode == self.input_mode:
            return
        self.input_mode = mode
        self.selected_keyboard_key = None
        set_setting("input_mode", mode)
        self.window.set_error("")
        self._stop_input_listeners()
        self._start_input_listener()
        self.window.refresh_setting_items()
        self.window.refresh_input_mode_controls()
        self.update_skills(self.window.combo_job.currentData())
        self.render_cards_ui()

    # ---------------------------------------------------------------- language
    def change_language(self, code):
        w = self.window
        skill, level = w.combo_skill.currentData(), w.combo_level.currentText()
        i18n.set_language(code)
        w.set_error("")
        w.retranslate()
        self.refresh_input_options()
        self.update_skills(w.combo_job.currentData())
        if skill is not None:
            w.select_data(w.combo_skill, skill)
            self.update_levels(skill)
            w.select_data(w.combo_level, level)
        self.render_cards_ui()

    # ------------------------------------------------------------------ data
    def load_user_buffs(self):
        if not os.path.exists(USER_BUFFS_PATH):
            return
        try:
            with open(USER_BUFFS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data:
                self.user_buffs.append(BuffItem(
                    item.get("id", str(uuid.uuid4())),
                    item.get("name", "Buff"),
                    item.get("duration", 60),
                    item.get("icon_file"),
                    item.get("sound_file", "bell1"),
                    normalize_id(item.get("input_key", NONE)),
                    normalize_id(item.get("modifier", NONE)),
                    item.get("is_consumable", False),
                    item.get("raw_skill_name"),
                    item.get("keyboard_key", NONE),
                ))
        except Exception:
            pass

    def save_user_buffs(self):
        data = [buff.to_dict() for buff in self.user_buffs]
        with open(USER_BUFFS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def sync_consumable_checkboxes(self):
        """Check saved consumables so saving again does not remove them."""
        saved = {b.name for b in self.user_buffs if b.is_consumable}
        for name, (chk, _details) in self.window.consumable_vars.items():
            chk.setChecked(name in saved)

    # ------------------------------------------------------------------ sounds
    def get_available_sounds(self):
        if os.path.exists(SOUNDS_DIR):
            sounds = [os.path.splitext(name)[0] for name in os.listdir(SOUNDS_DIR)
                      if name.lower().endswith((".mp3", ".wav", ".ogg"))]
            if sounds:
                return sorted(sounds, key=str.casefold)
        return ["bell1", "bell2", "hey"]

    def play_sound(self, sound_name):
        if not sound_name:
            return
        candidates = [sound_name]
        alias = LEGACY_SOUND_ALIASES.get(sound_name)
        if alias:
            candidates.append(alias)
        for candidate in candidates:
            for ext in (".mp3", ".wav", ".ogg"):
                path = os.path.join(SOUNDS_DIR, f"{candidate}{ext}")
                if os.path.exists(path):
                    try:
                        pygame.mixer.music.load(path)
                        pygame.mixer.music.play()
                        return
                    except Exception:
                        pass

    # --------------------------------------------------------------- shortcuts
    def get_used_shortcuts(self):
        return {(b.input_key, b.modifier) for b in self.user_buffs
                if not b.is_consumable and b.input_key != NONE}

    def get_used_keyboard_keys(self):
        return {b.keyboard_key for b in self.user_buffs
                if not b.is_consumable and b.keyboard_key != NONE}

    def refresh_input_options(self):
        used = self.get_used_shortcuts()
        w = self.window
        current_mod = w.combo_mod.currentData() or NONE
        ids = [NONE] + [i for i in INPUT_IDS if (i, current_mod) not in used]
        current = w.combo_input.currentData()
        w.set_combo_items(w.combo_input, [(input_label(i), i) for i in ids],
                          current if current in ids else NONE)
        self.update_previews()

    def trigger_buff_by_input(self, input_id, modifier_id):
        if self.input_mode != "joystick":
            return
        for buff in self.user_buffs:
            if not buff.is_consumable and buff.input_key == input_id and buff.modifier == modifier_id:
                self.start_buff(buff)

    def trigger_buff_by_key(self, key_id):
        if self.input_mode != "keyboard":
            return
        for buff in self.user_buffs:
            if not buff.is_consumable and buff.keyboard_key == key_id:
                self.start_buff(buff)

    # ----------------------------------------------------------------- cards
    def render_cards_ui(self):
        self.window.clear_cards()
        self.cards = {}

        if not self.user_buffs:
            self.window.show_empty_message(tr("empty.cards"))
            return

        for buff in self.user_buffs:
            icon = load_pixmap(os.path.join(ICONS_DIR, buff.icon_file), 44) if buff.icon_file else None

            shortcut = None
            if not buff.is_consumable:
                if self.input_mode == "keyboard":
                    asset = keyboard_asset_name(buff.keyboard_key)
                    asset_dir = KEYBOARD_DIR
                else:
                    asset = shortcut_asset_name(buff.input_key, buff.modifier)
                    asset_dir = DPAD_DIR
                if asset:
                    shortcut = load_pixmap(os.path.join(asset_dir, asset), 40)

            card = BuffCard(
                buff, icon, shortcut, self.start_buff, self.remove_buff,
                show_controller_badge=self.input_mode == "joystick",
            )
            self.cards[buff.id] = card
            self.window.add_card(card)

    def start_buff(self, buff):
        buff.remaining = buff.duration
        buff.is_active = True
        buff.sound_played_warning = False

    def remove_buff(self, buff):
        if buff in self.user_buffs:
            self.user_buffs.remove(buff)
            self.save_user_buffs()
            self.render_cards_ui()
            self.refresh_input_options()
            if buff.is_consumable:
                self.sync_consumable_checkboxes()
            else:
                self.update_skills(self.window.combo_job.currentData())

    def update_timers(self):
        for buff in self.user_buffs:
            if not buff.is_active:
                continue
            card = self.cards.get(buff.id)
            if buff.remaining > 0:
                buff.remaining -= 1
                if buff.remaining == 3 and not buff.sound_played_warning:
                    self.play_sound(buff.sound_file)
                    buff.sound_played_warning = True
                if card:
                    state = "warn" if buff.remaining <= 10 else "ok"
                    card.set_timer(tr("card.remaining", seconds=buff.remaining), state)
            else:
                buff.is_active = False
                if card:
                    card.set_timer(tr("card.expired"), "expired")

    # ------------------------------------------------------- configuration form
    def _branches(self, selected_class):
        """Return {display name: JSON key} for jobs after the first (e.g. 2nd job - Hunter -> Hunter)."""
        return {branch_label(key): key
                for key in self.classes_data.get(selected_class, {}) if not is_first_job(key)}

    def _class_skills(self, selected_class, branch_name):
        """Return skills from the first job and the selected second job."""
        jobs = self.classes_data.get(selected_class, {})
        skills = {}
        for key, data in jobs.items():
            if is_first_job(key):
                skills.update(data)
        branch_key = self._branches(selected_class).get(branch_name)
        if branch_key:
            for name, data in jobs[branch_key].items():
                skills.setdefault(name, data)
        return skills

    def update_jobs(self, selected_class):
        branches = list(self._branches(selected_class))
        items = branches or [(tr("combo.none"), None)]
        first = branches[0] if branches else None
        self.window.set_combo_items(self.window.combo_job, items, first)
        self.update_skills(first)

    def update_skills(self, selected_job):
        w = self.window
        skills = self._class_skills(w.combo_class.currentText(), selected_job)
        names = []
        for name in skills:
            existing = self._buff_for_skill(name)
            if existing is None or not self._has_binding_for_mode(existing):
                names.append(name)
        items = names or [(tr("combo.none_skill"), None)]
        first = names[0] if names else None
        w.set_combo_items(w.combo_skill, items, first)
        self.update_levels(first)

    def update_levels(self, selected_skill):
        w = self.window
        self.selected_keyboard_key = None
        if selected_skill is None:
            w.set_combo_items(w.combo_level, ["Lv. 1"], "Lv. 1")
            self.update_previews()
            return

        skill_data = self._class_skills(w.combo_class.currentText(), w.combo_job.currentData()).get(selected_skill, {})
        max_lv = skill_data.get("max_level", 20)
        levels = [f"Lv. {i}" for i in range(1, max_lv + 1)]
        w.set_combo_items(w.combo_level, levels, levels[-1])
        self.update_previews()

    def update_previews(self):
        """Update the preview for the selected shortcut."""
        w = self.window
        selected_skill = w.combo_skill.currentData()
        existing = self._buff_for_skill(selected_skill) if selected_skill else None
        if self.input_mode == "keyboard":
            key_id = self.selected_keyboard_key or (existing.keyboard_key if existing else NONE)
            w.refresh_keyboard_key_button(key_id)
            asset = keyboard_asset_name(key_id)
            asset_dir = KEYBOARD_DIR
        else:
            asset = shortcut_asset_name(w.combo_input.currentData() or NONE, w.combo_mod.currentData() or NONE)
            asset_dir = DPAD_DIR
        pix = load_pixmap(os.path.join(asset_dir, asset), 40) if asset else None
        if pix is not None:
            w.lbl_shortcut_preview.setPixmap(pix)
        else:
            w.lbl_shortcut_preview.clear()

    def _buff_for_skill(self, skill_name):
        return next((buff for buff in self.user_buffs
                     if not buff.is_consumable and buff.raw_skill_name == skill_name), None)

    def _has_binding_for_mode(self, buff):
        if self.input_mode == "keyboard":
            return buff.keyboard_key != NONE
        return buff.input_key != NONE

    def choose_keyboard_key(self):
        skill_name = self.window.combo_skill.currentData()
        if skill_name is None:
            return
        existing = self._buff_for_skill(skill_name)
        current_key = existing.keyboard_key if existing else None
        dialog = KeyboardPickerDialog(self.get_used_keyboard_keys(), current_key, self.window)
        if dialog.exec() == KeyboardPickerDialog.DialogCode.Accepted and dialog.selected_key:
            self.selected_keyboard_key = dialog.selected_key
            self.update_previews()

    def add_skill_to_preset(self):
        w = self.window
        selected_input = w.combo_input.currentData() or NONE
        selected_keyboard_key = self.selected_keyboard_key or NONE
        sel_skill = w.combo_skill.currentData()

        if sel_skill is None:
            w.set_error(tr("err.no_skills"))
            return
        if self.input_mode == "keyboard" and selected_keyboard_key == NONE:
            w.set_error(tr("err.no_shortcut"))
            return
        if self.input_mode == "joystick" and selected_input == NONE:
            w.set_error(tr("err.no_shortcut"))
            return

        w.set_error("")
        sel_class = w.combo_class.currentText()
        sel_job = w.combo_job.currentData()

        skill_data = self._class_skills(sel_class, sel_job).get(sel_skill, {})
        if not skill_data:
            return

        level_text = w.combo_level.currentText()
        lv_str = level_text.replace("Lv. ", "")
        durations = skill_data.get("durations", {})
        duration = durations.get(lv_str, durations.get("1", 60))

        existing = self._buff_for_skill(sel_skill)
        if existing is not None:
            if self._has_binding_for_mode(existing):
                w.set_error(tr("err.binding_exists"))
                return
            if self.input_mode == "keyboard":
                existing.keyboard_key = selected_keyboard_key
            else:
                existing.input_key = selected_input
                existing.modifier = w.combo_mod.currentData() or NONE
        else:
            self.user_buffs.append(BuffItem(
                str(uuid.uuid4()),
                f"{sel_skill} ({level_text})",
                duration,
                skill_data.get("icon_default"),
                w.combo_sound.currentText(),
                selected_input if self.input_mode == "joystick" else NONE,
                (w.combo_mod.currentData() or NONE) if self.input_mode == "joystick" else NONE,
                is_consumable=False,
                raw_skill_name=sel_skill,
                keyboard_key=selected_keyboard_key if self.input_mode == "keyboard" else NONE,
            ))
        self.save_user_buffs()
        self.render_cards_ui()
        self.refresh_input_options()
        self.update_skills(sel_job)
        w.set_tab(0)

    def save_all_configurations(self):
        w = self.window
        kept = {b.name: b for b in self.user_buffs if b.is_consumable}
        self.user_buffs = [b for b in self.user_buffs if not b.is_consumable]

        for item_name, (chk, details) in w.consumable_vars.items():
            if not chk.isChecked():
                continue
            # Keep the existing buff and its timer instead of recreating it.
            self.user_buffs.append(kept.get(item_name) or BuffItem(
                str(uuid.uuid4()),
                item_name,
                details["duration"],
                details.get("icon_default"),
                "bell1",
                NONE,
                NONE,
                is_consumable=True,
            ))

        self.save_user_buffs()
        self.render_cards_ui()
        self.refresh_input_options()
        self.update_skills(w.combo_job.currentData())
        w.set_tab(0)
