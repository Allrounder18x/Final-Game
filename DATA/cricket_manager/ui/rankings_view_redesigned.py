"""
Rankings Screen - Redesigned with proper headings and improved layout
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QFrame,
    QScrollArea, QHeaderView, QGridLayout, QButtonGroup, QRadioButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from cricket_manager.ui.styles import COLORS, get_skill_color, MAIN_STYLESHEET
from cricket_manager.ui.screen_manager import BaseScreen


class RankingsScreen(BaseScreen):
    """Redesigned player rankings screen with proper headings"""
    
    def __init__(self, screen_manager=None, game_engine=None):
        super().__init__(screen_manager)
        self.setStyleSheet(MAIN_STYLESHEET)
        self.game_engine = game_engine
        self.all_teams = game_engine.all_teams if game_engine else []
        self.current_format = "T20"
        self.current_category = "Batting"
        self.init_ui()
    
    def init_ui(self):
        """Initialize redesigned UI"""
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"border: none; background-color: {COLORS['bg_primary']};")
        
        # Content
        content = QWidget()
        content.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
        content_layout = QVBoxLayout()
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(25, 25, 25, 25)
        
        # Header
        header = self.create_header()
        content_layout.addWidget(header)
        
        # Filters
        filters = self.create_filters()
        content_layout.addWidget(filters)
        
        # Rankings table with proper headings
        self.rankings_table = self.create_rankings_table()
        content_layout.addWidget(self.rankings_table, 1)
        
        # Footer info
        footer = self.create_footer()
        content_layout.addWidget(footer)
        
        content.setLayout(content_layout)
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        self.setLayout(layout)
        self.load_rankings()
    
    def create_header(self):
        """Create compact professional header"""
        header_frame = QFrame()
        header_frame.setFixedHeight(46)
        header_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary']}, stop:1 {COLORS['secondary']});
                border-radius: 6px;
                padding: 0px 12px;
            }}
        """)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(8, 0, 8, 0)
        
        title = QLabel("🏆 PLAYER RANKINGS")
        title.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-size: 18px;
                font-weight: bold;
            }}
        """)
        
        subtitle = QLabel("Elite Player Performance Rankings")
        subtitle.setStyleSheet(f"""
            QLabel {{
                color: rgba(255, 255, 255, 0.8);
                font-size: 12px;
                margin-left: 10px;
            }}
        """)
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.3);
            }}
        """)
        refresh_btn.clicked.connect(self.load_rankings)
        header_layout.addWidget(refresh_btn)
        
        header_frame.setLayout(header_layout)
        return header_frame
    
    def create_filters(self):
        """Create filter controls with gradient header style"""
        filters_frame = QFrame()
        filters_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary']}, stop:1 {COLORS['secondary']});
                border-radius: 8px;
                padding: 12px 15px;
            }}
        """)
        filters_layout = QHBoxLayout()
        
        # Title
        title = QLabel("📊 Player Rankings")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        filters_layout.addWidget(title)
        
        filters_layout.addStretch()
        
        # Format selector
        format_label = QLabel("Format:")
        format_label.setStyleSheet("font-weight: bold; color: white;")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["T20", "ODI", "Test"])
        self.format_combo.setStyleSheet("background-color: #111827; padding: 4px; border-radius: 4px;")
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        
        # Category selector
        category_label = QLabel("Category:")
        category_label.setStyleSheet("font-weight: bold; color: white;")
        self.category_combo = QComboBox()
        self.category_combo.addItems(["Batting", "Bowling", "All-Rounders"])
        self.category_combo.setStyleSheet("background-color: #111827; padding: 4px; border-radius: 4px;")
        self.category_combo.currentTextChanged.connect(self.on_category_changed)
        
        # Skill filter
        skill_label = QLabel("Skill:")
        skill_label.setStyleSheet("font-weight: bold; color: white;")
        self.skill_combo = QComboBox()
        self.skill_combo.addItems(["All Players", "Elite (80+)", "Very Good (70+)", "Good (60+)"])
        self.skill_combo.setStyleSheet("background-color: #111827; padding: 4px; border-radius: 4px;")
        self.skill_combo.currentTextChanged.connect(self.load_rankings)
        
        filters_layout.addWidget(format_label)
        filters_layout.addWidget(self.format_combo)
        filters_layout.addSpacing(15)
        filters_layout.addWidget(category_label)
        filters_layout.addWidget(self.category_combo)
        filters_layout.addSpacing(15)
        filters_layout.addWidget(skill_label)
        filters_layout.addWidget(self.skill_combo)
        filters_layout.addStretch()
        
        filters_frame.setLayout(filters_layout)
        return filters_frame
    
    def create_rankings_table(self):
        """Create rankings table with proper headings"""
        table = QTableWidget()
        table.setColumnCount(8)
        table.setAlternatingRowColors(True)
        
        # Set proper column headers
        headers = ["Rank", "Player", "Team", "Skill", "Matches", "Primary Stat", "Average", "Economy/SR"]
        table.setHorizontalHeaderLabels(headers)
        
        # Style the table
        table.setStyleSheet(f"""
            QTableWidget {{
                gridline-color: #e0e0e0;
                background-color: #111827;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
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
            QHeaderView::section:first {{
                border-top-left-radius: 8px;
            }}
            QHeaderView::section:last {{
                border-top-right-radius: 8px;
            }}
        """)
        
        # Set column widths
        table.setColumnWidth(0, 60)   # Rank
        table.setColumnWidth(1, 180)  # Player
        table.setColumnWidth(2, 120)  # Team
        table.setColumnWidth(3, 60)   # Skill
        table.setColumnWidth(4, 70)   # Matches
        table.setColumnWidth(5, 100)  # Primary Stat
        table.setColumnWidth(6, 80)   # Average
        table.setColumnWidth(7, 80)   # Economy/SR
        
        # Make table read-only
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        return table
    
    def create_footer(self):
        """Create footer with stats summary"""
        footer_frame = QFrame()
        footer_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #e0e0e0;
            }}
        """)
        footer_layout = QHBoxLayout()
        
        self.stats_label = QLabel("Loading rankings...")
        self.stats_label.setStyleSheet("color: #666; font-size: 12px;")
        
        footer_layout.addWidget(self.stats_label)
        footer_layout.addStretch()
        
        footer_frame.setLayout(footer_layout)
        return footer_frame
    
    def on_format_changed(self, format_type):
        """Handle format change"""
        self.current_format = format_type
        self.load_rankings()
    
    def on_category_changed(self, category):
        """Handle category change"""
        self.current_category = category
        self.load_rankings()
    
    def load_rankings(self):
        """Load rankings based on current filters"""
        if not self.game_engine:
            return
        
        # Clear table
        self.rankings_table.setRowCount(0)
        
        # Get filter values
        skill_filter = self.skill_combo.currentText()
        min_skill = 0
        if "Elite" in skill_filter:
            min_skill = 80
        elif "Very Good" in skill_filter:
            min_skill = 70
        elif "Good" in skill_filter:
            min_skill = 60
        
        # Collect player data based on category
        players_data = []
        
        for team in self.all_teams:
            for player in team.players:
                # Apply skill filter
                if min_skill > 0 and player.batting < min_skill and player.bowling < min_skill:
                    continue
                
                if self.current_category == "Batting":
                    if any(role in player.role for role in ['Batter', 'Wicketkeeper', 'All-Rounder', 'Allrounder']):
                        if self.current_format in player.stats:
                            stats = player.stats[self.current_format]
                            if stats.get('dismissals', 0) > 0:
                                avg = stats['runs'] / stats['dismissals']
                                players_data.append({
                                    'name': player.name,
                                    'team': team.name,
                                    'skill': max(player.batting, player.bowling),
                                    'matches': stats['matches'],
                                    'runs': stats['runs'],
                                    'average': avg,
                                    'strike_rate': stats.get('strike_rate', 0),
                                    'centuries': stats.get('centuries', 0),
                                    'fifties': stats.get('fifties', 0)
                                })
                
                elif self.current_category == "Bowling":
                    if any(role in player.role for role in ['Bowler', 'Spinner', 'Pacer', 'All-Rounder', 'Allrounder']):
                        if self.current_format in player.stats:
                            stats = player.stats[self.current_format]
                            if stats.get('wickets', 0) > 0:
                                avg = stats['runs_conceded'] / stats['wickets']
                                players_data.append({
                                    'name': player.name,
                                    'team': team.name,
                                    'skill': max(player.batting, player.bowling),
                                    'matches': stats['matches'],
                                    'wickets': stats['wickets'],
                                    'average': avg,
                                    'economy': stats.get('economy_rate', 0),
                                    'five_wickets': stats.get('five_wickets', 0)
                                })
                
                elif self.current_category == "All-Rounders":
                    if 'All-Rounder' in player.role or 'Allrounder' in player.role:
                        if self.current_format in player.stats:
                            stats = player.stats[self.current_format]
                            if stats.get('dismissals', 0) > 0 and stats.get('wickets', 0) > 0:
                                batting_avg = stats['runs'] / stats['dismissals']
                                bowling_avg = stats['runs_conceded'] / stats['wickets']
                                players_data.append({
                                    'name': player.name,
                                    'team': team.name,
                                    'skill': max(player.batting, player.bowling),
                                    'matches': stats['matches'],
                                    'runs': stats['runs'],
                                    'wickets': stats['wickets'],
                                    'batting_avg': batting_avg,
                                    'bowling_avg': bowling_avg
                                })
        
        # Sort data
        if self.current_category == "Batting":
            players_data.sort(key=lambda x: x['average'], reverse=True)
        elif self.current_category == "Bowling":
            players_data.sort(key=lambda x: x['average'])
        else:  # All-Rounders
            players_data.sort(key=lambda x: x['batting_avg'], reverse=True)
        
        # Populate table
        self.rankings_table.setRowCount(min(len(players_data), 50))
        
        for row, player_data in enumerate(players_data[:50]):
            # Rank
            rank_item = QTableWidgetItem(str(row + 1))
            rank_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            rank_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            self.rankings_table.setItem(row, 0, rank_item)
            
            # Player name
            name_item = QTableWidgetItem(player_data['name'])
            name_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            self.rankings_table.setItem(row, 1, name_item)
            
            # Team
            team_item = QTableWidgetItem(player_data['team'])
            self.rankings_table.setItem(row, 2, team_item)
            
            # Skill
            skill_item = QTableWidgetItem(str(player_data['skill']))
            skill_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            skill_color = get_skill_color(player_data['skill'])
            skill_item.setStyleSheet(f"background-color: {skill_color}; color: white; font-weight: bold;")
            self.rankings_table.setItem(row, 3, skill_item)
            
            # Matches
            matches_item = QTableWidgetItem(str(player_data['matches']))
            matches_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.rankings_table.setItem(row, 4, matches_item)
            
            # Primary Stat (runs/wickets)
            if self.current_category == "Batting":
                primary_stat = f"{player_data['runs']} runs"
            elif self.current_category == "Bowling":
                primary_stat = f"{player_data['wickets']} wkts"
            else:  # All-Rounders
                primary_stat = f"{player_data['runs']} runs"
            
            stat_item = QTableWidgetItem(primary_stat)
            stat_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.rankings_table.setItem(row, 5, stat_item)
            
            # Average
            avg_item = QTableWidgetItem(f"{player_data.get('average', player_data.get('batting_avg', 0)):.2f}")
            avg_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if self.current_category == "Bowling":
                # Lower bowling average is better (green)
                if player_data['average'] < 25:
                    avg_item.setStyleSheet("color: #22C55E; font-weight: bold;")
                elif player_data['average'] < 30:
                    avg_item.setStyleSheet("color: #f57c17; font-weight: bold;")
                else:
                    avg_item.setStyleSheet("color: #d32f2f;")
            else:
                # Higher batting average is better (green)
                if player_data.get('average', player_data.get('batting_avg', 0)) > 40:
                    avg_item.setStyleSheet("color: #22C55E; font-weight: bold;")
                elif player_data.get('average', player_data.get('batting_avg', 0)) > 30:
                    avg_item.setStyleSheet("color: #f57c17; font-weight: bold;")
                else:
                    avg_item.setStyleSheet("color: #d32f2f;")
            self.rankings_table.setItem(row, 6, avg_item)
            
            # Economy/Strike Rate
            if self.current_category == "Batting":
                secondary_stat = f"{player_data.get('strike_rate', 0):.1f}"
                column_name = "SR"
            elif self.current_category == "Bowling":
                secondary_stat = f"{player_data.get('economy', 0):.2f}"
                column_name = "Econ"
            else:  # All-Rounders
                secondary_stat = f"{player_data.get('bowling_avg', 0):.2f}"
                column_name = "Bowl Avg"
            
            secondary_item = QTableWidgetItem(secondary_stat)
            secondary_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.rankings_table.setItem(row, 7, secondary_item)
        
        # Update headers based on category
        if self.current_category == "Batting":
            self.rankings_table.setHorizontalHeaderLabels(["Rank", "Player", "Team", "Skill", "Matches", "Runs", "Average", "Strike Rate"])
        elif self.current_category == "Bowling":
            self.rankings_table.setHorizontalHeaderLabels(["Rank", "Player", "Team", "Skill", "Matches", "Wickets", "Average", "Economy"])
        else:  # All-Rounders
            self.rankings_table.setHorizontalHeaderLabels(["Rank", "Player", "Team", "Skill", "Matches", "Runs", "Bat Avg", "Bowl Avg"])
        
        # Update footer
        self.stats_label.setText(f"Showing {min(len(players_data), 50)} of {len(players_data)} players • {self.current_format} • {self.current_category}")
        
        # Adjust column widths
        self.rankings_table.resizeColumnsToContents()
