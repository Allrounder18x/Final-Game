"""
Statistics Screen - Comprehensive batting and bowling stats across all seasons
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QFrame,
    QHeaderView, QTabWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from cricket_manager.ui.styles import COLORS, MAIN_STYLESHEET
from cricket_manager.ui.screen_manager import BaseScreen


class StatisticsScreen(BaseScreen):
    """Comprehensive statistics screen"""
    
    def __init__(self, screen_manager=None, game_engine=None):
        super().__init__(screen_manager)
        self.setStyleSheet(MAIN_STYLESHEET)
        self.game_engine = game_engine
        self.current_format = "T20"
        self.current_season = "All Stats"  # "All Stats" for cumulative, or season number
        self.stats_scope = "all"  # all | international | associate_international | domestic | u21
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Format and Tier selector
        format_bar = self.create_format_bar()
        layout.addWidget(format_bar)
        
        # Team filter
        team_filter_bar = self.create_team_filter_bar()
        layout.addWidget(team_filter_bar)
        
        # Tabs for batting/bowling
        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background: #111827;
            }}
            QTabBar::tab {{
                background: {COLORS['bg_secondary']};
                padding: 12px 25px;
                margin-right: 2px;
                font-size: 13px;
                font-weight: bold;
            }}
            QTabBar::tab:selected {{
                background: {COLORS['primary']};
                color: white;
            }}
        """)
        
        tabs.addTab(self.create_batting_tab(), "🏏 Batting Statistics")
        tabs.addTab(self.create_bowling_tab(), "⚾ Bowling Statistics")
        tabs.addTab(self.create_allrounder_tab(), "🌟 All-Rounders")
        
        layout.addWidget(tabs, 1)
        
        self.setLayout(layout)
    
    def create_header(self):
        """Create compact header section"""
        header = QFrame()
        header.setFixedHeight(50)
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary']}, stop:1 {COLORS['secondary']});
                padding: 0px 20px;
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)
        
        title = QLabel("📊 Career Statistics")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        layout.addWidget(title)
        
        subtitle = QLabel("Cumulative stats across all seasons and match types")
        subtitle.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.8); margin-left: 10px;")
        layout.addWidget(subtitle)
        
        layout.addStretch()
        
        header.setLayout(layout)
        return header
    
    def create_format_bar(self):
        """Create format and tier selector bar"""
        bar = QFrame()
        bar.setStyleSheet(f"""
            QFrame {{
                background: #111827;
                border-bottom: 2px solid {COLORS['border_light']};
                padding: 15px 20px;
            }}
        """)
        
        layout = QHBoxLayout()
        
        # Format selector
        layout.addWidget(QLabel("Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(['T20', 'ODI', 'Test', 'All Formats'])
        self.format_combo.setCurrentText(self.current_format)
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        self.format_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 8px 15px;
                border: 1px solid {COLORS['border_light']};
                border-radius: 5px;
                min-width: 120px;
                font-size: 13px;
            }}
        """)
        layout.addWidget(self.format_combo)
        
        layout.addSpacing(20)
        
        layout.addWidget(QLabel("Scope:"))
        self.scope_combo = QComboBox()
        self.scope_combo.addItem("All cricket (domestic + international)", "all")
        self.scope_combo.addItem("Senior international (full member)", "international")
        self.scope_combo.addItem("Associate international", "associate_international")
        self.scope_combo.addItem("Domestic only (club / league)", "domestic")
        self.scope_combo.addItem("U21 international (youth squad)", "u21")
        self.scope_combo.setCurrentIndex(0)
        self.scope_combo.currentIndexChanged.connect(self.on_stats_scope_changed)
        self.scope_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 8px 15px;
                border: 1px solid {COLORS['border_light']};
                border-radius: 5px;
                min-width: 220px;
                font-size: 13px;
            }}
        """)
        layout.addWidget(self.scope_combo)
        
        layout.addSpacing(20)
        
        # Tier selector
        layout.addWidget(QLabel("Tier:"))
        self.tier_combo = QComboBox()
        self.tier_combo.addItems(['All Tiers', 'Tier 1', 'Tier 2', 'Tier 3', 'Tier 4'])
        self.tier_combo.setCurrentText("All Tiers")
        self.tier_combo.currentTextChanged.connect(self.on_tier_changed)
        self.tier_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 8px 15px;
                border: 1px solid {COLORS['border_light']};
                border-radius: 5px;
                min-width: 100px;
                font-size: 13px;
            }}
        """)
        layout.addWidget(self.tier_combo)
        
        layout.addSpacing(20)
        
        # Season filter
        layout.addWidget(QLabel("Season:"))
        self.season_combo = QComboBox()
        self.season_combo.addItem("All Stats")  # Cumulative stats
        # Add seasons as years (most recent first)
        if self.game_engine:
            current_season = self.game_engine.current_season
            current_year = self.game_engine.current_year
            # Calculate base year (year when season 1 started)
            base_year = current_year - current_season + 1
            for s in range(current_season, 0, -1):
                year = base_year + s - 1
                self.season_combo.addItem(str(year))
        self.season_combo.setCurrentText("All Stats")
        self.season_combo.currentTextChanged.connect(self.on_season_changed)
        self.season_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 8px 15px;
                border: 1px solid {COLORS['border_light']};
                border-radius: 5px;
                min-width: 120px;
                font-size: 13px;
            }}
        """)
        layout.addWidget(self.season_combo)
        
        layout.addStretch()
        
        # Stats info
        if self.game_engine:
            _tu = self._teams_for_statistics()
            info = QLabel(f"Season {self.game_engine.current_season} • "
                         f"{len(_tu)} Teams • "
                         f"{sum(len(t.players) for t in _tu)} Players")
            info.setStyleSheet("color: gray; font-size: 12px;")
            layout.addWidget(info)
        
        bar.setLayout(layout)
        return bar
    
    def create_team_filter_bar(self):
        """Create team filter bar"""
        bar = QFrame()
        bar.setStyleSheet(f"""
            QFrame {{
                background-color: #111827;
                border-bottom: 1px solid {COLORS['border_light']};
                padding: 10px 20px;
            }}
        """)
        
        layout = QHBoxLayout()
        
        layout.addWidget(QLabel("Team:"))
        self.team_combo = QComboBox()
        self.team_combo.addItem("All Teams")
        if self.game_engine:
            for team in sorted(self.game_engine.all_teams, key=lambda t: t.name):
                self.team_combo.addItem(team.name)
            for dteam in sorted(getattr(self.game_engine, 'domestic_teams', None) or [], key=lambda t: t.name):
                self.team_combo.addItem(dteam.name)
        self.team_combo.setCurrentText("All Teams")
        self.team_combo.currentTextChanged.connect(self.on_team_changed)
        self.team_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 8px 15px;
                border: 1px solid {COLORS['border_light']};
                border-radius: 5px;
                min-width: 150px;
                font-size: 13px;
            }}
        """)
        layout.addWidget(self.team_combo)
        
        layout.addStretch()
        
        bar.setLayout(layout)
        return bar
    
    def create_batting_tab(self):
        """Create batting statistics tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Info label
        info_label = QLabel("💡 Double-click on any player row to view their profile")
        info_label.setStyleSheet("font-size: 12px; color: #666; padding: 5px; font-style: italic;")
        layout.addWidget(info_label)
        
        # Table
        table = QTableWidget()
        table.setColumnCount(11)
        table.setHorizontalHeaderLabels([
            "Rank", "Player", "Team", "Mat", "Runs", "Balls", "HS", "Avg", "SR", "100s", "50s"
        ])
        
        self.style_table(table)
        self.batting_table = table
        self.batting_players_data = []  # Store player data for click handling
        self.load_batting_stats()
        
        # Connect double-click to open player profile
        table.cellDoubleClicked.connect(self.on_batting_player_clicked)
        
        layout.addWidget(table)
        widget.setLayout(layout)
        return widget
    
    def create_bowling_tab(self):
        """Create bowling statistics tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Info label
        info_label = QLabel("💡 Double-click on any player row to view their profile")
        info_label.setStyleSheet("font-size: 12px; color: #666; padding: 5px; font-style: italic;")
        layout.addWidget(info_label)
        
        # Table
        table = QTableWidget()
        table.setColumnCount(11)
        table.setHorizontalHeaderLabels([
            "Rank", "Player", "Team", "Mat", "Wkts", "Balls", "Runs", "Avg", "Econ", "SR", "5W"
        ])
        
        self.style_table(table)
        self.bowling_table = table
        self.bowling_players_data = []  # Store player data for click handling
        self.load_bowling_stats()
        
        # Connect double-click to open player profile
        table.cellDoubleClicked.connect(self.on_bowling_player_clicked)
        
        layout.addWidget(table)
        widget.setLayout(layout)
        return widget
    
    def create_allrounder_tab(self):
        """Create all-rounder statistics tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Info label
        info_label = QLabel("💡 Double-click on any player row to view their profile")
        info_label.setStyleSheet("font-size: 12px; color: #666; padding: 5px; font-style: italic;")
        layout.addWidget(info_label)
        
        # Table
        table = QTableWidget()
        table.setColumnCount(9)
        table.setHorizontalHeaderLabels([
            "Rank", "Player", "Team", "Mat", "Runs", "Bat Avg", "Wickets", "Bowl Avg", "Rating"
        ])
        
        self.style_table(table)
        self.allrounder_table = table
        self.allrounder_players_data = []  # Store player data for click handling
        self.load_allrounder_stats()
        
        # Connect double-click to open player profile
        table.cellDoubleClicked.connect(self.on_allrounder_player_clicked)
        
        layout.addWidget(table)
        widget.setLayout(layout)
        return widget
    
    def style_table(self, table):
        """Apply consistent table styling"""
        table.setStyleSheet(f"""
            QTableWidget {{
                border: none;
                background-color: #111827;
                gridline-color: {COLORS['border_light']};
            }}
            QTableWidget::item {{
                padding: 10px;
                border-bottom: 1px solid {COLORS['border_light']};
                color: {COLORS['text_primary']};
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['highlight_blue']};
                color: {COLORS['text_primary']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['primary']};
                color: white;
                padding: 12px;
                border: none;
                border-bottom: 2px solid {COLORS['primary_dark']};
                font-weight: bold;
                font-size: 13px;
            }}
        """)
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        for i in range(3, table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSortingEnabled(True)
    
    def load_batting_stats(self):
        """Load batting statistics"""
        print(f"[Statistics] Loading batting stats for format: {self.current_format}, season: {self.current_season}")
        
        # Defensive checks to prevent crash when no season simulated
        if not self.game_engine:
            print("[Statistics] ERROR: No game engine available")
            self.batting_table.setRowCount(0)
            return
        
        teams_union = self._teams_for_statistics()
        if not teams_union:
            print("[Statistics] ERROR: No teams available - simulate a season first")
            self.batting_table.setRowCount(0)
            return
        
        print(f"[Statistics] Game engine has {len(self.game_engine.all_teams)} intl + "
              f"{len(getattr(self.game_engine, 'domestic_teams', None) or [])} domestic teams")
        
        # Get selected team filter
        selected_team = self.team_combo.currentText() if hasattr(self, 'team_combo') else "All Teams"
        selected_tier = self.tier_combo.currentText() if hasattr(self, 'tier_combo') else "All Tiers"
        tier_num = int(selected_tier.split()[1]) if selected_tier != "All Tiers" else None
        
        print(f"[Statistics] Team filter: {selected_team}, Tier filter: {selected_tier}")
        
        # Collect all players with batting stats
        players_data = []
        if getattr(self, "stats_scope", "all") == "u21":
            for player, team in self._u21_players_for_team_filter(selected_team, tier_num):
                stats = self._get_player_batting_stats(player)
                if stats is None:
                    stats = self._empty_batting_stats_row()
                players_data.append((player, team, stats))
            players_data = self._dedupe_statistics_player_rows(players_data)
        else:
            nation_ds = self._domestic_scope_nation_from_team_filter(selected_team)
            if nation_ds is not None:
                for team in getattr(self.game_engine, "domestic_teams", None) or []:
                    if getattr(team, "parent_nation", None) != nation_ds:
                        continue
                    if tier_num is not None:
                        team_tier = getattr(team, "tier", 1)
                        if team_tier != tier_num:
                            continue
                    for player in self._domestic_team_extended_roster(team):
                        stats = self._get_player_batting_stats(player)
                        if stats:
                            players_data.append((player, team, stats))
                players_data = self._dedupe_domestic_nation_statistics_rows(players_data, nation_ds)
            else:
                for team in teams_union:
                    if selected_team != "All Teams" and team.name != selected_team:
                        continue
                    if tier_num is not None:
                        team_tier = getattr(team, 'tier', 1)
                        if team_tier != tier_num:
                            continue
                    for player in self._roster_for_statistics_team(team, selected_team):
                        stats = self._get_player_batting_stats(player)
                        if stats:
                            players_data.append((player, team, stats))
                players_data = self._dedupe_statistics_player_rows(players_data)
        
        print(f"[Statistics] Found {len(players_data)} players with batting stats")
        
        if len(players_data) == 0:
            print("[Statistics] WARNING: No players found! Checking sample player stats...")
            if self.game_engine and teams_union:
                sample_team = teams_union[0]
                if sample_team.players:
                    sample_player = sample_team.players[0]
                    print(f"[Statistics] Sample player: {sample_player.name}")
                    print(f"[Statistics] Sample stats: {sample_player.stats}")
        
        # Sort by runs
        players_data.sort(key=lambda x: x[2]['runs'], reverse=True)
        
        # Store player data for click handling
        self.batting_players_data = players_data[:100]
        
        # For Test format, add Dismissals column so Avg = Runs/Dis is clear
        is_test = self.current_format == 'Test'
        if is_test:
            self.batting_table.setColumnCount(12)
            self.batting_table.setHorizontalHeaderLabels([
                "Rank", "Player", "Team", "Mat", "Runs", "Balls", "HS", "Dis", "Avg", "SR", "100s", "50s"
            ])
        else:
            self.batting_table.setColumnCount(11)
            self.batting_table.setHorizontalHeaderLabels([
                "Rank", "Player", "Team", "Mat", "Runs", "Balls", "HS", "Avg", "SR", "100s", "50s"
            ])
        
        # Populate table
        self.batting_table.setRowCount(min(len(players_data), 100))
        for row, (player, team, stats) in enumerate(players_data[:100]):
            # Rank
            rank_item = QTableWidgetItem(str(row + 1))
            rank_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            rank_item.setFont(QFont('Arial', 11, QFont.Weight.Bold))
            if row < 3:
                rank_item.setForeground(QColor(COLORS['warning']))
            self.batting_table.setItem(row, 0, rank_item)
            
            # Player
            self.batting_table.setItem(row, 1, QTableWidgetItem(player.name))
            
            # Team
            self.batting_table.setItem(row, 2, QTableWidgetItem(self._stats_team_display_name(team)))
            
            # Stats
            self.batting_table.setItem(row, 3, self.create_center_item(str(stats['matches'])))
            self.batting_table.setItem(row, 4, self.create_center_item(str(stats['runs'])))
            self.batting_table.setItem(row, 5, self.create_center_item(str(stats['balls_faced'])))
            self.batting_table.setItem(row, 6, self.create_center_item(str(stats['highest_score'])))
            if is_test:
                self.batting_table.setItem(row, 7, self.create_center_item(str(stats.get('dismissals', 0))))
                self.batting_table.setItem(row, 8, self.create_center_item(f"{stats['batting_average']:.2f}"))
                self.batting_table.setItem(row, 9, self.create_center_item(f"{stats['strike_rate']:.2f}"))
                self.batting_table.setItem(row, 10, self.create_center_item(str(stats['centuries'])))
                self.batting_table.setItem(row, 11, self.create_center_item(str(stats['fifties'])))
            else:
                self.batting_table.setItem(row, 7, self.create_center_item(f"{stats['batting_average']:.2f}"))
                self.batting_table.setItem(row, 8, self.create_center_item(f"{stats['strike_rate']:.2f}"))
                self.batting_table.setItem(row, 9, self.create_center_item(str(stats['centuries'])))
                self.batting_table.setItem(row, 10, self.create_center_item(str(stats['fifties'])))
            
            self.batting_table.setRowHeight(row, 45)
    
    def load_bowling_stats(self):
        """Load bowling statistics"""
        # Defensive checks to prevent crash when no season simulated
        if not self.game_engine:
            print("[Statistics] ERROR: No game engine available")
            self.bowling_table.setRowCount(0)
            return
        
        teams_union = self._teams_for_statistics()
        if not teams_union:
            print("[Statistics] ERROR: No teams available - simulate a season first")
            self.bowling_table.setRowCount(0)
            return
        
        # Get selected filters
        selected_team = self.team_combo.currentText() if hasattr(self, 'team_combo') else "All Teams"
        selected_tier = self.tier_combo.currentText() if hasattr(self, 'tier_combo') else "All Tiers"
        tier_num = int(selected_tier.split()[1]) if selected_tier != "All Tiers" else None
        
        # Collect all players with bowling stats
        players_data = []
        if getattr(self, "stats_scope", "all") == "u21":
            for player, team in self._u21_players_for_team_filter(selected_team, tier_num):
                stats = self._get_player_bowling_stats(player)
                if stats is None:
                    stats = self._empty_bowling_stats_row()
                players_data.append((player, team, stats))
            players_data = self._dedupe_statistics_player_rows(players_data)
        else:
            nation_ds = self._domestic_scope_nation_from_team_filter(selected_team)
            if nation_ds is not None:
                for team in getattr(self.game_engine, "domestic_teams", None) or []:
                    if getattr(team, "parent_nation", None) != nation_ds:
                        continue
                    if tier_num is not None:
                        team_tier = getattr(team, "tier", 1)
                        if team_tier != tier_num:
                            continue
                    for player in self._domestic_team_extended_roster(team):
                        stats = self._get_player_bowling_stats(player)
                        if stats:
                            players_data.append((player, team, stats))
                players_data = self._dedupe_domestic_nation_statistics_rows(players_data, nation_ds)
            else:
                for team in teams_union:
                    if selected_team != "All Teams" and team.name != selected_team:
                        continue
                    if tier_num is not None:
                        team_tier = getattr(team, 'tier', 1)
                        if team_tier != tier_num:
                            continue
                    for player in self._roster_for_statistics_team(team, selected_team):
                        stats = self._get_player_bowling_stats(player)
                        if stats:
                            players_data.append((player, team, stats))
                players_data = self._dedupe_statistics_player_rows(players_data)
        
        # Sort by wickets
        players_data.sort(key=lambda x: x[2]['wickets'], reverse=True)
        
        # Store player data for click handling
        self.bowling_players_data = players_data[:100]
        
        # Populate table
        self.bowling_table.setRowCount(min(len(players_data), 100))
        for row, (player, team, stats) in enumerate(players_data[:100]):
            # Rank
            rank_item = QTableWidgetItem(str(row + 1))
            rank_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            rank_item.setFont(QFont('Arial', 11, QFont.Weight.Bold))
            if row < 3:
                rank_item.setForeground(QColor(COLORS['warning']))
            self.bowling_table.setItem(row, 0, rank_item)
            
            # Player
            self.bowling_table.setItem(row, 1, QTableWidgetItem(player.name))
            
            # Team
            self.bowling_table.setItem(row, 2, QTableWidgetItem(self._stats_team_display_name(team)))
            
            # Stats
            self.bowling_table.setItem(row, 3, self.create_center_item(str(stats['matches'])))
            self.bowling_table.setItem(row, 4, self.create_center_item(str(stats['wickets'])))
            self.bowling_table.setItem(row, 5, self.create_center_item(str(stats['balls_bowled'])))
            self.bowling_table.setItem(row, 6, self.create_center_item(str(stats['runs_conceded'])))
            self.bowling_table.setItem(row, 7, self.create_center_item(f"{stats['bowling_average']:.2f}"))
            self.bowling_table.setItem(row, 8, self.create_center_item(f"{stats['economy_rate']:.2f}"))
            self.bowling_table.setItem(row, 9, self.create_center_item(f"{stats['strike_rate']:.1f}"))
            self.bowling_table.setItem(row, 10, self.create_center_item(str(stats['five_wickets'])))
            
            self.bowling_table.setRowHeight(row, 45)
    
    def load_allrounder_stats(self):
        """Load all-rounder statistics"""
        # Defensive checks to prevent crash when no season simulated
        if not self.game_engine:
            print("[Statistics] ERROR: No game engine available")
            self.allrounder_table.setRowCount(0)
            return
        
        teams_union = self._teams_for_statistics()
        if not teams_union:
            print("[Statistics] ERROR: No teams available - simulate a season first")
            self.allrounder_table.setRowCount(0)
            return
        
        selected_team = self.team_combo.currentText() if hasattr(self, 'team_combo') else "All Teams"
        selected_tier = self.tier_combo.currentText() if hasattr(self, 'tier_combo') else "All Tiers"
        tier_num = int(selected_tier.split()[1]) if selected_tier != "All Tiers" else None
        
        # Collect players with both batting and bowling stats
        formats = ['T20', 'ODI', 'Test'] if self.current_format == 'All Formats' else [self.current_format]
        players_data = []
        
        def _append_allrounder_row(team, player, allow_zero_matches=False):
            if self.current_season == "All Stats":
                # Use cumulative career stats
                proot = self._career_stats_for_player(player)
                total_runs = sum(proot[fmt]['runs'] for fmt in formats)
                total_wickets = sum(proot[fmt]['wickets'] for fmt in formats)
                total_matches = sum(proot[fmt]['matches'] for fmt in formats)
                total_runs_conceded = sum(proot[fmt]['runs_conceded'] for fmt in formats)
            else:
                # Use yearly_stats for specific year
                year = self.current_season
                yroot = self._yearly_stats_for_player(player)
                if not yroot or year not in yroot:
                    if not allow_zero_matches:
                        return
                    total_runs = 0
                    total_wickets = 0
                    total_matches = 0
                    total_runs_conceded = 0
                else:
                    year_data = yroot[year]
                    total_runs = sum(year_data.get(fmt, {}).get('runs', 0) for fmt in formats)
                    total_wickets = sum(year_data.get(fmt, {}).get('wickets', 0) for fmt in formats)
                    total_matches = sum(year_data.get(fmt, {}).get('matches', 0) for fmt in formats)
                    total_runs_conceded = sum(year_data.get(fmt, {}).get('runs_conceded', 0) for fmt in formats)
            
            if total_matches == 0 and not allow_zero_matches:
                return
            
            bat_avg = total_runs / total_matches if total_matches > 0 else 0
            bowl_avg = total_runs_conceded / total_wickets if total_wickets > 0 else 0
            rating = (total_runs / 10) + (total_wickets * 20)
            players_data.append((player, team, {
                'matches': total_matches,
                'runs': total_runs,
                'batting_average': bat_avg,
                'wickets': total_wickets,
                'bowling_average': bowl_avg,
                'rating': rating
            }))
        
        if getattr(self, "stats_scope", "all") == "u21":
            for player, team in self._u21_players_for_team_filter(selected_team, tier_num):
                _append_allrounder_row(team, player, allow_zero_matches=True)
            players_data = self._dedupe_statistics_player_rows(players_data)
        else:
            nation_ds = self._domestic_scope_nation_from_team_filter(selected_team)
            if nation_ds is not None:
                for team in getattr(self.game_engine, "domestic_teams", None) or []:
                    if getattr(team, "parent_nation", None) != nation_ds:
                        continue
                    if tier_num is not None:
                        team_tier = getattr(team, "tier", 1)
                        if team_tier != tier_num:
                            continue
                    for player in self._domestic_team_extended_roster(team):
                        _append_allrounder_row(team, player)
                players_data = self._dedupe_domestic_nation_statistics_rows(players_data, nation_ds)
            else:
                for team in teams_union:
                    if selected_team != "All Teams" and team.name != selected_team:
                        continue
                    if tier_num is not None:
                        team_tier = getattr(team, 'tier', 1)
                        if team_tier != tier_num:
                            continue
                    for player in self._roster_for_statistics_team(team, selected_team):
                        _append_allrounder_row(team, player)
                players_data = self._dedupe_statistics_player_rows(players_data)
        
        # Sort by rating
        players_data.sort(key=lambda x: x[2]['rating'], reverse=True)
        
        # Store player data for click handling
        self.allrounder_players_data = players_data[:100]
        
        # Populate table
        self.allrounder_table.setRowCount(min(len(players_data), 100))
        for row, (player, team, stats) in enumerate(players_data[:100]):
            # Rank
            rank_item = QTableWidgetItem(str(row + 1))
            rank_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            rank_item.setFont(QFont('Arial', 11, QFont.Weight.Bold))
            if row < 3:
                rank_item.setForeground(QColor(COLORS['warning']))
            self.allrounder_table.setItem(row, 0, rank_item)
            
            # Player
            self.allrounder_table.setItem(row, 1, QTableWidgetItem(player.name))
            
            # Team
            self.allrounder_table.setItem(row, 2, QTableWidgetItem(self._stats_team_display_name(team)))
            
            # Stats
            self.allrounder_table.setItem(row, 3, self.create_center_item(str(stats['matches'])))
            self.allrounder_table.setItem(row, 4, self.create_center_item(str(stats['runs'])))
            self.allrounder_table.setItem(row, 5, self.create_center_item(f"{stats['batting_average']:.2f}"))
            self.allrounder_table.setItem(row, 6, self.create_center_item(str(stats['wickets'])))
            self.allrounder_table.setItem(row, 7, self.create_center_item(f"{stats['bowling_average']:.2f}"))
            self.allrounder_table.setItem(row, 8, self.create_center_item(f"{stats['rating']:.1f}"))
            
            self.allrounder_table.setRowHeight(row, 45)
    
    def create_center_item(self, text):
        """Create centered table item"""
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item
    
    def _intl_teams_only(self):
        """International sides (exclude domestic club Team objects)."""
        if not self.game_engine:
            return []
        return [t for t in self.game_engine.all_teams if not getattr(t, "is_domestic", False)]
    
    def _u21_players_for_team_filter(self, selected_team, tier_num):
        """(player, parent_team) for U21 lists matching team and tier filters."""
        rows = []
        for team in self._intl_teams_only():
            if selected_team != "All Teams" and team.name != selected_team:
                continue
            if tier_num is not None and getattr(team, "tier", 1) != tier_num:
                continue
            for player in getattr(team, "u21_squad", None) or []:
                rows.append((player, team))
        return rows
    
    def _stats_team_display_name(self, team):
        """Team column label; U21 scope shows parent nation + U21."""
        if getattr(self, "stats_scope", "all") == "u21" and team is not None:
            return f"{team.name} U21"
        return team.name if team is not None else ""
    
    def _empty_batting_stats_row(self):
        return {
            "matches": 0,
            "runs": 0,
            "balls_faced": 0,
            "highest_score": 0,
            "dismissals": 0,
            "batting_average": 0.0,
            "strike_rate": 0.0,
            "centuries": 0,
            "fifties": 0,
        }
    
    def _empty_bowling_stats_row(self):
        return {
            "matches": 0,
            "wickets": 0,
            "balls_bowled": 0,
            "runs_conceded": 0,
            "bowling_average": 0.0,
            "economy_rate": 0.0,
            "strike_rate": 0.0,
            "five_wickets": 0,
        }
    
    def _apply_team_combo_for_statistics_scope(self):
        """U21 scope: team filter is international nations only (U21 lives on those squads)."""
        if not self.game_engine or not hasattr(self, "team_combo"):
            return
        scope = getattr(self, "stats_scope", "all")
        current = self.team_combo.currentText()
        self.team_combo.blockSignals(True)
        self.team_combo.clear()
        self.team_combo.addItem("All Teams")
        if scope == "u21":
            for team in sorted(self._intl_teams_only(), key=lambda t: t.name):
                self.team_combo.addItem(team.name)
        else:
            for team in sorted(self.game_engine.all_teams, key=lambda t: t.name):
                self.team_combo.addItem(team.name)
            for dteam in sorted(getattr(self.game_engine, "domestic_teams", None) or [], key=lambda t: t.name):
                self.team_combo.addItem(dteam.name)
        idx = self.team_combo.findText(current)
        self.team_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.team_combo.blockSignals(False)
    
    def _dedupe_statistics_player_rows(self, players_data):
        """One row per player object (same cap can appear multiple times on a squad list)."""
        seen = set()
        out = []
        for row in players_data:
            if not row:
                continue
            player = row[0]
            pid = id(player)
            if pid in seen:
                continue
            seen.add(pid)
            out.append(row)
        return out
    
    def _domestic_scope_nation_from_team_filter(self, selected_team):
        """
        When scope is domestic and the user picks an international side (e.g. Pakistan),
        treat the filter as 'all domestic clubs for this nation', not the national squad list.
        """
        if selected_team == "All Teams" or not self.game_engine:
            return None
        if getattr(self, "stats_scope", "all") not in ("domestic",):
            return None
        for t in self.game_engine.all_teams:
            if getattr(t, "is_domestic", False):
                continue
            if t.name == selected_team:
                return selected_team
        return None
    
    def _preferred_domestic_club_team_for_row(self, player, nation):
        """Domestic Team to show in the Team column (format-aware club name, then squad membership)."""
        if not self.game_engine:
            return None
        fmt = self.current_format
        candidates = []
        if fmt == "T20":
            candidates.append((getattr(player, "domestic_t20_club_name", None) or "").strip())
            candidates.append((getattr(player, "domestic_odi_fc_club_name", None) or "").strip())
        elif fmt == "ODI":
            candidates.append((getattr(player, "domestic_odi_fc_club_name", None) or "").strip())
            candidates.append((getattr(player, "domestic_t20_club_name", None) or "").strip())
        elif fmt == "Test":
            candidates.append((getattr(player, "domestic_odi_fc_club_name", None) or "").strip())
            candidates.append((getattr(player, "domestic_t20_club_name", None) or "").strip())
        else:
            candidates.append((getattr(player, "domestic_t20_club_name", None) or "").strip())
            candidates.append((getattr(player, "domestic_odi_fc_club_name", None) or "").strip())
        seen = set()
        domestic = getattr(self.game_engine, "domestic_teams", None) or []
        for cname in candidates:
            if not cname or cname in seen:
                continue
            seen.add(cname)
            for dt in domestic:
                if getattr(dt, "parent_nation", None) == nation and dt.name == cname:
                    return dt
        for dt in domestic:
            if getattr(dt, "parent_nation", None) != nation:
                continue
            if player in getattr(dt, "players", []):
                return dt
        return None
    
    def _dedupe_domestic_nation_statistics_rows(self, players_data, nation):
        """One row per player; Team column uses preferred domestic club for that nation."""
        by_pid = {}
        for player, src_team, stats in players_data:
            pid = id(player)
            disp = self._preferred_domestic_club_team_for_row(player, nation)
            if disp is None:
                disp = src_team
            by_pid[pid] = (player, disp, stats)
        return list(by_pid.values())
    
    def _teams_for_statistics(self):
        """International + domestic club teams for filters and leaderboards."""
        if not self.game_engine:
            return []
        out = list(self.game_engine.all_teams)
        out.extend(getattr(self.game_engine, 'domestic_teams', None) or [])
        return out
    
    def _domestic_team_extended_roster(self, dteam):
        """
        Domestic club senior list plus national-team players whose profile lists this
        club as home T20 or ODI/FC affiliation (same nation). Fixes missing rows when
        a star is only on the international squad but tagged with a domestic side.
        """
        if not self.game_engine or not getattr(dteam, 'is_domestic', False):
            return list(getattr(dteam, 'players', []))
        seen = set()
        out = []
        for p in getattr(dteam, 'players', []):
            seen.add(id(p))
            out.append(p)
        nation = getattr(dteam, 'parent_nation', None)
        club = getattr(dteam, 'name', None)
        if not nation or not club:
            return out
        for nt in self.game_engine.all_teams:
            if getattr(nt, 'is_domestic', False):
                continue
            if nt.name != nation:
                continue
            for p in getattr(nt, 'players', []):
                if id(p) in seen:
                    continue
                if getattr(p, 'nationality', None) != nation:
                    continue
                t20 = (getattr(p, 'domestic_t20_club_name', None) or '').strip()
                odi_fc = (getattr(p, 'domestic_odi_fc_club_name', None) or '').strip()
                if club == t20 or club == odi_fc:
                    seen.add(id(p))
                    out.append(p)
        return out
    
    def _roster_for_statistics_team(self, team, selected_team):
        """Players to show for this team row when a single team filter is active."""
        if (
            selected_team != 'All Teams'
            and team.name == selected_team
            and getattr(team, 'is_domestic', False)
        ):
            return self._domestic_team_extended_roster(team)
        return list(getattr(team, 'players', []))
    
    def _career_stats_for_player(self, player):
        scope = getattr(self, 'stats_scope', 'all')
        if scope == 'international':
            return getattr(player, 'international_stats', None) or player.stats
        if scope == 'associate_international':
            ds = getattr(player, 'associate_international_stats', None)
            return ds if isinstance(ds, dict) else {}
        if scope == 'domestic':
            ds = getattr(player, 'domestic_stats', None)
            return ds if isinstance(ds, dict) else {}
        if scope == 'u21':
            return player.stats
        return player.stats
    
    def _yearly_stats_for_player(self, player):
        scope = getattr(self, 'stats_scope', 'all')
        if scope == 'international':
            return getattr(player, 'international_yearly_stats', None) or {}
        if scope == 'associate_international':
            return getattr(player, 'associate_international_yearly_stats', None) or {}
        if scope == 'domestic':
            return getattr(player, 'domestic_yearly_stats', None) or {}
        if scope == 'u21':
            return getattr(player, 'yearly_stats', None) or {}
        return getattr(player, 'yearly_stats', None) or {}
    
    def on_stats_scope_changed(self, _index=None):
        data = self.scope_combo.currentData() if hasattr(self, 'scope_combo') else "all"
        self.stats_scope = data if data in ('all', 'international', 'associate_international', 'domestic', 'u21') else 'all'
        self._apply_team_combo_for_statistics_scope()
        self.load_batting_stats()
        self.load_bowling_stats()
        self.load_allrounder_stats()
    
    def on_format_changed(self, format_type):
        """Handle format change"""
        self.current_format = format_type
        self.load_batting_stats()
        self.load_bowling_stats()
        self.load_allrounder_stats()
    
    def on_team_changed(self, team_name):
        """Handle team filter change"""
        print(f"[Statistics] Team filter changed to: {team_name}")
        self.load_batting_stats()
        self.load_bowling_stats()
        self.load_allrounder_stats()
    
    def on_tier_changed(self, tier_name):
        """Handle tier filter change"""
        print(f"[Statistics] Tier filter changed to: {tier_name}")
        self.load_batting_stats()
        self.load_bowling_stats()
        self.load_allrounder_stats()
    
    def on_season_changed(self, season_text):
        """Handle season filter change"""
        if season_text == "All Stats":
            self.current_season = "All Stats"
        else:
            # Store year directly (like gamer 2024.py uses player['season_stats'][year])
            self.current_season = int(season_text)
        print(f"[Statistics] Season filter changed to: {self.current_season} (year: {season_text})")
        self.load_batting_stats()
        self.load_bowling_stats()
        self.load_allrounder_stats()
    
    def refresh_all_stats(self):
        """Refresh all statistics (called after season simulation)"""
        print("[Statistics] Refreshing all statistics...")
        print(f"[Statistics] Current format: {self.current_format}")
        print(f"[Statistics] Game engine available: {self.game_engine is not None}")
        if self.game_engine:
            print(f"[Statistics] Teams: {len(self.game_engine.all_teams)}")
            print(f"[Statistics] Current season: {self.game_engine.current_season}")
        
        self.load_batting_stats()
        self.load_bowling_stats()
        self.load_allrounder_stats()
        print("[Statistics] Statistics refreshed successfully")
    
    def refresh_data(self):
        """Refresh data when tab is clicked (called by main window navigation)"""
        if self.game_engine and hasattr(self, 'team_combo'):
            self._apply_team_combo_for_statistics_scope()
        # Update season dropdown with latest years
        if self.game_engine and hasattr(self, 'season_combo'):
            current_items = [self.season_combo.itemText(i) for i in range(self.season_combo.count())]
            current_season = self.game_engine.current_season
            current_year = self.game_engine.current_year
            base_year = current_year - current_season + 1
            for s in range(current_season, 0, -1):
                year = base_year + s - 1
                year_text = str(year)
                if year_text not in current_items:
                    self.season_combo.insertItem(1, year_text)  # Insert after "All Stats"
        self.refresh_all_stats()
    
    def _get_player_batting_stats(self, player):
        """Get batting stats for a player, filtered by current season selection"""
        formats = ['T20', 'ODI', 'Test'] if self.current_format == 'All Formats' else [self.current_format]
        
        if self.current_season == "All Stats":
            # Use cumulative stats
            proot = self._career_stats_for_player(player)
            if self.current_format == 'All Formats':
                total_runs = sum(proot[fmt]['runs'] for fmt in formats)
                total_matches = sum(proot[fmt]['matches'] for fmt in formats)
                total_balls = sum(proot[fmt]['balls_faced'] for fmt in formats)
                total_centuries = sum(proot[fmt]['centuries'] for fmt in formats)
                total_fifties = sum(proot[fmt]['fifties'] for fmt in formats)
                highest_score = max(proot[fmt]['highest_score'] for fmt in formats)
                total_dismissals = sum(proot[fmt].get('dismissals', 0) for fmt in formats)
                # For mixed formats, use runs/dismissals when we have Test dismissals, else runs/matches
                if total_dismissals > 0:
                    avg = round(total_runs / total_dismissals, 2)
                else:
                    avg = total_runs / total_matches if total_matches > 0 else 0
                sr = (total_runs / total_balls * 100) if total_balls > 0 else 0
                return {
                    'matches': total_matches,
                    'runs': total_runs,
                    'balls_faced': total_balls,
                    'highest_score': highest_score,
                    'batting_average': avg,
                    'strike_rate': sr,
                    'centuries': total_centuries,
                    'fifties': total_fifties,
                    'dismissals': total_dismissals
                }
            else:
                stats = proot[self.current_format].copy()
                # Ensure strike rate is calculated; Test average already uses dismissals in career dict
                if stats['balls_faced'] > 0:
                    stats['strike_rate'] = round((stats['runs'] / stats['balls_faced']) * 100, 2)
                stats['dismissals'] = stats.get('dismissals', 0)
                return stats
        else:
            # Get stats for specific year from yearly_stats (like gamer 2024.py)
            year = self.current_season  # This is now the year directly
            
            yroot = self._yearly_stats_for_player(player)
            if not yroot or year not in yroot:
                return None
            
            year_data = yroot[year]
            
            total_runs = 0
            total_matches = 0
            total_balls = 0
            total_dismissals = 0
            highest_score = 0
            total_centuries = 0
            total_fifties = 0
            
            for fmt in formats:
                if fmt in year_data:
                    fs = year_data[fmt]
                    total_runs += fs.get('runs', 0)
                    total_matches += fs.get('matches', 0)
                    total_balls += fs.get('balls_faced', 0)
                    total_dismissals += fs.get('dismissals', 0)
                    highest_score = max(highest_score, fs.get('highest_score', 0))
                    total_centuries += fs.get('centuries', 0)
                    total_fifties += fs.get('fifties', 0)
            
            if total_matches == 0:
                return None
            
            # Test uses runs/dismissals; limited-overs use runs/matches
            if total_dismissals > 0:
                avg = round(total_runs / total_dismissals, 2)
            else:
                avg = total_runs / total_matches if total_matches > 0 else 0
            sr = (total_runs / total_balls * 100) if total_balls > 0 else 0
            return {
                'matches': total_matches,
                'runs': total_runs,
                'balls_faced': total_balls,
                'highest_score': highest_score,
                'batting_average': avg,
                'strike_rate': sr,
                'centuries': total_centuries,
                'fifties': total_fifties,
                'dismissals': total_dismissals
            }
    
    def _get_player_bowling_stats(self, player):
        """Get bowling stats for a player, filtered by current season selection"""
        formats = ['T20', 'ODI', 'Test'] if self.current_format == 'All Formats' else [self.current_format]
        
        if self.current_season == "All Stats":
            # Use cumulative stats
            proot = self._career_stats_for_player(player)
            if self.current_format == 'All Formats':
                total_wickets = sum(proot[fmt]['wickets'] for fmt in formats)
                total_matches = sum(proot[fmt]['matches'] for fmt in formats)
                total_balls = sum(proot[fmt]['balls_bowled'] for fmt in formats)
                total_runs = sum(proot[fmt]['runs_conceded'] for fmt in formats)
                total_5w = sum(proot[fmt]['five_wickets'] for fmt in formats)
                
                avg = total_runs / total_wickets if total_wickets > 0 else 0
                econ = (total_runs / (total_balls / 6)) if total_balls > 0 else 0
                sr = total_balls / total_wickets if total_wickets > 0 else 0
                return {
                    'matches': total_matches,
                    'wickets': total_wickets,
                    'balls_bowled': total_balls,
                    'runs_conceded': total_runs,
                    'bowling_average': avg,
                    'economy_rate': econ,
                    'strike_rate': sr,
                    'five_wickets': total_5w
                }
            else:
                stats = proot[self.current_format].copy()
                sr = stats['balls_bowled'] / stats['wickets'] if stats['wickets'] > 0 else 0
                stats['strike_rate'] = sr
                return stats
        else:
            # Get stats for specific year from yearly_stats (like gamer 2024.py)
            year = self.current_season  # This is now the year directly
            
            yroot = self._yearly_stats_for_player(player)
            if not yroot or year not in yroot:
                return None
            
            year_data = yroot[year]
            
            total_wickets = 0
            total_matches = 0
            total_balls = 0
            total_runs = 0
            total_5w = 0
            
            for fmt in formats:
                if fmt in year_data:
                    fs = year_data[fmt]
                    total_wickets += fs.get('wickets', 0)
                    total_matches += fs.get('matches', 0)
                    total_balls += fs.get('balls_bowled', 0)
                    total_runs += fs.get('runs_conceded', 0)
                    total_5w += fs.get('five_wickets', 0)
            
            if total_matches == 0:
                return None
            
            avg = total_runs / total_wickets if total_wickets > 0 else 0
            econ = (total_runs / (total_balls / 6)) if total_balls > 0 else 0
            sr = total_balls / total_wickets if total_wickets > 0 else 0
            return {
                'matches': total_matches,
                'wickets': total_wickets,
                'balls_bowled': total_balls,
                'runs_conceded': total_runs,
                'bowling_average': avg,
                'economy_rate': econ,
                'strike_rate': sr,
                'five_wickets': total_5w
            }
    
    def on_batting_player_clicked(self, row, col):
        """Open player profile when batting table row is double-clicked"""
        player, team = self._get_player_team_from_row(self.batting_table, row, 1, getattr(self, 'batting_players_data', []))
        if player is not None and team is not None:
            self.open_player_profile(player, team)
    
    def on_bowling_player_clicked(self, row, col):
        """Open player profile when bowling table row is double-clicked"""
        player, team = self._get_player_team_from_row(self.bowling_table, row, 1, getattr(self, 'bowling_players_data', []))
        if player is not None and team is not None:
            self.open_player_profile(player, team)
    
    def on_allrounder_player_clicked(self, row, col):
        """Open player profile when allrounder table row is double-clicked"""
        player, team = self._get_player_team_from_row(self.allrounder_table, row, 1, getattr(self, 'allrounder_players_data', []))
        if player is not None and team is not None:
            self.open_player_profile(player, team)
    
    def _get_player_team_from_row(self, table, row, player_col, players_data):
        """Resolve (player, team) from table row, so it works correctly when sorting is enabled."""
        if not table or not players_data:
            return None, None
        item = table.item(row, player_col) if row >= 0 and row < table.rowCount() else None
        player_name = item.text().strip() if item and item.text() else None
        if not player_name:
            return None, None
        for entry in players_data:
            if len(entry) >= 2 and getattr(entry[0], 'name', None) == player_name:
                return entry[0], entry[1]
        return None, None
    
    def open_player_profile(self, player, team):
        """Open player profile dialog"""
        if player is None or team is None:
            return
        try:
            from cricket_manager.ui.player_profile_dialog import PlayerProfileDialog
            dialog = PlayerProfileDialog(self, player, team, self.game_engine)
            dialog.exec()
        except Exception as e:
            import traceback
            traceback.print_exc()
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Error opening profile",
                f"Could not open player profile:\n{str(e)}",
                QMessageBox.StandardButton.Ok
            )
