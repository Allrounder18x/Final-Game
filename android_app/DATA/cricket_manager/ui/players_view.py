"""
Enhanced Players Screen - View players with detailed statistics
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QFrame,
    QScrollArea, QHeaderView, QLineEdit, QTabWidget, QDialog
)
from PyQt6.QtWidgets import QAbstractItemView
from PyQt6.QtCore import Qt

from cricket_manager.ui.styles import COLORS, get_skill_color, MAIN_STYLESHEET
from cricket_manager.ui.screen_manager import BaseScreen


class PlayersScreen(BaseScreen):
    """Enhanced players screen with statistics"""
    
    def __init__(self, screen_manager=None, game_engine=None):
        super().__init__(screen_manager)
        self.setStyleSheet(MAIN_STYLESHEET)
        self.game_engine = game_engine
        self.current_format = "T20"
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Filters
        filters = self.create_filters()
        layout.addWidget(filters)
        
        # Tabs for different views - Only All Players tab
        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {COLORS['border']};
                background-color: #111827;
            }}
            QTabBar::tab {{
                background-color: {COLORS['bg_tertiary']};
                color: #EAF1FF;
                padding: 12px 24px;
                margin-right: 2px;
                font-size: 13px;
                font-weight: 600;
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS['primary']};
                color: white;
            }}
        """)
        
        # All Players tab
        self.all_players_tab = self.create_all_players_tab()
        tabs.addTab(self.all_players_tab, "👥 All Players")
        
        layout.addWidget(tabs, 1)
        self.setLayout(layout)
    
    def create_filters(self):
        """Create filter controls with team filter"""
        container = QFrame()
        container.setFixedHeight(50)
        container.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {COLORS['primary']}, stop:1 {COLORS['secondary']});
            padding: 0px 20px;
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)
        
        # Title
        title = QLabel("👥 Players & Statistics")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: white;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Team filter
        team_label = QLabel("Team:")
        team_label.setStyleSheet("font-size: 13px; font-weight: 600; color: white;")
        layout.addWidget(team_label)
        
        self.team_combo = QComboBox()
        self.team_combo.addItem("All Teams")
        if self.game_engine:
            # Add senior teams
            for team in sorted(self.game_engine.all_teams, key=lambda t: t.name):
                self.team_combo.addItem(team.name)
            # Add U21 teams
            for team in sorted(self.game_engine.all_teams, key=lambda t: t.name):
                if hasattr(team, 'u21_squad') and team.u21_squad:
                    self.team_combo.addItem(f"{team.name} U21")
            # Domestic club teams
            domestic = getattr(self.game_engine, 'domestic_teams', None) or []
            for dteam in sorted(domestic, key=lambda t: t.name):
                self.team_combo.addItem(dteam.name)
        self.team_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: #111827;
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                min-width: 150px;
            }}
        """)
        self.team_combo.currentTextChanged.connect(self.refresh_players_table)
        layout.addWidget(self.team_combo)
        
        layout.addSpacing(20)
        
        # Player search
        search_label = QLabel("Search:")
        search_label.setStyleSheet("font-size: 13px; font-weight: 600; color: white;")
        layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type player name...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: #111827;
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                min-width: 200px;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORS['primary']};
            }}
        """)
        self.search_input.textChanged.connect(self.refresh_players_table)
        layout.addWidget(self.search_input)
        
        layout.addSpacing(20)
        
        # Format selector
        format_label = QLabel("Format:")
        format_label.setStyleSheet("font-size: 13px; font-weight: 600; color: white;")
        layout.addWidget(format_label)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["T20", "ODI", "Test"])
        self.format_combo.setCurrentText(self.current_format)
        self.format_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: #111827;
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                min-width: 100px;
            }}
        """)
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        layout.addWidget(self.format_combo)
        
        container.setLayout(layout)
        return container
    
    def create_all_players_tab(self):
        """Create all players table with refresh capability"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Create table and store reference
        self.players_table = QTableWidget()
        self.players_table.setColumnCount(9)
        self.players_table.setHorizontalHeaderLabels([
            "Player", "Team", "Age", "Role", "Bat", "Bowl", "Field", "Form", "Traits"
        ])
        
        self.style_table(self.players_table)
        
        # Initial population
        self.refresh_players_table()
        
        layout.addWidget(self.players_table)
        widget.setLayout(layout)
        return widget
    
    def _format_team_column_text(self, player, team, is_u21):
        """One cell: national + FC/ODI + T20 domestic labels for internationals; no extra table rows."""
        if is_u21:
            return f"{team.name} U21"
        if getattr(team, "is_domestic", False):
            return team.name
        odi = (getattr(player, "domestic_odi_fc_club_name", None) or "").strip()
        t20 = (getattr(player, "domestic_t20_club_name", None) or "").strip()
        parts = [team.name]
        if odi:
            parts.append(odi)
        if t20 and t20 != odi:
            parts.append(t20)
        return " · ".join(parts)
    
    def _collect_players_overview_data(self, selected_team: str):
        """
        Build (player, team, is_u21) rows. For 'All Teams', each player appears once (dedupe by id):
        prefer international senior, else U21 parent, else domestic-only roster.
        """
        ge = self.game_engine
        rows = []
        if selected_team == "All Teams":
            seen = set()
            for team in ge.all_teams:
                if getattr(team, "is_domestic", False):
                    continue
                for player in team.players:
                    pid = id(player)
                    if pid in seen:
                        continue
                    seen.add(pid)
                    rows.append((player, team, False))
            for team in ge.all_teams:
                if getattr(team, "is_domestic", False):
                    continue
                for player in getattr(team, "u21_squad", None) or []:
                    pid = id(player)
                    if pid in seen:
                        continue
                    seen.add(pid)
                    rows.append((player, team, True))
            for dteam in getattr(ge, "domestic_teams", None) or []:
                for player in dteam.players:
                    pid = id(player)
                    if pid in seen:
                        continue
                    seen.add(pid)
                    rows.append((player, dteam, False))
            return rows
        for team in ge.all_teams:
            if getattr(team, "is_domestic", False):
                continue
            if team.name == selected_team:
                for player in team.players:
                    rows.append((player, team, False))
            u21_team_name = f"{team.name} U21"
            if selected_team == u21_team_name:
                for player in getattr(team, "u21_squad", None) or []:
                    rows.append((player, team, True))
        for dteam in getattr(ge, "domestic_teams", None) or []:
            if dteam.name == selected_team:
                for player in dteam.players:
                    rows.append((player, dteam, False))
        return rows
    
    def refresh_players_table(self):
        """Refresh the players table with current data and filters"""
        if not hasattr(self, 'players_table') or not self.game_engine:
            return
        
        table = self.players_table
        
        # Get filter values
        selected_team = self.team_combo.currentText() if hasattr(self, 'team_combo') else "All Teams"
        search_text = self.search_input.text().strip().lower() if hasattr(self, 'search_input') else ""
        
        players_data = self._collect_players_overview_data(selected_team)
        
        # Apply search filter (forename, surname, or full name)
        if search_text:
            filtered_data = []
            for item in players_data:
                player, team, is_u21 = item[0], item[1], item[2]
                player_name = player.name.lower()
                # Check if search text matches any part of the name
                if search_text in player_name:
                    filtered_data.append(item)
                else:
                    # Also check individual name parts (forename/surname)
                    name_parts = player_name.split()
                    for part in name_parts:
                        if search_text in part:
                            filtered_data.append(item)
                            break
            players_data = filtered_data
        
        # Update table
        table.setRowCount(len(players_data))
        for row, item in enumerate(players_data):
            player, team, is_u21 = item[0], item[1], item[2]
            team_display = self._format_team_column_text(player, team, is_u21)
            hide_bat_bowl = getattr(self.game_engine, 'hide_batting_bowling_ratings', False) if self.game_engine else False
            table.setItem(row, 0, self.create_table_item(player.name))
            table.setItem(row, 1, self.create_table_item(team_display))
            table.setItem(row, 2, self.create_table_item(str(player.age), center=True))
            table.setItem(row, 3, self.create_table_item(player.role))
            table.setItem(row, 4, self.create_table_item("—", center=True) if hide_bat_bowl else self.create_skill_item(player.batting))
            table.setItem(row, 5, self.create_table_item("—", center=True) if hide_bat_bowl else self.create_skill_item(player.bowling))
            table.setItem(row, 6, self.create_skill_item(player.fielding))
            table.setItem(row, 7, self.create_skill_item(player.form))
            table.setItem(row, 8, self.create_table_item(str(len(player.traits)), center=True))
        
        # Store data (player, team) for profile; team is always real (parent for U21)
        self.players_overview_data = [(item[0], item[1]) for item in players_data]
        try:
            table.cellClicked.disconnect()
        except TypeError:
            pass
        table.cellClicked.connect(lambda row, col: self.on_player_double_click(row, col, 'overview'))
    
    def create_batting_stats_tab(self):
        """Create batting statistics table - DEPRECATED, kept for compatibility"""
        widget = QWidget()
        layout = QVBoxLayout()
        label = QLabel("Batting statistics now shown in All Players tab")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        widget.setLayout(layout)
        return widget
    
    def create_bowling_stats_tab(self):
        """Create bowling statistics table - DEPRECATED, kept for compatibility"""
        widget = QWidget()
        layout = QVBoxLayout()
        label = QLabel("Bowling statistics now shown in All Players tab")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        widget.setLayout(layout)
        return widget
    
    def style_table(self, table):
        """Apply consistent styling to table"""
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: #111827;
                alternate-background-color: {COLORS['bg_tertiary']};
                border: none;
                gridline-color: {COLORS['border']};
                font-size: 12px;
            }}
            QTableWidget::item {{
                padding: 8px;
                color: {COLORS['text_primary']};
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['primary_light']};
                color: {COLORS['text_primary']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['primary']};
                color: white;
                padding: 10px;
                border: none;
                font-weight: 700;
                font-size: 12px;
            }}
        """)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setVisible(False)
    
    def create_table_item(self, text, center=False):
        """Create a table item"""
        item = QTableWidgetItem(text)
        if center:
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item
    
    def create_skill_item(self, value):
        """Create a colored skill item"""
        item = QTableWidgetItem(str(value))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        color = get_skill_color(value)
        item.setForeground(Qt.GlobalColor.white if value >= 80 else Qt.GlobalColor.black)
        from PyQt6.QtGui import QColor, QBrush
        item.setBackground(QBrush(QColor(color)))
        return item
    
    def on_format_changed(self, format_type):
        """Handle format change"""
        self.current_format = format_type
        # Refresh the players table
        self.refresh_players_table()
    
    def on_player_double_click(self, row, col, tab_type):
        """Handle player double-click from any tab"""
        try:
            if tab_type == 'overview' and hasattr(self, 'players_overview_data'):
                if row < len(self.players_overview_data):
                    player, team = self.players_overview_data[row]
                    self.show_player_details(player, team)
            elif tab_type == 'batting' and hasattr(self, 'players_batting_data'):
                if row < len(self.players_batting_data):
                    player, team, _ = self.players_batting_data[row]
                    self.show_player_details(player, team)
            elif tab_type == 'bowling' and hasattr(self, 'players_bowling_data'):
                if row < len(self.players_bowling_data):
                    player, team, _ = self.players_bowling_data[row]
                    self.show_player_details(player, team)
        except Exception as e:
            print(f"Error showing player details: {e}")
    
    def show_player_details(self, player, team):
        """Show detailed player information"""
        from cricket_manager.ui.player_profile_dialog import PlayerProfileDialog
        dialog = PlayerProfileDialog(self, player, team, self.game_engine)
        dialog.exec()
    
    def refresh_data(self):
        """Refresh all data - called after season simulation"""
        # Update team filter dropdown (in case teams were added/removed)
        if hasattr(self, 'team_combo') and self.game_engine:
            current_selection = self.team_combo.currentText()
            self.team_combo.blockSignals(True)
            self.team_combo.clear()
            self.team_combo.addItem("All Teams")
            # Add senior teams
            for team in sorted(self.game_engine.all_teams, key=lambda t: t.name):
                self.team_combo.addItem(team.name)
            # Add U21 teams
            for team in sorted(self.game_engine.all_teams, key=lambda t: t.name):
                if hasattr(team, 'u21_squad') and team.u21_squad:
                    self.team_combo.addItem(f"{team.name} U21")
            for dteam in sorted(getattr(self.game_engine, 'domestic_teams', None) or [], key=lambda t: t.name):
                self.team_combo.addItem(dteam.name)
            # Restore previous selection if it still exists
            index = self.team_combo.findText(current_selection)
            if index >= 0:
                self.team_combo.setCurrentIndex(index)
            self.team_combo.blockSignals(False)
        
        # Refresh the players table
        self.refresh_players_table()


class PlayerDetailsDialog(QDialog):
    """Dialog showing detailed player information"""
    
    def __init__(self, parent, player, team, format_type):
        super().__init__(parent)
        self.player = player
        self.team = team
        self.format_type = format_type
        
        self.setWindowTitle(f"{player.name} - Player Details")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Header
        header = QLabel(f"{self.player.name}")
        header.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 700;
            color: {COLORS['primary']};
            padding: 20px;
        """)
        layout.addWidget(header)
        
        # Basic info
        engine = getattr(self.parent(), 'game_engine', None) if self.parent() else None
        hide_bat_bowl = getattr(engine, 'hide_batting_bowling_ratings', False) if engine else False
        if hide_bat_bowl:
            skills_line = "Fielding: {0} | Form: {1}".format(self.player.fielding, self.player.form)
        else:
            skills_line = "Batting: {0} | Bowling: {1} | Fielding: {2}<br>Form: {3}".format(
                self.player.batting, self.player.bowling, self.player.fielding, self.player.form)
        info_text = f"""
        <b>Team:</b> {self.team.name}<br>
        <b>Age:</b> {self.player.age}<br>
        <b>Role:</b> {self.player.role}<br>
        <b>Nationality:</b> {self.player.nationality}<br><br>
        <b>Skills:</b><br>
        {skills_line}<br><br>
        <b>Traits:</b> {len(self.player.traits)}<br>
        """
        
        for trait in self.player.traits:
            if isinstance(trait, dict):
                info_text += f"• {trait.get('name', 'Unknown')} (Level {trait.get('strength', 1)})<br>"
        
        info_label = QLabel(info_text)
        info_label.setStyleSheet("font-size: 13px; padding: 20px;")
        layout.addWidget(info_label)
        
        # Statistics
        stats = self.player.stats.get(self.format_type, {})
        if stats:
            stats_text = f"""
            <b>{self.format_type} Statistics:</b><br>
            Matches: {stats.get('matches', 0)}<br>
            Runs: {stats.get('runs', 0)} | Balls: {stats.get('balls_faced', 0)} | SR: {stats.get('strike_rate', 0):.2f}<br>
            Highest Score: {stats.get('highest_score', 0)} | 100s: {stats.get('centuries', 0)} | 50s: {stats.get('fifties', 0)}<br>
            Wickets: {stats.get('wickets', 0)} | Balls Bowled: {stats.get('balls_bowled', 0)}<br>
            Bowling Avg: {stats.get('bowling_average', 0):.2f} | Economy: {stats.get('economy_rate', 0):.2f}<br>
            5-wicket hauls: {stats.get('five_wickets', 0)}
            """
            stats_label = QLabel(stats_text)
            stats_label.setStyleSheet("font-size: 13px; padding: 20px; background-color: #0B1220;")
            layout.addWidget(stats_label)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
