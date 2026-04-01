"""
Statistics Screen - Redesigned with proper headings and improved layout
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QFrame,
    QHeaderView, QTabWidget, QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from cricket_manager.ui.styles import COLORS, MAIN_STYLESHEET
from cricket_manager.ui.screen_manager import BaseScreen


class StatisticsScreen(BaseScreen):
    """Redesigned comprehensive statistics screen"""
    
    def __init__(self, screen_manager=None, game_engine=None):
        super().__init__(screen_manager)
        self.setStyleSheet(MAIN_STYLESHEET)
        self.game_engine = game_engine
        self.current_format = "T20"
        self.init_ui()
    
    def init_ui(self):
        """Initialize redesigned UI"""
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Controls
        controls = self.create_controls()
        layout.addWidget(controls)
        
        # Team filter
        team_filter = self.create_team_filter()
        layout.addWidget(team_filter)
        
        # Main content with tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid #e0e0e0;
                background-color: #111827;
                border-radius: 8px;
            }}
            QTabWidget::tab-bar {{
                alignment: left;
            }}
            QTabBar::tab {{
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                padding: 12px 24px;
                margin-right: 2px;
                font-weight: bold;
                color: #B8C3D9;
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS['primary']};
                color: white;
            }}
            QTabBar::tab:hover {{
                background-color: #e8f5e8;
            }}
        """)
        
        # Create tabs
        self.batting_table = self.create_batting_table()
        self.bowling_table = self.create_bowling_table()
        self.allrounder_table = self.create_allrounder_table()
        
        self.tabs.addTab(self.batting_table, "🏏 Batting Stats")
        self.tabs.addTab(self.bowling_table, "⚡ Bowling Stats")
        self.tabs.addTab(self.allrounder_table, "🔄 All-Rounders")
        
        layout.addWidget(self.tabs, 1)
        
        # Footer
        footer = self.create_footer()
        layout.addWidget(footer)
        
        self.setLayout(layout)
        self.load_statistics()
    
    def create_header(self):
        """Create professional header"""
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['primary']};
                border-radius: 8px;
                padding: 20px;
            }}
        """)
        header_layout = QHBoxLayout()
        
        title = QLabel("📊 PLAYER STATISTICS")
        title.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-size: 28px;
                font-weight: bold;
            }}
        """)
        
        subtitle = QLabel("Comprehensive Player Performance Analysis")
        subtitle.setStyleSheet(f"""
            QLabel {{
                color: rgba(255, 255, 255, 0.9);
                font-size: 16px;
                margin-left: 15px;
            }}
        """)
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 Refresh All")
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.3);
            }}
        """)
        refresh_btn.clicked.connect(self.load_statistics)
        header_layout.addWidget(refresh_btn)
        
        header_frame.setLayout(header_layout)
        return header_frame
    
    def create_controls(self):
        """Create control section"""
        controls_frame = QFrame()
        controls_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #111827;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #e0e0e0;
                margin: 10px 0;
            }}
        """)
        controls_layout = QHBoxLayout()
        
        # Format selector
        format_label = QLabel("Format:")
        format_label.setStyleSheet("font-weight: bold; color: #B8C3D9; margin-right: 8px;")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["T20", "ODI", "Test", "All Formats"])
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        self.format_combo.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 1px solid #334155;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        
        controls_layout.addWidget(format_label)
        controls_layout.addWidget(self.format_combo)
        controls_layout.addStretch()
        
        # Stats info
        if self.game_engine:
            info = QLabel(f"Season {self.game_engine.current_season} • "
                         f"{len(self.game_engine.all_teams)} Teams • "
                         f"{sum(len(t.players) for t in self.game_engine.all_teams)} Players")
            info.setStyleSheet("color: #666; font-size: 12px;")
            controls_layout.addWidget(info)
        
        controls_frame.setLayout(controls_layout)
        return controls_frame
    
    def create_team_filter(self):
        """Create team filter section"""
        filter_frame = QFrame()
        filter_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #111827;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #e0e0e0;
                margin-bottom: 10px;
            }}
        """)
        filter_layout = QHBoxLayout()
        
        team_label = QLabel("Filter by Team:")
        team_label.setStyleSheet("font-weight: bold; color: #B8C3D9; margin-right: 8px;")
        self.team_combo = QComboBox()
        self.team_combo.addItem("All Teams")
        if self.game_engine:
            for team in sorted(self.game_engine.all_teams, key=lambda t: t.name):
                self.team_combo.addItem(team.name)
        self.team_combo.setCurrentText("All Teams")
        self.team_combo.currentTextChanged.connect(self.load_statistics)
        self.team_combo.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 1px solid #334155;
                border-radius: 4px;
                font-weight: bold;
                min-width: 200px;
            }
        """)
        
        filter_layout.addWidget(team_label)
        filter_layout.addWidget(self.team_combo)
        filter_layout.addStretch()
        
        filter_frame.setLayout(filter_layout)
        return filter_frame
    
    def create_batting_table(self):
        """Create batting statistics table"""
        table = QTableWidget()
        table.setColumnCount(10)
        table.setAlternatingRowColors(True)
        
        # Set proper column headers
        headers = [
            "Rank", "Player", "Team", "Skill", "Matches", "Runs", "Average", 
            "Strike Rate", "Centuries", "Fifties"
        ]
        table.setHorizontalHeaderLabels(headers)
        
        # Style the table
        table.setStyleSheet(f"""
            QTableWidget {{
                gridline-color: #e0e0e0;
                background-color: #111827;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                selection-background-color: {COLORS['primary']};
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['primary']};
                color: white;
            }}
            QHeaderView::section {{
                background-color: {COLORS['primary']};
                color: white;
                padding: 12px;
                font-weight: bold;
                border: none;
                text-align: left;
            }}
        """)
        
        # Set column widths
        table.setColumnWidth(0, 50)   # Rank
        table.setColumnWidth(1, 150)  # Player
        table.setColumnWidth(2, 100)  # Team
        table.setColumnWidth(3, 60)   # Skill
        table.setColumnWidth(4, 70)   # Matches
        table.setColumnWidth(5, 80)   # Runs
        table.setColumnWidth(6, 80)   # Average
        table.setColumnWidth(7, 80)   # Strike Rate
        table.setColumnWidth(8, 80)   # Centuries
        table.setColumnWidth(9, 70)   # Fifties
        
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        return table
    
    def create_bowling_table(self):
        """Create bowling statistics table"""
        table = QTableWidget()
        table.setColumnCount(10)
        table.setAlternatingRowColors(True)
        
        # Set proper column headers
        headers = [
            "Rank", "Player", "Team", "Skill", "Matches", "Wickets", "Average", 
            "Economy Rate", "Strike Rate", "5-Wickets"
        ]
        table.setHorizontalHeaderLabels(headers)
        
        # Style the table
        table.setStyleSheet(f"""
            QTableWidget {{
                gridline-color: #e0e0e0;
                background-color: #111827;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                selection-background-color: {COLORS['primary']};
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['primary']};
                color: white;
            }}
            QHeaderView::section {{
                background-color: {COLORS['primary']};
                color: white;
                padding: 12px;
                font-weight: bold;
                border: none;
                text-align: left;
            }}
        """)
        
        # Set column widths
        table.setColumnWidth(0, 50)   # Rank
        table.setColumnWidth(1, 150)  # Player
        table.setColumnWidth(2, 100)  # Team
        table.setColumnWidth(3, 60)   # Skill
        table.setColumnWidth(4, 70)   # Matches
        table.setColumnWidth(5, 70)   # Wickets
        table.setColumnWidth(6, 80)   # Average
        table.setColumnWidth(7, 80)   # Economy Rate
        table.setColumnWidth(8, 80)   # Strike Rate
        table.setColumnWidth(9, 80)   # 5-Wickets
        
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        return table
    
    def create_allrounder_table(self):
        """Create all-rounder statistics table"""
        table = QTableWidget()
        table.setColumnCount(9)
        table.setAlternatingRowColors(True)
        
        # Set proper column headers
        headers = [
            "Rank", "Player", "Team", "Skill", "Matches", "Runs", 
            "Batting Avg", "Wickets", "Bowling Avg"
        ]
        table.setHorizontalHeaderLabels(headers)
        
        # Style the table
        table.setStyleSheet(f"""
            QTableWidget {{
                gridline-color: #e0e0e0;
                background-color: #111827;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                selection-background-color: {COLORS['primary']};
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['primary']};
                color: white;
            }}
            QHeaderView::section {{
                background-color: {COLORS['primary']};
                color: white;
                padding: 12px;
                font-weight: bold;
                border: none;
                text-align: left;
            }}
        """)
        
        # Set column widths
        table.setColumnWidth(0, 50)   # Rank
        table.setColumnWidth(1, 150)  # Player
        table.setColumnWidth(2, 100)  # Team
        table.setColumnWidth(3, 60)   # Skill
        table.setColumnWidth(4, 70)   # Matches
        table.setColumnWidth(5, 80)   # Runs
        table.setColumnWidth(6, 90)   # Batting Avg
        table.setColumnWidth(7, 70)   # Wickets
        table.setColumnWidth(8, 90)   # Bowling Avg
        
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        return table
    
    def create_footer(self):
        """Create footer with summary"""
        footer_frame = QFrame()
        footer_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #e0e0e0;
                margin-top: 10px;
            }}
        """)
        footer_layout = QHBoxLayout()
        
        self.footer_label = QLabel("Loading statistics...")
        self.footer_label.setStyleSheet("color: #666; font-size: 12px;")
        
        footer_layout.addWidget(self.footer_label)
        footer_layout.addStretch()
        
        footer_frame.setLayout(footer_layout)
        return footer_frame
    
    def on_format_changed(self, format_type):
        """Handle format change"""
        self.current_format = format_type
        self.load_statistics()
    
    def load_statistics(self):
        """Load all statistics"""
        if not self.game_engine:
            return
        
        # Get selected filters
        selected_team = self.team_combo.currentText() if hasattr(self, 'team_combo') else "All Teams"
        
        # Load batting stats
        self.load_batting_stats()
        
        # Load bowling stats
        self.load_bowling_stats()
        
        # Load all-rounder stats
        self.load_allrounder_stats()
        
        # Update footer
        total_players = sum(len(t.players) for t in self.game_engine.all_teams)
        self.footer_label.setText(f"Showing statistics for {total_players} players • {self.current_format} • Team: {selected_team}")
    
    def load_batting_stats(self):
        """Load batting statistics"""
        if not self.game_engine:
            return
        
        # Get selected team filter
        selected_team = self.team_combo.currentText() if hasattr(self, 'team_combo') else "All Teams"
        
        # Collect all players with batting stats
        players_data = []
        for team in self.game_engine.all_teams:
            # Skip teams not selected in filter
            if selected_team != "All Teams" and team.name != selected_team:
                continue
            
            for player in team.players:
                if self.current_format == 'All Formats':
                    # Aggregate across all formats
                    total_runs = sum(player.stats.get(fmt, {}).get('runs', 0) for fmt in ['T20', 'ODI', 'Test'])
                    total_matches = sum(player.stats.get(fmt, {}).get('matches', 0) for fmt in ['T20', 'ODI', 'Test'])
                    total_balls = sum(player.stats.get(fmt, {}).get('balls_faced', 0) for fmt in ['T20', 'ODI', 'Test'])
                    total_centuries = sum(player.stats.get(fmt, {}).get('centuries', 0) for fmt in ['T20', 'ODI', 'Test'])
                    total_fifties = sum(player.stats.get(fmt, {}).get('fifties', 0) for fmt in ['T20', 'ODI', 'Test'])
                    highest_score = max((player.stats.get(fmt, {}).get('highest_score', 0) for fmt in ['T20', 'ODI', 'Test']), default=0)
                    
                    avg = total_runs / total_matches if total_matches > 0 else 0
                    sr = total_balls / total_runs if total_runs > 0 else 0
                    
                    players_data.append((player, team, {
                        'matches': total_matches,
                        'runs': total_runs,
                        'average': avg,
                        'strike_rate': sr,
                        'centuries': total_centuries,
                        'fifties': total_fifties,
                        'highest_score': highest_score
                    }))
                else:
                    stats = player.stats.get(self.current_format, {})
                    if stats.get('matches', 0) > 0:
                        players_data.append((player, team, stats))
        
        # Sort by runs
        players_data.sort(key=lambda x: x[2]['runs'], reverse=True)
        
        # Populate table
        self.batting_table.setRowCount(min(len(players_data), 100))
        
        for row, (player, team, stats) in enumerate(players_data[:100]):
            # Rank
            rank_item = QTableWidgetItem(str(row + 1))
            rank_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            rank_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            self.batting_table.setItem(row, 0, rank_item)
            
            # Player
            name_item = QTableWidgetItem(player.name)
            name_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            self.batting_table.setItem(row, 1, name_item)
            
            # Team
            team_item = QTableWidgetItem(team.name)
            self.batting_table.setItem(row, 2, team_item)
            
            # Skill
            skill_item = QTableWidgetItem(str(player.batting))
            skill_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.batting_table.setItem(row, 3, skill_item)
            
            # Matches
            matches_item = QTableWidgetItem(str(stats['matches']))
            matches_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.batting_table.setItem(row, 4, matches_item)
            
            # Runs
            runs_item = QTableWidgetItem(str(stats['runs']))
            runs_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            runs_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            self.batting_table.setItem(row, 5, runs_item)
            
            # Average
            batting_avg = stats.get('batting_average', 0)
            avg_item = QTableWidgetItem(f"{batting_avg:.2f}")
            avg_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if batting_avg > 40:
                avg_item.setForeground(QBrush(QColor("#22C55E")))
                avg_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            elif batting_avg > 30:
                avg_item.setForeground(QBrush(QColor("#f57c17")))
                avg_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            self.batting_table.setItem(row, 6, avg_item)
            
            # Strike Rate
            sr_item = QTableWidgetItem(f"{stats.get('strike_rate', 0):.1f}")
            sr_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.batting_table.setItem(row, 7, sr_item)
            
            # Centuries
            centuries_item = QTableWidgetItem(str(stats.get('centuries', 0)))
            centuries_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if stats.get('centuries', 0) > 0:
                centuries_item.setForeground(QBrush(QColor("#d32f2f")))
                centuries_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            self.batting_table.setItem(row, 8, centuries_item)
            
            # Fifties
            fifties_item = QTableWidgetItem(str(stats.get('fifties', 0)))
            fifties_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if stats.get('fifties', 0) > 0:
                fifties_item.setForeground(QBrush(QColor("#ff9800")))
                fifties_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            self.batting_table.setItem(row, 9, fifties_item)
    
    def load_bowling_stats(self):
        """Load bowling statistics"""
        if not self.game_engine:
            return
        
        # Get selected filters
        selected_team = self.team_combo.currentText() if hasattr(self, 'team_combo') else "All Teams"
        
        # Collect all players with bowling stats
        players_data = []
        for team in self.game_engine.all_teams:
            # Skip teams not selected in filter
            if selected_team != "All Teams" and team.name != selected_team:
                continue
            
            for player in team.players:
                if self.current_format == 'All Formats':
                    # Aggregate across all formats
                    total_wickets = sum(player.stats.get(fmt, {}).get('wickets', 0) for fmt in ['T20', 'ODI', 'Test'])
                    total_matches = sum(player.stats.get(fmt, {}).get('matches', 0) for fmt in ['T20', 'ODI', 'Test'])
                    total_balls = sum(player.stats.get(fmt, {}).get('balls_bowled', 0) for fmt in ['T20', 'ODI', 'Test'])
                    total_runs = sum(player.stats.get(fmt, {}).get('runs_conceded', 0) for fmt in ['T20', 'ODI', 'Test'])
                    total_5w = sum(player.stats.get(fmt, {}).get('five_wickets', 0) for fmt in ['T20', 'ODI', 'Test'])
                    
                    avg = total_runs / total_wickets if total_wickets > 0 else 0
                    econ = total_runs / (total_balls/6) if total_balls > 0 else 0
                    sr = total_balls / total_wickets if total_wickets > 0 else 0
                    
                    players_data.append((player, team, {
                        'matches': total_matches,
                        'wickets': total_wickets,
                        'average': avg,
                        'economy_rate': econ,
                        'strike_rate': sr,
                        'five_wickets': total_5w
                    }))
                else:
                    stats = player.stats.get(self.current_format, {})
                    if stats.get('matches', 0) > 0:
                        # Calculate strike rate
                        sr = stats.get('balls_bowled', 0) / stats['wickets'] if stats['wickets'] > 0 else 0
                        stats['strike_rate'] = sr
                        players_data.append((player, team, stats))
        
        # Sort by wickets
        players_data.sort(key=lambda x: x[2]['wickets'], reverse=True)
        
        # Populate table
        self.bowling_table.setRowCount(min(len(players_data), 100))
        
        for row, (player, team, stats) in enumerate(players_data[:100]):
            # Rank
            rank_item = QTableWidgetItem(str(row + 1))
            rank_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            rank_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            self.bowling_table.setItem(row, 0, rank_item)
            
            # Player
            name_item = QTableWidgetItem(player.name)
            name_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            self.bowling_table.setItem(row, 1, name_item)
            
            # Team
            team_item = QTableWidgetItem(team.name)
            self.bowling_table.setItem(row, 2, team_item)
            
            # Skill
            skill_item = QTableWidgetItem(str(player.bowling))
            skill_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.bowling_table.setItem(row, 3, skill_item)
            
            # Matches
            matches_item = QTableWidgetItem(str(stats['matches']))
            matches_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.bowling_table.setItem(row, 4, matches_item)
            
            # Wickets
            wickets_item = QTableWidgetItem(str(stats['wickets']))
            wickets_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            wickets_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            self.bowling_table.setItem(row, 5, wickets_item)
            
            # Average
            avg_item = QTableWidgetItem(f"{stats['average']:.2f}")
            avg_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if stats['average'] < 25:
                avg_item.setForeground(QBrush(QColor("#22C55E")))
                avg_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            elif stats['average'] < 30:
                avg_item.setForeground(QBrush(QColor("#f57c17")))
                avg_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            self.bowling_table.setItem(row, 6, avg_item)
            
            # Economy Rate
            econ_item = QTableWidgetItem(f"{stats.get('economy_rate', 0):.2f}")
            econ_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if stats.get('economy_rate', 0) < 4:
                econ_item.setForeground(QBrush(QColor("#22C55E")))
                econ_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            elif stats.get('economy_rate', 0) < 6:
                econ_item.setForeground(QBrush(QColor("#f57c17")))
                econ_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            self.bowling_table.setItem(row, 7, econ_item)
            
            # Strike Rate
            sr_item = QTableWidgetItem(f"{stats.get('strike_rate', 0):.1f}")
            sr_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.bowling_table.setItem(row, 8, sr_item)
            
            # 5-Wickets
            five_wickets_item = QTableWidgetItem(str(stats.get('five_wickets', 0)))
            five_wickets_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if stats.get('five_wickets', 0) > 0:
                five_wickets_item.setForeground(QBrush(QColor("#d32f2f")))
                five_wickets_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            self.bowling_table.setItem(row, 9, five_wickets_item)
    
    def load_allrounder_stats(self):
        """Load all-rounder statistics"""
        if not self.game_engine:
            return
        
        # Get selected filters
        selected_team = self.team_combo.currentText() if hasattr(self, 'team_combo') else "All Teams"
        
        # Collect players with both batting and bowling stats
        players_data = []
        for team in self.game_engine.all_teams:
            # Skip teams not selected in filter
            if selected_team != "All Teams" and team.name != selected_team:
                continue
            
            for player in team.players:
                if 'All-Rounder' in player.role or 'Allrounder' in player.role:
                    if self.current_format == 'All Formats':
                        total_runs = sum(player.stats.get(fmt, {}).get('runs', 0) for fmt in ['T20', 'ODI', 'Test'])
                        total_wickets = sum(player.stats.get(fmt, {}).get('wickets', 0) for fmt in ['T20', 'ODI', 'Test'])
                        total_matches = sum(player.stats.get(fmt, {}).get('matches', 0) for fmt in ['T20', 'ODI', 'Test'])
                        
                        batting_avg = total_runs / total_matches if total_matches > 0 else 0
                        bowling_avg = sum(player.stats.get(fmt, {}).get('runs_conceded', 0) for fmt in ['T20', 'ODI', 'Test']) / total_wickets if total_wickets > 0 else 0
                        
                        players_data.append((player, team, {
                            'matches': total_matches,
                            'runs': total_runs,
                            'batting_avg': batting_avg,
                            'wickets': total_wickets,
                            'bowling_avg': bowling_avg
                        }))
                    else:
                        stats = player.stats.get(self.current_format, {})
                        if stats.get('dismissals', 0) > 0 and stats.get('wickets', 0) > 0:
                            batting_avg = stats['runs'] / stats['dismissals']
                            bowling_avg = stats['runs_conceded'] / stats['wickets']
                            players_data.append((player, team, {
                                'matches': stats['matches'],
                                'runs': stats['runs'],
                                'batting_avg': batting_avg,
                                'wickets': stats['wickets'],
                                'bowling_avg': bowling_avg
                            }))
        
        # Sort by batting average
        players_data.sort(key=lambda x: x[2]['batting_avg'], reverse=True)
        
        # Populate table
        self.allrounder_table.setRowCount(min(len(players_data), 100))
        
        for row, (player, team, stats) in enumerate(players_data[:100]):
            # Rank
            rank_item = QTableWidgetItem(str(row + 1))
            rank_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            rank_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            self.allrounder_table.setItem(row, 0, rank_item)
            
            # Player
            name_item = QTableWidgetItem(player.name)
            name_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            self.allrounder_table.setItem(row, 1, name_item)
            
            # Team
            team_item = QTableWidgetItem(team.name)
            self.allrounder_table.setItem(row, 2, team_item)
            
            # Skill
            skill_item = QTableWidgetItem(str(max(player.batting, player.bowling)))
            skill_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.allrounder_table.setItem(row, 3, skill_item)
            
            # Matches
            matches_item = QTableWidgetItem(str(stats['matches']))
            matches_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.allrounder_table.setItem(row, 4, matches_item)
            
            # Runs
            runs_item = QTableWidgetItem(str(stats['runs']))
            runs_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.allrounder_table.setItem(row, 5, runs_item)
            
            # Batting Average
            batting_avg_item = QTableWidgetItem(f"{stats['batting_avg']:.2f}")
            batting_avg_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if stats['batting_avg'] > 35:
                batting_avg_item.setForeground(QBrush(QColor("#22C55E")))
                batting_avg_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            self.allrounder_table.setItem(row, 6, batting_avg_item)
            
            # Wickets
            wickets_item = QTableWidgetItem(str(stats['wickets']))
            wickets_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.allrounder_table.setItem(row, 7, wickets_item)
            
            # Bowling Average
            bowling_avg_item = QTableWidgetItem(f"{stats['bowling_avg']:.2f}")
            bowling_avg_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if stats['bowling_avg'] < 30:
                bowling_avg_item.setForeground(QBrush(QColor("#22C55E")))
                bowling_avg_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            self.allrounder_table.setItem(row, 8, bowling_avg_item)
