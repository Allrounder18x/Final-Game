"""Shared dark theme and style helpers for all UI screens."""

# Unified palette: one dark system + one accent family (blue)
COLORS = {
    # Accent family
    'primary': '#3B82F6',
    'primary_light': '#60A5FA',
    'primary_dark': '#2563EB',
    'secondary': '#2563EB',
    'secondary_light': '#3B82F6',
    'secondary_dark': '#1D4ED8',
    'accent': '#3B82F6',
    'accent_light': '#60A5FA',

    # Dark surfaces
    'bg_primary': '#0B1220',     # app shell
    'bg_secondary': '#111827',   # cards/panels
    'bg_tertiary': '#1F2937',    # raised/alternate rows
    'bg_card': '#111827',
    'bg_hover': '#1E293B',

    # Typography (light-on-dark)
    'text_primary': '#EAF1FF',
    'text_secondary': '#B8C3D9',
    'text_disabled': '#6B7280',
    'text_accent': '#93C5FD',

    # Status colors
    'success': '#22C55E',
    'success_dark': '#16A34A',
    'warning': '#F59E0B',
    'danger': '#EF4444',
    'info': '#38BDF8',

    # Borders/dividers
    'border': '#334155',
    'border_light': '#475569',
    'border_focus': '#60A5FA',

    # Special
    'gold': '#FBBF24',
    'silver': '#C8D0DF',
    'bronze': '#B7791F',
    'grass': '#16A34A',
    'pitch': '#A78B6D',
    'boundary': '#EAF1FF',
    'highlight_blue': '#1E3A8A',
    'highlight_yellow': '#78350F',
    'highlight_green': '#14532D',
    'highlight_red': '#7F1D1D',
    'gray': '#94A3B8',
}

# Main Application Stylesheet - Sports Style
MAIN_STYLESHEET = f"""
/* ===== MAIN WINDOW ===== */
QMainWindow {{
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_primary']};
}}

QWidget {{
    color: {COLORS['text_primary']};
}}

/* ===== BUTTONS ===== */
QPushButton {{
    background-color: {COLORS['primary']};
    color: #FFFFFF;
    border: 1px solid {COLORS['border_light']};
    padding: 8px 14px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 700;
    min-width: 100px;
}}

QPushButton:hover {{
    background-color: {COLORS['primary_light']};
}}

QPushButton:pressed {{
    background-color: {COLORS['primary_dark']};
}}

QPushButton:disabled {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_disabled']};
}}

/* Secondary Button */
QPushButton[class="secondary"] {{
    background-color: {COLORS['secondary']};
}}

QPushButton[class="secondary"]:hover {{
    background-color: {COLORS['secondary_light']};
}}

/* Danger Button */
QPushButton[class="danger"] {{
    background-color: {COLORS['danger']};
}}

QPushButton[class="danger"]:hover {{
    background-color: #E53935;
}}

/* Success Button */
QPushButton[class="success"] {{
    background-color: {COLORS['success']};
}}

QPushButton[class="success"]:hover {{
    background-color: #66BB6A;
}}

/* ===== TABLE WIDGET ===== */
QTableWidget {{
    background-color: {COLORS['bg_secondary']};
    alternate-background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    gridline-color: {COLORS['border']};
    selection-background-color: {COLORS['primary_dark']};
    selection-color: #FFFFFF;
    font-size: 13px;
}}

QTableWidget::item {{
    padding: 10px;
    border: none;
}}

QTableWidget::item:hover {{
    background-color: {COLORS['bg_hover']};
}}

QTableWidget::item:selected {{
    background-color: {COLORS['primary']};
    color: white;
}}

QHeaderView::section {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_primary']};
    padding: 10px;
    border: none;
    border-right: 1px solid {COLORS['border']};
    font-weight: 700;
    font-size: 13px;
}}

QHeaderView::section:hover {{
    background-color: {COLORS['bg_hover']};
}}

/* ===== SCROLL BAR ===== */
QScrollBar:vertical {{
    background-color: {COLORS['bg_tertiary']};
    width: 14px;
    border-radius: 7px;
    margin: 2px;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS['primary']};
    border-radius: 7px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS['primary_light']};
}}

QScrollBar:horizontal {{
    background-color: {COLORS['bg_tertiary']};
    height: 14px;
    border-radius: 7px;
    margin: 2px;
}}

QScrollBar::handle:horizontal {{
    background-color: {COLORS['primary']};
    border-radius: 7px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {COLORS['primary_light']};
}}

QScrollBar::add-line, QScrollBar::sub-line {{
    border: none;
    background: none;
}}

/* ===== LINE EDIT ===== */
QLineEdit {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px;
    font-size: 13px;
}}

QLineEdit:focus {{
    border: 2px solid {COLORS['border_focus']};
}}

/* ===== LIST WIDGET ===== */
QListWidget {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    font-size: 13px;
}}

QListWidget::item {{
    padding: 10px;
    border-bottom: 1px solid {COLORS['border_light']};
}}

QListWidget::item:hover {{
    background-color: {COLORS['bg_hover']};
}}

QListWidget::item:selected {{
    background-color: {COLORS['primary']};
    color: white;
}}

/* ===== LABELS ===== */
QLabel {{
    color: {COLORS['text_primary']};
    font-size: 13px;
}}

QCheckBox, QRadioButton {{
    color: {COLORS['text_primary']};
}}

QLabel[class="title"] {{
    font-size: 28px;
    font-weight: 700;
    color: {COLORS['text_primary']};
    padding: 10px 0;
}}

QLabel[class="subtitle"] {{
    font-size: 18px;
    font-weight: 600;
    color: {COLORS['text_secondary']};
}}

QLabel[class="stat-value"] {{
    font-size: 32px;
    font-weight: 700;
    color: {COLORS['accent']};
}}

QLabel[class="stat-label"] {{
    font-size: 12px;
    color: {COLORS['text_secondary']};
    text-transform: uppercase;
    font-weight: 600;
}}

/* ===== GROUP BOX ===== */
QGroupBox {{
    background-color: {COLORS['bg_secondary']};
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
    margin-top: 16px;
    padding-top: 16px;
    font-weight: 700;
    font-size: 14px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 6px 16px;
    color: {COLORS['text_primary']};
    background-color: {COLORS['bg_tertiary']};
    border-radius: 6px;
    margin-left: 12px;
}}

/* ===== FRAME ===== */
QFrame[class="card"] {{
    background-color: {COLORS['bg_secondary']};
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
    padding: 20px;
}}

QFrame[class="stat-card"] {{
    background-color: {COLORS['bg_secondary']};
    border-left: 5px solid {COLORS['primary']};
    border-radius: 8px;
    padding: 20px;
}}

/* ===== DIALOG ===== */
QDialog {{
    background-color: {COLORS['bg_primary']};
}}

QComboBox {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 6px 10px;
}}
QComboBox::drop-down {{
    border: none;
    width: 20px;
}}
QComboBox QAbstractItemView {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    selection-background-color: {COLORS['primary_dark']};
}}

QToolTip {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border_light']};
    padding: 4px;
}}

/* ===== SCROLL AREA ===== */
QScrollArea {{
    background-color: transparent;
    border: none;
}}

QScrollArea > QWidget > QWidget {{
    background-color: transparent;
}}
"""

# Widget-specific styles
CARD_STYLE = f"""
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 16px;
"""

STAT_CARD_STYLE = f"""
    background-color: {COLORS['bg_card']};
    border-left: 4px solid {COLORS['primary']};
    border-radius: 4px;
    padding: 16px;
"""


def button_style(kind='primary'):
    base = COLORS['primary']
    hov = COLORS['primary_light']
    if kind == 'secondary':
        base = COLORS['bg_tertiary']
        hov = COLORS['bg_hover']
    elif kind == 'danger':
        base = COLORS['danger']
        hov = '#DC2626'
    elif kind == 'success':
        base = COLORS['success']
        hov = COLORS['success_dark']
    return (
        f"QPushButton {{ background-color: {base}; color: #FFFFFF; "
        f"border: 1px solid {COLORS['border_light']}; border-radius: 6px; "
        "padding: 8px 12px; font-size: 12px; font-weight: 700; } "
        f"QPushButton:hover {{ background-color: {hov}; }} "
        f"QPushButton:disabled {{ background-color: {COLORS['bg_tertiary']}; color: {COLORS['text_disabled']}; }}"
    )


def combo_style(min_w=120):
    return (
        f"QComboBox {{ background-color: {COLORS['bg_secondary']}; color: {COLORS['text_primary']}; "
        f"border: 1px solid {COLORS['border']}; border-radius: 6px; padding: 6px 10px; min-width: {min_w}px; }} "
        "QComboBox::drop-down { border: none; width: 20px; } "
        f"QComboBox QAbstractItemView {{ background-color: {COLORS['bg_secondary']}; color: {COLORS['text_primary']}; "
        f"border: 1px solid {COLORS['border']}; selection-background-color: {COLORS['primary_dark']}; }}"
    )


def card_style():
    return (
        f"background-color: {COLORS['bg_secondary']}; border: 1px solid {COLORS['border']}; "
        "border-radius: 8px;"
    )


def table_style():
    return (
        f"QTableWidget {{ background-color: {COLORS['bg_secondary']}; color: {COLORS['text_primary']}; "
        f"gridline-color: {COLORS['border']}; border: 1px solid {COLORS['border']}; border-radius: 8px; "
        f"selection-background-color: {COLORS['primary_dark']}; selection-color: #FFFFFF; }} "
        f"QHeaderView::section {{ background-color: {COLORS['bg_tertiary']}; color: {COLORS['text_primary']}; "
        f"border-right: 1px solid {COLORS['border']}; padding: 8px; font-weight: 700; }}"
    )


def dialog_style():
    return (
        f"QDialog {{ background-color: {COLORS['bg_primary']}; color: {COLORS['text_primary']}; }} "
        f"QLabel {{ color: {COLORS['text_primary']}; }} "
        f"QLineEdit {{ background-color: {COLORS['bg_secondary']}; color: {COLORS['text_primary']}; "
        f"border: 1px solid {COLORS['border']}; border-radius: 6px; padding: 6px; }}"
    )


def apply_main_theme(widget):
    """Apply the global dark stylesheet on any QWidget/QMainWindow/QDialog."""
    if widget is not None:
        widget.setStyleSheet(MAIN_STYLESHEET)
        apply_windows_dark_title_bar(widget)


def apply_windows_dark_title_bar(widget):
    """Enable dark native title bar on Windows 10/11 when available."""
    if widget is None:
        return
    try:
        import sys
        if not sys.platform.startswith("win"):
            return
        import ctypes
        hwnd = int(widget.winId())
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        val = ctypes.c_int(1)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            ctypes.c_void_p(hwnd),
            ctypes.c_uint(DWMWA_USE_IMMERSIVE_DARK_MODE),
            ctypes.byref(val),
            ctypes.sizeof(val),
        )
    except Exception:
        # Ignore if unsupported; app styles still apply.
        pass

TITLE_STYLE = f"""
    font-size: 24px;
    font-weight: 700;
    color: {COLORS['text_primary']};
    padding: 10px 0;
"""

SUBTITLE_STYLE = f"""
    font-size: 16px;
    font-weight: 600;
    color: {COLORS['text_secondary']};
"""

# Icon colors for different stats
STAT_COLORS = {
    'batting': COLORS['success'],
    'bowling': COLORS['info'],
    'fielding': COLORS['warning'],
    'allrounder': COLORS['accent'],
    'win': COLORS['success'],
    'loss': COLORS['danger'],
    'draw': COLORS['text_secondary'],
}

def get_skill_color(skill_value):
    """Get color based on skill value (0-100)"""
    if skill_value >= 85:
        return COLORS['gold']
    elif skill_value >= 70:
        return COLORS['success']
    elif skill_value >= 50:
        return COLORS['info']
    elif skill_value >= 30:
        return COLORS['warning']
    else:
        return COLORS['danger']

def get_form_color(form_value):
    """Get color based on form value (0-100)"""
    if form_value >= 80:
        return COLORS['success']
    elif form_value >= 60:
        return COLORS['info']
    elif form_value >= 40:
        return COLORS['warning']
    else:
        return COLORS['danger']

def get_tier_color(tier):
    """Get color based on tier (1-5)"""
    tier_colors = {
        1: COLORS['gold'],
        2: COLORS['silver'],
        3: COLORS['bronze'],
        4: COLORS['info'],
        5: COLORS['text_secondary']
    }
    return tier_colors.get(tier, COLORS['text_secondary'])
