from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
from PySide6.QtCore import QRegularExpression


class CodeBlockHighlighter(QSyntaxHighlighter):
    STATE_NONE = 0
    STATE_CODE = 1

    def __init__(self, document, is_dark=False):
        super().__init__(document)

        self.code_format = QTextCharFormat()
        self.is_dark = is_dark
        self._update_format()

        # WICHTIG: Exakt 3 Backticks (```) - nicht 2!
        self.fence_re = QRegularExpression(r"^\s*```\s*$")
    
    def _update_format(self):
        """Aktualisiert das Format basierend auf dem aktuellen Theme."""
        if self.is_dark:
            # DARK: Textbereich #2b2b2b -> Codeblock #1f1f1f (dunkler)
            self.code_format.setBackground(QColor("#1f1f1f"))
            self.code_format.setForeground(QColor("#ffffff"))
        else:
            # LIGHT: Textbereich #ffffff -> Codeblock #e0e0e0 (dunkler)
            self.code_format.setBackground(QColor("#e0e0e0"))
            self.code_format.setForeground(QColor("#000000"))
    
    def set_theme(self, is_dark):
        """Setzt das Theme und aktualisiert das Format."""
        if self.is_dark != is_dark:
            self.is_dark = is_dark
            self._update_format()
            # Neu formatieren, damit Änderungen sichtbar werden
            self.rehighlight()

    def highlightBlock(self, text: str) -> None:
        in_code = (self.previousBlockState() == self.STATE_CODE)

        # Wenn diese Zeile ein Fence ist, immer formatieren
        if self.fence_re.match(text).hasMatch():
            self.setFormat(0, len(text), self.code_format)
            # Toggle state
            self.setCurrentBlockState(self.STATE_NONE if in_code else self.STATE_CODE)
            return

        # Normale Zeilen: wenn wir im Codeblock sind -> formatieren
        if in_code:
            self.setFormat(0, len(text), self.code_format)
            self.setCurrentBlockState(self.STATE_CODE)
        else:
            self.setCurrentBlockState(self.STATE_NONE)
