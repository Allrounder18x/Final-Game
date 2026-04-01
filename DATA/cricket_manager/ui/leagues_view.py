"""
Leagues Screen - Live standings table with real-time updates
Shows 12 teams per tier with format and tier filters
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QFrame,
    QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from cricket_manager.ui.styles import COLORS, MAIN_STYLESHEET
from cricket_manager.ui.screen_manager import BaseScreen


class LeaguesScreen(BaseScreen):
    """Live league standings with real-time updates"""
    
    def __init__(self, screen_manager=None, game_engine=None):
        super().__init__(screen_manager)
        self.setStyleSheet(MAIN_STYLESHEET)
        self.game_engine = game_engine
        self.current_format = "T20"
        self.current_tier = 1
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Filters
        filters = self.create_filters()
        layout.addWidget(filters)
        
        # Standings table
        self.standings_table = self.create_standings_table()
        layout.addWidget(self.standings_table, 1)
        
        # Action buttons
        actions = self.create_action_buttons()
        layout.addWidget(actions)
        
        self.setLayout(layout)
        self.load_standings()
    
    def create_header(self):
        """Create header section"""
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary']}, stop:1 {COLORS['secondary']});
                padding: 20px;
            }}
        """)
        
        layout = QHBoxLayout()
        
        # Title
        title_layout = QVBoxLayout()
        title = QLabel("League Standings")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        title_layout.addWidget(title)
        
        subtitle = QLabel("Live standings - updates after every match")
        subtitle.setStyleSheet("font-size: 14px; color: white;")
        title_layout.addWidget(subtitle)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        # Season info
        if self.game_engine:
            season_info = QLabel(f"Season {self.game_engine.current_season} • {self.game_engine.current_year}")
            season_info.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
            layout.addWidget(season_info)
        
        header.setLayout(layout)
        return header
    
    def create_filters(self):
        """Create filter section"""
        filters = QFrame()
        filters.setStyleSheet(f"""
            QFrame {{
                background: #111827;
                border-bottom: 2px solid {COLORS['border_light']};
                padding: 15px 20px;
            }}
        """)
        
        layout = QHBoxLayout()
        
        # Format selector
        format_label = QLabel("Format:")
        format_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(format_label)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(['T20', 'ODI', 'Test'])
        self.format_combo.setCurrentText(self.current_format)
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        self.format_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 10px 20px;
                border: 2px solid {COLORS['primary']};
                border-radius: 6px;
                min-width: 100px;
                font-size: 14px;
                font-weight: bold;
                background: #111827;
            }}
            QComboBox:hover {{
                background: {COLORS['bg_hover']};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
        """)
        layout.addWidget(self.format_combo)
        
        layout.addSpacing(30)
        
        # Tier selector
        tier_label = QLabel("Tier:")
        tier_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(tier_label)
        
        self.tier_combo = QComboBox()
        self.tier_combo.addItems(['Tier 1', 'Tier 2', 'Tier 3', 'Tier 4'])
        self.tier_combo.setCurrentIndex(self.current_tier - 1)
        self.tier_combo.currentIndexChanged.connect(self.on_tier_changed)
        self.tier_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 10px 20px;
                border: 2px solid {COLORS['primary']};
                border-radius: 6px;
                min-width: 100px;
                font-size: 14px;
                font-weight: bold;
                background: #111827;
            }}
            QComboBox:hover {{
                background: {COLORS['bg_hover']};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
        """)
        layout.addWidget(self.tier_combo)
        
        layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_standings)
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['info']};
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary']};
            }}
        """)
        layout.addWidget(refresh_btn)
        
        filters.setLayout(layout)
        return filters
    
    def create_standings_table(self):
        """Create standings table"""
        table = QTableWidget()
        table.setColumnCount(9)
        table.setHorizontalHeaderLabels([
            "Pos", "Team", "Played", "Won", "Lost", "Drawn", "Points", "NRR", "Form"
        ])
        
        # Style table
        table.setStyleSheet(f"""
            QTableWidget {{
                border: none;
                background-color: #111827;
                gridline-color: {COLORS['border_light']};
                font-size: 13px;
            }}
            QTableWidget::item {{
                padding: 12px 8px;
                border-bottom: 1px solid {COLORS['border_light']};
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['highlight_blue']};
                color: {COLORS['text_primary']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['primary']};
                color: white;
                padding: 14px 8px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }}
        """)
        
        # Set column widths
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed)
        
        table.setColumnWidth(0, 50)   # Pos
        table.setColumnWidth(2, 80)   # Played
        table.setColumnWidth(3, 70)   # Won
        table.setColumnWidth(4, 70)   # Lost
        table.setColumnWidth(5, 70)   # Drawn
        table.setColumnWidth(6, 80)   # Points
        table.setColumnWidth(7, 80)   # NRR
        table.setColumnWidth(8, 100)  # Form
        
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setAlternatingRowColors(True)
        
        return table
    
    def create_action_buttons(self):
        """Create action buttons"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: #111827;
                border-top: 2px solid {COLORS['border_light']};
                padding: 15px 20px;
            }}
        """)
        
        layout = QHBoxLayout()
        
        # Info label
        info = QLabel("💡 Standings update automatically after each match")
        info.setStyleSheet("font-size: 13px; color: #666;")
        layout.addWidget(info)
        
        layout.addStretch()
        
        # Simulate season button
        sim_season_btn = QPushButton("⚡ Simulate Season")
        sim_season_btn.clicked.connect(self.simulate_season)
        sim_season_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['warning']};
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['danger']};
            }}
        """)
        layout.addWidget(sim_season_btn)
        
        frame.setLayout(layout)
        return frame
    
    def load_standings(self):
        """Load and display standings for current format and tier"""
        if not self.game_engine:
            return
        
        # Get tier system for current format
        tier_system = self.game_engine.tier_manager.tier_systems[self.current_format]
        
        # Get standings for current tier
        standings = tier_system.get_tier_standings(self.current_tier)
        
        # Update table
        self.standings_table.setRowCount(len(standings))
        
        for row, team in enumerate(standings):
            # Get team stats for current format
            stats = team.format_stats[self.current_format]
            
            # Position
            pos_item = QTableWidgetItem(str(row + 1))
            pos_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            pos_item.setFont(QFont('Arial', 12, QFont.Weight.Bold))
            
            # Color code positions
            if row == 0:  # Champion
                pos_item.setForeground(QColor('#FFD700'))  # Gold
            elif row == 1:  # Runner-up
                pos_item.setForeground(QColor('#C0C0C0'))  # Silver
            elif row <= 1 and self.current_tier > 1:  # Promotion zone
                pos_item.setBackground(QColor('#d4edda'))
            elif row >= len(standings) - 2 and self.current_tier < 4:  # Relegation zone
                pos_item.setBackground(QColor('#f8d7da'))
            
            self.standings_table.setItem(row, 0, pos_item)
            
            # Team name
            team_item = QTableWidgetItem(team.name)
            team_item.setFont(QFont('Arial', 12, QFont.Weight.Bold))
            
            # Highlight user team
            if self.game_engine.user_team and team.name == self.game_engine.user_team.name:
                team_item.setBackground(QColor(COLORS['highlight_blue']))
            
            self.standings_table.setItem(row, 1, team_item)
            
            # Played
            played_item = self.create_center_item(str(stats['matches_played']))
            self.standings_table.setItem(row, 2, played_item)
            
            # Won
            won_item = self.create_center_item(str(stats['wins']))
            won_item.setForeground(QColor('#27ae60'))
            self.standings_table.setItem(row, 3, won_item)
            
            # Lost
            lost_item = self.create_center_item(str(stats['losses']))
            lost_item.setForeground(QColor('#e74c3c'))
            self.standings_table.setItem(row, 4, lost_item)
            
            # Drawn
            drawn_item = self.create_center_item(str(stats['draws']))
            self.standings_table.setItem(row, 5, drawn_item)
            
            # Points
            points_item = self.create_center_item(str(stats['points']))
            points_item.setFont(QFont('Arial', 12, QFont.Weight.Bold))
            points_item.setForeground(QColor(COLORS['primary']))
            self.standings_table.setItem(row, 6, points_item)
            
            # NRR
            nrr = stats.get('nrr', 0.0)
            nrr_text = f"+{nrr:.3f}" if nrr >= 0 else f"{nrr:.3f}"
            nrr_item = self.create_center_item(nrr_text)
            nrr_item.setForeground(QColor('#27ae60') if nrr >= 0 else QColor('#e74c3c'))
            self.standings_table.setItem(row, 7, nrr_item)
            
            # Form (last 5 matches)
            form = self.get_team_form(team, stats)
            form_item = QTableWidgetItem(form)
            form_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            form_item.setFont(QFont('Arial', 11, QFont.Weight.Bold))
            self.standings_table.setItem(row, 8, form_item)
        
        # Adjust row heights
        for row in range(self.standings_table.rowCount()):
            self.standings_table.setRowHeight(row, 45)
    
    def get_team_form(self, team, stats):
        """Get team's recent form (last 5 matches)"""
        # For now, generate based on win percentage
        matches = stats['matches_played']
        if matches == 0:
            return "-"
        
        wins = stats['wins']
        win_pct = wins / matches if matches > 0 else 0
        
        # Generate form string (W = Win, L = Loss, D = Draw)
        form_chars = []
        recent_matches = min(5, matches)
        
        for i in range(recent_matches):
            rand = random.random()
            if rand < win_pct:
                form_chars.append("W")
            elif rand < win_pct + 0.2:
                form_chars.append("D")
            else:
                form_chars.append("L")
        
        return " ".join(form_chars) if form_chars else "-"
    
    def create_center_item(self, text):
        """Create centered table item"""
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item
    
    def on_format_changed(self, format_type):
        """Handle format change"""
        self.current_format = format_type
        self.load_standings()
    
    def on_tier_changed(self, index):
        """Handle tier change"""
        self.current_tier = index + 1
        self.load_standings()
    
    def simulate_season(self):
        """Simulate entire season"""
        from PyQt6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self,
            "Simulate Season",
            f"Simulate entire season for {self.current_format}?\n\nThis will simulate all remaining matches.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Show progress
            from PyQt6.QtWidgets import QProgressDialog
            from PyQt6.QtCore import Qt
            
            progress = QProgressDialog(
                f"Simulating {self.current_format} season...",
                "Cancel",
                0,
                100,
                self
            )
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setMinimumDuration(0)
            progress.setValue(0)
            
            # Simulate season
            def update_progress(message, value):
                progress.setLabelText(message)
                progress.setValue(int(value))
                QApplication.processEvents()
            
            from PyQt6.QtWidgets import QApplication
            summary = self.game_engine.simulate_season(
                format_type=self.current_format,
                headless=True,
                progress_callback=update_progress
            )
            
            progress.setValue(100)
            progress.close()
            
            # Complete season (player development, tier changes, etc.)
            completion_summary = self.game_engine.complete_season(self.current_format)
            
            # Merge summaries
            summary.update(completion_summary)
            
            # Refresh standings
            self.load_standings()
            
            # Show season summary
            from cricket_manager.ui.season_summary_view import SeasonSummaryDialog
            dialog = SeasonSummaryDialog(summary, self)
            dialog.exec()
    
    def refresh_standings(self):
        """Public method to refresh standings (called after matches)"""
        self.load_standings()


import random
