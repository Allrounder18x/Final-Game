"""
Training Screen - Beautiful modern player training interface
"""

import random
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QScrollArea,
    QMessageBox, QDialog, QDialogButtonBox, QProgressBar, QGridLayout,
    QComboBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from cricket_manager.ui.styles import COLORS, MAIN_STYLESHEET
from cricket_manager.ui.screen_manager import BaseScreen


# Skill bar color thresholds
def _skill_color(val):
    if val >= 85:
        return '#2E7D32'
    elif val >= 70:
        return '#1976D2'
    elif val >= 50:
        return '#F57C00'
    else:
        return '#C62828'


def _age_badge(age):
    if age < 25:
        return ('Young', '#4CAF50')
    elif age <= 30:
        return ('Prime', '#1976D2')
    elif age <= 35:
        return ('Veteran', '#FF9800')
    else:
        return ('Old', '#F44336')


class TrainingScreen(BaseScreen):
    """Full-screen view for player training with modern card-based UI"""

    back_clicked = pyqtSignal()

    def __init__(self, screen_manager=None, game_engine=None):
        super().__init__(screen_manager)
        self.setStyleSheet(MAIN_STYLESHEET)
        self.game_engine = game_engine
        self.team = game_engine.user_team if game_engine else None
        self.training_system = game_engine.training_system if game_engine else None
        self._init_ui()

    # ------------------------------------------------------------------
    # UI SETUP
    # ------------------------------------------------------------------
    def _init_ui(self):
        root = QVBoxLayout()
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # ── Header ──
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1B4332, stop:1 #2D6A4F);
            }
        """)
        header.setFixedHeight(100)
        h_lay = QHBoxLayout()
        h_lay.setContentsMargins(30, 0, 30, 0)

        # Team dropdown — select any team to train its players
        h_lay.addWidget(QLabel("Team:"))
        self.team_combo = QComboBox()
        self.team_combo.setMinimumWidth(180)
        self.team_combo.setStyleSheet("""
            QComboBox {
                background: rgba(255,255,255,0.2); color: white;
                font-size: 14px; font-weight: 600;
                padding: 8px 12px; border: 1px solid rgba(255,255,255,0.4);
                border-radius: 6px; min-height: 20px;
            }
            QComboBox:hover { background: rgba(255,255,255,0.25); }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView { background: #111827; color: #B8C3D9; }
        """)
        self._populate_team_combo()
        self.team_combo.currentIndexChanged.connect(self._on_team_selected)
        h_lay.addWidget(self.team_combo)
        h_lay.addSpacing(20)

        self.title_label = QLabel(f"🎯  {self.team.name if self.team else ''} Training Center")
        self.title_label.setStyleSheet("font-size: 26px; font-weight: 800; color: white; background: transparent;")
        h_lay.addWidget(self.title_label)

        h_lay.addStretch()

        # Points badge
        pts = self.training_system.get_training_points(self.team) if self.training_system and self.team else 0
        self.points_label = QLabel(f"⚡ {pts} Training Points")
        self.points_label.setStyleSheet("""
            font-size: 16px; font-weight: 700; color: #FFD700;
            background-color: rgba(0,0,0,0.3); padding: 10px 24px;
            border-radius: 8px;
        """)
        h_lay.addWidget(self.points_label)

        header.setLayout(h_lay)
        root.addWidget(header)

        # ── Stats summary row ──
        self.stats_row = QFrame()
        self.stats_row.setFixedHeight(70)
        self.stats_row.setStyleSheet("background-color: #111827; border-bottom: 1px solid #e0e0e0;")
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setContentsMargins(30, 0, 30, 0)
        self.stats_layout.setSpacing(40)
        self.stats_row.setLayout(self.stats_layout)
        root.addWidget(self.stats_row)

        # ── Scrollable player cards ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{ border: none; background-color: {COLORS['bg_primary']}; }}
            QScrollBar:vertical {{ background: #f0f0f0; width: 8px; }}
            QScrollBar::handle:vertical {{ background: #bbb; border-radius: 4px; min-height: 30px; }}
        """)

        self.cards_container = QWidget()
        self.cards_container.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
        self.cards_layout = QVBoxLayout()
        self.cards_layout.setSpacing(10)
        self.cards_layout.setContentsMargins(30, 20, 30, 20)
        self.cards_container.setLayout(self.cards_layout)
        scroll.setWidget(self.cards_container)
        root.addWidget(scroll, 1)

        self.setLayout(root)
        self._populate()

    def _populate_team_combo(self):
        """Fill team dropdown with all teams and select current team."""
        if not self.game_engine or not hasattr(self, 'team_combo'):
            return
        self.team_combo.blockSignals(True)
        self.team_combo.clear()
        for t in self.game_engine.all_teams:
            self.team_combo.addItem(t.name, t)
        # Select current team (user_team by default)
        idx = next((i for i, t in enumerate(self.game_engine.all_teams) if t is self.team), 0)
        self.team_combo.setCurrentIndex(max(0, idx))
        self.team_combo.blockSignals(False)

    def _on_team_selected(self, index):
        """Switch to the selected team and refresh squad and points."""
        if index < 0 or not hasattr(self, 'team_combo'):
            return
        self.team = self.team_combo.currentData()
        if not self.team:
            return
        if hasattr(self, 'title_label'):
            self.title_label.setText(f"🎯  {self.team.name} Training Center")
        self._refresh_points()
        self._populate()

    # ------------------------------------------------------------------
    def _populate(self):
        if not self.team:
            return

        # ── Stats summary ──
        while self.stats_layout.count():
            child = self.stats_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        squad = self.team.players
        avg_bat = sum(p.batting for p in squad) / len(squad) if squad else 0
        avg_bowl = sum(p.bowling for p in squad) / len(squad) if squad else 0
        avg_field = sum(p.fielding for p in squad) / len(squad) if squad else 0
        avg_age = sum(p.age for p in squad) / len(squad) if squad else 0

        for label, val, color in [
            ("Squad Size", str(len(squad)), COLORS['primary']),
            ("Avg Batting", f"{avg_bat:.1f}", '#1976D2'),
            ("Avg Bowling", f"{avg_bowl:.1f}", '#E91E63'),
            ("Avg Fielding", f"{avg_field:.1f}", '#FF9800'),
            ("Avg Age", f"{avg_age:.1f}", '#666'),
        ]:
            w = QLabel(f"<span style='font-size:11px;color:#888;'>{label}</span><br>"
                        f"<span style='font-size:18px;font-weight:700;color:{color};'>{val}</span>")
            w.setStyleSheet("background: transparent;")
            self.stats_layout.addWidget(w)
        self.stats_layout.addStretch()

        # ── Player cards ──
        while self.cards_layout.count():
            child = self.cards_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Section header
        sec = QLabel(f"👥  Squad — {len(squad)} Players")
        sec.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {COLORS['text_primary']}; padding: 4px 0;")
        self.cards_layout.addWidget(sec)

        for player in squad:
            card = self._make_player_card(player)
            self.cards_layout.addWidget(card)

        self.cards_layout.addStretch()

    # ------------------------------------------------------------------
    def _make_player_card(self, player):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #111827;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            QFrame:hover {
                border-color: #4CAF50;
            }
        """)
        lay = QHBoxLayout()
        lay.setContentsMargins(16, 10, 16, 10)
        lay.setSpacing(16)

        # Name (age) + role
        age_text, age_color = _age_badge(player.age)
        info = QVBoxLayout()
        info.setSpacing(2)
        name_lbl = QLabel(f"{player.name} ({player.age})")
        name_lbl.setStyleSheet("font-size: 14px; font-weight: 700; color: #EAF1FF;")
        name_lbl.setMinimumWidth(180)
        info.addWidget(name_lbl)
        role_lbl = QLabel(player.role)
        role_lbl.setStyleSheet("font-size: 11px; color: #888;")
        info.addWidget(role_lbl)
        lay.addLayout(info)

        # Skill bars (hide BAT/BOWL when setting is on)
        hide_bat_bowl = getattr(self.game_engine, 'hide_batting_bowling_ratings', False) if self.game_engine else False
        skill_list = [("FIELD", player.fielding)]
        if not hide_bat_bowl:
            skill_list = [("BAT", player.batting), ("BOWL", player.bowling)] + skill_list
        for skill_name, skill_val in skill_list:
            sk_lay = QVBoxLayout()
            sk_lay.setSpacing(1)
            sk_label = QLabel(f"{skill_name}  {skill_val}")
            sk_label.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {_skill_color(skill_val)};")
            sk_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sk_lay.addWidget(sk_label)
            bar = QProgressBar()
            bar.setRange(0, 99)
            bar.setValue(skill_val)
            bar.setTextVisible(False)
            bar.setFixedSize(80, 6)
            bar.setStyleSheet(f"""
                QProgressBar {{ background-color: #e0e0e0; border-radius: 3px; border: none; }}
                QProgressBar::chunk {{ background-color: {_skill_color(skill_val)}; border-radius: 3px; }}
            """)
            sk_lay.addWidget(bar, alignment=Qt.AlignmentFlag.AlignCenter)
            lay.addLayout(sk_lay)

        lay.addStretch()

        # Train button
        train_btn = QPushButton("🎯 Train")
        train_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        train_btn.setFixedSize(90, 36)
        train_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']}; color: white;
                font-size: 12px; font-weight: 700; border: none; border-radius: 6px;
            }}
            QPushButton:hover {{ background-color: #388E3C; }}
        """)
        train_btn.clicked.connect(lambda checked, p=player: self._on_train(p))
        lay.addWidget(train_btn)

        card.setLayout(lay)
        return card

    # ------------------------------------------------------------------
    # ACTIONS
    # ------------------------------------------------------------------
    def _on_train(self, player):
        if self.training_system.get_training_points(self.team) <= 0:
            QMessageBox.warning(self, "No Training Points",
                                "Your team has no training points remaining.\n"
                                "Training points reset at the start of each season.")
            return

        dialog = TrainingDialog(self, player, self.team, self.training_system)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._refresh_points()
            self._populate()

    def _refresh_points(self):
        pts = self.training_system.get_training_points(self.team) if self.training_system and self.team else 0
        self.points_label.setText(f"⚡ {pts} Training Points")

    def on_back(self):
        self.back_clicked.emit()

    def refresh_data(self):
        if self.game_engine:
            new_team = self.game_engine.user_team
            if new_team:
                self.team = new_team
                self._populate_team_combo()
                if hasattr(self, 'title_label'):
                    self.title_label.setText(f"🎯  {self.team.name} Training Center")
                self._refresh_points()
                self._populate()


# ======================================================================
# TRAINING DIALOG
# ======================================================================
class TrainingDialog(QDialog):
    """Modern dialog for training a specific player"""

    def __init__(self, parent, player, team, training_system):
        super().__init__(parent)
        self.player = player
        self.team = team
        self.training_system = training_system
        self.setWindowTitle(f"Train — {player.name}")
        self.setModal(True)
        self.setMinimumSize(550, 520)
        self.setMaximumHeight(650)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        hdr = QFrame()
        hdr.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #1B4332, stop:1 #2D6A4F);
            }
        """)
        hdr.setFixedHeight(80)
        hdr_lay = QVBoxLayout()
        hdr_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_lbl = QLabel(self.player.name)
        name_lbl.setStyleSheet("font-size: 22px; font-weight: 800; color: white; background: transparent;")
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hdr_lay.addWidget(name_lbl)
        age_text, age_color = _age_badge(self.player.age)
        sub = QLabel(f"{self.player.role}  •  Age {self.player.age} ({age_text})")
        sub.setStyleSheet("font-size: 12px; color: #ccc; background: transparent;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hdr_lay.addWidget(sub)
        hdr.setLayout(hdr_lay)
        layout.addWidget(hdr)

        # Scroll content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: #0B1220;")

        content = QWidget()
        content.setStyleSheet("background: #0B1220;")
        c_lay = QVBoxLayout()
        c_lay.setSpacing(12)
        c_lay.setContentsMargins(20, 16, 20, 16)

        # Skills section (hide batting/bowling when setting is on)
        engine = getattr(self.parent(), 'game_engine', None) if self.parent() else None
        hide_bat_bowl = getattr(engine, 'hide_batting_bowling_ratings', False) if engine else False
        skills_to_show = ['fielding'] if hide_bat_bowl else ['batting', 'bowling', 'fielding']
        c_lay.addWidget(QLabel("<b style='font-size:14px;color:#B8C3D9;'>📊 Skill Training</b>"))
        for skill in skills_to_show:
            self._add_skill_card(c_lay, skill)

        # Traits section
        c_lay.addWidget(QLabel("<b style='font-size:14px;color:#B8C3D9;'>⭐ Trait Training</b>"))
        if hasattr(self.player, 'traits') and len(self.player.traits) > 0:
            for trait in self.player.traits:
                self._add_trait_card(c_lay, trait)
        else:
            lbl = QLabel("No traits to train.")
            lbl.setStyleSheet("font-size: 12px; color: #999; font-style: italic; padding: 8px;")
            c_lay.addWidget(lbl)

        c_lay.addStretch()
        content.setLayout(c_lay)
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        # Close button
        btn_bar = QFrame()
        btn_bar.setStyleSheet("background: #111827; border-top: 1px solid #ddd;")
        btn_bar.setFixedHeight(50)
        bb_lay = QHBoxLayout()
        bb_lay.setContentsMargins(20, 0, 20, 0)
        bb_lay.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(f"""
            QPushButton {{ background: {COLORS['primary']}; color: white; padding: 8px 30px;
                           border: none; border-radius: 5px; font-weight: 700; }}
            QPushButton:hover {{ background: #388E3C; }}
        """)
        close_btn.clicked.connect(self.reject)
        bb_lay.addWidget(close_btn)
        btn_bar.setLayout(bb_lay)
        layout.addWidget(btn_bar)

        self.setLayout(layout)

    def _add_skill_card(self, parent_layout, skill_type):
        info = self.training_system.get_training_info(self.player, skill_type)
        if not info:
            return

        card = QFrame()
        card.setStyleSheet("background: #111827; border-radius: 6px; border: 1px solid #e0e0e0;")
        lay = QHBoxLayout()
        lay.setContentsMargins(14, 10, 14, 10)

        # Left: skill info
        left = QVBoxLayout()
        left.setSpacing(2)
        sk_lbl = QLabel(f"{skill_type.title()}")
        sk_lbl.setStyleSheet("font-size: 14px; font-weight: 700; color: #B8C3D9;")
        left.addWidget(sk_lbl)

        val = info['current_skill']
        bar = QProgressBar()
        bar.setRange(0, 99)
        bar.setValue(val)
        bar.setFormat(f"{val}")
        bar.setFixedHeight(14)
        bar.setStyleSheet(f"""
            QProgressBar {{ background: #e0e0e0; border-radius: 7px; border: none; text-align: center; font-size: 10px; font-weight: 700; color: white; }}
            QProgressBar::chunk {{ background: {_skill_color(val)}; border-radius: 7px; }}
        """)
        left.addWidget(bar)

        rate_lbl = QLabel(f"Success: {info['success_percentage']}%  •  {info['age_category'].title()} / {info['skill_category'].title()}")
        rate_lbl.setStyleSheet("font-size: 10px; color: #999;")
        left.addWidget(rate_lbl)
        lay.addLayout(left, 1)

        # Right: button
        if info['at_maximum']:
            mx = QLabel("✓ MAX")
            mx.setStyleSheet(f"font-size: 12px; font-weight: 700; color: {COLORS['success']};")
            lay.addWidget(mx)
        else:
            btn = QPushButton(f"Train (1 pt)")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedSize(90, 32)
            btn.setStyleSheet(f"""
                QPushButton {{ background: {COLORS['primary']}; color: white; font-size: 11px;
                               font-weight: 700; border: none; border-radius: 5px; }}
                QPushButton:hover {{ background: #388E3C; }}
            """)
            btn.clicked.connect(lambda checked, s=skill_type: self._train_skill(s))
            lay.addWidget(btn)

        card.setLayout(lay)
        parent_layout.addWidget(card)

    def _add_trait_card(self, parent_layout, trait):
        from player_traits import POSITIVE_TRAITS, NEGATIVE_TRAITS

        if isinstance(trait, dict):
            trait_key = trait.get('name', '')
            trait_strength = trait.get('strength', 1)
        else:
            trait_key = str(trait)
            trait_strength = 1

        trait_info = POSITIVE_TRAITS.get(trait_key, NEGATIVE_TRAITS.get(trait_key, {}))
        display_name = trait_info.get('name', trait_key.replace('_', ' ').title())
        desc = trait_info.get('description', '')

        card = QFrame()
        card.setStyleSheet("background: #111827; border-radius: 6px; border: 1px solid #C8E6C9;")
        lay = QHBoxLayout()
        lay.setContentsMargins(14, 10, 14, 10)

        left = QVBoxLayout()
        left.setSpacing(2)
        t_lbl = QLabel(f"⭐ {display_name}  (Lv. {trait_strength})")
        t_lbl.setStyleSheet("font-size: 13px; font-weight: 700; color: #2E7D32;")
        left.addWidget(t_lbl)
        if desc:
            d_lbl = QLabel(desc)
            d_lbl.setStyleSheet("font-size: 10px; color: #888;")
            d_lbl.setWordWrap(True)
            left.addWidget(d_lbl)
        lay.addLayout(left, 1)

        btn = QPushButton("Upgrade (1 pt)")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedSize(100, 32)
        btn.setStyleSheet(f"""
            QPushButton {{ background: #2D6A4F; color: white; font-size: 11px;
                           font-weight: 700; border: none; border-radius: 5px; }}
            QPushButton:hover {{ background: #388E3C; }}
        """)
        btn.clicked.connect(lambda checked, t=trait: self._train_trait(t))
        lay.addWidget(btn)

        card.setLayout(lay)
        parent_layout.addWidget(card)

    # ------------------------------------------------------------------
    def _train_skill(self, skill_type):
        if not self.training_system.use_training_point(self.team):
            QMessageBox.warning(self, "No Points", "No training points available!")
            return

        success, old_value, new_value, message = self.training_system.train_player(self.player, skill_type)
        pts = self.training_system.get_training_points(self.team)

        if success:
            QMessageBox.information(self, "Training Success! 🎉",
                                    f"{message}\n\n{skill_type.title()}: {old_value} → {new_value}\n\nPoints remaining: {pts}")
        else:
            QMessageBox.information(self, "Training Failed",
                                    f"{message}\n\nPoints remaining: {pts}")
        self.accept()

    def _train_trait(self, trait):
        from player_traits import POSITIVE_TRAITS, NEGATIVE_TRAITS

        if isinstance(trait, dict):
            trait_key = trait.get('name', '')
        else:
            trait_key = str(trait)
        trait_info = POSITIVE_TRAITS.get(trait_key, NEGATIVE_TRAITS.get(trait_key, {}))
        display_name = trait_info.get('name', trait_key.replace('_', ' ').title())

        if not self.training_system.use_training_point(self.team):
            QMessageBox.warning(self, "No Points", "No training points available!")
            return

        success = random.random() < 0.5
        pts = self.training_system.get_training_points(self.team)

        if success:
            QMessageBox.information(self, "Trait Upgraded! 🎉",
                                    f"'{display_name}' effectiveness increased by 10%.\n\nPoints remaining: {pts}")
        else:
            QMessageBox.information(self, "Upgrade Failed",
                                    f"Failed to upgrade '{display_name}'.\n\nPoints remaining: {pts}")
        self.accept()
