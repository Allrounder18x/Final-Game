"""
Enhanced Players Screen - View players with detailed statistics
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QFrame,
    QScrollArea, QHeaderView, QLineEdit, QTabWidget, QDialog
)
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
        
        # Tabs for different views
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
        tabs.addTab(self.create_all_players_tab(), "👥 All Players")
        
        # Batting Stats tab
        tabs.addTab(self.create_batting_stats_tab(), "🏏 Batting Stats")
        
        # Bowling Stats tab
        tabs.addTab(self.create_bowling_stats_tab(), "⚾ Bowling Stats")
        
        layout.addWidget(tabs, 1)
        self.setLayout(layout)
    
    def create_filters(self):
        """Create filter controls"""
        container = QFrame()
        container.setStyleSheet(f"""
            background-color: #111827;
            border: 1px solid {COLORS['border']};
            padding: 15px 30px;
        """)
        
        layout = QHBoxLayout()
        
        # Title
        title = QLabel("Players & Statistics")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #EAF1FF;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Format selector
        format_label = QLabel("Format:")
        format_label.setStyleSheet("font-size: 13px; font-weight: 600;")
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
        """Create all players table"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Table
        table = QTableWidget()
        table.setColumnCount(9)
        table.setHorizontalHeaderLabels([
            "Player", "Team", "Age", "Role", "Bat", "Bowl", "Field", "Form", "Traits"
        ])
        
        self.style_table(table)
        
        # Populate with real data
        if self.game_engine:
            players_data = []
            for team in self.game_engine.all_teams:
                for player in team.players:
                    players_data.append((player, team))
            
            table.setRowCount(len(players_data))
            for row, (player, team) in enumerate(players_data[:100]):  # Limit to 100 for performance
                table.setItem(row, 0, self.create_table_item(player.name))
                table.setItem(row, 1, self.create_table_item(team.name))
                table.setItem(row, 2, self.create_table_item(str(player.age), center=True))
                table.setItem(row, 3, self.create_table_item(player.role))
                table.setItem(row, 4, self.create_skill_item(player.batting))
                table.setItem(row, 5, self.create_skill_item(player.bowling))
                table.setItem(row, 6, self.create_skill_item(player.fielding))
                table.setItem(row, 7, self.create_skill_item(player.form))
                table.setItem(row, 8, self.create_table_item(str(len(player.traits)), center=True))
                
                # Make row clickable
                table.cellDoubleClicked.connect(lambda r, c, p=player, t=team: self.show_player_details(p, t))
        
        layout.addWidget(table)
        widget.setLayout(layout)
        return widget
    
    def create_batting_stats_tab(self):
        """Create batting statistics table"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Table
        table = QTableWidget()
        table.setColumnCount(10)
        table.setHorizontalHeaderLabels([
            "Player", "Team", "Mat", "Runs", "Balls", "HS", "Avg", "SR", "100s", "50s"
        ])
        
        self.style_table(table)
        
        # Populate with real data
        if self.game_engine:
            players_data = []
            for team in self.game_engine.all_teams:
                for player in team.players:
                    stats = player.stats.get(self.current_format, {})
                    if stats.get('runs', 0) > 0:  # Only show players with runs
                        players_data.append((player, team, stats))
            
            # Sort by runs
            players_data.sort(key=lambda x: x[2].get('runs', 0), reverse=True)
            
            table.setRowCount(len(players_data))
            for row, (player, team, stats) in enumerate(players_data[:100]):
                table.setItem(row, 0, self.create_table_item(player.name))
                table.setItem(row, 1, self.create_table_item(team.name))
                table.setItem(row, 2, self.create_table_item(str(stats.get('matches', 0)), center=True))
                table.setItem(row, 3, self.create_table_item(str(stats.get('runs', 0)), center=True))
                table.setItem(row, 4, self.create_table_item(str(stats.get('balls_faced', 0)), center=True))
                table.setItem(row, 5, self.create_table_item(str(stats.get('highest_score', 0)), center=True))
                
                # Calculate average
                runs = stats.get('runs', 0)
                matches = stats.get('matches', 0)
                avg = f"{runs/matches:.2f}" if matches > 0 else "0.00"
                table.setItem(row, 6, self.create_table_item(avg, center=True))
                
                # Strike rate
                sr = f"{stats.get('strike_rate', 0):.2f}"
                table.setItem(row, 7, self.create_table_item(sr, center=True))
                
                table.setItem(row, 8, self.create_table_item(str(stats.get('centuries', 0)), center=True))
                table.setItem(row, 9, self.create_table_item(str(stats.get('fifties', 0)), center=True))
        
        layout.addWidget(table)
        widget.setLayout(layout)
        return widget
    
    def create_bowling_stats_tab(self):
        """Create bowling statistics table"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Table
        table = QTableWidget()
        table.setColumnCount(9)
        table.setHorizontalHeaderLabels([
            "Player", "Team", "Mat", "Wkts", "Balls", "Runs", "Avg", "Econ", "5W"
        ])
        
        self.style_table(table)
        
        # Populate with real data
        if self.game_engine:
            players_data = []
            for team in self.game_engine.all_teams:
                for player in team.players:
                    stats = player.stats.get(self.current_format, {})
                    if stats.get('wickets', 0) > 0:  # Only show players with wickets
                        players_data.append((player, team, stats))
            
            # Sort by wickets
            players_data.sort(key=lambda x: x[2].get('wickets', 0), reverse=True)
            
            table.setRowCount(len(players_data))
            for row, (player, team, stats) in enumerate(players_data[:100]):
                table.setItem(row, 0, self.create_table_item(player.name))
                table.setItem(row, 1, self.create_table_item(team.name))
                table.setItem(row, 2, self.create_table_item(str(stats.get('matches', 0)), center=True))
                table.setItem(row, 3, self.create_table_item(str(stats.get('wickets', 0)), center=True))
                table.setItem(row, 4, self.create_table_item(str(stats.get('balls_bowled', 0)), center=True))
                table.setItem(row, 5, self.create_table_item(str(stats.get('runs_conceded', 0)), center=True))
                
                # Calculate average
                avg = f"{stats.get('bowling_average', 0):.2f}"
                table.setItem(row, 6, self.create_table_item(avg, center=True))
                
                # Economy rate
                econ = f"{stats.get('economy_rate', 0):.2f}"
                table.setItem(row, 7, self.create_table_item(econ, center=True))
                
                table.setItem(row, 8, self.create_table_item(str(stats.get('five_wickets', 0)), center=True))
        
        layout.addWidget(table)
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
        # Refresh tabs
        # TODO: Implement tab refresh
    
    def show_player_details(self, player, team):
        """Show detailed player information"""
        from cricket_manager.ui.player_profile_dialog import PlayerProfileDialog
        dialog = PlayerProfileDialog(self, player, team, self.game_engine)
        dialog.exec()
    
    def refresh_data(self):
        """Refresh all data"""
        # Recreate UI
        pass


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
        info_text = f"""
        <b>Team:</b> {self.team.name}<br>
        <b>Age:</b> {self.player.age}<br>
        <b>Role:</b> {self.player.role}<br>
        <b>Nationality:</b> {self.player.nationality}<br><br>
        <b>Skills:</b><br>
        Batting: {self.player.batting} | Bowling: {self.player.bowling} | Fielding: {self.player.fielding}<br>
        Form: {self.player.form}<br><br>
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
