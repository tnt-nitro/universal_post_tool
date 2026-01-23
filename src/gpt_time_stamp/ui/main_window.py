from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel
)
from PySide6.QtGui import QTextCursor
from PySide6.QtCore import QTimer, Qt
from datetime import datetime
import threading
from gpt_time_stamp.core.timestamp import generate_timestamp
from gpt_time_stamp.core.clipboard import copy_to_clipboard
from gpt_time_stamp.core.position_recorder import record_send_position, record_once
from gpt_time_stamp.core.config import load_config, save_config
from gpt_time_stamp.core.sender import send_to_chatgpt
from gpt_time_stamp.core.constants import APP_TITLE, APP_VERSION, WINDOW_WIDTH, WINDOW_HEIGHT


LIGHT_THEME = """
QMainWindow {
    background-color: #f5f5f5;
}

QTextEdit {
    background-color: #ffffff;
    color: #000000;
    border-radius: 6px;
    padding: 8px;
    font-size: 11pt;
}

QPushButton#copyButton {
    background-color: #3a86ff;
    color: white;
    border-radius: 6px;
    padding: 8px;
}

QPushButton#copyButton:hover {
    background-color: #5fa8ff;
}

QPushButton#themeButton {
    background-color: #e0e0e0;
    color: #000000;
    border-radius: 6px;
    padding: 8px;
}

QPushButton#themeButton:hover {
    background-color: #d0d0d0;
}

QPushButton#formatButton {
    background-color: #e0e0e0;
    color: #000000;
    border-radius: 6px;
    padding: 6px;
}

QPushButton#formatButton:hover {
    background-color: #d0d0d0;
}

QLabel#timestampLabel {
    background-color: #e8e8e8;
    color: #000000;
    border-radius: 6px;
    padding: 8px;
    font-size: 10pt;
    font-weight: bold;
}

QLabel#uptimeLabel {
    background-color: #e8e8e8;
    color: #000000;
    border-radius: 6px;
    padding: 8px;
    font-size: 10pt;
    font-weight: bold;
}

QLabel#positionStatus {
    background-color: #e0e0e0;
    color: #000000;
    border-radius: 6px;
    padding: 4px 8px;
}
"""

DARK_THEME = """
QMainWindow {
    background-color: #1e1e1e;
}

QTextEdit {
    background-color: #2b2b2b;
    color: #ffffff;
    border-radius: 6px;
    padding: 8px;
    font-size: 11pt;
}

QPushButton#copyButton {
    background-color: #3a86ff;
    color: white;
    border-radius: 6px;
    padding: 8px;
}

QPushButton#copyButton:hover {
    background-color: #5fa8ff;
}

QPushButton#themeButton {
    background-color: #3a3a3a;
    color: white;
    border-radius: 6px;
    padding: 8px;
}

QPushButton#themeButton:hover {
    background-color: #4a4a4a;
}

QPushButton#formatButton {
    background-color: #3a3a3a;
    color: white;
    border-radius: 6px;
    padding: 6px;
}

QPushButton#formatButton:hover {
    background-color: #4a4a4a;
}

QLabel#timestampLabel {
    background-color: #2b2b2b;
    color: #ffffff;
    border-radius: 6px;
    padding: 8px;
    font-size: 10pt;
    font-weight: bold;
}

QLabel#uptimeLabel {
    background-color: #2b2b2b;
    color: #ffffff;
    border-radius: 6px;
    padding: 8px;
    font-size: 10pt;
    font-weight: bold;
}

QLabel#positionStatus {
    background-color: #3a3a3a;
    color: white;
    border-radius: 6px;
    padding: 4px 8px;
}
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"{APP_TITLE} v{APP_VERSION}")
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self.timestamp_label = QLabel()
        self.timestamp_label.setObjectName("timestampLabel")
        self.timestamp_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.position_status = QLabel("Bereit – keine Position")
        self.position_status.setObjectName("positionStatus")
        self.position_status.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.uptime_label = QLabel("Laufzeit: 00:00:00")
        self.uptime_label.setObjectName("uptimeLabel")
        self.uptime_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Text eingeben…")

        self.copy_button = QPushButton("In Zwischenablage kopieren")
        self.copy_button.setObjectName("copyButton")
        self.copy_button.setFixedHeight(36)
        self.copy_button.clicked.connect(self.on_copy_and_send)

        # Format-Buttons vertikal links
        self.format_layout = QVBoxLayout()

        # Einheitliche Button-Größe
        BUTTON_SIZE = 36

        self.btn_learn = QPushButton("🎯")
        self.btn_learn.setObjectName("formatButton")
        self.btn_learn.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)
        self.btn_learn.clicked.connect(self.learn_send_position)

        btn_code = QPushButton("```")
        btn_bold = QPushButton("**")
        btn_italic = QPushButton("_")
        btn_strike = QPushButton("~~")

        btn_code.clicked.connect(self.insert_codeblock)
        btn_bold.clicked.connect(lambda: self.insert_inline_format("**"))
        btn_italic.clicked.connect(lambda: self.insert_inline_format("_"))
        btn_strike.clicked.connect(lambda: self.insert_inline_format("~~"))

        btn_code.setObjectName("formatButton")
        btn_bold.setObjectName("formatButton")
        btn_italic.setObjectName("formatButton")
        btn_strike.setObjectName("formatButton")

        # Alle Format-Buttons auf gleiche Größe setzen
        btn_code.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)
        btn_bold.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)
        btn_italic.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)
        btn_strike.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)

        self.format_layout.insertWidget(0, self.btn_learn)
        self.format_layout.addWidget(btn_code)
        self.format_layout.addWidget(btn_bold)
        self.format_layout.addWidget(btn_italic)
        self.format_layout.addWidget(btn_strike)

        self.format_layout.addStretch()  # schiebt alles darunter nach unten
        self.format_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        btn_clear = QPushButton("🗑️")
        btn_clear.setObjectName("formatButton")
        btn_clear.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)
        btn_clear.clicked.connect(self.clear_text)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(btn_clear)

        self.copy_button.setMinimumHeight(BUTTON_SIZE)
        bottom_layout.addWidget(self.copy_button, stretch=1)

        self.theme_button = QPushButton("☀️")
        self.theme_button.setObjectName("themeButton")
        self.theme_button.clicked.connect(self.toggle_theme)
        self.theme_button.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)

        layout = QVBoxLayout()

        time_layout = QHBoxLayout()
        time_layout.addWidget(self.theme_button)
        time_layout.addWidget(self.timestamp_label)
        time_layout.addWidget(self.position_status)
        time_layout.addStretch()
        time_layout.addWidget(self.uptime_label)
        layout.addLayout(time_layout)

        editor_layout = QHBoxLayout()
        editor_layout.addLayout(self.format_layout)
        editor_layout.addWidget(self.text_edit)

        layout.addLayout(editor_layout)
        layout.addLayout(bottom_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.is_dark = False
        self.setStyleSheet(LIGHT_THEME)

        # Statusbar aktivieren
        self.statusBar()

        # Recorder-Zustand initialisieren
        self.recorder_state = "idle"
        self.update_recorder_ui()

        # Timer für Recorder
        self.record_timer = QTimer(self)
        self.record_timer.setSingleShot(True)
        self.record_timer.timeout.connect(self.record_timeout)

        # Startzeit für Laufzeit-Anzeige
        self.start_time = datetime.now()

        # Timer für Live-Timestamp-Vorschau und Laufzeit
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timestamp)
        self.timer.timeout.connect(self.update_uptime)
        self.timer.start(1000)  # Aktualisiert jede Sekunde
        self.update_timestamp()  # Initiale Anzeige
        self.update_uptime()  # Initiale Laufzeit-Anzeige

    def on_copy_and_send(self):
        user_text = self.text_edit.toPlainText()
        timestamp = generate_timestamp()
        final_text = f"{timestamp}\n\n{user_text}"
        copy_to_clipboard(final_text)

        try:
            send_to_chatgpt(final_text)
            self.statusBar().showMessage("Gesendet an ChatGPT", 5000)
        except Exception as e:
            self.statusBar().showMessage(str(e), 5000)

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        if self.is_dark:
            self.setStyleSheet(DARK_THEME)
            self.theme_button.setText("🌙")
        else:
            self.setStyleSheet(LIGHT_THEME)
            self.theme_button.setText("☀️")

    def update_timestamp(self):
        """Aktualisiert die Live-Timestamp-Vorschau."""
        timestamp = generate_timestamp()
        self.timestamp_label.setText(timestamp)

    def update_uptime(self):
        """Aktualisiert die Laufzeit-Anzeige."""
        delta = datetime.now() - self.start_time
        seconds = int(delta.total_seconds())
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        self.uptime_label.setText(f"Laufzeit: {h:02}:{m:02}:{s:02}")

    def clear_text(self):
        """Löscht den Text im Textfeld."""
        self.text_edit.clear()
        self.text_edit.setFocus()

    def learn_send_position(self):
        """Lernt die Sendeposition von ChatGPT."""
        if self.recorder_state == "ready":
            config = load_config()
            config["chatgpt_input"] = None
            save_config(config)
            self.recorder_state = "idle"
            self.update_recorder_ui()
            return

        if self.recorder_state == "idle":
            self.recorder_state = "recording"
            self.update_recorder_ui()

            self.btn_learn.setEnabled(False)
            QTimer.singleShot(3000, lambda: self.btn_learn.setEnabled(True))

            self.record_timer.start(10000)
            threading.Thread(target=self.start_mouse_recording,
                             daemon=True).start()

    def start_mouse_recording(self):
        """Startet den Mauslistener für die Positionsaufnahme."""
        def on_position(x, y):
            if self.recorder_state != "recording":
                return

            config = load_config()
            config["chatgpt_input"] = [x, y]
            save_config(config)

            self.record_timer.stop()
            self.recorder_state = "ready"
            self.update_recorder_ui()

        record_once(on_position)

    def record_timeout(self):
        """Wird aufgerufen, wenn das 10-Sekunden-Aufnahmefenster abläuft."""
        if self.recorder_state == "recording":
            self.recorder_state = "idle"
            self.update_recorder_ui()

    def update_recorder_ui(self):
        """Aktualisiert die UI basierend auf dem Recorder-Zustand."""
        if self.recorder_state == "idle":
            self.position_status.setText("Bereit – keine Position")
            self.position_status.setStyleSheet(
                "background-color: #a0a0a0; color: black;")
            self.btn_learn.setStyleSheet("background-color: #a0a0a0;")

        elif self.recorder_state == "recording":
            self.position_status.setText("Warte auf Klick…")
            self.position_status.setStyleSheet(
                "background-color: #d9534f; color: white;")
            self.btn_learn.setStyleSheet("background-color: #d9534f;")

        elif self.recorder_state == "ready":
            config = load_config()
            pos = config.get("chatgpt_input")
            if pos:
                self.position_status.setText(f"X: {pos[0]} | Y: {pos[1]}")
            else:
                self.position_status.setText("Position gespeichert")
            self.position_status.setStyleSheet(
                "background-color: #5cb85c; color: white;")
            self.btn_learn.setStyleSheet("background-color: #5cb85c;")

    def insert_inline_format(self, wrapper: str) -> None:
        cursor = self.text_edit.textCursor()
        selected = cursor.selectedText()

        if selected:
            cursor.insertText(f"{wrapper}{selected}{wrapper}")
            self.text_edit.setTextCursor(cursor)
        else:
            start_pos = cursor.position()
            cursor.insertText(f"{wrapper}{wrapper}")
            cursor.setPosition(start_pos + len(wrapper))
            self.text_edit.setTextCursor(cursor)

        self.text_edit.setFocus()

    def insert_codeblock(self) -> None:
        cursor = self.text_edit.textCursor()
        start_pos = cursor.position()

        prefix = "\n\n```\n"
        middle = "\n"
        suffix = "```\n\n"

        cursor.insertText(prefix + middle + suffix)

        # Cursor in die Leerzeile zwischen die Backticks setzen
        cursor.setPosition(start_pos + len(prefix))
        self.text_edit.setTextCursor(cursor)
        self.text_edit.setFocus()
