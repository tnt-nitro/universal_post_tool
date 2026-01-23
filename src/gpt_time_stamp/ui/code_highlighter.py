from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
from PySide6.QtCore import QRegularExpression


class CodeBlockHighlighter(QSyntaxHighlighter):
    STATE_NONE = 0
    STATE_CODE = 1

    def __init__(self, document):
        super().__init__(document)

        self.code_format = QTextCharFormat()
        self.code_format.setBackground(QColor("#2b2b2b"))
        self.code_format.setForeground(QColor("#e6e6e6"))

        # WICHTIG: Exakt 3 Backticks (```) - nicht 2!
        self.fence_re = QRegularExpression(r"^\s*```\s*$")

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
