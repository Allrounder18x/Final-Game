"""
Team Selection Screen - First screen shown on game launch
PRO CRICKET MANAGER 2026 branding with team picker

Flow: pick an international (or U21) side, then choose either that national squad
or one of its domestic club teams.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QGridLayout, QStackedWidget,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage

from cricket_manager.ui.styles import MAIN_STYLESHEET


TIER_LABELS = {
    1: "Tier 1 - Full Members",
    2: "Tier 2 - Associate Elite",
    3: "Tier 3 - Associate",
    4: "Tier 4 - Affiliate",
}

TIER_COLORS = {
    1: "#FFD700",
    2: "#C0C0C0",
    3: "#CD7F32",
    4: "#8B8B8B",
}


def _nation_key_for_team(team):
    """Map international/U21 team name to parent nation used by domestic_teams (e.g. India U21 -> India)."""
    name = getattr(team, "name", "") or ""
    if name.endswith(" U21"):
        return name[:-4].strip()
    return name


class TeamSelectionScreen(QWidget):
    """Full-screen team selection: international list, then national vs domestic clubs for that nation."""

    team_selected = pyqtSignal(object)  # Emits the chosen Team object (international or domestic)

    def __init__(self, all_teams, domestic_teams=None):
        super().__init__()
        self.setStyleSheet(MAIN_STYLESHEET)
        self.all_teams = [t for t in (all_teams or []) if not getattr(t, "is_domestic", False)]
        self.domestic_teams = domestic_teams or []
        self.selected_team = None
        self._buttons = {}
        self._drill_team = None
        self._nation_button_style_pairs = []
        self._init_ui()

    # ------------------------------------------------------------------
    def _init_ui(self):
        root = QVBoxLayout()
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        self.setStyleSheet("background-color: #0a0a0a;")

        # ---- Top branding area with logo ----
        brand = QFrame()
        brand.setFixedHeight(240)
        brand.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0d3b1e, stop:0.5 #1a5c32, stop:1 #0d3b1e);
            }
        """)
        brand_layout = QVBoxLayout()
        brand_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        import os
        logo_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', '..', '..', 'logo cricket.jpg'
        ))

        print(f"[TeamSelection] Looking for logo at: {logo_path}")
        print(f"[TeamSelection] Logo exists: {os.path.exists(logo_path)}")
        print(f"[TeamSelection] International teams: {len(self.all_teams)}, domestic: {len(self.domestic_teams)}")

        logo_label = QLabel()
        if os.path.exists(logo_path):
            pixmap = self._load_logo_pixmap(logo_path)
            print(f"[TeamSelection] Logo loaded: {pixmap.width()}x{pixmap.height()}")
            scaled = pixmap.scaledToHeight(180, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled)
        else:
            logo_label.setText("PRO CRICKET MANAGER 2026")
            logo_label.setStyleSheet("font-size: 32px; font-weight: 900; color: #FFD700;")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("background: transparent;")
        brand_layout.addWidget(logo_label)

        tagline = QLabel("Select Your Team")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tagline.setStyleSheet("""
            font-size: 16px; color: #FFD700; margin-top: 8px;
            letter-spacing: 2px; background: transparent; font-weight: 600;
        """)
        brand_layout.addWidget(tagline)

        brand.setLayout(brand_layout)
        root.addWidget(brand)

        # ---- Stacked: (0) international tiers, (1) national vs domestic ----
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: #111;")

        # Page 0 — international only
        page_intl = QWidget()
        page_intl.setStyleSheet("background-color: #111;")
        intl_outer = QVBoxLayout(page_intl)
        intl_outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background-color: #111; }
            QScrollBar:vertical {
                background: #1a1a1a; width: 10px; border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #444; border-radius: 5px; min-height: 30px;
            }
        """)

        content = QWidget()
        content.setStyleSheet("background-color: #111;")
        self._intl_content_layout = QVBoxLayout()
        self._intl_content_layout.setSpacing(24)
        self._intl_content_layout.setContentsMargins(40, 24, 40, 24)

        hint = QLabel(
            "Tap a country or side to choose the national squad or a domestic team."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet(
            "font-size: 13px; color: #aaa; background: transparent; padding-bottom: 8px;"
        )
        self._intl_content_layout.addWidget(hint)

        tiers = {}
        for t in self.all_teams:
            tier = t.format_tiers.get("T20", t.format_tiers.get("ODI", 1))
            tiers.setdefault(tier, []).append(t)

        for tier_num in sorted(tiers.keys()):
            teams = sorted(tiers[tier_num], key=lambda t: t.name)
            label_text = TIER_LABELS.get(tier_num, f"Tier {tier_num}")
            tier_color = TIER_COLORS.get(tier_num, "#888")

            tier_label = QLabel(f"  {label_text}")
            tier_label.setStyleSheet(f"""
                font-size: 16px; font-weight: 700; color: {tier_color};
                padding: 8px 0 4px 0; background: transparent;
                border-bottom: 2px solid {tier_color};
            """)
            self._intl_content_layout.addWidget(tier_label)

            grid = QGridLayout()
            grid.setSpacing(12)
            cols = 6
            for idx, team in enumerate(teams):
                card = self._make_international_card(team, tier_color)
                grid.addWidget(card, idx // cols, idx % cols)

            grid_widget = QWidget()
            grid_widget.setLayout(grid)
            grid_widget.setStyleSheet("background: transparent;")
            self._intl_content_layout.addWidget(grid_widget)

        self._intl_content_layout.addStretch()
        content.setLayout(self._intl_content_layout)
        scroll.setWidget(content)
        intl_outer.addWidget(scroll)
        self.stack.addWidget(page_intl)

        # Page 1 — national + domestic clubs
        self.page_nation = QWidget()
        self.page_nation.setStyleSheet("background-color: #111;")
        self._nation_outer_layout = QVBoxLayout(self.page_nation)
        self._nation_outer_layout.setContentsMargins(40, 24, 40, 24)
        self._nation_outer_layout.setSpacing(16)
        self.stack.addWidget(self.page_nation)

        root.addWidget(self.stack, 1)

        # ---- Bottom confirm bar ----
        bottom = QFrame()
        bottom.setFixedHeight(70)
        bottom.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border-top: 1px solid #333;
            }
        """)
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(40, 0, 40, 0)

        self.selection_label = QLabel("Select an international team to continue")
        self.selection_label.setStyleSheet("font-size: 15px; color: #888; background: transparent;")
        bottom_layout.addWidget(self.selection_label)

        bottom_layout.addStretch()

        self.confirm_btn = QPushButton("  START GAME  ")
        self.confirm_btn.setEnabled(False)
        self.confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #2E7D32; color: white;
                font-size: 16px; font-weight: 700; padding: 12px 40px;
                border-radius: 6px; border: none; letter-spacing: 2px;
            }
            QPushButton:hover { background-color: #388E3C; }
            QPushButton:disabled { background-color: #444; color: #777; }
        """)
        self.confirm_btn.clicked.connect(self._on_confirm)
        bottom_layout.addWidget(self.confirm_btn)

        bottom.setLayout(bottom_layout)
        root.addWidget(bottom)

        self.setLayout(root)

    # ------------------------------------------------------------------
    def _load_logo_pixmap(self, path):
        """Load logo and remove near-white background for seamless blending."""
        pixmap = QPixmap(path)
        if pixmap.isNull():
            return pixmap

        image = pixmap.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        width, height = image.width(), image.height()
        for y in range(height):
            for x in range(width):
                color = image.pixelColor(x, y)
                if color.red() > 245 and color.green() > 245 and color.blue() > 245:
                    color.setAlpha(0)
                    image.setPixelColor(x, y, color)

        return QPixmap.fromImage(image)

    # ------------------------------------------------------------------
    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
            else:
                sub = item.layout()
                if sub is not None:
                    self._clear_layout(sub)
                    sub.deleteLater()

    def _make_international_card(self, team, tier_color):
        btn = QPushButton(team.name)
        btn.setFixedSize(170, 52)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        base = "#1565C0"
        border = "#1976D2"
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {base}; color: white;
                font-size: 12px; font-weight: 600;
                border: 2px solid {border}; border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {border}; border-color: #FFD700;
                color: #FFD700;
            }}
        """)
        btn.clicked.connect(lambda checked, t=team, c=tier_color: self._on_international_clicked(t, c))
        self._buttons[team.name] = btn
        return btn

    def _on_international_clicked(self, team, tier_color):
        self._drill_team = team
        self._build_nation_choice_page()
        self.stack.setCurrentIndex(1)
        self.selected_team = None
        self.confirm_btn.setEnabled(False)
        self.selection_label.setText(f"Choose national or domestic squad for {team.name}")
        self.selection_label.setStyleSheet("font-size: 15px; color: #ccc; font-weight: 600; background: transparent;")

    def _build_nation_choice_page(self):
        self._clear_layout(self._nation_outer_layout)
        self._nation_button_style_pairs.clear()

        team = self._drill_team
        if not team:
            return

        nation_key = _nation_key_for_team(team)
        domestic_for_nation = [
            t for t in self.domestic_teams
            if getattr(t, "parent_nation", None) == nation_key
        ]
        domestic_for_nation.sort(key=lambda t: t.name)

        back_row = QHBoxLayout()
        back_btn = QPushButton("←  All nations")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #37474F; color: white;
                font-size: 13px; font-weight: 600; padding: 10px 20px;
                border-radius: 6px; border: none;
            }
            QPushButton:hover { background-color: #455A64; color: #FFD700; }
        """)
        back_btn.clicked.connect(self._on_back_to_international)
        back_row.addWidget(back_btn)
        back_row.addStretch()
        self._nation_outer_layout.addLayout(back_row)

        title = QLabel(f"Choose your team — {team.name}")
        title.setStyleSheet(
            "font-size: 20px; font-weight: 800; color: #FFD700; background: transparent;"
        )
        title.setWordWrap(True)
        self._nation_outer_layout.addWidget(title)

        sub = QLabel(
            "Play as the national squad listed below, or pick a domestic club from this country."
        )
        sub.setWordWrap(True)
        sub.setStyleSheet("font-size: 13px; color: #aaa; background: transparent;")
        self._nation_outer_layout.addWidget(sub)

        nat_btn = QPushButton(f"★  National team: {team.name}")
        nat_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        nat_btn.setMinimumHeight(56)
        nat_default_qss = """
            QPushButton {
                background-color: #0D47A1; color: #FFD700;
                font-size: 14px; font-weight: 700;
                border: 2px solid #FFD700; border-radius: 8px;
            }
            QPushButton:hover { background-color: #1565C0; }
        """
        nat_btn.setStyleSheet(nat_default_qss)
        nat_btn.clicked.connect(lambda checked, t=team: self._select_final_team(t, is_domestic=False))
        self._nation_outer_layout.addWidget(nat_btn)
        self._nation_button_style_pairs.append((nat_btn, nat_default_qss))

        if domestic_for_nation:
            dom_header = QLabel(f"Domestic teams ({nation_key}) — {len(domestic_for_nation)} clubs")
            dom_header.setStyleSheet(
                "font-size: 15px; font-weight: 700; color: #4CAF50; margin-top: 12px; background: transparent;"
            )
            self._nation_outer_layout.addWidget(dom_header)

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("QScrollArea { border: none; background: #111; }")
            inner = QWidget()
            inner.setStyleSheet("background: #111;")
            grid = QGridLayout()
            grid.setSpacing(12)
            cols = 5
            dom_default_qss = """
                QPushButton {
                    background-color: #2E7D32; color: white;
                    font-size: 12px; font-weight: 600;
                    border: 2px solid #4CAF50; border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #4CAF50; border-color: #FFD700; color: #FFD700;
                }
            """
            for idx, dt in enumerate(domestic_for_nation):
                btn = QPushButton(dt.name)
                btn.setFixedSize(200, 52)
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.setStyleSheet(dom_default_qss)
                btn.clicked.connect(lambda checked, d=dt: self._select_final_team(d, is_domestic=True))
                grid.addWidget(btn, idx // cols, idx % cols)
                self._nation_button_style_pairs.append((btn, dom_default_qss))
            inner.setLayout(grid)
            scroll.setWidget(inner)
            self._nation_outer_layout.addWidget(scroll, 1)
        else:
            note = QLabel(
                f"No domestic league teams are set up for {nation_key} in this save. "
                "You can still play as the national side above."
            )
            note.setWordWrap(True)
            note.setStyleSheet("font-size: 12px; color: #888; background: transparent; padding: 8px 0;")
            self._nation_outer_layout.addWidget(note)

        self._nation_outer_layout.addStretch()

    def _on_back_to_international(self):
        self.stack.setCurrentIndex(0)
        self._drill_team = None
        self.selected_team = None
        self.confirm_btn.setEnabled(False)
        self.selection_label.setText("Select an international team to continue")
        self.selection_label.setStyleSheet("font-size: 15px; color: #888; background: transparent;")

    def _select_final_team(self, team, is_domestic=False):
        self.selected_team = team
        for btn, qss in self._nation_button_style_pairs:
            btn.setStyleSheet(qss)
        sender = self.sender()
        if sender and isinstance(sender, QPushButton):
            if is_domestic:
                sender.setStyleSheet("""
                    QPushButton {
                        background-color: #1B5E20; color: #FFD700;
                        font-size: 12px; font-weight: 700;
                        border: 3px solid #FFD700; border-radius: 8px;
                    }
                """)
            else:
                sender.setStyleSheet("""
                    QPushButton {
                        background-color: #0D47A1; color: #FFD700;
                        font-size: 14px; font-weight: 700;
                        border: 3px solid #FFD700; border-radius: 8px;
                    }
                """)
        if is_domestic:
            nat = getattr(team, "parent_nation", "") or ""
            self.selection_label.setText(f"Selected: {team.name} ({nat}) — Domestic club")
        else:
            tier = team.format_tiers.get("T20", 1)
            self.selection_label.setText(f"Selected: {team.name} (Tier {tier} — National squad)")
        self.selection_label.setStyleSheet(
            "font-size: 15px; color: #FFD700; font-weight: 700; background: transparent;"
        )
        self.confirm_btn.setEnabled(True)

    def _on_confirm(self):
        if self.selected_team:
            self.team_selected.emit(self.selected_team)
