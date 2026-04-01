"""
Enhanced Fixtures Screen - View and play individual matches
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QFrame,
    QScrollArea, QHeaderView, QGridLayout, QDialog, QTextEdit, QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from cricket_manager.ui.styles import COLORS, get_tier_color, MAIN_STYLESHEET
from cricket_manager.ui.screen_manager import BaseScreen


class FixturesScreenEnhanced(BaseScreen):
    """Enhanced fixtures screen with play functionality"""
    
    def __init__(self, screen_manager=None, game_engine=None):
        super().__init__(screen_manager)
        self.setStyleSheet(MAIN_STYLESHEET)
        self.game_engine = game_engine
        self.current_format = "T20"
        self.current_tier = 1
        self.show_completed = False
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
        
        # Content widget
        content = QWidget()
        content.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
        content_layout = QVBoxLayout()
        content_layout.setSpacing(25)
        content_layout.setContentsMargins(30, 30, 30, 30)
        
        # Filters section
        filters = self.create_filters()
        content_layout.addWidget(filters)
        
        # Season info
        season_info = self.create_season_info()
        content_layout.addWidget(season_info)
        
        # Fixtures list
        self.fixtures_container = self.create_fixtures_list()
        content_layout.addWidget(self.fixtures_container)
        
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
        
        # Title
        title = QLabel("Match Fixtures")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: 700;
            color: #EAF1FF;
        """)
        layout.addWidget(title)
        
        layout.addStretch()
        
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
        
        # Tier selector
        tier_label = QLabel("Tier:")
        tier_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #EAF1FF;")
        layout.addWidget(tier_label)
        
        self.tier_combo = QComboBox()
        self.tier_combo.addItems(["Tier 1", "Tier 2", "Tier 3", "Tier 4"])
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
        
        # Show completed toggle
        self.completed_btn = QPushButton("Show Completed")
        self.completed_btn.setCheckable(True)
        self.completed_btn.setChecked(self.show_completed)
        self.completed_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.completed_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_tertiary']};
                color: #EAF1FF;
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:checked {{
                background-color: {COLORS['primary']};
                color: white;
                border: 2px solid {COLORS['primary']};
            }}
            QPushButton:hover {{
                border: 2px solid {COLORS['primary']};
            }}
        """)
        self.completed_btn.clicked.connect(self.on_toggle_completed)
        layout.addWidget(self.completed_btn)
        
        container.setLayout(layout)
        return container
    
    def create_season_info(self):
        """Create season information cards"""
        container = QFrame()
        container.setStyleSheet(f"""
            background-color: #111827;
            border-radius: 8px;
            border: 1px solid {COLORS['border']};
            padding: 20px;
        """)
        
        layout = QGridLayout()
        layout.setSpacing(15)
        
        # Get real fixture counts
        if self.game_engine:
            fixtures = self.game_engine.fixtures.get(self.current_format, [])
            total = len(fixtures)
            completed = sum(1 for f in fixtures if f.get('completed', False))
            remaining = total - completed
        else:
            total = 330
            completed = 0
            remaining = 330
        
        info_items = [
            (str(total), "Total Fixtures", f"{self.current_format} season", COLORS['primary']),
            (str(completed), "Completed", "This season", COLORS['success']),
            (str(remaining), "Remaining", "To play", COLORS['warning']),
            (f"Tier {self.current_tier}", "Viewing", "Current filter", COLORS['info']),
        ]
        
        for i, (value, title_text, subtitle, color) in enumerate(info_items):
            card = self.create_info_card(value, title_text, subtitle, color)
            layout.addWidget(card, 0, i)
        
        container.setLayout(layout)
        return container
    
    def create_info_card(self, value, title_text, subtitle, color):
        """Create an info card"""
        card = QFrame()
        card.setMinimumHeight(90)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_tertiary']};
                border-radius: 6px;
                border-left: 4px solid {color};
                padding: 12px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(4)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 700;
            color: {color};
            background: transparent;
        """)
        layout.addWidget(value_label)
        
        title_label = QLabel(title_text)
        title_label.setStyleSheet("""
            font-size: 12px;
            font-weight: 600;
            color: #EAF1FF;
            background: transparent;
        """)
        layout.addWidget(title_label)
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("""
            font-size: 10px;
            color: #888;
            background: transparent;
        """)
        layout.addWidget(subtitle_label)
        
        card.setLayout(layout)
        return card
    
    def create_fixtures_list(self):
        """Create fixtures list with play buttons"""
        container = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        
        if not self.game_engine:
            # Show placeholder
            placeholder = QLabel("No fixtures available")
            placeholder.setStyleSheet("font-size: 14px; color: #888; padding: 50px;")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(placeholder)
            container.setLayout(layout)
            return container
        
        # Get fixtures for current format and tier
        all_fixtures = self.game_engine.fixtures.get(self.current_format, [])
        
        # Filter by tier
        tier_fixtures = []
        for fixture in all_fixtures:
            team1 = fixture.get('team1')
            if team1 and team1.format_tiers.get(self.current_format) == self.current_tier:
                # Filter by completion status
                is_completed = fixture.get('completed', False)
                if self.show_completed == is_completed or (self.show_completed and is_completed):
                    tier_fixtures.append(fixture)
        
        if not tier_fixtures:
            # Show no fixtures message
            msg = "No completed fixtures" if self.show_completed else "No upcoming fixtures"
            placeholder = QLabel(msg)
            placeholder.setStyleSheet("font-size: 14px; color: #888; padding: 50px;")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(placeholder)
        else:
            # Show fixtures (limit to 50 for performance)
            for fixture in tier_fixtures[:50]:
                fixture_card = self.create_fixture_card(fixture)
                layout.addWidget(fixture_card)
        
        layout.addStretch()
        container.setLayout(layout)
        return container
    
    def create_fixture_card(self, fixture):
        """Create a fixture card with play button"""
        card = QFrame()
        is_completed = fixture.get('completed', False)
        
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #111827;
                border-radius: 8px;
                border: 1px solid {COLORS['border']};
                padding: 15px;
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setSpacing(20)
        
        # Team 1
        team1 = fixture.get('team1')
        team1_label = QLabel(team1.name if team1 else "TBD")
        team1_label.setStyleSheet("""
            font-size: 14px;
            font-weight: 600;
            color: #EAF1FF;
            min-width: 150px;
        """)
        team1_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(team1_label)
        
        # VS or Score
        if is_completed:
            # Show result
            winner = fixture.get('winner', 'Draw')
            margin = fixture.get('margin', '')
            
            result_widget = QWidget()
            result_layout = QVBoxLayout()
            result_layout.setSpacing(2)
            result_layout.setContentsMargins(0, 0, 0, 0)
            
            vs_label = QLabel("RESULT")
            vs_label.setStyleSheet(f"""
                font-size: 10px;
                font-weight: 700;
                color: {COLORS['success']};
            """)
            vs_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            result_layout.addWidget(vs_label)
            
            winner_label = QLabel(f"{winner}")
            winner_label.setStyleSheet("""
                font-size: 12px;
                font-weight: 700;
                color: #EAF1FF;
            """)
            winner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            result_layout.addWidget(winner_label)
            
            margin_label = QLabel(f"by {margin}")
            margin_label.setStyleSheet("""
                font-size: 10px;
                color: #666;
            """)
            margin_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            result_layout.addWidget(margin_label)
            
            result_widget.setLayout(result_layout)
            result_widget.setFixedWidth(120)
            layout.addWidget(result_widget)
        else:
            vs_label = QLabel("VS")
            vs_label.setStyleSheet(f"""
                font-size: 16px;
                font-weight: 700;
                color: {COLORS['text_secondary']};
                min-width: 60px;
            """)
            vs_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(vs_label)
        
        # Team 2
        team2 = fixture.get('team2')
        team2_label = QLabel(team2.name if team2 else "TBD")
        team2_label.setStyleSheet("""
            font-size: 14px;
            font-weight: 600;
            color: #EAF1FF;
            min-width: 150px;
        """)
        team2_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(team2_label)
        
        layout.addStretch()
        
        # Home indicator
        home_team = fixture.get('home_team')
        if home_team:
            home_label = QLabel(f"🏠 {home_team.name}")
            home_label.setStyleSheet("""
                font-size: 11px;
                color: #666;
            """)
            layout.addWidget(home_label)
        
        # Action buttons
        if is_completed:
            # View scorecard button
            view_btn = QPushButton("📊 View Scorecard")
            view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            view_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['info']};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-size: 13px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: #2196F3;
                }}
            """)
            view_btn.clicked.connect(lambda: self.view_scorecard(fixture))
            layout.addWidget(view_btn)
        else:
            # Play Interactive button
            interactive_btn = QPushButton("🎮 Play Interactive")
            interactive_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            interactive_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['accent']};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-size: 13px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: #E91E63;
                }}
            """)
            interactive_btn.clicked.connect(lambda: self.play_interactive(fixture))
            layout.addWidget(interactive_btn)
            
            # Quick Sim button
            play_btn = QPushButton("⚡ Quick Sim")
            play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            play_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['success']};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-size: 13px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: #45a049;
                }}
            """)
            play_btn.clicked.connect(lambda: self.play_match(fixture))
            layout.addWidget(play_btn)
        
        card.setLayout(layout)
        return card
    
    def play_match(self, fixture):
        """Play a single match"""
        if not self.game_engine:
            return
        
        # Simulate the match
        result = self.game_engine.simulate_match(fixture, self.current_format, headless=True)
        
        # Show result dialog
        self.show_match_result(fixture, result)
        
        # Refresh the fixtures list
        self.refresh_data()
        
        # Update main window top bar
        if hasattr(self.parent(), 'update_top_bar'):
            self.parent().update_top_bar()
    
    def show_match_result(self, fixture, result):
        """Show match result in a dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Match Result")
        dialog.setMinimumWidth(800)
        dialog.setMinimumHeight(600)
        
        layout = QVBoxLayout()
        
        # Header
        header = QFrame()
        header.setStyleSheet(f"background-color: {COLORS['primary']}; padding: 20px;")
        header_layout = QVBoxLayout()
        
        title = QLabel(f"{fixture['team1'].name} vs {fixture['team2'].name}")
        title.setStyleSheet("font-size: 24px; font-weight: 700; color: white;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)
        
        result_label = QLabel(f"Winner: {result['winner']} by {result['margin']}")
        result_label.setStyleSheet("font-size: 16px; color: white;")
        result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(result_label)
        
        header.setLayout(header_layout)
        layout.addWidget(header)
        
        # Scorecard tabs
        tabs = QTabWidget()
        
        # Get scorecard
        scorecard = result.get('scorecard', {})
        innings_list = scorecard.get('innings', [])
        
        for innings in innings_list:
            tab = self.create_innings_tab(innings)
            innings_num = innings.get('innings_num', 1)
            batting_team = innings.get('batting_team', 'Team')
            tabs.addTab(tab, f"Innings {innings_num}: {batting_team}")
        
        layout.addWidget(tabs)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                padding: 12px;
                font-size: 14px;
                font-weight: 600;
                border-radius: 6px;
            }}
        """)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def create_innings_tab(self, innings):
        """Create innings scorecard tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Innings summary
        summary = QLabel(
            f"{innings['batting_team']}: {innings['total_runs']}/{innings['wickets_fallen']} "
            f"({innings['overs']} overs)"
        )
        summary.setStyleSheet("font-size: 16px; font-weight: 700; padding: 10px;")
        layout.addWidget(summary)
        
        # Batting card
        batting_label = QLabel("Batting")
        batting_label.setStyleSheet("font-size: 14px; font-weight: 700;")
        layout.addWidget(batting_label)
        
        batting_table = QTableWidget()
        batting_table.setColumnCount(6)
        batting_table.setHorizontalHeaderLabels(["Batter", "Runs", "Balls", "4s", "6s", "SR"])
        
        batting_card = innings.get('batting_card', [])
        batting_table.setRowCount(len(batting_card))
        
        for row, perf in enumerate(batting_card):
            batting_table.setItem(row, 0, QTableWidgetItem(perf['player']))
            batting_table.setItem(row, 1, QTableWidgetItem(str(perf['runs'])))
            batting_table.setItem(row, 2, QTableWidgetItem(str(perf['balls'])))
            batting_table.setItem(row, 3, QTableWidgetItem(str(perf['fours'])))
            batting_table.setItem(row, 4, QTableWidgetItem(str(perf['sixes'])))
            batting_table.setItem(row, 5, QTableWidgetItem(f"{perf['strike_rate']:.1f}"))
        
        self.style_scorecard_table(batting_table)
        layout.addWidget(batting_table)
        
        # Bowling card
        bowling_label = QLabel("Bowling")
        bowling_label.setStyleSheet("font-size: 14px; font-weight: 700;")
        layout.addWidget(bowling_label)
        
        bowling_table = QTableWidget()
        bowling_table.setColumnCount(6)
        bowling_table.setHorizontalHeaderLabels(["Bowler", "Overs", "Maidens", "Runs", "Wickets", "Econ"])
        
        bowling_card = innings.get('bowling_card', [])
        bowling_table.setRowCount(len(bowling_card))
        
        for row, perf in enumerate(bowling_card):
            bowling_table.setItem(row, 0, QTableWidgetItem(perf['player']))
            bowling_table.setItem(row, 1, QTableWidgetItem(str(perf['overs'])))
            bowling_table.setItem(row, 2, QTableWidgetItem(str(perf['maidens'])))
            bowling_table.setItem(row, 3, QTableWidgetItem(str(perf['runs'])))
            bowling_table.setItem(row, 4, QTableWidgetItem(str(perf['wickets'])))
            bowling_table.setItem(row, 5, QTableWidgetItem(f"{perf['economy']:.2f}"))
        
        self.style_scorecard_table(bowling_table)
        layout.addWidget(bowling_table)
        
        widget.setLayout(layout)
        return widget
    
    def style_scorecard_table(self, table):
        """Style scorecard table"""
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: #111827;
                border: 1px solid {COLORS['border']};
                font-size: 12px;
            }}
            QHeaderView::section {{
                background-color: {COLORS['primary']};
                color: white;
                padding: 8px;
                font-weight: 700;
            }}
        """)
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
    
    def view_scorecard(self, fixture):
        """View scorecard for completed match"""
        # Get scorecard from match_scorecards
        team1 = fixture['team1']
        team2 = fixture['team2']
        scorecard_key = (team1.name, team2.name, self.game_engine.current_season, self.current_format)
        
        scorecard = self.game_engine.match_scorecards.get(scorecard_key)
        
        if not scorecard:
            # Try reverse key
            scorecard_key = (team2.name, team1.name, self.game_engine.current_season, self.current_format)
            scorecard = self.game_engine.match_scorecards.get(scorecard_key)
        
        if scorecard:
            result = {
                'winner': fixture.get('winner', 'Draw'),
                'margin': fixture.get('margin', ''),
                'scorecard': scorecard
            }
            self.show_match_result(fixture, result)
    
    def on_format_changed(self, format_type):
        """Handle format change"""
        self.current_format = format_type
        self.refresh_data()
    
    def on_tier_changed(self, tier_text):
        """Handle tier change"""
        self.current_tier = int(tier_text.split()[-1])
        self.refresh_data()
    
    def on_toggle_completed(self):
        """Toggle showing completed fixtures"""
        self.show_completed = self.completed_btn.isChecked()
        self.refresh_data()
    
    def refresh_data(self):
        """Refresh fixtures list"""
        # Recreate fixtures list
        old_container = self.fixtures_container
        self.fixtures_container = self.create_fixtures_list()
        
        # Replace in layout
        layout = self.layout().itemAt(0).widget().widget().layout()
        layout.replaceWidget(old_container, self.fixtures_container)
        old_container.deleteLater()
        
        # Update season info
        season_info_widget = layout.itemAt(1).widget()
        new_season_info = self.create_season_info()
        layout.replaceWidget(season_info_widget, new_season_info)
        season_info_widget.deleteLater()

    
    def play_interactive(self, fixture):
        """Play match interactively with controls"""
        if not self.game_engine:
            return
        
        from cricket_manager.ui.interactive_match_player import InteractiveMatchPlayer
        
        # Open interactive match player
        player = InteractiveMatchPlayer(
            self,
            fixture['team1'],
            fixture['team2'],
            self.current_format,
            self.game_engine
        )
        
        # Connect completion signal
        player.match_completed.connect(lambda result: self.on_interactive_match_complete(fixture, result))
        
        # Show dialog
        player.exec()
    
    def on_interactive_match_complete(self, fixture, result):
        """Handle interactive match completion"""
        # Mark fixture as completed
        fixture['completed'] = True
        fixture['winner'] = result['winner']
        fixture['margin'] = result.get('margin', '')
        
        # Store scorecard (create a basic scorecard from the match data)
        # Note: Interactive matches don't generate full scorecards like fast simulator
        # We could enhance this later to store detailed ball-by-ball data
        
        # Refresh display
        self.refresh_data()
        
        # Update main window
        if hasattr(self.parent(), 'update_top_bar'):
            self.parent().update_top_bar()
