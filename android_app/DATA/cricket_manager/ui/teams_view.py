"""
Teams Screen - View and manage all teams
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QFrame,
    QScrollArea, QHeaderView, QGridLayout
)
from PyQt6.QtCore import Qt

from cricket_manager.ui.styles import COLORS, get_tier_color, MAIN_STYLESHEET
from cricket_manager.ui.screen_manager import BaseScreen


class TeamsScreen(BaseScreen):
    """Teams management screen"""
    
    def __init__(self, screen_manager=None, game_engine=None):
        super().__init__(screen_manager)
        self.setStyleSheet(MAIN_STYLESHEET)
        self.game_engine = game_engine
        self.tier_manager = game_engine.tier_manager if game_engine else None
        self.current_format = "T20"
        self.current_tier = 1
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
        
        # Stats summary
        stats = self.create_stats_summary()
        content_layout.addWidget(stats)
        
        # Teams table
        self.teams_table = self.create_teams_table()
        content_layout.addWidget(self.teams_table, 1)
        
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
        
        layout = QHBoxLayout()
        layout.setSpacing(20)
        
        # Format selector
        format_label = QLabel("Format:")
        format_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #EAF1FF;")
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
            QComboBox:hover {{
                border: 2px solid {COLORS['primary']};
            }}
        """)
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        layout.addWidget(self.format_combo)
        
        layout.addSpacing(20)
        
        # Tier selector
        tier_label = QLabel("Tier:")
        tier_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #EAF1FF;")
        layout.addWidget(tier_label)
        
        self.tier_combo = QComboBox()
        self.tier_combo.addItems(["Tier 1", "Tier 2", "Tier 3", "Tier 4", "Tier 5"])
        self.tier_combo.setCurrentIndex(0)
        self.tier_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: #111827;
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                min-width: 100px;
            }}
            QComboBox:hover {{
                border: 2px solid {COLORS['primary']};
            }}
        """)
        self.tier_combo.currentTextChanged.connect(self.on_tier_changed)
        layout.addWidget(self.tier_combo)
        
        layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
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
        layout.addWidget(refresh_btn)
        
        container.setLayout(layout)
        return container
    
    def create_stats_summary(self):
        """Create stats summary cards"""
        container = QWidget()
        layout = QGridLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Calculate stats
        total_teams = 76
        teams_in_tier = 16 if self.current_tier == 1 else 15
        
        stats = [
            (str(total_teams), "Total Teams", "All formats", COLORS['primary']),
            (str(teams_in_tier), f"Teams in Tier {self.current_tier}", self.current_format, COLORS['info']),
            ("5", "Tiers", "Per format", COLORS['warning']),
            ("15", "Players", "Per team", COLORS['success']),
        ]
        
        for i, (value, title, subtitle, color) in enumerate(stats):
            card = self.create_stat_card(value, title, subtitle, color)
            layout.addWidget(card, 0, i)
        
        container.setLayout(layout)
        return container
    
    def create_stat_card(self, value, title, subtitle, color):
        """Create a stat card"""
        card = QFrame()
        card.setMinimumHeight(100)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #111827;
                border-radius: 8px;
                border-left: 4px solid {color};
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(5)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            font-size: 28px;
            font-weight: 700;
            color: {color};
            background: transparent;
        """)
        layout.addWidget(value_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 13px;
            font-weight: 600;
            color: #EAF1FF;
            background: transparent;
        """)
        layout.addWidget(title_label)
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("""
            font-size: 11px;
            color: #888;
            background: transparent;
        """)
        layout.addWidget(subtitle_label)
        
        card.setLayout(layout)
        return card
    
    def create_teams_table(self):
        """Create teams table"""
        container = QFrame()
        container.setStyleSheet(f"""
            background-color: #111827;
            border-radius: 8px;
            border: 1px solid {COLORS['border']};
            padding: 20px;
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Title
        title = QLabel(f"Teams - {self.current_format} Tier {self.current_tier}")
        title.setStyleSheet("""
            font-size: 16px;
            font-weight: 700;
            color: #EAF1FF;
        """)
        layout.addWidget(title)
        
        # Table
        table = QTableWidget()
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels([
            "Rank", "Team", "Played", "Won", "Lost", "Points", "NRR", "Strength"
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
                color: {COLORS['text_primary']};
            }}
            QTableWidget::item:hover {{
                background-color: {COLORS['bg_hover']};
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['primary_light']};
                color: {COLORS['text_primary']};
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
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        table.setColumnWidth(0, 60)
        table.setColumnWidth(2, 80)
        table.setColumnWidth(3, 70)
        table.setColumnWidth(4, 70)
        table.setColumnWidth(5, 80)
        table.setColumnWidth(6, 90)
        table.setColumnWidth(7, 90)
        
        # Populate with sample data
        self.populate_teams_table(table)
        
        layout.addWidget(table, 1)
        container.setLayout(layout)
        return container
    
    def populate_teams_table(self, table):
        """Populate table with team data"""
        # Sample data for testing
        sample_teams = [
            ("1", "India", "10", "8", "2", "16", "+1.25", "85"),
            ("2", "Australia", "10", "7", "3", "14", "+0.95", "83"),
            ("3", "England", "10", "7", "3", "14", "+0.78", "82"),
            ("4", "Pakistan", "10", "6", "4", "12", "+0.45", "80"),
            ("5", "South Africa", "10", "5", "5", "10", "+0.12", "78"),
            ("6", "New Zealand", "10", "5", "5", "10", "-0.08", "77"),
            ("7", "West Indies", "10", "4", "6", "8", "-0.35", "75"),
            ("8", "Sri Lanka", "10", "3", "7", "6", "-0.62", "73"),
        ]
        
        table.setRowCount(len(sample_teams))
        for row, team_data in enumerate(sample_teams):
            for col, value in enumerate(team_data):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # Color code rank
                if col == 0:
                    rank = int(value)
                    if rank <= 2:
                        item.setForeground(Qt.GlobalColor.darkGreen)
                    elif rank >= 7:
                        item.setForeground(Qt.GlobalColor.darkRed)
                
                table.setItem(row, col, item)
    
    def on_format_changed(self, format_type):
        """Handle format change"""
        self.current_format = format_type
        self.refresh_data()
    
    def on_tier_changed(self, tier_text):
        """Handle tier change"""
        self.current_tier = int(tier_text.split()[-1])
        self.refresh_data()
    
    def refresh_data(self):
        """Refresh all data"""
        # Update title
        title_label = self.teams_table.findChild(QLabel)
        if title_label:
            title_label.setText(f"Teams - {self.current_format} Tier {self.current_tier}")
        
        # Repopulate table
        table = self.teams_table.findChild(QTableWidget)
        if table:
            self.populate_teams_table(table)
        
        print(f"[Teams] Refreshed: {self.current_format} Tier {self.current_tier}")
