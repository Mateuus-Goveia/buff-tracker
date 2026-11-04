"""Compact, always-on-top view of the configured buff timers."""
import math
import os

from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtGui import QMouseEvent, QPixmap
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget

from src.i18n import tr
from src.utils import ICONS_DIR


class BuffOverlay(QWidget):
    position_changed = Signal(int, int)

    COLUMNS = 5
    ITEM_WIDTH = 70
    ITEM_HEIGHT = 58

    def __init__(self):
        super().__init__(None, Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setObjectName("buffOverlay")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowTitle("Buff Tracker Overlay")
        self.setStyleSheet("""
            QWidget#buffOverlay { background-color: rgba(17, 19, 25, 220); border: 1px solid rgba(240, 207, 122, 150); border-radius: 7px; }
            QFrame#overlayItem { background-color: rgba(42, 45, 54, 175); border-radius: 4px; }
            QLabel#overlayTimer { background: transparent; color: #c8cbd2; font-size: 10px; }
            QLabel#overlayTimer[state="active"] { color: #4ade80; }
            QLabel#overlayTimer[state="warn"] { color: #facc15; }
        """)
        self._enabled = False
        self._click_through = False
        self._drag_position = None
        self._timer_labels = {}
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(7, 7, 7, 7)
        self._layout.setHorizontalSpacing(2)
        self._layout.setVerticalSpacing(2)
        self.set_buffs([])

    def set_enabled(self, enabled):
        self._enabled = bool(enabled)
        self.setVisible(self._enabled)

    def set_opacity(self, percent):
        self.setWindowOpacity(max(0.3, min(1.0, int(percent) / 100)))

    def set_click_through(self, enabled):
        enabled = bool(enabled)
        if enabled == self._click_through:
            return
        self._click_through = enabled
        was_visible = self.isVisible()
        self.setWindowFlag(Qt.WindowType.WindowTransparentForInput, enabled)
        if was_visible:
            self.show()

    def set_buffs(self, buffs):
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.removeEventFilter(self)
                for child in widget.findChildren(QWidget):
                    child.removeEventFilter(self)
                widget.deleteLater()

        self._timer_labels = {}
        for index, buff in enumerate(buffs):
            tile = QFrame(self)
            tile.setObjectName("overlayItem")
            tile.setFixedSize(self.ITEM_WIDTH, self.ITEM_HEIGHT)
            tile.setToolTip(buff.name)
            tile.installEventFilter(self)
            for child in tile.findChildren(QWidget):
                child.installEventFilter(self)

            tile_layout = QVBoxLayout(tile)
            tile_layout.setContentsMargins(2, 2, 2, 2)
            tile_layout.setSpacing(0)
            icon_label = QLabel(tile)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_label.setFixedHeight(36)
            icon_path = os.path.join(ICONS_DIR, buff.icon_file) if buff.icon_file else ""
            pixmap = QPixmap(icon_path) if icon_path and os.path.isfile(icon_path) else QPixmap()
            if not pixmap.isNull():
                icon_label.setPixmap(pixmap.scaled(
                    34, 34, Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                ))
            icon_label.installEventFilter(self)
            tile_layout.addWidget(icon_label)

            timer_label = QLabel(tile)
            timer_label.setObjectName("overlayTimer")
            timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            timer_label.setFixedHeight(15)
            timer_label.setMinimumWidth(self.ITEM_WIDTH - 4)
            timer_label.installEventFilter(self)
            tile_layout.addWidget(timer_label)
            self._timer_labels[buff.id] = (buff, timer_label)
            self._layout.addWidget(tile, index // self.COLUMNS, index % self.COLUMNS)

        empty_label = None
        if not buffs:
            empty_label = QLabel(tr("overlay.empty"), self)
            empty_label.setObjectName("overlayTimer")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.installEventFilter(self)
            self._layout.addWidget(empty_label, 0, 0)

        columns = min(self.COLUMNS, max(1, len(buffs)))
        width = columns * self.ITEM_WIDTH + max(0, columns - 1) * self._layout.horizontalSpacing() + 14
        rows = max(1, math.ceil(len(buffs) / self.COLUMNS))
        height = rows * self.ITEM_HEIGHT + max(0, rows - 1) * self._layout.verticalSpacing() + 14
        if empty_label is not None:
            width = max(width, empty_label.sizeHint().width() + 14)
            height = max(height, empty_label.sizeHint().height() + 14)
        self.setFixedSize(width, height)
        self._place_initially_if_needed()
        self.refresh_timers()

    def refresh_timers(self):
        for buff, label in self._timer_labels.values():
            if buff.is_active:
                seconds = max(0, buff.remaining)
                label.setText(f"{seconds // 60:02d}:{seconds % 60:02d}")
                label.setProperty("state", "warn" if seconds <= 10 else "active")
            else:
                label.setText(tr("overlay.ready"))
                label.setProperty("state", "ready")
            label.style().unpolish(label)
            label.style().polish(label)

    def _place_initially_if_needed(self):
        if self.property("positionRestored"):
            return
        screen = self.screen()
        if screen is None:
            from PySide6.QtGui import QGuiApplication
            screen = QGuiApplication.primaryScreen()
        if screen is not None:
            area = screen.availableGeometry()
            # Top-center of the screen: visible and out of the way on first run.
            self.move(area.left() + (area.width() - self.width()) // 2, area.top() + 12)
        self.setProperty("positionRestored", True)

    def eventFilter(self, watched, event):
        if self._click_through:
            return super().eventFilter(watched, event)
        if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            return True
        if event.type() == QEvent.Type.MouseMove and self._drag_position is not None:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            return True
        if event.type() == QEvent.Type.MouseButtonRelease and event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = None
            self.position_changed.emit(self.x(), self.y())
            return True
        return super().eventFilter(watched, event)

    def mousePressEvent(self, event: QMouseEvent):
        if not self._click_through and event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if not self._click_through and self._drag_position is not None:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = None
            self.position_changed.emit(self.x(), self.y())
        super().mouseReleaseEvent(event)

