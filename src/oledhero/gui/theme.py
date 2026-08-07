BACKGROUND_COLOR = "#1b1b1b"
PANEL_COLOR = "#2b2b2b"
BORDER_COLOR = "#3a3a3a"
PRIMARY_TEXT_COLOR = "#f4f4f4"
MUTED_TEXT_COLOR = "#b7bcc5"

APP_STYLESHEET = f"""
QWidget#centralWidget {{
    background: {BACKGROUND_COLOR};
    color: {PRIMARY_TEXT_COLOR};
}}
QLabel#title {{
    font-size: 24px;
    font-weight: bold;
}}
QLabel#version {{
    color: {MUTED_TEXT_COLOR};
}}
QFrame#displaySettings {{
    background: {PANEL_COLOR};
    border: 1px solid {BORDER_COLOR};
    border-radius: 7px;
}}
QLabel#displaySettingsTitle {{
    font-size: 20px;
    font-weight: bold;
}}
QLabel#displaySettingsValue {{
    color: {MUTED_TEXT_COLOR};
}}
QStatusBar#statusBar {{
    background: {BACKGROUND_COLOR};
    border-top: 1px solid {PANEL_COLOR};
}}
"""
