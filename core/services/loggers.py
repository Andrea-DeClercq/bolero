#!/usr/bin/env python
"""
DOC
"""
# Import from stdlib
import logging
import traceback

# Imports from external libraries
from pygments import highlight, console
from pygments.lexers import get_lexer_by_name
from pygments.formatters.terminal256 import Terminal256Formatter, EscapeSequence

# Import from local code


class ColorTermFormatter(logging.Formatter):
    """
    Permet d'afficher de la couleur dans le terminal.
    Les traceback sont également plus lisibles.
    """

    def __init__(self, *args, **kwargs):
        # Récupération des styles ANSI depuis pygments
        self.styles = console.codes.copy()
        self.styles.pop("", None)
        # Pygments n'a pas inclus par défaut les codes pour les couleurs de background
        for color in console.dark_colors + console.light_colors:
            escape = EscapeSequence(bg="ansi%s" % color)
            self.styles["bg%s" % color] = escape.color_string()
        # Une couleur custom par niveau de log
        self.colors_mapping = {
            "DEBUG": self.styles["blue"],
            "WARNING": self.styles["yellow"],
            "ERROR": self.styles["red"],
            "CRITICAL": self.styles["white"] + self.styles["bgred"],
        }

        self.tb_lexer = get_lexer_by_name("py3tb")
        self.tb_formatter = Terminal256Formatter()
        super().__init__(*args, **kwargs)

    def format(self, record):
        # Injection (sans effet de bord) de la couleur custom par niveau de log
        styles = {"_%s_" % k: v for k, v in self.styles.items()}
        styles["_clog_"] = self.colors_mapping.get(record.levelname, "")
        record.__dict__.update(styles)
        return super().format(record)

    def formatException(self, exc_info):
        text = "".join(traceback.format_exception(*exc_info))
        text = highlight(text, self.tb_lexer, self.tb_formatter)
        return "\n%s" % text
