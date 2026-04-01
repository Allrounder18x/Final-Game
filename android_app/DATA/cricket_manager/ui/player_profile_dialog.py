"""
Phase 14: Comprehensive Player Profile Dialog
Cricinfo-style detailed player profile with season-by-season statistics
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QTableWidget, QTableWidgetItem, QPushButton,
    QScrollArea, QFrame, QGridLayout, QHeaderView, QMessageBox, QComboBox,
    QSizePolicy, QApplication,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor

from cricket_manager.config.colors import COLORS, get_format_color, get_tier_color
from cricket_manager.ui.styles import MAIN_STYLESHEET
from cricket_manager.utils.constants import MAX_SQUAD_SIZE
from cricket_manager.ui.rankings_view import (
    player_profile_career_ranking_chips,
    player_profile_rankings_tab_tables,
)
from cricket_manager.utils.career_history_article import build_career_history_article


class PlayerProfileDialog(QDialog):
    """
    Comprehensive player profile dialog with Cricinfo-style layout
    
    Features:
    - Overview tab with basic info and current stats
    - Career Stats tab with season-by-season breakdown (last 20 seasons)
    - Traits & Development tab showing trait history
    - Milestones tab with career achievements
    """
    
    def __init__(self, parent, player, team, game_engine=None):
        super().__init__(None)
        self.setStyleSheet(MAIN_STYLESHEET)
        self.player = player
        self.game_engine = game_engine
        self.team = self._resolve_profile_team(player, team)
        self._opener_parent = parent
        
        self.setWindowTitle(f"{getattr(player, 'name', 'Player')} - Player Profile")
        self.setMinimumWidth(800)
        self.setMinimumHeight(500)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        self.init_ui()
    
    def _resolve_profile_team(self, player, preferred_team):
        """
        Use the Team object that actually lists this player (senior or U21).
        Callers sometimes pass the wrong squad (e.g. national side while the player is only on a domestic club),
        which hid squad actions. Prefer the real roster; fall back to preferred_team.
        """
        ge = self.game_engine
        if ge is None:
            return preferred_team
        
        pname = (getattr(player, "name", "") or "").strip()

        def _has_player_by_name(pool):
            if not pname:
                return False
            for p in (pool or []):
                if (getattr(p, "name", "") or "").strip() == pname:
                    return True
            return False

        def _bind_player_instance_from_team(team):
            """If profile got a detached player instance, rebind to roster instance by name."""
            if not team or not pname:
                return
            for p in (getattr(team, "players", []) or []):
                if (getattr(p, "name", "") or "").strip() == pname:
                    self.player = p
                    return
            for p in (getattr(team, "u21_squad", []) or []):
                if (getattr(p, "name", "") or "").strip() == pname:
                    self.player = p
                    return

        def player_on_team(team):
            if not team:
                return False
            if player in getattr(team, "players", []) or []:
                return True
            if player in getattr(team, "u21_squad", []) or []:
                return True
            # Fallback for save/load paths where profile gets a different player instance.
            if _has_player_by_name(getattr(team, "players", []) or []):
                return True
            if _has_player_by_name(getattr(team, "u21_squad", []) or []):
                return True
            return False

        def player_on_senior_list(team):
            """True only when player is on team's senior squad list (not U21)."""
            if not team:
                return False
            if player in getattr(team, "players", []) or []:
                return True
            return _has_player_by_name(getattr(team, "players", []) or [])
        
        # Priority 1: if player is on any national senior squad, always use that context.
        for t in ge.all_teams:
            if getattr(t, "is_domestic", False):
                continue
            if player_on_senior_list(t):
                _bind_player_instance_from_team(t)
                return t

        # Priority 2: use caller-provided context when valid.
        if preferred_team and player_on_team(preferred_team):
            _bind_player_instance_from_team(preferred_team)
            return preferred_team

        # Priority 3: any national/U21 context.
        for t in ge.all_teams:
            if player_on_team(t):
                _bind_player_instance_from_team(t)
                return t

        # Priority 4: domestic context fallback.
        for t in getattr(ge, "domestic_teams", []) or []:
            if player_on_team(t):
                _bind_player_instance_from_team(t)
                return t
        return preferred_team
    
    def _refresh_profile_action_buttons(self):
        """Enable/disable squad actions and set tooltips (buttons are always visible)."""
        self._btn_promote_national.setEnabled(self._can_promote_to_national_squad())
        self._btn_promote_national.setToolTip(self._tooltip_promote_to_national_squad())
        self._btn_promote_domestic.setEnabled(self._can_promote_u21_to_domestic())
        self._btn_promote_domestic.setToolTip(self._tooltip_promote_u21_to_domestic())
        self._btn_move_associate.setEnabled(self._can_move_to_associate())
        self._btn_move_associate.setToolTip(self._tooltip_move_associate())
        self._btn_back_national.setEnabled(self._can_return_to_national())
        self._btn_back_national.setToolTip(self._tooltip_back_national())
        self._btn_send_domestic.setEnabled(self._can_send_back_to_domestic())
        self._btn_send_domestic.setToolTip(self._tooltip_send_domestic())
        self._btn_u21_stats.setEnabled(True)
        self._btn_u21_stats.setToolTip(
            "Frozen U21 career totals (if any). Still in U21? A snapshot is saved when they leave youth cricket."
        )
    
    def _can_promote_u21_action(self):
        if not self._is_u21_player() or not self.team:
            return False
        return len(getattr(self.team, "players", []) or []) < MAX_SQUAD_SIZE
    
    def _tooltip_promote_u21(self):
        if self._can_promote_u21_action():
            return ""
        if not self.game_engine:
            return "Game not loaded."
        if not self.team:
            return "No team context."
        if not self._is_u21_player():
            return "Only players listed in a national U21 squad can be promoted to the senior squad."
        return f"Senior squad is full (max {MAX_SQUAD_SIZE}). Release a player first."
    
    def _tooltip_promote_national(self):
        if self._can_promote_domestic_to_national():
            return ""
        return self._explain_why_not_promote_domestic()
    
    def _explain_why_not_promote_domestic(self):
        if not self.game_engine:
            return "Game not loaded."
        if not self.team or not getattr(self.team, "is_domestic", False):
            return "Use this for a player on a domestic club squad (not already on the national team)."
        if self.player not in getattr(self.team, "players", []):
            return "Player is not on this domestic club's senior list."
        nation = getattr(self.team, "parent_nation", None)
        if not nation:
            return "This club has no parent nation configured."
        national_team = self.game_engine.get_team_by_name(nation)
        if not national_team:
            return f"Could not find national team for {nation}."
        if self.player in national_team.players:
            return "Player is already on the national senior squad."
        pname = (getattr(self.player, "name", "") or "").strip()
        if any((getattr(p, "name", "") or "").strip() == pname for p in (national_team.players or [])):
            return "Player is already on the national senior squad."
        if len(national_team.players) >= MAX_SQUAD_SIZE:
            return f"{nation}'s national squad is full ({MAX_SQUAD_SIZE})."
        return "Cannot promote this player right now."
    
    def _can_promote_to_national_squad(self):
        """U21 → senior national, or domestic club → national senior (single button)."""
        return self._can_promote_u21_action() or self._can_promote_domestic_to_national()
    
    def _tooltip_promote_to_national_squad(self):
        if self._can_promote_u21_action():
            return self._tooltip_promote_u21()
        if self._can_promote_domestic_to_national():
            return ""
        if self._is_u21_player():
            return self._tooltip_promote_u21()
        if self._is_domestic_club_senior():
            return self._explain_why_not_promote_domestic()
        return (
            "Use this from a national U21 squad (promote to senior) or from a domestic club "
            "(add to national squad)."
        )
    
    def _on_promote_to_national_squad(self):
        if self._can_promote_u21_action():
            self._on_promote_to_senior()
        elif self._can_promote_domestic_to_national():
            self._on_promote_domestic_to_national()
    
    def _can_promote_u21_to_domestic(self):
        """National U21 squad → domestic club (same country)."""
        if not self.game_engine or not self.team:
            return False
        if getattr(self.team, "is_domestic", False):
            return False
        if not self._is_main_team(self.team):
            return False
        if not self._is_u21_player():
            return False
        domestic_teams = getattr(self.game_engine, "domestic_teams", None) or []
        nation = self.team.name
        nation_domestic = [
            dt for dt in domestic_teams if getattr(dt, "parent_nation", None) == nation
        ]
        if not nation_domestic:
            return False
        if not any(len(dt.players) < MAX_SQUAD_SIZE for dt in nation_domestic):
            return False
        return True
    
    def _tooltip_promote_u21_to_domestic(self):
        if self._can_promote_u21_to_domestic():
            return ""
        if not self.game_engine or not self.team:
            return "Game not loaded or no team."
        if getattr(self.team, "is_domestic", False):
            return "Open this profile from a Test nation's national squad (not a domestic club)."
        if not self._is_main_team(self.team):
            return "Only available when viewing a Tier 1 national team."
        if not self._is_u21_player():
            return "Only for players on the national U21 squad."
        nation = self.team.name
        domestic_teams = getattr(self.game_engine, "domestic_teams", None) or []
        nation_domestic = [
            dt for dt in domestic_teams if getattr(dt, "parent_nation", None) == nation
        ]
        if not nation_domestic:
            return f"No domestic league teams for {nation}."
        if not any(len(dt.players) < MAX_SQUAD_SIZE for dt in nation_domestic):
            return "All domestic squads for this nation are full."
        return "Cannot promote this player to domestic right now."
    
    def _on_promote_u21_to_domestic(self):
        if not self._can_promote_u21_to_domestic():
            return
        nation = getattr(self.team, "name", "national")
        reply = QMessageBox.question(
            self,
            "Promote to domestic team",
            f"Remove {self.player.name} from {nation}'s U21 squad and place them on a domestic club?\n\n"
            "Preferred: a club matching their listed domestic affiliations (if it has space). "
            "Otherwise: a random domestic squad with an open slot.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        ok, info = self.game_engine.send_u21_player_to_domestic(self.player, self.team)
        if not ok:
            QMessageBox.warning(self, "Cannot promote to domestic", info, QMessageBox.StandardButton.Ok)
            return
        QMessageBox.information(
            self,
            "Done",
            f"{self.player.name} has been moved to domestic side: {info}.",
            QMessageBox.StandardButton.Ok,
        )
        self.accept()
    
    def _tooltip_move_associate(self):
        if self._can_move_to_associate():
            return ""
        if not self.game_engine or not self.team:
            return "Game not loaded or no team."
        associates = [t for t in self.game_engine.all_teams if getattr(t, "format_tiers", {}).get("Test", 1) != 1]
        if not associates:
            return "No associate nations exist in this save."
        if self._is_associate_team(self.team):
            return "Player is already with an associate nation. Use 'Back to national team' when available."
        if getattr(self.team, "is_domestic", False):
            if self.player not in getattr(self.team, "players", []):
                return "Player must be on this domestic club's senior list."
            return "Cannot move this player to an associate nation right now."
        if self._is_main_team(self.team):
            if self.player not in getattr(self.team, "players", []) and not self._is_u21_player():
                return "Player must be on the national senior squad or U21 squad."
        return "This action is not available for this player."
    
    def _tooltip_back_national(self):
        if self._can_return_to_national():
            return ""
        return (
            "Only available for players on an associate nation who were transferred from a Test nation "
            "(and have an original team to return to)."
        )
    
    def _tooltip_send_domestic(self):
        if self._can_send_back_to_domestic():
            return ""
        if not self.game_engine or not self.team:
            return "Game not loaded or no team."
        if getattr(self.team, "is_domestic", False):
            return "Use this for a senior player on a Test nation's national squad, not a domestic club."
        if self._is_u21_player():
            return "Promote U21 players to senior first, or use other squad moves."
        if not self._is_main_team(self.team):
            return "Only Test-tier national squads can send players back to domestic cricket."
        if self.player not in getattr(self.team, "players", []):
            return "Player must be on this national senior squad."
        nation = self.team.name
        domestic_teams = getattr(self.game_engine, "domestic_teams", None) or []
        nation_domestic = [dt for dt in domestic_teams if getattr(dt, "parent_nation", None) == nation]
        if not nation_domestic:
            return f"No domestic league teams for {nation}."
        if not any(len(dt.players) < MAX_SQUAD_SIZE for dt in nation_domestic):
            return "All domestic squads for this nation are full."
        return "Cannot send this player to domestic cricket right now."
    
    def _on_view_u21_stats_footer(self):
        """Frozen snapshot after leaving U21, or live youth-international totals while still in U21."""
        if getattr(self.player, "u21_career_stats", None):
            self._show_u21_stats_dialog(use_snapshot=True)
            return
        if self._is_u21_player():
            live = getattr(self.player, "u21_international_stats", None)
            if live and any(live.get(fmt, {}).get("matches", 0) > 0 for fmt in ("T20", "ODI", "Test")):
                self._show_u21_stats_dialog(use_snapshot=False)
                return
            QMessageBox.information(
                self,
                "U21 stats",
                "Youth international stats (U21 vs U21) will appear here as this player completes matches. "
                "A frozen copy is also saved when they are promoted to senior cricket or leave the U21 system.",
                QMessageBox.StandardButton.Ok,
            )
            return
        QMessageBox.information(
            self,
            "U21 stats",
            "No U21 career snapshot is stored for this player. Snapshots are created when a player leaves the U21 "
            "system via promotion to senior cricket or a transfer to an associate nation.",
            QMessageBox.StandardButton.Ok,
        )
    
    def init_ui(self):
        """Initialize UI with tabs"""
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Compact single-row header (fixed height set inside create_header)
        header = self.create_header()
        layout.addWidget(header)
        
        # Tab widget
        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {COLORS['border_light']};
                background: #111827;
            }}
            QTabBar::tab {{
                background: #1F2937;
                color: #EAF1FF;
                border: 1px solid {COLORS['border_light']};
                padding: 10px 20px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background: {COLORS['primary']};
                color: white;
            }}
            QTabBar::tab:hover {{
                background: #1E293B;
            }}
        """)
        
        # Add tabs (with safety wrappers)
        self._career_history_tab_index = None
        for tab_name, tab_func in [
            ("Overview", self.create_overview_tab),
            ("Development", self.create_traits_tab),
            ("Season stats", self.create_season_stats_tab),
            ("Rankings", self.create_rankings_tab),
            ("Career history", self.create_career_history_tab),
        ]:
            try:
                tabs.addTab(tab_func(), tab_name)
            except Exception as e:
                import traceback
                traceback.print_exc()
                error_widget = QWidget()
                error_layout = QVBoxLayout()
                error_label = QLabel(f"Error loading {tab_name}: {str(e)}")
                error_label.setStyleSheet("color: red; padding: 20px; font-size: 14px;")
                error_layout.addWidget(error_label)
                error_widget.setLayout(error_layout)
                tabs.addTab(error_widget, tab_name)
            if tab_name == "Career history":
                self._career_history_tab_index = tabs.count() - 1
        
        self._profile_tabs = tabs
        tabs.currentChanged.connect(self._on_profile_tab_changed)
        
        tabs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # Stretch so header + tab stack shrink to fit the window; footer buttons stay visible above the taskbar.
        layout.addWidget(tabs, 1)
        
        # Squad actions: always show same buttons; enable only when the action applies (tooltips explain why not).
        btn_style = f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                font-size: 11px;
            }}
            QPushButton:hover:enabled {{
                background-color: {COLORS['secondary']};
            }}
            QPushButton:disabled {{
                background-color: #b0b0b0;
                color: #f0f0f0;
            }}
        """
        btn_outer = QVBoxLayout()
        btn_outer.setContentsMargins(0, 4, 0, 0)
        btn_outer.setSpacing(4)
        row_a = QHBoxLayout()
        row_a.setSpacing(6)
        row_b = QHBoxLayout()
        row_b.setSpacing(6)
        
        self._btn_promote_national = QPushButton("Promote to national squad")
        self._btn_promote_domestic = QPushButton("Promote to domestic team")
        self._btn_move_associate = QPushButton("Move to associate nation")
        self._btn_back_national = QPushButton("Back to national team")
        for b in (self._btn_promote_national, self._btn_promote_domestic, self._btn_move_associate, self._btn_back_national):
            b.setStyleSheet(btn_style)
        self._btn_promote_national.clicked.connect(self._on_promote_to_national_squad)
        self._btn_promote_domestic.clicked.connect(self._on_promote_u21_to_domestic)
        self._btn_move_associate.clicked.connect(self._on_move_to_associate)
        self._btn_back_national.clicked.connect(self._on_back_to_national)
        row_a.addWidget(self._btn_promote_national)
        row_a.addWidget(self._btn_promote_domestic)
        row_a.addWidget(self._btn_move_associate)
        row_a.addWidget(self._btn_back_national)
        row_a.addStretch()
        
        self._btn_send_domestic = QPushButton("Send back to domestic cricket")
        self._btn_u21_stats = QPushButton("View U21 stats")
        close_btn = QPushButton("Close")
        for b in (self._btn_send_domestic, self._btn_u21_stats, close_btn):
            b.setStyleSheet(btn_style)
        self._btn_send_domestic.clicked.connect(self._on_send_back_to_domestic)
        self._btn_u21_stats.clicked.connect(self._on_view_u21_stats_footer)
        close_btn.clicked.connect(self.close)
        row_b.addWidget(self._btn_send_domestic)
        row_b.addWidget(self._btn_u21_stats)
        row_b.addStretch()
        row_b.addWidget(close_btn)
        
        self._refresh_profile_action_buttons()
        btn_outer.addLayout(row_a)
        btn_outer.addLayout(row_b)
        btn_widget = QWidget()
        btn_widget.setLayout(btn_outer)
        layout.addWidget(btn_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.setLayout(layout)
        
        if hasattr(self, '_profile_scope_combo'):
            self._profile_scope_combo.currentIndexChanged.connect(self._on_profile_stats_scope_changed)
    
    def _is_u21_player(self):
        """Return True if this player is in the team's U21 squad."""
        if not self.team:
            return False
        if not hasattr(self.team, 'u21_squad') or not self.team.u21_squad:
            return False
        if self.player in self.team.u21_squad:
            return True
        pname = (getattr(self.player, "name", "") or "").strip()
        return any((getattr(p, "name", "") or "").strip() == pname for p in (self.team.u21_squad or []))
    
    def _on_promote_to_senior(self):
        """Promote this U21 player to the senior squad."""
        if not self._is_u21_player():
            return
        if len(self.team.players) >= MAX_SQUAD_SIZE:
            QMessageBox.warning(
                self,
                "Squad Full",
                f"Senior squad is full (maximum {MAX_SQUAD_SIZE} players).\nPlease release a player first.",
                QMessageBox.StandardButton.Ok
            )
            return
        reply = QMessageBox.question(
            self,
            "Confirm Promotion",
            f"Promote {self.player.name} ({self.player.role}, Age {self.player.age}) to the senior team?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            # Snapshot U21 career and reset senior stats before promotion
            if hasattr(self.player, 'snapshot_u21_and_reset_senior_career'):
                self.player.snapshot_u21_and_reset_senior_career()
            # Remove from U21 squad
            if hasattr(self.team, 'u21_squad') and self.player in self.team.u21_squad:
                self.team.u21_squad.remove(self.player)
            if hasattr(self.player, 'is_youth_player'):
                self.player.is_youth_player = False
            self.team.add_player(self.player)
            QMessageBox.information(
                self,
                "Success",
                f"{self.player.name} has been promoted to the senior team!",
                QMessageBox.StandardButton.Ok
            )
            self.accept()
    
    def _is_domestic_club_senior(self):
        """True if profile context is a domestic club and player is on its senior list."""
        if not self.team:
            return False
        if not getattr(self.team, 'is_domestic', False):
            return False
        players = getattr(self.team, 'players', []) or []
        if self.player in players:
            return True
        pname = (getattr(self.player, "name", "") or "").strip()
        return any((getattr(p, "name", "") or "").strip() == pname for p in players)
    
    def _can_promote_domestic_to_national(self):
        """Domestic squad player whose parent nation has room on the international senior squad."""
        if not self.game_engine or not self._is_domestic_club_senior():
            return False
        nation = getattr(self.team, 'parent_nation', None)
        if not nation:
            return False
        national_team = self.game_engine.get_team_by_name(nation)
        if not national_team or getattr(national_team, 'is_domestic', False):
            return False
        if self.player in national_team.players:
            return False
        pname = (getattr(self.player, "name", "") or "").strip()
        if any((getattr(p, "name", "") or "").strip() == pname for p in (national_team.players or [])):
            return False
        if len(national_team.players) >= MAX_SQUAD_SIZE:
            return False
        return True
    
    def _on_promote_domestic_to_national(self):
        """Promote this domestic-club player to their country's national senior squad."""
        if not self._can_promote_domestic_to_national():
            return
        nation = getattr(self.team, 'parent_nation', '') or 'national'
        club_name = getattr(self.team, 'name', 'this domestic club')
        reply = QMessageBox.question(
            self,
            "Promote to senior side",
            f"Add {self.player.name} to {nation}'s national senior squad?\n\n"
            f"They will leave {club_name}.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        ok, info = self.game_engine.promote_domestic_player_to_national(self.player, self.team)
        if not ok:
            QMessageBox.warning(self, "Cannot promote", info, QMessageBox.StandardButton.Ok)
            return
        QMessageBox.information(
            self,
            "Success",
            f"{self.player.name} has been added to {info}'s senior squad.",
            QMessageBox.StandardButton.Ok,
        )
        self.accept()
    
    def _is_main_team(self, team):
        """Return True if team is a Tier 1 (Test) nation."""
        if not team:
            return False
        return getattr(team, 'format_tiers', {}).get('Test', 1) == 1
    
    def _is_associate_team(self, team):
        """Return True if team is an associate nation (Tier 2/3/4)."""
        if not team:
            return False
        if getattr(team, 'is_domestic', False):
            return False
        return getattr(team, 'format_tiers', {}).get('Test', 1) != 1
    
    def _can_move_to_associate(self):
        """Senior/U21 on a Test nation, or senior on a domestic club — can move to an associate."""
        if not self.team or not self.game_engine:
            return False
        associate_teams = [t for t in self.game_engine.all_teams if getattr(t, 'format_tiers', {}).get('Test', 1) != 1]
        if not associate_teams:
            return False
        if self._is_associate_team(self.team):
            return False
        if getattr(self.team, 'is_domestic', False):
            return self.player in getattr(self.team, 'players', [])
        if self._is_main_team(self.team):
            if self.player in getattr(self.team, 'players', []):
                return True
            if self._is_u21_player():
                return True
        return False
    
    def _can_return_to_national(self):
        """Return True if this player is in an associate team and has an original national team to return to."""
        if not self.team or not self.game_engine:
            return False
        if not self._is_associate_team(self.team):
            return False
        return bool(getattr(self.player, 'original_team_name', None))
    
    def _can_send_back_to_domestic(self):
        """Senior on a Test-tier national team with domestic clubs available (mirror domestic call-up scope)."""
        if not self.team or not self.game_engine:
            return False
        if getattr(self.team, 'is_domestic', False):
            return False
        if self._is_u21_player():
            return False
        if not self._is_main_team(self.team):
            return False
        if self.player not in getattr(self.team, 'players', []):
            return False
        domestic_teams = getattr(self.game_engine, 'domestic_teams', None) or []
        nation = self.team.name
        nation_domestic = [
            dt for dt in domestic_teams if getattr(dt, 'parent_nation', None) == nation
        ]
        if not nation_domestic:
            return False
        from cricket_manager.utils.constants import MAX_SQUAD_SIZE
        if not any(len(dt.players) < MAX_SQUAD_SIZE for dt in nation_domestic):
            return False
        return True
    
    def _on_send_back_to_domestic(self):
        """Move this national-team player to a domestic club (same country)."""
        if not self._can_send_back_to_domestic():
            return
        nation = getattr(self.team, 'name', 'national')
        reply = QMessageBox.question(
            self,
            "Send back to domestic",
            f"Remove {self.player.name} from {nation}'s national squad and place them on a domestic team?\n\n"
            "Preferred: a club matching their listed domestic affiliations (if it has space). "
            "Otherwise: a random domestic squad with an open slot.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        ok, info = self.game_engine.send_national_player_to_domestic(self.player, self.team)
        if not ok:
            QMessageBox.warning(self, "Cannot send to domestic", info, QMessageBox.StandardButton.Ok)
            return
        QMessageBox.information(
            self,
            "Done",
            f"{self.player.name} has been moved to domestic side: {info}.",
            QMessageBox.StandardButton.Ok,
        )
        self.accept()
    
    def _on_move_to_associate(self):
        """Transfer this player to a random associate nation."""
        if not self._can_move_to_associate():
            return
        import random
        associate_teams = [t for t in self.game_engine.all_teams if getattr(t, 'format_tiers', {}).get('Test', 1) != 1]
        if not associate_teams:
            QMessageBox.warning(self, "Error", "No associate nations available.", QMessageBox.StandardButton.Ok)
            return
        to_team = random.choice(associate_teams)
        reply = QMessageBox.question(
            self,
            "Move to associate nation",
            f"Move {self.player.name} to {to_team.name}?\n\nThey can be brought back later via \"BACK TO NATIONAL TEAM\".",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        # Remove from current team (senior squad or U21 squad)
        removed = False
        if hasattr(self.team, 'players') and self.player in self.team.players:
            self.team.players.remove(self.player)
            removed = True
        elif hasattr(self.team, 'u21_squad') and self.player in self.team.u21_squad:
            # Snapshot U21 stats before sending directly to associate senior team
            if hasattr(self.player, 'snapshot_u21_and_reset_senior_career'):
                self.player.snapshot_u21_and_reset_senior_career()
            self.team.u21_squad.remove(self.player)
            removed = True
        if not removed:
            QMessageBox.warning(self, "Error", "Player not found in current squad.", QMessageBox.StandardButton.Ok)
            return
        # Player always joins associate senior squad
        if hasattr(self.player, 'is_youth_player'):
            self.player.is_youth_player = False
        to_team.players.append(self.player)
        self.player.nationality = to_team.name
        self.player.original_team_name = self.team.name
        QMessageBox.information(
            self,
            "Done",
            f"{self.player.name} has been moved to {to_team.name}.",
            QMessageBox.StandardButton.Ok
        )
        self.accept()
    
    def _on_back_to_national(self):
        """Move this player back from associate nation to their original national team."""
        if not self._can_return_to_national():
            return
        original_name = getattr(self.player, 'original_team_name', None)
        national_team = self.game_engine.get_team_by_name(original_name) if self.game_engine else None
        if not national_team:
            QMessageBox.warning(
                self,
                "Error",
                f"Could not find original team \"{original_name}\".",
                QMessageBox.StandardButton.Ok
            )
            return
        if len(national_team.players) >= MAX_SQUAD_SIZE:
            QMessageBox.warning(
                self,
                "Squad Full",
                f"{national_team.name} squad is full (maximum {MAX_SQUAD_SIZE} players).\nPlease release a player first.",
                QMessageBox.StandardButton.Ok
            )
            return
        reply = QMessageBox.question(
            self,
            "Back to national team",
            f"Move {self.player.name} back to {national_team.name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            self.team.players.remove(self.player)
        except ValueError:
            QMessageBox.warning(self, "Error", "Player not found in current squad.", QMessageBox.StandardButton.Ok)
            return
        national_team.add_player(self.player)
        self.player.nationality = national_team.name
        setattr(self.player, 'clear_intl_rank_until_next_match', True)
        if hasattr(self.player, 'original_team_name'):
            delattr(self.player, 'original_team_name')
        QMessageBox.information(
            self,
            "Done",
            f"{self.player.name} has been moved back to {national_team.name}.",
            QMessageBox.StandardButton.Ok
        )
        self.accept()
    
    def create_header(self):
        """Create header with player name and photo placeholder"""
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary']}, stop:1 {COLORS['secondary']});
                border-radius: 5px;
                padding: 8px 12px;
            }}
        """)
        header_frame.setFixedHeight(72)
        
        outer = QVBoxLayout()
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(6)
        
        name = getattr(self.player, 'name', 'Unknown')
        role = getattr(self.player, 'role', 'Player')
        nationality = getattr(self.player, 'nationality', '')
        age = getattr(self.player, 'age', 0)
        team_display = f"{getattr(self.team, 'name', '')} U21" if self._is_u21_player() else getattr(self.team, 'name', '')
        
        row1 = QHBoxLayout()
        row1.setContentsMargins(0, 2, 0, 4)
        row1.setSpacing(8)
        name_label = QLabel(f"<b>{name}</b>")
        name_label.setStyleSheet(
            "font-size: 16px; color: white; padding: 4px 0px 6px 0px; min-height: 22px;"
        )
        name_label.setTextFormat(Qt.TextFormat.RichText)
        name_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        row1.addWidget(name_label)
        detail_parts = [role]
        if nationality:
            detail_parts.append(nationality)
        detail_parts.append(f"Age {age}")
        if team_display:
            detail_parts.append(f"Team: {team_display}")
        details_label = QLabel(" \u00b7 ".join(detail_parts))
        details_label.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.85); padding: 4px 0px;")
        details_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        row1.addWidget(details_label)
        row1.addStretch()
        outer.addLayout(row1)
        
        row2 = QHBoxLayout()
        row2.setContentsMargins(0, 0, 0, 0)
        row2.setSpacing(6)
        self._profile_rank_chip_labels = []
        chip_style = (
            "font-size: 10px; color: rgba(255,255,255,0.95); "
            "background-color: rgba(0, 45, 58, 0.55); padding: 2px 6px; border-radius: 3px;"
        )
        for _ in range(6):
            lbl = QLabel("")
            lbl.setStyleSheet(chip_style)
            lbl.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
            row2.addWidget(lbl)
            self._profile_rank_chip_labels.append(lbl)
        row2.addStretch()
        self._profile_scope_combo = QComboBox()
        self._profile_scope_combo.addItem("All stats", "all")
        self._profile_scope_combo.addItem("Senior international", "international")
        self._profile_scope_combo.addItem("Associate international", "associate_international")
        self._profile_scope_combo.addItem("Domestic", "domestic")
        self._profile_scope_combo.setCurrentIndex(1)  # Default to Senior international
        self._profile_scope_combo.setToolTip("Filter career stats scope")
        self._profile_scope_combo.setFixedWidth(200)
        self._profile_scope_combo.setStyleSheet("""
            QComboBox {
                combobox-popup: 0; background-color: rgba(0,55,72,0.95); color: #fff;
                padding: 2px 18px 2px 6px; border: 1px solid rgba(255,255,255,0.35);
                border-radius: 3px; font-size: 11px;
            }
            QComboBox::drop-down { width: 18px; border: none; background: transparent; }
            QComboBox QAbstractItemView {
                background-color: rgba(0,45,58,0.98); color: #fff;
                selection-background-color: rgba(0,110,140,0.95);
                border: 1px solid rgba(255,255,255,0.35); padding: 2px;
            }
        """)
        row2.addWidget(self._profile_scope_combo)
        outer.addLayout(row2)
        
        header_frame.setLayout(outer)
        self._refresh_profile_header_rankings()
        return header_frame
    
    def _refresh_profile_header_rankings(self):
        """Six international rank chips in one horizontal row."""
        chips = getattr(self, "_profile_rank_chip_labels", None) or []
        if not chips:
            return
        segs = player_profile_career_ranking_chips(
            self.game_engine, self.player, profile_team=self.team
        )
        for i, lbl in enumerate(chips):
            txt = segs[i] if i < len(segs) else ""
            lbl.setText(txt)
            lbl.setVisible(bool(txt))

    def create_rankings_tab(self):
        """Season ranks: three-season grid per scope (International, Domestic, U21)."""
        widget = QWidget()
        outer = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        inner = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(4, 8, 4, 8)
        ge = self.game_engine
        if not ge:
            layout.addWidget(QLabel("No game data loaded."))
        else:
            sections = player_profile_rankings_tab_tables(ge, self.player)
            cy = getattr(ge, "current_year", None) or 2000
            y1, y2, y3 = cy - 1, cy - 2, cy - 3
            for sec in sections:
                card = QFrame()
                card.setStyleSheet(f"""
                    QFrame {{
                        background: #111827;
                        border: 1px solid {COLORS['border_light']};
                        border-radius: 12px;
                    }}
                """)
                cv = QVBoxLayout()
                cv.setContentsMargins(16, 14, 16, 16)
                cv.setSpacing(10)
                head = QHBoxLayout()
                badge = QLabel(sec["title"])
                badge.setStyleSheet(f"""
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {COLORS['primary']}, stop:1 {COLORS.get('secondary', COLORS['primary'])});
                    color: white;
                    padding: 6px 14px;
                    border-radius: 16px;
                    font-weight: bold;
                    font-size: 13px;
                """)
                head.addWidget(badge)
                head.addStretch()
                cv.addLayout(head)
                sub = QLabel(sec["subtitle"])
                sub.setStyleSheet("font-size: 11px; color: #94A3B8;")
                sub.setWordWrap(True)
                cv.addWidget(sub)
                rows_data = sec["rows"]
                tbl = QTableWidget(len(rows_data), 7)
                tbl.setHorizontalHeaderLabels([
                    "Format",
                    f"{y1} bat", f"{y2} bat", f"{y3} bat",
                    f"{y1} bowl", f"{y2} bowl", f"{y3} bowl",
                ])
                tbl.verticalHeader().setVisible(False)
                tbl.setShowGrid(True)
                tbl.setAlternatingRowColors(True)
                tbl.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
                tbl.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                tbl.setStyleSheet(f"""
                    QTableWidget {{
                        background: #111827;
                        border: 1px solid #334155;
                        border-radius: 8px;
                        gridline-color: #334155;
                        font-size: 12px;
                    }}
                    QTableWidget::item {{
                        padding: 8px 6px;
                    }}
                    QHeaderView::section {{
                        background: #1F2937;
                        color: #EAF1FF;
                        padding: 10px 6px;
                        font-weight: 600;
                        font-size: 11px;
                        border: none;
                        border-bottom: 2px solid {COLORS['primary']};
                    }}
                """)
                hdr = tbl.horizontalHeader()
                hdr.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
                hdr.setMinimumSectionSize(72)
                for ri, row in enumerate(rows_data):
                    fmt = row["format"]
                    fc = get_format_color(fmt)
                    fmt_item = QTableWidgetItem(fmt)
                    fmt_item.setForeground(QColor(fc))
                    f = fmt_item.font()
                    f.setBold(True)
                    fmt_item.setFont(f)
                    tbl.setItem(ri, 0, fmt_item)
                    for ci in range(3):
                        b = QTableWidgetItem(row["bat_display"][ci] if ci < len(row["bat_display"]) else "—")
                        b.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        tbl.setItem(ri, 1 + ci, b)
                    for ci in range(3):
                        b = QTableWidgetItem(row["bowl_display"][ci] if ci < len(row["bowl_display"]) else "—")
                        b.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        tbl.setItem(ri, 4 + ci, b)
                tbl.setMinimumHeight(min(280, 52 + len(rows_data) * 42))
                cv.addWidget(tbl)
                card.setLayout(cv)
                layout.addWidget(card)
        layout.addStretch()
        inner.setLayout(layout)
        scroll.setWidget(inner)
        scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        outer.addWidget(scroll, 1)
        widget.setLayout(outer)
        return widget
    
    def create_career_history_tab(self):
        """Cricinfo-style career narrative; regenerates when this tab is selected."""
        w = QWidget()
        lay = QVBoxLayout()
        lay.setContentsMargins(8, 8, 8, 8)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._career_history_label = QLabel()
        self._career_history_label.setWordWrap(True)
        self._career_history_label.setTextFormat(Qt.TextFormat.RichText)
        self._career_history_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self._career_history_label.setText(
            "<p style=\"color:#B8C3D9;\"><em>Loading career story...</em></p>"
        )
        self._career_history_label.setStyleSheet(
            "font-size: 14px; line-height: 1.6; color: #EAF1FF; padding: 8px 12px; background: transparent;"
        )
        scroll.setWidget(self._career_history_label)
        scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        lay.addWidget(scroll, 1)
        w.setLayout(lay)
        return w
    
    def _on_profile_tab_changed(self, index):
        if self._career_history_tab_index is None:
            return
        if index == self._career_history_tab_index:
            self._refresh_career_history_tab()
    
    def _refresh_career_history_tab(self):
        if not hasattr(self, "_career_history_label"):
            return
        html = build_career_history_article(self.game_engine, self.player, self.team)
        self._career_history_label.setText(html)
    
    def create_overview_tab(self):
        """Create overview tab with current stats"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        
        # Skills section (use getattr to avoid crash if attributes missing)
        hide_bat_bowl = getattr(self.game_engine, 'hide_batting_bowling_ratings', False) if self.game_engine else False
        skills_data = []
        if not hide_bat_bowl:
            skills_data.append(("Batting", getattr(self.player, 'batting', 0), 100))
            skills_data.append(("Bowling", getattr(self.player, 'bowling', 0), 100))
            skills_data.append(("Fielding", getattr(self.player, 'fielding', 0), 100))
        skills_data.extend([
            ("Form", getattr(self.player, 'form', 50), 100),
            ("Fitness", getattr(self.player, 'fitness', 100), 100)
        ])
        
        # Add pace speeds for bowlers
        if hasattr(self.player, 'avg_pace') and self.player.avg_pace > 0:
            skills_data.append(("Avg Pace", self.player.avg_pace, 160))
            skills_data.append(("Top Pace", self.player.top_pace, 160))
        
        skills_frame = self.create_section("📊 Skills Overview", skills_data)
        scroll_layout.addWidget(skills_frame)
        
        t20_club = getattr(self.player, 'domestic_t20_club_name', '') or '—'
        odi_fc_club = getattr(self.player, 'domestic_odi_fc_club_name', '') or '—'
        foreign_t20 = (getattr(self.player, 'foreign_t20_club_name', '') or '').strip()
        aff_frame = QFrame()
        aff_frame.setStyleSheet(f"""
            QFrame {{
                background: #111827;
                border: 1px solid {COLORS['border_light']};
                border-radius: 5px;
                padding: 15px;
                margin: 5px;
            }}
        """)
        aff_outer = QVBoxLayout()
        aff_title = QLabel("🏏 Domestic club affiliations")
        aff_title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COLORS['primary']};")
        aff_outer.addWidget(aff_title)
        aff_rows = [
            ("Home T20 domestic side", t20_club),
            ("Home ODI & First-Class (FC) side", odi_fc_club),
        ]
        if foreign_t20:
            aff_rows.append(("Additional overseas T20 franchise", foreign_t20))
        for lbl, val in aff_rows:
            row = QHBoxLayout()
            lw = QLabel(f"{lbl}:")
            lw.setStyleSheet("font-weight: bold;")
            vw = QLabel(str(val))
            vw.setStyleSheet("color: #B8C3D9;")
            row.addWidget(lw)
            row.addWidget(vw)
            row.addStretch()
            aff_outer.addLayout(row)
        aff_frame.setLayout(aff_outer)
        scroll_layout.addWidget(aff_frame)
        
        # Bowling Movements section (only for bowlers with movements; hide when ratings hidden)
        if (not hide_bat_bowl and hasattr(self.player, 'bowling_movements') and 
            self.player.bowling_movements and 
            getattr(self.player, 'bowling', 0) > 40):
            
            bowling_frame = self.create_bowling_movements_section()
            scroll_layout.addWidget(bowling_frame)
        
        # Career statistics for all formats (refreshed when header scope changes)
        self._career_stats_layout = QVBoxLayout()
        self._career_stats_container = QWidget()
        self._career_stats_container.setLayout(self._career_stats_layout)
        self._populate_career_stats_sections()
        scroll_layout.addWidget(self._career_stats_container)
        
        # Traits section
        traits_frame = self.create_traits_overview()
        scroll_layout.addWidget(traits_frame)
        
        scroll_layout.addStretch()
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        
        layout.addWidget(scroll, 1)
        widget.setLayout(layout)
        return widget
    
    def create_section(self, title, items):
        """Create a section with title and items"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: #111827;
                border: 1px solid {COLORS['border_light']};
                border-radius: 5px;
                padding: 15px;
                margin: 5px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COLORS['primary']};")
        layout.addWidget(title_label)
        
        # Items
        grid = QGridLayout()
        for i, (label, value, max_val) in enumerate(items):
            label_widget = QLabel(f"{label}:")
            label_widget.setStyleSheet("font-weight: bold;")
            grid.addWidget(label_widget, i, 0)
            
            # Special display for pace speeds
            if label in ["Avg Pace", "Top Pace"]:
                value_label = QLabel(f"{value:.0f} kph")
                value_label.setStyleSheet(f"color: {self.get_skill_color(value, max_val)};")
            else:
                value_label = QLabel(f"{value}/{max_val}")
                value_label.setStyleSheet(f"color: {self.get_skill_color(value, max_val)};")
            grid.addWidget(value_label, i, 1)
            
            # Progress bar
            bar = self.create_progress_bar(value, max_val)
            grid.addWidget(bar, i, 2)
        
        layout.addLayout(grid)
        frame.setLayout(layout)
        return frame
    
    def create_progress_bar(self, value, max_val):
        """Create a visual progress bar"""
        bar = QFrame()
        percentage = (value / max_val) * 100 if max_val > 0 else 0
        color = self.get_skill_color(value, max_val)
        
        bar.setStyleSheet(f"""
            QFrame {{
                background: #1F2937;
                border-radius: 3px;
            }}
        """)
        bar.setFixedHeight(20)
        bar.setFixedWidth(200)
        
        inner = QFrame(bar)
        inner.setStyleSheet(f"""
            QFrame {{
                background: {color};
                border-radius: 3px;
            }}
        """)
        inner.setFixedHeight(20)
        inner.setFixedWidth(int(200 * percentage / 100))
        
        return bar
    
    def get_skill_color(self, value, max_val):
        """Get color based on skill value"""
        percentage = (value / max_val) * 100 if max_val > 0 else 0
        
        if percentage >= 90:
            return COLORS['success']
        elif percentage >= 60:
            return COLORS['info']
        elif percentage >= 40:
            return COLORS['warning']
        else:
            return COLORS['danger']
    
    def _profile_stats_career_root(self):
        if hasattr(self, '_profile_scope_combo'):
            mode = self._profile_scope_combo.currentData()
            if mode == "international":
                return getattr(self.player, 'international_stats', None) or getattr(self.player, 'stats', {})
            if mode == "associate_international":
                ds = getattr(self.player, 'associate_international_stats', None)
                return ds if isinstance(ds, dict) else {}
            if mode == "domestic":
                ds = getattr(self.player, 'domestic_stats', None)
                return ds if isinstance(ds, dict) else {}
        return getattr(self.player, 'stats', {})
    
    def _profile_yearly_root(self):
        if hasattr(self, '_profile_scope_combo'):
            mode = self._profile_scope_combo.currentData()
            if mode == "international":
                return getattr(self.player, 'international_yearly_stats', None) or {}
            if mode == "associate_international":
                return getattr(self.player, 'associate_international_yearly_stats', None) or {}
            if mode == "domestic":
                return getattr(self.player, 'domestic_yearly_stats', None) or {}
        return getattr(self.player, 'yearly_stats', None) or {}
    
    def _populate_career_stats_sections(self):
        if not hasattr(self, '_career_stats_layout'):
            return
        while self._career_stats_layout.count():
            item = self._career_stats_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        for format_type in ['T20', 'ODI', 'Test']:
            self._career_stats_layout.addWidget(self.create_format_stats_section(format_type))
    
    def _rebuild_milestone_format_tabs(self):
        if not hasattr(self, '_milestone_format_tabs'):
            return
        self._milestone_format_tabs.clear()
        for fmt in ['T20', 'ODI', 'Test']:
            self._milestone_format_tabs.addTab(self._create_format_stats_tab(fmt), fmt)
    
    def _on_profile_stats_scope_changed(self, *_args):
        self._populate_career_stats_sections()
        self._rebuild_milestone_format_tabs()
    
    def create_format_stats_section(self, format_type):
        """Create statistics section for a format"""
        root = self._profile_stats_career_root()
        stats = root.get(format_type, {}) if isinstance(root, dict) else {}
        
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: #111827;
                border: 1px solid {COLORS['border_light']};
                border-radius: 5px;
                padding: 15px;
                margin: 5px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        # Title with format color
        title_label = QLabel(f"{format_type} Statistics")
        title_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {get_format_color(format_type)};
        """)
        layout.addWidget(title_label)
        
        # Stats grid
        grid = QGridLayout()
        
        batting_stats = [
            ("Matches", stats.get('matches', 0)),
            ("Runs", stats.get('runs', 0)),
            ("Batting Avg", f"{stats.get('batting_average', 0):.2f}"),
            ("Strike Rate", f"{stats.get('strike_rate', 0):.2f}"),
            ("Highest Score", stats.get('highest_score', 0)),
            ("Centuries", stats.get('centuries', 0)),
            ("Fifties", stats.get('fifties', 0))
        ]
        
        bowling_stats = [
            ("Wickets", stats.get('wickets', 0)),
            ("Bowling Avg", f"{stats.get('bowling_average', 0):.2f}"),
            ("Economy", f"{stats.get('economy_rate', 0):.2f}"),
            ("5-wicket hauls", stats.get('five_wickets', 0))
        ]
        
        row = 0
        for label, value in batting_stats:
            label_widget = QLabel(f"{label}:")
            label_widget.setStyleSheet("font-weight: bold;")
            grid.addWidget(label_widget, row, 0)
            
            value_widget = QLabel(str(value))
            grid.addWidget(value_widget, row, 1)
            row += 1
        
        row = 0
        for label, value in bowling_stats:
            label_widget = QLabel(f"{label}:")
            label_widget.setStyleSheet("font-weight: bold;")
            grid.addWidget(label_widget, row, 2)
            
            value_widget = QLabel(str(value))
            grid.addWidget(value_widget, row, 3)
            row += 1
        
        layout.addLayout(grid)
        frame.setLayout(layout)
        return frame
    
    def _create_format_stats_frame_from_dict(self, format_type, stats):
        """Build a stats section frame from a stats dict (e.g. for U21 career snapshot)."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: #111827;
                border: 1px solid {COLORS['border_light']};
                border-radius: 5px;
                padding: 15px;
                margin: 5px;
            }}
        """)
        layout = QVBoxLayout()
        title_label = QLabel(f"{format_type} Statistics (U21)")
        title_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {get_format_color(format_type)};
        """)
        layout.addWidget(title_label)
        grid = QGridLayout()
        batting_stats = [
            ("Matches", stats.get('matches', 0)),
            ("Runs", stats.get('runs', 0)),
            ("Batting Avg", f"{stats.get('batting_average', 0):.2f}"),
            ("Strike Rate", f"{stats.get('strike_rate', 0):.2f}"),
            ("Highest Score", stats.get('highest_score', 0)),
            ("Centuries", stats.get('centuries', 0)),
            ("Fifties", stats.get('fifties', 0))
        ]
        bowling_stats = [
            ("Wickets", stats.get('wickets', 0)),
            ("Bowling Avg", f"{stats.get('bowling_average', 0):.2f}"),
            ("Economy", f"{stats.get('economy_rate', 0):.2f}"),
            ("5-wicket hauls", stats.get('five_wickets', 0))
        ]
        row = 0
        for label, value in batting_stats:
            grid.addWidget(QLabel(f"{label}:"), row, 0)
            grid.addWidget(QLabel(str(value)), row, 1)
            row += 1
        row = 0
        for label, value in bowling_stats:
            grid.addWidget(QLabel(f"{label}:"), row, 2)
            grid.addWidget(QLabel(str(value)), row, 3)
            row += 1
        layout.addLayout(grid)
        frame.setLayout(layout)
        return frame
    
    def _show_u21_stats_dialog(self, use_snapshot=True):
        """Show U21 youth-international stats: frozen snapshot after promotion, or live totals while in U21."""
        if use_snapshot:
            u21 = getattr(self.player, "u21_career_stats", None)
            info_text = (
                "Frozen U21 youth-international stats from when this player left the youth system. "
                "They do not change after joining the senior team."
            )
        else:
            u21 = getattr(self.player, "u21_international_stats", None)
            info_text = (
                "Live youth international career (national U21 vs U21). These are separate from senior international caps "
                "shown under “Senior international only”."
            )
        if not u21:
            return
        d = QDialog(self)
        d.setWindowTitle(f"{self.player.name} – U21 Career Stats")
        d.setMinimumSize(500, 480)
        layout = QVBoxLayout()
        info = QLabel(info_text)
        info.setStyleSheet("font-size: 12px; color: #B8C3D9; padding: 8px;")
        info.setWordWrap(True)
        layout.addWidget(info)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        content = QWidget()
        content_layout = QVBoxLayout()
        for fmt in ['T20', 'ODI', 'Test']:
            stats = u21.get(fmt, {})
            content_layout.addWidget(self._create_format_stats_frame_from_dict(fmt, stats))
        content.setLayout(content_layout)
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(d.accept)
        layout.addWidget(close_btn)
        d.setLayout(layout)
        d.exec()
    
    def create_traits_overview(self):
        """Create traits overview section"""
        from cricket_manager.systems.trait_assignment import ALL_PLAYER_TRAITS as ALL_TRAITS, is_positive_trait
        
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: #111827;
                border: 1px solid {COLORS['border_light']};
                border-radius: 5px;
                padding: 15px;
                margin: 5px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        title_label = QLabel("Traits")
        title_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COLORS['primary']};")
        layout.addWidget(title_label)
        
        # Store layout reference for refresh
        self.traits_layout = layout
        
        # Store frame reference for refresh
        self.traits_frame = frame
        
        self._refresh_traits_content()
        
        frame.setLayout(layout)
        return frame
    
    def _refresh_traits_content(self):
        """Refresh the traits content dynamically"""
        if not getattr(self, 'traits_layout', None):
            return
        from cricket_manager.systems.trait_assignment import ALL_PLAYER_TRAITS as ALL_TRAITS, is_positive_trait
        
        # Remove old trait widgets (keep the title at index 0)
        while self.traits_layout.count() > 1:
            item = self.traits_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()
        
        if getattr(self.player, 'traits', None):
            for trait in self.player.traits:
                if isinstance(trait, dict):
                    trait_key = trait.get('name', 'Unknown')
                    trait_level = trait.get('strength', 1)
                    # Get display name from traits.py
                    trait_info = ALL_TRAITS.get(trait_key, {})
                    display_name = trait_info.get('name', trait_key.replace('_', ' ').title())
                    # Color based on positive/negative
                    color = '#22C55E' if is_positive_trait(trait_key) else '#c62828'
                    trait_label = QLabel(f"• {display_name} (Level {trait_level})")
                    trait_label.setStyleSheet(f"font-size: 13px; padding: 3px; color: {color};")
                    self.traits_layout.addWidget(trait_label)
                else:
                    trait_label = QLabel(f"• {trait}")
                    trait_label.setStyleSheet("font-size: 13px; padding: 3px;")
                    self.traits_layout.addWidget(trait_label)
        else:
            no_traits = QLabel("No traits")
            no_traits.setStyleSheet("font-style: italic; color: gray;")
            self.traits_layout.addWidget(no_traits)
    
    def create_career_stats_tab(self):
        """Create career statistics tab with season-by-season breakdown"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Format selector
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        
        from PyQt6.QtWidgets import QComboBox
        format_combo = QComboBox()
        format_combo.addItems(['T20', 'ODI', 'Test'])
        format_combo.currentTextChanged.connect(lambda fmt: self.update_season_table(table, fmt))
        format_layout.addWidget(format_combo)
        format_layout.addStretch()
        
        layout.addLayout(format_layout)
        
        # Season statistics table
        table = QTableWidget()
        table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #334155;
                gridline-color: #334155;
            }
            QHeaderView::section {
                background-color: #1F2937;
                color: #EAF1FF;
                padding: 8px;
                border: 1px solid #334155;
                font-weight: bold;
            }
        """)
        
        # Set up table
        headers = ['Year', 'Age', 'Matches', 'Runs', 'Bat Avg', 'Wickets', 'Bowl Avg']
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSortingEnabled(True)
        
        layout.addWidget(table)
        
        # Initial load
        self.update_season_table(table, 'T20')
        
        widget.setLayout(layout)
        return widget
    
    def update_season_table(self, table, format_type):
        """Update season table with data for selected format"""
        get_history = getattr(self.player, 'get_season_history', None)
        history = get_history(format_type, max_seasons=20) if callable(get_history) else []
        
        # Calculate base year for converting season numbers to years
        base_year = 2025  # Default base year
        if self.game_engine:
            current_year = self.game_engine.current_year
            current_season = self.game_engine.current_season
            base_year = current_year - current_season + 1
        
        table.setSortingEnabled(False)
        table.setRowCount(len(history))
        
        for row, season_data in enumerate(history):
            # Convert season number to year
            season_num = season_data.get('season', 1)
            year = base_year + season_num - 1 if isinstance(season_num, int) else season_num
            table.setItem(row, 0, QTableWidgetItem(str(year)))
            table.setItem(row, 1, QTableWidgetItem(str(season_data.get('age', 'N/A'))))
            table.setItem(row, 2, QTableWidgetItem(str(season_data.get('matches', 0))))
            table.setItem(row, 3, QTableWidgetItem(str(season_data.get('runs', 0))))
            
            bat_avg = season_data.get('batting_avg', 0.0)
            table.setItem(row, 4, QTableWidgetItem(f"{bat_avg:.2f}"))
            
            table.setItem(row, 5, QTableWidgetItem(str(season_data.get('wickets', 0))))
            
            bowl_avg = season_data.get('bowling_avg', 0.0)
            table.setItem(row, 6, QTableWidgetItem(f"{bowl_avg:.2f}"))
        
        table.setSortingEnabled(True)
        
        # If no history, show message
        if not history:
            table.setRowCount(1)
            no_data = QTableWidgetItem("No season history available yet")
            no_data.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(0, 0, no_data)
            table.setSpan(0, 0, 1, 7)
    
    def create_traits_tab(self):
        """Create traits and development tab - combined skill + trait evolution per season"""
        from cricket_manager.systems.trait_assignment import ALL_PLAYER_TRAITS as ALL_TRAITS, is_positive_trait
        
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # ── Current Traits section (scrollable) ──
        traits_title = QLabel("Current Traits")
        traits_title.setMinimumHeight(28)
        traits_title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['primary']}; background: transparent; border: none; padding: 4px;")
        layout.addWidget(traits_title)
        
        from PyQt6.QtWidgets import QScrollArea
        
        traits_scroll = QScrollArea()
        traits_scroll.setWidgetResizable(True)
        traits_scroll.setMinimumHeight(160)
        traits_scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        traits_scroll.setStyleSheet(f"""
            QScrollArea {{
                border: 1px solid {COLORS['border_light']};
                border-radius: 5px;
                background: #111827;
            }}
            QScrollBar:vertical {{
                background: #1F2937;
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS['primary']};
                border-radius: 5px;
                min-height: 30px;
            }}
        """)
        
        traits_content = QWidget()
        traits_content.setStyleSheet("background: #111827;")
        traits_inner = QVBoxLayout()
        traits_inner.setContentsMargins(12, 12, 12, 12)
        traits_inner.setSpacing(8)
        
        if getattr(self.player, 'traits', None):
            for trait in self.player.traits:
                if isinstance(trait, dict):
                    trait_key = trait.get('name', 'Unknown')
                    trait_level = trait.get('strength', 1)
                    trait_info = ALL_TRAITS.get(trait_key, {})
                    display_name = trait_info.get('name', trait_key.replace('_', ' ').title())
                    trait_desc = trait_info.get('description', '')
                    trait_type = trait_info.get('type', '').capitalize()
                    trait_phase = trait_info.get('phase', '').replace('_', ' ').capitalize()
                    positive = is_positive_trait(trait_key)
                    bg_color = '#143227' if positive else '#3A1F24'
                    text_color = '#22C55E' if positive else '#c62828'
                    stars = '\u2605' * trait_level
                    
                    # Calculate effect multiplier
                    try:
                        import sys, os
                        _data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '')
                        if _data_dir not in sys.path:
                            sys.path.insert(0, _data_dir)
                        from player_traits import get_trait_effect, get_negative_trait_effect
                        if positive:
                            effect_val = get_trait_effect(trait_key, trait_level)
                        else:
                            effect_val = get_negative_trait_effect(trait_key, trait_level)
                        effect_pct = (effect_val - 1.0) * 100
                        if effect_pct >= 0:
                            effect_str = f"+{effect_pct:.0f}%"
                        else:
                            effect_str = f"{effect_pct:.0f}%"
                    except Exception:
                        effect_str = ""
                    
                    # Build label text
                    meta_parts = []
                    if trait_type:
                        meta_parts.append(trait_type)
                    if trait_phase and trait_phase != 'All':
                        meta_parts.append(f"Phase: {trait_phase}")
                    if effect_str:
                        meta_parts.append(f"Effect: {effect_str}")
                    meta_line = " \u00b7 ".join(meta_parts)
                    
                    label_html = f"<b>{display_name}</b> {stars}"
                    label_html += f"<br><i>{trait_desc}</i>"
                    if meta_line:
                        label_html += f"<br><span style='font-size:11px; color:#94A3B8;'>{meta_line}</span>"
                    
                    tw = QLabel(label_html)
                    tw.setWordWrap(True)
                    tw.setMinimumHeight(70)
                    tw.setStyleSheet(f"padding: 10px; background: {bg_color}; color: {text_color}; border-radius: 4px; margin: 2px; font-size: 13px; border: none;")
                    traits_inner.addWidget(tw)
        else:
            no_lbl = QLabel("No traits")
            no_lbl.setStyleSheet("background: transparent; border: none; font-size: 13px; color: #94A3B8;")
            traits_inner.addWidget(no_lbl)
        
        traits_inner.addStretch()
        traits_content.setLayout(traits_inner)
        traits_scroll.setWidget(traits_content)
        layout.addWidget(traits_scroll, 1)
        
        table = QTableWidget()
        table.setStyleSheet(f"""
            QTableWidget {{
                border: 1px solid {COLORS['border_light']};
                gridline-color: #334155;
                background: #111827;
                font-size: 12px;
            }}
            QHeaderView::section {{
                background-color: {COLORS['primary']};
                color: white;
                padding: 6px 3px;
                border: 1px solid {COLORS['border_light']};
                font-weight: bold;
                font-size: 11px;
            }}
            QTableWidget::item {{
                padding: 4px 3px;
            }}
        """)
        
        headers = ['Season', 'Age', 'Bat', 'Bowl', 'Field', 'Bat \u0394', 'Bowl \u0394', 'Trait Changes']
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        table.horizontalHeader().setMinimumSectionSize(45)
        table.horizontalHeader().setDefaultSectionSize(60)
        # Let the Trait Changes column stretch
        for c in range(7):
            table.horizontalHeader().setSectionResizeMode(c, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)
        
        # Build trait changes grouped by season
        trait_changes_by_season = {}
        if getattr(self.player, 'trait_history', None):
            for change in self.player.trait_history:
                s = change.get('season', '?')
                if s not in trait_changes_by_season:
                    trait_changes_by_season[s] = []
                action = change.get('action', '').title()
                trait_key = change.get('trait', '')
                t_info = ALL_TRAITS.get(trait_key, {})
                t_name = t_info.get('name', trait_key.replace('_', ' ').title())
                lvl = change.get('level', '')
                entry = f"{action}: {t_name}"
                if lvl:
                    entry += f" (Lv{lvl})"
                trait_changes_by_season[s].append(entry)
        
        skill_history = getattr(self.player, 'skill_history', None) or []
        # Show most recent first
        reversed_history = list(reversed(skill_history))
        table.setRowCount(len(reversed_history))
        
        for row, snapshot in enumerate(reversed_history):
            season = snapshot.get('season', '?')
            age = snapshot.get('age', '?')
            bat = snapshot.get('batting', 0)
            bowl = snapshot.get('bowling', 0)
            field = snapshot.get('fielding', 0)
            
            # Calculate deltas vs previous season (next item in reversed list = earlier season)
            orig_idx = len(skill_history) - 1 - row
            if orig_idx > 0:
                prev = skill_history[orig_idx - 1]
                bat_delta = bat - prev.get('batting', bat)
                bowl_delta = bowl - prev.get('bowling', bowl)
            else:
                bat_delta = 0
                bowl_delta = 0
            
            # Format delta strings with color
            def delta_str(d):
                if d > 0:
                    return f"+{d}"
                elif d < 0:
                    return str(d)
                return "-"
            
            # Trait changes for this season
            trait_text = "; ".join(trait_changes_by_season.get(season, []))
            if not trait_text:
                trait_text = "-"
            
            hide_bat_bowl_dev = getattr(self.game_engine, 'hide_batting_bowling_ratings', False) if self.game_engine else False
            values = [str(season), str(age), str(bat), str(bowl), str(field),
                      delta_str(bat_delta), delta_str(bowl_delta), trait_text]
            if hide_bat_bowl_dev:
                values[2] = values[3] = values[4] = values[5] = values[6] = "—"
            
            for col, val in enumerate(values):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                # Color the delta columns
                if col == 5 or col == 6:
                    if val.startswith('+'):
                        item.setForeground(Qt.GlobalColor.darkGreen)
                        item.setFont(QFont('Arial', 11, QFont.Weight.Bold))
                    elif val.startswith('-') and val != '-':
                        item.setForeground(Qt.GlobalColor.red)
                        item.setFont(QFont('Arial', 11, QFont.Weight.Bold))
                if col == 7:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                if col == 0:
                    item.setFont(QFont('Arial', 11, QFont.Weight.Bold))
                table.setItem(row, col, item)
            
            table.setRowHeight(row, 32)
        
        if not skill_history:
            table.setRowCount(1)
            no_data = QTableWidgetItem("No development history yet. Simulate seasons to track progression.")
            no_data.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(0, 0, no_data)
            table.setSpan(0, 0, 1, len(headers))
        
        layout.addWidget(table, 1)
        
        widget.setLayout(layout)
        return widget
    
    def create_season_stats_tab(self):
        """Year-by-year season statistics (T20 / ODI / Test); milestones list removed to give the table full height."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # Format sub-tabs for season stats
        self._milestone_format_tabs = QTabWidget()
        self._milestone_format_tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {COLORS['border_light']};
                background: #111827;
            }}
            QTabBar::tab {{
                padding: 8px 20px;
                font-size: 13px;
                font-weight: bold;
                border: 1px solid {COLORS['border_light']};
                border-bottom: none;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                margin-right: 2px;
                background: #1F2937;
                color: #EAF1FF;
            }}
            QTabBar::tab:selected {{
                background: #111827;
                color: {COLORS['primary']};
                border-bottom: 2px solid {COLORS['primary']};
            }}
            QTabBar::tab:hover {{
                background: #1E293B;
            }}
        """)
        
        self._rebuild_milestone_format_tabs()
        
        layout.addWidget(self._milestone_format_tabs, 1)
        
        widget.setLayout(layout)
        return widget
    
    def _create_format_stats_tab(self, format_type):
        """Create a season-by-season stats table for a specific format"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 5, 0, 0)
        
        table = QTableWidget()
        table.setStyleSheet(f"""
            QTableWidget {{
                border: 1px solid {COLORS['border_light']};
                gridline-color: #334155;
                background: #111827;
                font-size: 12px;
            }}
            QHeaderView::section {{
                background-color: {COLORS['primary']};
                color: white;
                padding: 8px 4px;
                border: 1px solid {COLORS['border_light']};
                font-weight: bold;
                font-size: 11px;
            }}
            QTableWidget::item {{
                padding: 6px 4px;
            }}
        """)
        
        headers = [
            'Year', 'Age', 'Mat', 'Runs', 'Bat Avg', 'SR', 'HS', '100s', '50s',
            'Wkts', 'Bowl Avg', 'Bowl SR', 'Econ', '5W'
        ]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        table.setMinimumHeight(420)
        table.horizontalHeader().setMinimumSectionSize(55)
        table.horizontalHeader().setDefaultSectionSize(70)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        yearly_data = self._profile_yearly_root()
        
        # Filter years that have data for this format
        years_with_data = []
        try:
            for year in sorted(yearly_data.keys(), reverse=True):
                fs = yearly_data.get(year, {}).get(format_type, {})
                if fs.get('matches', 0) > 0:
                    years_with_data.append(year)
        except (TypeError, AttributeError):
            years_with_data = []
        
        table.setRowCount(len(years_with_data))
        
        current_age = self.player.age
        try:
            current_year = max(yearly_data.keys()) if yearly_data else 0
        except (TypeError, ValueError):
            current_year = 0
        
        for row, year in enumerate(years_with_data):
            fs = yearly_data[year].get(format_type, {})
            
            matches = fs.get('matches', 0)
            runs = fs.get('runs', 0)
            balls_faced = fs.get('balls_faced', 0)
            wickets = fs.get('wickets', 0)
            balls_bowled = fs.get('balls_bowled', 0)
            runs_conceded = fs.get('runs_conceded', 0)
            centuries = fs.get('centuries', 0)
            fifties = fs.get('fifties', 0)
            five_w = fs.get('five_wickets', 0)
            highest = fs.get('highest_score', 0)
            
            bat_avg = runs / matches if matches > 0 else 0
            sr = (runs / balls_faced * 100) if balls_faced > 0 else 0
            bowl_avg = runs_conceded / wickets if wickets > 0 else 0
            bowl_sr = balls_bowled / wickets if wickets > 0 else 0
            econ = (runs_conceded / (balls_bowled / 6)) if balls_bowled > 0 else 0
            
            player_age = current_age - (current_year - year)
            
            values = [
                str(year), str(player_age), str(matches), str(runs),
                f"{bat_avg:.1f}", f"{sr:.1f}", str(highest),
                str(centuries), str(fifties),
                str(wickets), f"{bowl_avg:.1f}" if wickets > 0 else "-",
                f"{bowl_sr:.1f}" if wickets > 0 else "-",
                f"{econ:.1f}" if balls_bowled > 0 else "-", str(five_w)
            ]
            
            for col, val in enumerate(values):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if col == 0:
                    item.setFont(QFont('Arial', 11, QFont.Weight.Bold))
                table.setItem(row, col, item)
            
            table.setRowHeight(row, 35)
        
        if not years_with_data:
            table.setRowCount(1)
            no_data = QTableWidgetItem(f"No {format_type} data available yet.")
            no_data.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            no_data.setFont(QFont('Arial', 11))
            table.setItem(0, 0, no_data)
            table.setSpan(0, 0, 1, len(headers))
        
        layout.addWidget(table, 1)
        widget.setLayout(layout)
        return widget
    
    def refresh_traits(self):
        """Public method to refresh traits display - call when reopening dialog"""
        if hasattr(self, '_refresh_traits_content'):
            self._refresh_traits_content()
    
    def create_bowling_movements_section(self):
        """Create bowling movements section with dynamic attributes"""
        from cricket_manager.systems.bowling_movements import get_movement_display_name, format_movement_rating
        
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: #111827;
                border: 1px solid {COLORS['border_light']};
                border-radius: 5px;
                padding: 15px;
                margin: 5px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Bowling Movements")
        title_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COLORS['primary']};")
        layout.addWidget(title_label)
        
        # Get bowling movements data
        movements_data = self.player.bowling_movements
        bowler_type = movements_data.get('bowler_type', 'pace').title()
        movements = movements_data.get('movements', {})
        
        # Bowler type label
        type_label = QLabel(f"Type: {bowler_type}")
        type_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #B8C3D9; margin-bottom: 10px;")
        layout.addWidget(type_label)
        
        # Create grid for movements
        grid = QGridLayout()
        row = 0
        
        # Sort movements: major movements first, then by rating
        sorted_movements = sorted(
            movements.items(), 
            key=lambda x: (0 if x[1]['category'] == 'major' else 1, -x[1]['rating'])
        )
        
        for movement_type, movement_data in sorted_movements:
            rating = movement_data['rating']
            category = movement_data['category']
            
            # Movement name
            name_label = QLabel(f"{get_movement_display_name(movement_type)}:")
            name_label.setStyleSheet("font-weight: bold;")
            grid.addWidget(name_label, row, 0)
            
            # Rating with star for major movements
            rating_text = format_movement_rating(rating, category)
            rating_label = QLabel(rating_text)
            
            # Color coding based on rating
            if rating >= 80:
                color = "#27ae60"  # Green
            elif rating >= 60:
                color = "#f39c12"  # Orange
            else:
                color = "#e74c3c"  # Red
            
            rating_label.setStyleSheet(f"color: {color}; font-weight: bold;")
            grid.addWidget(rating_label, row, 1)
            
            # Progress bar
            bar = self.create_progress_bar(rating, 100)
            grid.addWidget(bar, row, 2)
            
            row += 1
        
        layout.addLayout(grid)
        frame.setLayout(layout)
        return frame
    
    def _apply_player_profile_initial_geometry(self):
        """
        Fill the available screen area with a tiny margin so the title bar,
        all content, and the taskbar are fully visible and the window can be
        dragged / resized if needed.
        """
        if self.isFullScreen():
            self.showNormal()
        screen = None
        app = QApplication.instance()
        if app is not None:
            screen = app.primaryScreen()
        if screen is None:
            self.resize(1200, 800)
        else:
            ag = screen.availableGeometry()
            m = 6
            self.setGeometry(ag.x() + m, ag.y() + m, ag.width() - 2 * m, ag.height() - 2 * m)
        self.raise_()
        self.activateWindow()
    
    def keyPressEvent(self, event):
        """Esc: close the profile dialog."""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
            event.accept()
            return
        super().keyPressEvent(event)
    
    def showEvent(self, event):
        """First show: maximize inside the work area with a visible title bar; refresh traits when shown."""
        super().showEvent(event)
        if not getattr(self, "_profile_initial_geometry_done", False):
            self._profile_initial_geometry_done = True
            QTimer.singleShot(0, self._apply_player_profile_initial_geometry)
        self.refresh_traits()
        if (
            getattr(self, "_profile_tabs", None)
            and self._career_history_tab_index is not None
            and self._profile_tabs.currentIndex() == self._career_history_tab_index
        ):
            self._refresh_career_history_tab()
