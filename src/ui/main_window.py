import os
import json
import webbrowser

from PySide6.QtCore import QByteArray, QSize, Qt, QUrl
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PySide6.QtWidgets import (
    QButtonGroup, QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFrame, QGridLayout, QHBoxLayout, QLabel, QListView,
    QMainWindow, QMessageBox, QPushButton, QScrollArea, QSizePolicy, QStackedWidget, QVBoxLayout, QWidget,
)

from src.i18n import current_language, tr
from src.options import NONE, input_label, modifier_items
from src.utils import ICONS_DIR, KEYBOARD_DIR, keyboard_asset_name
from src.ui.theme import theme_asset
from src.ui.widgets import add_shadow
from src.update_checker import (
    APP_VERSION, GITHUB_REPOSITORY, REQUEST_TIMEOUT_MS, UpdateCheckError,
    evaluate_releases, releases_api_url, validate_repository,
)

DONATE_URL = "https://www.paypal.com/donate/?hosted_button_id=3MHRZ5NYLQZRS"
PIX_URL = "https://nubank.com.br/cobrar/gfgdg/6ae9fc91-b114-4cb5-90af-09fc73cbed4e"

KEY_ROWS = [
    [(f"f{i}", i - 1) for i in range(1, 13)],
    [(key, col) for col, key in enumerate(("backtick", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "minus", "equals"))],
    [(key, col) for col, key in enumerate(("q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "bracket_left", "bracket_right", "backslash"))],
    [(key, col + 1) for col, key in enumerate(("a", "s", "d", "f", "g", "h", "j", "k", "l", "semicolon", "quote"))],
    [("shift", 0)] + [(key, col + 1) for col, key in enumerate(("z", "x", "c", "v", "b", "n", "m", "comma", "period", "slash"))],
    [("ctrl", 0), ("alt", 1), ("space", 2, 5), ("hm", 8), ("ins", 9), ("del", 10),
     ("arrow_left", 11), ("arrow_up", 12), ("arrow_down", 13), ("arrow_right", 14)],
    [("end", 8), ("pup", 9), ("pdn", 10)],
]


class KeyboardPickerDialog(QDialog):
    def __init__(self, used_keys, current_key=None, parent=None):
        super().__init__(parent)
        self.selected_key = None
        self.setWindowTitle(tr("keyboard.title"))
        self.setModal(True)
        self.setMinimumWidth(660)

        layout = QVBoxLayout(self)
        hint = QLabel(tr("keyboard.hint"))
        hint.setWordWrap(True)
        layout.addWidget(hint)

        grid = QGridLayout()
        grid.setHorizontalSpacing(3)
        grid.setVerticalSpacing(4)
        for row_index, keys in enumerate(KEY_ROWS):
            for entry in keys:
                key_id, column = entry[:2]
                span = entry[2] if len(entry) > 2 else 1
                asset = keyboard_asset_name(key_id)
                pixmap = load_pixmap(os.path.join(KEYBOARD_DIR, asset), 38) if asset else None
                if pixmap is None:
                    continue
                button = QPushButton()
                button.setObjectName("keyboardKey")
                button.setFixedSize(42 * span, 42)
                button.setIcon(QIcon(pixmap))
                button.setIconSize(QSize(38, 38))
                button.setToolTip(key_id.upper() if len(key_id) == 1 else key_id.replace("_", " ").title())
                button.setEnabled(key_id not in used_keys or key_id == current_key)
                button.clicked.connect(lambda _checked=False, selected=key_id: self._select_key(selected))
                grid.addWidget(button, row_index, column, 1, span)
        layout.addLayout(grid)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _select_key(self, key_id):
        self.selected_key = key_id
        self.accept()


def load_pixmap(path, size):
    """Load a PNG and scale it to size x size.

    Small pixel-art icons are enlarged without smoothing to keep their edges crisp;
    large images (e.g. 1024 px) are reduced with smoothing to avoid jagged edges.
    """
    if not path or not os.path.exists(path):
        return None
    pix = QPixmap(path)
    if pix.isNull():
        return None
    big = max(pix.width(), pix.height()) > size * 2
    mode = Qt.TransformationMode.SmoothTransformation if big else Qt.TransformationMode.FastTransformation
    return pix.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, mode)


def set_combo_items(combo, items, current=None):
    """Replace combo-box items without emitting signals.

    items: strings or (label, data) pairs. Data is language-neutral and read with
    combo.currentData(). current is the value to select (defaults to the first item).
    """
    combo.blockSignals(True)
    combo.clear()
    for item in items:
        text, data = item if isinstance(item, tuple) else (item, item)
        combo.addItem(text, data)
    idx = combo.findData(current) if current is not None else -1
    combo.setCurrentIndex(idx if idx >= 0 else 0)
    combo.blockSignals(False)


def make_combo(values=()):
    combo = QComboBox()
    view = QListView()  # Required for QSS to style the list items.
    view.setMouseTracking(True)  # Highlight items on hover.
    combo.setView(view)
    combo.setIconSize(QSize(24, 24))
    combo.setMaxVisibleItems(10)
    # Let the layout determine width so a long item does not extend beyond the panel.
    combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
    combo.setMinimumContentsLength(6)
    combo.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)  # Ignored = zero minimum width.
    set_combo_items(combo, values)
    return combo


class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self._network_manager = QNetworkAccessManager(self)
        self._network_manager.setTransferTimeout(REQUEST_TIMEOUT_MS)
        self._i18n = []  # (widget, text function) pairs for live language switching.

        icon_path = theme_asset("app_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.setMinimumSize(540, 480)
        self.resize(620, 760)

        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(10, 10, 10, 0)
        layout.setSpacing(8)

        layout.addWidget(self._build_header())

        # Custom tabs (checkable buttons + QStackedWidget) keep equal widths and swappable sprites.
        tab_row = QHBoxLayout()
        tab_row.setSpacing(6)
        self.stack = QStackedWidget()
        self.tab_buttons = []
        pages = [
            ("tab.counters", "tab_timer.png", self._build_timer_tab()),
            ("tab.settings", "tab_config.png", self._build_config_tab()),
        ]
        for index, (key, icon_name, page) in enumerate(pages):
            btn = QPushButton()
            btn.setObjectName("tab")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setIcon(QIcon(theme_asset(icon_name)))
            btn.setIconSize(QSize(24, 24))
            btn.clicked.connect(lambda _checked=False, i=index: self.set_tab(i))
            self._reg(btn, lambda k=key: "  " + tr(k))
            tab_row.addWidget(btn, 1)
            self.tab_buttons.append(btn)
            self.stack.addWidget(page)
        layout.addLayout(tab_row)
        layout.addWidget(self.stack, 1)
        self.set_tab(0)

        btn_donate = QPushButton()
        btn_donate.setObjectName("donate")
        btn_donate.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_donate.setIcon(QIcon(theme_asset("coffee.png")))
        btn_donate.setIconSize(QSize(32, 32))
        btn_donate.clicked.connect(self.show_donation_options)
        self._reg(btn_donate, lambda: "  " + tr("donate"))
        layout.addWidget(btn_donate)

        self.retranslate()

    def show_donation_options(self):
        dialog = QDialog(self)
        dialog.setObjectName("donationDialog")
        dialog.setWindowTitle(tr("donate.title"))
        dialog.setModal(True)
        layout = QVBoxLayout(dialog)
        message = QLabel(tr("donate.choose_method"))
        message.setObjectName("donationPrompt")
        message.setWordWrap(True)
        layout.addWidget(message)

        paypal_button = QPushButton(tr("donate.paypal"))
        paypal_button.clicked.connect(lambda: self._open_donation_link(DONATE_URL, dialog))
        layout.addWidget(paypal_button)

        pix_button = QPushButton(tr("donate.pix"))
        pix_button.clicked.connect(lambda: self._open_donation_link(PIX_URL, dialog))
        layout.addWidget(pix_button)

        cancel_button = QPushButton(tr("btn.cancel"))
        cancel_button.clicked.connect(dialog.reject)
        layout.addWidget(cancel_button)
        dialog.exec()

    @staticmethod
    def _open_donation_link(url, dialog):
        webbrowser.open(url)
        dialog.accept()

    # ---------------------------------------------------------------- language
    def _reg(self, widget, text_fn):
        """Register a widget whose text depends on the selected language."""
        self._i18n.append((widget, text_fn))
        widget.setText(text_fn())
        return widget

    def _label(self, key, object_name="fieldLabel", wrap=False, shadow=False):
        lbl = QLabel()
        lbl.setObjectName(object_name)
        if wrap:
            lbl.setWordWrap(True)
        if shadow:
            add_shadow(lbl)
        return self._reg(lbl, lambda: tr(key))

    def retranslate(self):
        self.setWindowTitle(tr("app.title"))
        for widget, text_fn in self._i18n:
            widget.setText(text_fn())
        self.refresh_setting_items()
        self.refresh_input_mode_controls()
        self.refresh_modifier_items()

    def refresh_setting_items(self):
        set_combo_items(self.combo_language, [(tr("language.pt"), "pt"), (tr("language.en"), "en")], current_language())

    def refresh_input_mode_controls(self):
        keyboard_mode = self.controller.input_mode == "keyboard"
        self.btn_mode_joystick.setChecked(not keyboard_mode)
        self.btn_mode_keyboard.setChecked(keyboard_mode)
        self.combo_mod.setVisible(not keyboard_mode)
        self.combo_input.setVisible(not keyboard_mode)
        self.btn_choose_key.setVisible(keyboard_mode)
        self.lbl_shortcut_preview.setVisible(not keyboard_mode)

    def refresh_modifier_items(self):
        current = self.combo_mod.currentData() or NONE
        set_combo_items(self.combo_mod, modifier_items(), current)

    def set_tab(self, index):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.tab_buttons):
            btn.setChecked(i == index)

    # ------------------------------------------------------------------ header
    def _build_header(self):
        header = QFrame()
        header.setObjectName("header")
        row = QHBoxLayout(header)
        row.setContentsMargins(2, 0, 2, 0)

        logo_box = QLabel()
        logo_box.setObjectName("iconFrame")
        logo_box.setFixedSize(44, 44)
        logo_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo = QPixmap(theme_asset("logo.png"))
        if not logo.isNull():
            logo_box.setPixmap(logo)
        row.addWidget(logo_box)

        title = self._label("app.title", "appTitle", shadow=True)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.addWidget(title, 1)

        return header

    # ------------------------------------------------------------ scroll helper
    @staticmethod
    def _scroll_area():
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.viewport().setAutoFillBackground(False)
        inner = QWidget()
        inner.setAutoFillBackground(False)
        inner.setObjectName("scrollInner")
        inner.setStyleSheet("QWidget#scrollInner { background: transparent; }")
        scroll.setWidget(inner)
        return scroll, inner

    @staticmethod
    def _content_frame(scroll):
        """Panel with an ornamental frame around a tab's content."""
        frame = QFrame()
        frame.setObjectName("content")
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(2, 2, 2, 2)
        lay.addWidget(scroll)
        return frame

    # -------------------------------------------------------------- timer tab
    def _build_timer_tab(self):
        scroll, inner = self._scroll_area()
        self.cards_layout = QVBoxLayout(inner)
        self.cards_layout.setContentsMargins(4, 4, 4, 4)
        self.cards_layout.setSpacing(6)
        self.cards_layout.addStretch(1)
        return self._content_frame(scroll)

    def clear_cards(self):
        while self.cards_layout.count() > 1:  # Keep the final stretch item.
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def add_card(self, widget):
        self.cards_layout.insertWidget(self.cards_layout.count() - 1, widget)

    def show_empty_message(self, text):
        lbl = QLabel(text)
        lbl.setObjectName("hint")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setWordWrap(True)
        self.add_card(lbl)

    # ---------------------------------------------------------- settings tab
    def _build_config_tab(self):
        scroll, inner = self._scroll_area()
        col = QVBoxLayout(inner)
        col.setContentsMargins(8, 6, 8, 8)
        col.setSpacing(8)

        preferences = QFrame()
        preferences.setObjectName("inset")
        preferences_grid = QGridLayout(preferences)
        preferences_grid.setContentsMargins(10, 6, 10, 6)
        preferences_grid.setHorizontalSpacing(10)
        preferences_grid.setVerticalSpacing(6)
        self.combo_language = make_combo()
        self.btn_mode_joystick = QPushButton()
        self.btn_mode_joystick.setObjectName("small")
        self.btn_mode_joystick.setCheckable(True)
        self.btn_mode_joystick.setCursor(Qt.CursorShape.PointingHandCursor)
        self._reg(self.btn_mode_joystick, lambda: tr("mode.joystick"))
        self.btn_mode_keyboard = QPushButton()
        self.btn_mode_keyboard.setObjectName("small")
        self.btn_mode_keyboard.setCheckable(True)
        self.btn_mode_keyboard.setCursor(Qt.CursorShape.PointingHandCursor)
        self._reg(self.btn_mode_keyboard, lambda: tr("mode.keyboard"))
        self.mode_button_group = QButtonGroup(self)
        self.mode_button_group.setExclusive(True)
        self.mode_button_group.addButton(self.btn_mode_joystick)
        self.mode_button_group.addButton(self.btn_mode_keyboard)
        mode_buttons = QHBoxLayout()
        mode_buttons.setSpacing(6)
        mode_buttons.addWidget(self.btn_mode_joystick)
        mode_buttons.addWidget(self.btn_mode_keyboard)
        preferences_grid.addWidget(self._label("settings.input_mode"), 0, 0)
        preferences_grid.addLayout(mode_buttons, 0, 1)
        preferences_grid.addWidget(self._label("settings.language"), 1, 0)
        preferences_grid.addWidget(self.combo_language, 1, 1)
        self.btn_check_updates = QPushButton()
        self.btn_check_updates.setObjectName("small")
        self.btn_check_updates.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_check_updates.clicked.connect(self.check_for_updates)
        self._reg(self.btn_check_updates, lambda: tr("update.check"))
        preferences_grid.addWidget(self.btn_check_updates, 2, 0, 1, 2)
        col.addWidget(preferences)

        col.addWidget(self._label("settings.title", "sectionTitle", wrap=True, shadow=True))

        # --- Buff form
        builder = QFrame()
        builder.setObjectName("inset")
        grid = QGridLayout(builder)
        grid.setContentsMargins(10, 6, 10, 6)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(6)
        grid.setColumnStretch(1, 1)

        class_names = list(self.controller.classes_data.keys()) if self.controller.classes_data else ["Warrior"]
        self.combo_class = make_combo(class_names)
        self.combo_job = make_combo([(tr("combo.none"), None)])
        self.combo_skill = make_combo([(tr("combo.none_skill"), None)])
        self.combo_level = make_combo(["Lv. 1"])
        self.combo_mod = make_combo()
        self.combo_input = make_combo([(input_label(NONE), NONE)])
        self.btn_choose_key = QPushButton()
        self.btn_choose_key.setObjectName("keyboardKey")
        self.btn_choose_key.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_choose_key.clicked.connect(self.controller.choose_keyboard_key)
        self.refresh_keyboard_key_button(None)
        self.combo_sound = make_combo(self.controller.get_available_sounds())

        rows = [
            ("label.class", self.combo_class),
            ("label.job", self.combo_job),
            ("label.skill", self.combo_skill),
            ("label.level", self.combo_level),
        ]
        for i, (key, combo) in enumerate(rows):
            grid.addWidget(self._label(key), i, 0)
            grid.addWidget(combo, i, 1, 1, 2)

        # Controller shortcut = modifier + button; keyboard mode uses the key picker.
        grid.addWidget(self._label("label.shortcut"), 4, 0)
        shortcut_row = QHBoxLayout()
        shortcut_row.setSpacing(8)
        shortcut_row.addWidget(self.combo_mod, 1)
        shortcut_row.addWidget(self.combo_input, 1)
        shortcut_row.addWidget(self.btn_choose_key, 2)
        self.lbl_shortcut_preview = QLabel()
        self.lbl_shortcut_preview.setFixedSize(40, 40)
        self.lbl_shortcut_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        shortcut_row.addWidget(self.lbl_shortcut_preview)
        grid.addLayout(shortcut_row, 4, 1, 1, 2)

        grid.addWidget(self._label("label.sound"), 5, 0)
        grid.addWidget(self.combo_sound, 5, 1, 1, 2)
        col.addWidget(builder)

        self.lbl_error = QLabel("")
        self.lbl_error.setObjectName("error")
        self.lbl_error.setWordWrap(True)
        self.lbl_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        col.addWidget(self.lbl_error)

        btn_add = QPushButton()
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.clicked.connect(self.controller.add_skill_to_preset)
        self._reg(btn_add, lambda: tr("btn.add_skill"))
        col.addWidget(btn_add)

        # --- Consumables
        col.addWidget(self._label("settings.consumables", "sectionTitle", wrap=True, shadow=True))

        cons = QFrame()
        cons.setObjectName("inset")
        clay = QVBoxLayout(cons)
        clay.setContentsMargins(12, 6, 12, 6)
        clay.setSpacing(4)

        self.consumable_vars = {}  # nome -> (QCheckBox, detalhes)
        for items in (self.controller.consumables_data or {}).values():
            for item_name, details in items.items():
                chk = QCheckBox(f"{item_name} ({details['duration']}s)")
                icon_file = details.get("icon_default")
                if icon_file:
                    pix = load_pixmap(os.path.join(ICONS_DIR, icon_file), 32)
                    if pix is not None:
                        chk.setIcon(QIcon(pix))
                        chk.setIconSize(QSize(32, 32))
                clay.addWidget(chk)
                self.consumable_vars[item_name] = (chk, details)
        col.addWidget(cons)

        btn_save = QPushButton()
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.clicked.connect(self.controller.save_all_configurations)
        self._reg(btn_save, lambda: tr("btn.save"))
        col.addWidget(btn_save)
        col.addStretch()

        # Use signals for user actions only (activated), like CustomTkinter's "command".
        # Values come from currentData() (internal IDs), not translated labels.
        self.combo_class.textActivated.connect(self.controller.update_jobs)
        self.combo_job.activated.connect(lambda _i: self.controller.update_skills(self.combo_job.currentData()))
        self.combo_skill.activated.connect(lambda _i: self.controller.update_levels(self.combo_skill.currentData()))
        self.combo_mod.activated.connect(lambda _i: self.controller.refresh_input_options())
        self.combo_input.activated.connect(lambda _i: self.controller.update_previews())
        self.combo_sound.textActivated.connect(self.controller.play_sound)  # Preview the selected sound.
        self.btn_mode_joystick.clicked.connect(lambda: self.controller.change_input_mode("joystick"))
        self.btn_mode_keyboard.clicked.connect(lambda: self.controller.change_input_mode("keyboard"))
        self.combo_language.activated.connect(lambda _i: self.controller.change_language(self.combo_language.currentData()))

        return self._content_frame(scroll)

    def check_for_updates(self):
        if not GITHUB_REPOSITORY:
            self._show_update_message(tr("update.not_configured"))
            return
        if not self.btn_check_updates.isEnabled():
            return

        try:
            repository = validate_repository(GITHUB_REPOSITORY)
        except UpdateCheckError:
            self._show_update_message(tr("update.not_configured"))
            return
        request = QNetworkRequest(QUrl(releases_api_url(repository)))
        request.setRawHeader(QByteArray(b"Accept"), QByteArray(b"application/vnd.github+json"))
        request.setRawHeader(QByteArray(b"User-Agent"), QByteArray(f"BuffTracker/{APP_VERSION}".encode("ascii")))
        request.setRawHeader(QByteArray(b"X-GitHub-Api-Version"), QByteArray(b"2022-11-28"))
        self.btn_check_updates.setEnabled(False)
        reply = self._network_manager.get(request)
        reply.finished.connect(lambda current_reply=reply: self._on_update_reply(current_reply))

    def _on_update_reply(self, reply):
        try:
            if reply.error() != QNetworkReply.NetworkError.NoError:
                self._show_update_message(tr("update.network_error"))
                return
            releases = json.loads(bytes(reply.readAll()).decode("utf-8"))
            result = evaluate_releases(releases, APP_VERSION)
            self._show_update_result(result)
        except (UpdateCheckError, UnicodeDecodeError, json.JSONDecodeError):
            self._show_update_message(tr("update.network_error"))
        finally:
            reply.deleteLater()
            self.btn_check_updates.setEnabled(True)

    def _show_update_result(self, result):
        if result["update_available"]:
            box = QMessageBox(self)
            box.setIcon(QMessageBox.Icon.Information)
            box.setWindowTitle(tr("update.title"))
            box.setTextFormat(Qt.TextFormat.PlainText)
            box.setText(tr("update.available", version=result["latest_version"]))
            open_button = box.addButton(tr("update.open_releases"), QMessageBox.ButtonRole.AcceptRole)
            box.addButton(tr("update.later"), QMessageBox.ButtonRole.RejectRole)
            box.exec()
            if box.clickedButton() is open_button:
                webbrowser.open(f"https://github.com/{GITHUB_REPOSITORY}/releases")
        else:
            self._show_update_message(tr("update.current", version=result["current_version"]))

    def _show_update_message(self, message):
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Information)
        box.setWindowTitle(tr("update.title"))
        box.setTextFormat(Qt.TextFormat.PlainText)
        box.setText(message)
        box.exec()

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def set_combo_items(combo, items, current=None):
        set_combo_items(combo, items, current)

    @staticmethod
    def select_data(combo, data):
        idx = combo.findData(data)
        if idx >= 0:
            combo.setCurrentIndex(idx)

    def set_error(self, text):
        self.lbl_error.setText(text)

    def refresh_keyboard_key_button(self, key_id):
        self.btn_choose_key.setEnabled(self.combo_skill.currentData() is not None)
        if not key_id or key_id == NONE:
            self.btn_choose_key.setText(tr("keyboard.choose"))
            self.btn_choose_key.setIcon(QIcon())
            return
        asset = keyboard_asset_name(key_id)
        pixmap = load_pixmap(os.path.join(KEYBOARD_DIR, asset), 32) if asset else None
        self.btn_choose_key.setText(key_id.upper() if len(key_id) == 1 else key_id.replace("_", " ").title())
        self.btn_choose_key.setIcon(QIcon(pixmap) if pixmap else QIcon())
        self.btn_choose_key.setIconSize(QSize(32, 32))
