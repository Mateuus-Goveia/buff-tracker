from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout,
)

from src.i18n import tr
from src.options import NONE, input_label


def repolish(widget):
    """Reapply QSS after changing a dynamic property (e.g. state)."""
    widget.style().unpolish(widget)
    widget.style().polish(widget)


def add_shadow(label, offset=2, color="#000000"):
    """Add a hard one-pixel text shadow (QSS does not support text-shadow)."""
    effect = QGraphicsDropShadowEffect(label)
    effect.setBlurRadius(0)
    effect.setOffset(offset, offset)
    effect.setColor(QColor(color))
    label.setGraphicsEffect(effect)


class ElidedLabel(QLabel):
    """A QLabel without a minimum width; elide text with '…' when space is limited (the tooltip shows the full text)."""

    def __init__(self, text=""):
        super().__init__()
        self._full = ""
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.setMinimumWidth(30)
        self.setText(text)

    def setText(self, text):
        self._full = text
        self.setToolTip(text)
        self._refresh()

    def _refresh(self):
        width = self.width()
        shown = self.fontMetrics().elidedText(self._full, Qt.TextElideMode.ElideRight, width) if width > 30 else self._full
        QLabel.setText(self, shown)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._refresh()


class BuffCard(QFrame):
    """A buff card on the Counters tab."""

    def __init__(self, buff, icon_pixmap, shortcut_pixmap, on_start, on_remove, show_controller_badge=True):
        super().__init__()
        self.setObjectName("card")
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        row = QHBoxLayout(self)
        row.setContentsMargins(2, 0, 2, 0)
        row.setSpacing(10)

        lbl_icon = QLabel()
        lbl_icon.setObjectName("iconFrame")
        lbl_icon.setFixedSize(56, 56)
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if icon_pixmap is not None:
            lbl_icon.setPixmap(icon_pixmap)
        row.addWidget(lbl_icon)

        info = QVBoxLayout()
        info.setSpacing(2)
        self.lbl_name = ElidedLabel(buff.name)
        self.lbl_name.setObjectName("cardName")
        add_shadow(self.lbl_name)
        self.lbl_timer = QLabel()
        self.lbl_timer.setObjectName("timer")
        add_shadow(self.lbl_timer)
        info.addStretch()
        info.addWidget(self.lbl_name)
        info.addWidget(self.lbl_timer)
        info.addStretch()
        row.addLayout(info, 1)

        if shortcut_pixmap is not None:
            lbl_shortcut = QLabel()
            lbl_shortcut.setPixmap(shortcut_pixmap)
            row.addWidget(lbl_shortcut)
        elif show_controller_badge and not buff.is_consumable and buff.input_key != NONE:
            badge = QLabel(input_label(buff.input_key))
            badge.setObjectName("badge")
            row.addWidget(badge)

        btn_start = QPushButton(tr("btn.activate"))
        btn_start.setObjectName("small")
        btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_start.clicked.connect(lambda: on_start(buff))
        row.addWidget(btn_start)

        btn_del = QPushButton("X")
        btn_del.setObjectName("danger")
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.clicked.connect(lambda: on_remove(buff))
        row.addWidget(btn_del)

        self.set_timer(*self._initial_state(buff))

    @staticmethod
    def _initial_state(buff):
        if buff.is_active:
            return tr("card.remaining", seconds=buff.remaining), "ok"
        return tr("card.ready", seconds=buff.duration), "ready"

    def set_timer(self, text, state):
        self.lbl_timer.setText(text)
        self.lbl_timer.setProperty("state", state)
        repolish(self.lbl_timer)
