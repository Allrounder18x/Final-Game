"""
Players Screen - View and manage all players
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QFrame,
    QScrollArea, QHeaderView, QLineEdit
)
from PyQt6.QtCore import Qt

from cricket_manager.ui.styles import COLORS, get_skill_color, MAIN_STYLESHEET
from cricket_manager.ui.screen_manager import BaseScreen


class PlayersScreen(BaseScreen):
    """Players management screen"""
    
    def __init__(self, screen_manager=None, game_engine=None):
        super().__init__(screen_manager)
        self.setStyleSheet(MAIN_STYLESHEET)
        self.game_engine = game_engine
        self.all_teams = game_engine.all_teams if game_engine else []
        self.current_team = "All Teams"
        self.current_role = "All Roles"
        self.search_text = ""
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
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
        content_layout.setSpacing(25)
        content_layout.setContentsMargins(30, 30, 30, 30)
        
        # Filters section
        filters = self.create_filters()
        content_layout.addWidget(filters)
        
        # Players table
        self.players_table = self.create_players_table()
        content_layout.addWidget(self.players_table, 1)
        
        content.setLayout(content_layout)
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)
        
        self.setLayout(layout)
    
    def create_filters(self):
        """Create filter controls"""
        container = QFrame()
        container.setStyleSheet(f"""
            background-color: #111827;
            border-radius: 8px;
            border: 1px solid {COLORS['border']};
            padding: 20px;
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # First row - dropdowns
        row1 = QHBoxLayout()
        row1.setSpacing(20)
        
        # Team selector
        team_label = QLabel("Team:")
        team_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #EAF1FF;")
        row1.addWidget(team_label)
        
        self.team_combo = QComboBox()
        team_names = ["All Teams", "India", "Australia", "England"]
        self.team_combo.addItems(team_names)
        self.team_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: #111827;
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                min-width: 150px;
            }}
            QComboBox:hover {{
                border: 2px solid {COLORS['primary']};
            }}
        """)
        self.team_combo.currentTextChanged.connect(self.on_team_changed)
        row1.addWidget(self.team_combo)
        
        row1.addSpacing(20)
        
        # Role selector
        role_label = QLabel("Role:")
        role_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #EAF1FF;")
        row1.addWidget(role_label)
        
        self.role_combo = QComboBox()
        self.role_combo.addItems([
            "All Roles", "Opening Batter", "Top Order Batter", "Middle Order Batter",
            "Lower Order Batter", "Wicketkeeper Batter", "Pace Bowler", "Spin Bowler",
            "All-Rounder"
        ])
        self.role_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: #111827;
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                min-width: 180px;
            }}
            QComboBox:hover {{
                border: 2px solid {COLORS['primary']};
            }}
        """)
        self.role_combo.currentTextChanged.connect(self.on_role_changed)
        row1.addWidget(self.role_combo)
        
        row1.addStretch()
        layout.addLayout(row1)
        
        # Second row - search
        row2 = QHBoxLayout()
        row2.setSpacing(15)
        
        search_label = QLabel("Search:")
        search_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #EAF1FF;")
        row2.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by player name...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: #111827;
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORS['primary']};
            }}
        """)
        self.search_input.textChanged.connect(self.on_search_changed)
        row2.addWidget(self.search_input, 1)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_light']};
            }}
        """)
        refresh_btn.clicked.connect(self.refresh_data)
        row2.addWidget(refresh_btn)
        
        layout.addLayout(row2)
        container.setLayout(layout)
        return container
    
    def create_players_table(self):
        """Create players table"""
        container = QFrame()
        container.setStyleSheet(f"""
            background-color: #111827;
            border-radius: 8px;
            border: 1px solid {COLORS['border']};
            padding: 20px;
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Title with count
        self.table_title = QLabel("All Players (1,140)")
        self.table_title.setStyleSheet("""
            font-size: 16px;
            font-weight: 700;
            color: #EAF1FF;
        """)
        layout.addWidget(self.table_title)
        
        # Table
        table = QTableWidget()
        table.setColumnCount(9)
        table.setHorizontalHeaderLabels([
            "Name", "Team", "Age", "Role", "Batting", "Bowling", "Fielding", "Form", "Traits"
        ])
        
        # Style table
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: #111827;
                alternate-background-color: {COLORS['bg_tertiary']};
                border: none;
                gridline-color: {COLORS['border']};
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
                background-color: {COLORS['primary']};
                color: white;
                padding: 12px;
                border: none;
                font-weight: 700;
                font-size: 13px;
            }}
        """)
        
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setVisible(False)
        
        # Set column widths
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        table.setColumnWidth(2, 60)
        table.setColumnWidth(4, 80)
        table.setColumnWidth(5, 80)
        table.setColumnWidth(6, 80)
        table.setColumnWidth(7, 70)
        table.setColumnWidth(8, 60)
        
        # Populate with sample data
        self.populate_players_table(table)
        
        layout.addWidget(table, 1)
        container.setLayout(layout)
        return container
    
    def populate_players_table(self, table):
        """Populate table with player data"""
        # Sample data for testing
        sample_players = [
            ("Virat Kohli", "India", "35", "Top Order Batter", "92", "45", "88", "85", "3"),
            ("Steve Smith", "Australia", "34", "Top Order Batter", "90", "42", "82", "82", "2"),
            ("Joe Root", "England", "33", "Top Order Batter", "89", "48", "80", "88", "3"),
            ("Kane Williamson", "New Zealand", "33", "Top Order Batter", "88", "40", "85", "80", "2"),
            ("Babar Azam", "Pakistan", "29", "Top Order Batter", "87", "38", "78", "83", "2"),
            ("Jasprit Bumrah", "India", "30", "Pace Bowler", "35", "95", "82", "90", "4"),
            ("Pat Cummins", "Australia", "31", "Pace Bowler", "42", "93", "80", "88", "3"),
            ("Rashid Khan", "Afghanistan", "25", "Spin Bowler", "48", "92", "75", "85", "3"),
        ]
        
        table.setRowCount(len(sample_players))
        for row, player_data in enumerate(sample_players):
            for col, value in enumerate(player_data):
                item = QTableWidgetItem(value)
                
                # Center align numeric columns
                if col in [2, 4, 5, 6, 7, 8]:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                else:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                
                table.setItem(row, col, item)
    
    def on_team_changed(self, team_name):
        """Handle team change"""
        self.current_team = team_name
        self.refresh_data()
    
    def on_role_changed(self, role):
        """Handle role change"""
        self.current_role = role
        self.refresh_data()
    
    def on_search_changed(self, text):
        """Handle search text change"""
        self.search_text = text
        self.refresh_data()
    
    def refresh_data(self):
        """Refresh all data"""
        table = self.players_table.findChild(QTableWidget)
        if table:
            self.populate_players_table(table)
        
        print(f"[Players] Refreshed: Team={self.current_team}, Role={self.current_role}, Search='{self.search_text}'")
