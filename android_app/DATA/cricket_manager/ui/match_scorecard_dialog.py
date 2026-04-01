"""
Match Scorecard Dialog - Cricinfo Style with One Scrollbar
Batting tab: 11 batters, Bowling tab: 6 bowlers, No sub-scrollbars
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QFrame, QTabWidget,
    QHeaderView, QScrollArea, QDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from cricket_manager.ui.styles import COLORS, MAIN_STYLESHEET


class MatchScorecardDialog(QDialog):
    """Cricinfo-style match scorecard with single scrollbar"""
    
    def __init__(self, scorecard, parent=None):
        super().__init__(parent)
        self.setStyleSheet(MAIN_STYLESHEET)
        self.scorecard = scorecard
        self.setWindowTitle(f"{scorecard['team1']} vs {scorecard['team2']} - Scorecard")
        self.showMaximized()
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI with single main scrollbar"""
        # Main scroll area - ONLY ONE SCROLLBAR
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")
        
        # Main content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = self.create_header()
        content_layout.addWidget(header)
        
        # Innings tabs (Batting and Bowling for each innings)
        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 2px solid {COLORS['border']};
                background: #111827;
                border-top: none;
            }}
            QTabBar::tab {{
                background: {COLORS['bg_secondary']};
                color: #B8C3D9;
                padding: 15px 30px;
                margin-right: 2px;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #334155;
                border-bottom: none;
            }}
            QTabBar::tab:selected {{
                background: #111827;
                color: {COLORS['primary']};
                border-bottom: 2px solid white;
            }}
        """)
        
        # Create tabs for each innings - SEPARATE BATTING AND BOWLING TABS
        innings = self.scorecard.get('innings', [])
        for i, innings_data in enumerate(innings):
            # Batting tab - 11 batters
            batting_tab = self.create_batting_tab(innings_data)
            tabs.addTab(batting_tab, f"Inn {i+1} Batting: {innings_data['batting_team']}")
            
            # Bowling tab - 6 bowlers  
            bowling_tab = self.create_bowling_tab(innings_data)
            tabs.addTab(bowling_tab, f"Inn {i+1} Bowling: {innings_data['bowling_team']}")
        
        content_layout.addWidget(tabs, 1)
        
        content_widget.setLayout(content_layout)
        self.scroll_area.setWidget(content_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.scroll_area)
        self.setLayout(main_layout)
    
    def create_header(self):
        """Create full match header"""
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary']}, stop:1 {COLORS['secondary']});
                padding: 20px;
                border-bottom: 3px solid {COLORS['primary_dark']};
            }}
        """)
        
        layout = QVBoxLayout()
        
        # Match title
        title = QLabel(f"{self.scorecard['team1']} vs {self.scorecard['team2']}")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Format and result
        info_layout = QHBoxLayout()
        
        format_label = QLabel(f"{self.scorecard['format']} • Unknown Venue")
        format_label.setStyleSheet("font-size: 16px; color: #e3f2fd;")
        info_layout.addWidget(format_label)
        
        if self.scorecard.get('pitch_report'):
            pitch_label = QLabel(self.scorecard['pitch_report'])
            pitch_label.setStyleSheet("font-size: 12px; color: #b0bec5; font-style: italic;")
            layout.addWidget(pitch_label)
        
        info_layout.addStretch()
        
        result_label = QLabel(f"Winner: {self.scorecard['winner']} ({self.scorecard['margin']})")
        result_label.setStyleSheet("font-size: 18px; color: #FFD700; font-weight: bold;")
        info_layout.addWidget(result_label)
        
        if self.scorecard.get('potm'):
            potm_label = QLabel(f"Player of the Match: {self.scorecard['potm']}")
            potm_label.setStyleSheet("font-size: 14px; color: #e3f2fd;")
            layout.addWidget(potm_label)
        
        layout.addLayout(info_layout)
        header.setLayout(layout)
        return header
    
    def create_batting_tab(self, innings_data):
        """Create batting tab with EXACTLY 11 batters - NO SUB-SCROLLBAR"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Innings header
        innings_header = self.create_innings_header(innings_data)
        layout.addWidget(innings_header)
        
        # Batting section title
        batting_title = QLabel("BATTING")
        batting_title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #B8C3D9;
            padding: 15px 30px;
            background-color: #f8f9fa;
            border-bottom: 3px solid #007bff;
        """)
        layout.addWidget(batting_title)
        
        # Batting table - FIXED 11 ROWS
        batting_card = innings_data['batting_card']
        table = self.create_batting_table(batting_card)
        layout.addWidget(table)
        
        # Extras and total
        extras_frame = self.create_extras_total(innings_data)
        layout.addWidget(extras_frame)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_bowling_tab(self, innings_data):
        """Create bowling tab with EXACTLY 6 bowlers - NO SUB-SCROLLBAR"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Bowling section title
        bowling_title = QLabel("BOWLING")
        bowling_title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #B8C3D9;
            padding: 15px 30px;
            background-color: #f8f9fa;
            border-bottom: 3px solid #dc3545;
        """)
        layout.addWidget(bowling_title)
        
        # Bowling table - FIXED 6 ROWS
        bowling_card = innings_data['bowling_card']
        table = self.create_bowling_table(bowling_card)
        layout.addWidget(table)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_innings_header(self, innings_data):
        """Create innings header"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
                padding: 20px 30px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Team name and score
        score_label = QLabel(
            f"{innings_data['batting_team']} - {innings_data['total_runs']}/{innings_data['wickets_fallen']} ({innings_data['overs']} overs)"
        )
        score_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #EAF1FF;")
        layout.addWidget(score_label)
        
        header.setLayout(layout)
        return header
    
    def create_batting_table(self, batting_card):
        """Create batting table - EXACTLY 11 rows, NO scrollbar"""
        table = QTableWidget()
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels([
            "BATSMAN", "DISMISSAL", "RUNS", "BALLS", "4s", "6s", "SR", "MINS"
        ])
        
        # FIXED: Exactly 11 rows
        table.setRowCount(11)
        
        # Style - NO SCROLLBARS
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: #111827;
                border: none;
                gridline-color: #e9ecef;
                font-size: 14px;
            }}
            QTableWidget::item {{
                padding: 8px 10px;
                border-bottom: 1px solid #e9ecef;
            }}
            QHeaderView::section {{
                background-color: #f8f9fa;
                color: #B8C3D9;
                padding: 12px 10px;
                border: 1px solid #dee2e6;
                border-bottom: 2px solid #007bff;
                font-weight: 600;
                font-size: 13px;
            }}
        """)
        
        # DISABLE ALL SCROLLBARS
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Populate batting data
        for row in range(11):
            if row < len(batting_card):
                perf = batting_card[row]
                # Batsman name - support both 'name' and 'player' keys
                player_name = perf.get('name', perf.get('player', 'Unknown'))
                name_item = QTableWidgetItem(player_name)
                name_item.setFont(QFont('Arial', 12, QFont.Weight.Bold))
                table.setItem(row, 0, name_item)
                
                # Dismissal
                dismissal = perf.get('dismissal', 'not out')
                dismissal_item = QTableWidgetItem(dismissal)
                if dismissal == 'not out':
                    dismissal_item.setForeground(QColor('#28a745'))
                    dismissal_item.setFont(QFont('Arial', 12, QFont.Weight.Bold))
                elif dismissal == 'did not bat':
                    dismissal_item.setForeground(QColor('#888888'))
                    dismissal_item.setFont(QFont('Arial', 11, QFont.Weight.Normal))
                table.setItem(row, 1, dismissal_item)
                
                # Runs - show empty for did not bat
                if dismissal == 'did not bat':
                    table.setItem(row, 2, QTableWidgetItem(""))
                    table.setItem(row, 3, QTableWidgetItem(""))
                    table.setItem(row, 4, QTableWidgetItem(""))
                    table.setItem(row, 5, QTableWidgetItem(""))
                    table.setItem(row, 6, QTableWidgetItem(""))
                    table.setItem(row, 7, QTableWidgetItem(""))
                else:
                    # Runs
                    runs_item = QTableWidgetItem(str(perf['runs']))
                    if perf['runs'] >= 100:
                        runs_item.setForeground(QColor('#dc3545'))
                        runs_item.setFont(QFont('Arial', 12, QFont.Weight.Bold))
                    elif perf['runs'] >= 50:
                        runs_item.setForeground(QColor('#ffc107'))
                        runs_item.setFont(QFont('Arial', 12, QFont.Weight.Bold))
                    table.setItem(row, 2, runs_item)
                    
                    # Balls
                    table.setItem(row, 3, QTableWidgetItem(str(perf['balls'])))
                    
                    # Fours
                    table.setItem(row, 4, QTableWidgetItem(str(perf.get('fours', 0))))
                    
                    # Sixes
                    table.setItem(row, 5, QTableWidgetItem(str(perf.get('sixes', 0))))
                    
                    # Strike rate
                    sr = (perf['runs'] / perf['balls'] * 100) if perf['balls'] > 0 else 0
                    table.setItem(row, 6, QTableWidgetItem(f"{sr:.2f}"))
                    
                    # Minutes (estimated)
                    minutes = max(1, perf['balls'] // 6)
                    table.setItem(row, 7, QTableWidgetItem(str(minutes)))
            else:
                # Empty rows for padding to 11
                for col in range(8):
                    table.setItem(row, col, QTableWidgetItem(""))
            
            table.setRowHeight(row, 38)
        
        # Set column widths
        table.horizontalHeader().resizeSection(0, 220)  # Batsman
        table.horizontalHeader().resizeSection(1, 200)  # Dismissal
        table.horizontalHeader().resizeSection(2, 60)   # Runs
        table.horizontalHeader().resizeSection(3, 60)   # Balls
        table.horizontalHeader().resizeSection(4, 40)   # 4s
        table.horizontalHeader().resizeSection(5, 40)   # 6s
        table.horizontalHeader().resizeSection(6, 70)   # SR
        table.horizontalHeader().resizeSection(7, 60)   # Mins
        
        table.horizontalHeader().setStretchLastSection(False)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        
        # FIXED SIZE - NO SCROLLING
        table.setFixedHeight(11 * 38 + 50)  # 11 rows + header
        
        return table
    
    def create_bowling_table(self, bowling_card):
        """Create bowling table - EXACTLY 6 rows, NO scrollbar"""
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "BOWLER", "OVERS", "MAIDENS", "RUNS", "WICKETS", "ECON", "DOTS"
        ])
        
        # FIXED: Exactly 6 rows
        table.setRowCount(6)
        
        # Style - NO SCROLLBARS
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: #111827;
                border: none;
                gridline-color: #e9ecef;
                font-size: 14px;
            }}
            QTableWidget::item {{
                padding: 8px 10px;
                border-bottom: 1px solid #e9ecef;
            }}
            QHeaderView::section {{
                background-color: #f8f9fa;
                color: #B8C3D9;
                padding: 12px 10px;
                border: 1px solid #dee2e6;
                border-bottom: 2px solid #dc3545;
                font-weight: 600;
                font-size: 13px;
            }}
        """)
        
        # DISABLE ALL SCROLLBARS
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Populate bowling data
        for row in range(6):
            if row < len(bowling_card):
                perf = bowling_card[row]
                # Bowler name - support both 'name' and 'player' keys
                player_name = perf.get('name', perf.get('player', 'Unknown'))
                name_item = QTableWidgetItem(player_name)
                name_item.setFont(QFont('Arial', 12, QFont.Weight.Bold))
                table.setItem(row, 0, name_item)
                
                # Overs
                table.setItem(row, 1, QTableWidgetItem(f"{perf['overs']:.1f}"))
                
                # Maidens
                table.setItem(row, 2, QTableWidgetItem(str(perf.get('maidens', 0))))
                
                # Runs
                table.setItem(row, 3, QTableWidgetItem(str(perf['runs'])))
                
                # Wickets
                wickets_item = QTableWidgetItem(str(perf['wickets']))
                if perf['wickets'] >= 5:
                    wickets_item.setForeground(QColor('#dc3545'))
                    wickets_item.setFont(QFont('Arial', 12, QFont.Weight.Bold))
                elif perf['wickets'] >= 3:
                    wickets_item.setForeground(QColor('#ffc107'))
                    wickets_item.setFont(QFont('Arial', 12, QFont.Weight.Bold))
                table.setItem(row, 4, wickets_item)
                
                # Economy
                table.setItem(row, 5, QTableWidgetItem(f"{perf['economy']:.2f}"))
                
                # Dot balls
                table.setItem(row, 6, QTableWidgetItem(str(perf.get('dot_balls', 0))))
            else:
                # Empty rows for padding to 6
                for col in range(7):
                    table.setItem(row, col, QTableWidgetItem(""))
            
            table.setRowHeight(row, 38)
        
        # Set column widths
        table.horizontalHeader().resizeSection(0, 200)  # Bowler
        table.horizontalHeader().resizeSection(1, 70)   # Overs
        table.horizontalHeader().resizeSection(2, 70)   # Maidens
        table.horizontalHeader().resizeSection(3, 60)   # Runs
        table.horizontalHeader().resizeSection(4, 70)   # Wickets
        table.horizontalHeader().resizeSection(5, 70)   # Econ
        table.horizontalHeader().resizeSection(6, 70)   # Dots
        
        table.horizontalHeader().setStretchLastSection(False)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        
        # FIXED SIZE - NO SCROLLING
        table.setFixedHeight(6 * 38 + 50)  # 6 rows + header
        
        return table
    
    def create_extras_total(self, innings_data):
        """Create extras and total section"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-top: 2px solid #dee2e6;
                padding: 15px 30px;
            }
        """)
        
        layout = QHBoxLayout()
        
        # Extras
        extras = innings_data.get('extras', 0)
        extras_label = QLabel(f"Extras: {extras}")
        extras_label.setStyleSheet("font-size: 14px; color: #94A3B8;")
        layout.addWidget(extras_label)
        
        layout.addStretch()
        
        # Total
        total_label = QLabel(
            f"TOTAL: {innings_data['total_runs']}/{innings_data['wickets_fallen']} "
            f"({innings_data['overs']} Overs)"
        )
        total_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #EAF1FF;")
        layout.addWidget(total_label)
        
        frame.setLayout(layout)
        return frame
