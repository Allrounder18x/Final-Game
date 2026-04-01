"""
Match Simulator View - Professional match simulation with T20/ODI/Test support
Uses t20oversimulation.py and test_match_enhanced.py for accurate simulation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QFrame, QHeaderView,
    QScrollArea, QTextEdit, QSlider, QGroupBox, QGridLayout,
    QMessageBox, QProgressBar, QTabWidget, QSplitter
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap

from cricket_manager.ui.styles import COLORS, MAIN_STYLESHEET
from cricket_manager.ui.screen_manager import BaseScreen


class MatchSimulatorThread(QThread):
    """Thread for running match simulation in background"""
    update_signal = pyqtSignal(dict)
    finished_signal = pyqtSignal(dict)
    
    def __init__(self, match_type, team1, team2, match_format):
        super().__init__()
        self.setStyleSheet(MAIN_STYLESHEET)
        self.match_type = match_type
        self.team1 = team1
        self.team2 = team2
        self.match_format = match_format
        self.result = None
        
    def run(self):
        """Run the match simulation"""
        try:
            if self.match_type in ['T20', 'ODI']:
                # Use t20oversimulation.py
                from t20oversimulation import T20Match
                
                # Convert teams to expected format
                team1_data = self._convert_team_to_format(self.team1)
                team2_data = self._convert_team_to_format(self.team2)
                
                # Create match in headless mode
                match = T20Match(None, team1_data, team2_data, self.match_format, headless=True)
                match.quick_simulate_match()
                
                # Get result
                self.result = {
                    'winner': match.result,
                    'team1_score': f"{match.first_innings_score}/{match.first_innings_wickets}",
                    'team2_score': f"{match.total_runs}/{match.total_wickets}",
                    'match_stats': match.match_stats,
                    'pitch_conditions': {
                        'pace': match.pitch_pace_rating,
                        'spin': match.pitch_spin_rating,
                        'bounce': match.pitch_bounce_rating
                    }
                }
                
            else:  # Test match
                # Use test_match_enhanced.py
                from test_match_enhanced import TestMatchSimulator
                
                # Convert teams to expected format
                team1_data = self._convert_team_to_format(self.team1)
                team2_data = self._convert_team_to_format(self.team2)
                
                # Create test match
                test_match = TestMatchSimulator(team1_data, team2_data)
                test_match.auto_select_xi(team1_data)
                test_match.auto_select_xi(team2_data)
                
                # Simulate match (simplified for now)
                test_match.simulate_full_match()
                
                # Get result
                self.result = {
                    'winner': test_match.winner,
                    'result': test_match.result,
                    'innings_data': test_match.innings_data,
                    'pitch_type': test_match.pitch_type,
                    'pitch_conditions': {
                        'pace': test_match.pitch_pace,
                        'spin': test_match.pitch_spin,
                        'bounce': test_match.pitch_bounce
                    }
                }
            
            self.finished_signal.emit(self.result)
            
        except Exception as e:
            print(f"Match simulation error: {e}")
            self.result = {'error': str(e)}
            self.finished_signal.emit(self.result)
    
    def _convert_team_to_format(self, team):
        """Convert team object to expected format for simulators"""
        players = []
        for player in team.players:
            players.append({
                'name': player.name,
                'role': player.role,
                'batting': player.batting,
                'bowling': player.bowling,
                'fielding': player.fielding,
                'age': player.age
            })
        
        return {
            'name': team.name,
            'players': players
        }


class MatchSimulatorView(BaseScreen):
    """Professional match simulator view with accurate simulation engines"""
    
    def __init__(self, screen_manager=None, game_engine=None):
        super().__init__(screen_manager)
        self.game_engine = game_engine
        self.match_thread = None
        self.current_match = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the match simulator UI"""
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Main content area
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Match setup and controls
        left_panel = self.create_left_panel()
        main_splitter.addWidget(left_panel)
        
        # Right panel - Live match display
        right_panel = self.create_right_panel()
        main_splitter.addWidget(right_panel)
        
        main_splitter.setSizes([400, 800])
        layout.addWidget(main_splitter)
        
        self.setLayout(layout)
    
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
        
        layout = QVBoxLayout()
        
        title = QLabel("⚡ Match Simulator")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        layout.addWidget(title)
        
        subtitle = QLabel("Professional match simulation with accurate engines")
        subtitle.setStyleSheet("font-size: 14px; color: white;")
        layout.addWidget(subtitle)
        
        header.setLayout(layout)
        return header
    
    def create_left_panel(self):
        """Create left control panel"""
        left_panel = QFrame()
        left_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_primary']};
                border-right: 2px solid {COLORS['border']};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Match Setup Group
        setup_group = QGroupBox("Match Setup")
        setup_group.setStyleSheet(f"""
            QGroupBox {{
                font-size: 16px;
                font-weight: bold;
                color: {COLORS['text_primary']};
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                margin-top: 16px;
                padding-top: 20px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 6px 16px;
                color: white;
                background-color: {COLORS['primary']};
                border-radius: 6px;
                margin-left: 12px;
            }}
        """)
        
        setup_layout = QVBoxLayout()
        
        # Team selection
        team_label = QLabel("Select Teams:")
        team_label.setStyleSheet("font-size: 14px; font-weight: 600;")
        setup_layout.addWidget(team_label)
        
        self.team1_combo = self.create_team_combo()
        setup_layout.addWidget(self.team1_combo)
        
        self.team2_combo = self.create_team_combo()
        setup_layout.addWidget(self.team2_combo)
        
        # Format selection
        format_label = QLabel("Match Format:")
        format_label.setStyleSheet("font-size: 14px; font-weight: 600;")
        setup_layout.addWidget(format_label)
        
        self.format_combo = self.create_format_combo()
        setup_layout.addWidget(self.format_combo)
        
        # Pitch conditions
        pitch_group = QGroupBox("Pitch Conditions")
        pitch_group.setStyleSheet(f"""
            QGroupBox {{
                font-size: 14px;
                font-weight: 600;
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border_light']};
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 16px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 12px;
                color: {COLORS['text_primary']};
                background-color: {COLORS['bg_tertiary']};
                border-radius: 4px;
                margin-left: 8px;
            }}
        """)
        
        pitch_layout = QGridLayout()
        
        # Pace slider
        pace_label = QLabel("Pace Assistance:")
        pace_label.setStyleSheet("font-size: 12px;")
        pitch_layout.addWidget(pace_label, 0, 0)
        
        self.pace_slider = QSlider(Qt.Orientation.Horizontal)
        self.pace_slider.setRange(1, 10)
        self.pace_slider.setValue(5)
        self.pace_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                height: 6px;
                background: {COLORS['bg_tertiary']};
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {COLORS['primary']};
                border: 2px solid white;
                width: 18px;
                height: 18px;
                border-radius: 9px;
            }}
        """)
        pitch_layout.addWidget(self.pace_slider, 0, 1)
        
        self.pace_value = QLabel("5")
        self.pace_value.setStyleSheet("font-size: 12px; font-weight: 600;")
        pitch_layout.addWidget(self.pace_value, 0, 2)
        
        # Spin slider
        spin_label = QLabel("Spin Assistance:")
        spin_label.setStyleSheet("font-size: 12px;")
        pitch_layout.addWidget(spin_label, 1, 0)
        
        self.spin_slider = QSlider(Qt.Orientation.Horizontal)
        self.spin_slider.setRange(1, 10)
        self.spin_slider.setValue(5)
        self.spin_slider.setStyleSheet(self.pace_slider.styleSheet())
        pitch_layout.addWidget(self.spin_slider, 1, 1)
        
        self.spin_value = QLabel("5")
        self.spin_value.setStyleSheet("font-size: 12px; font-weight: 600;")
        pitch_layout.addWidget(self.spin_value, 1, 2)
        
        # Bounce slider
        bounce_label = QLabel("Bounce:")
        bounce_label.setStyleSheet("font-size: 12px;")
        pitch_layout.addWidget(bounce_label, 2, 0)
        
        self.bounce_slider = QSlider(Qt.Orientation.Horizontal)
        self.bounce_slider.setRange(1, 10)
        self.bounce_slider.setValue(5)
        self.bounce_slider.setStyleSheet(self.pace_slider.styleSheet())
        pitch_layout.addWidget(self.bounce_slider, 2, 1)
        
        self.bounce_value = QLabel("5")
        self.bounce_value.setStyleSheet("font-size: 12px; font-weight: 600;")
        pitch_layout.addWidget(self.bounce_value, 2, 2)
        
        # Connect sliders
        self.pace_slider.valueChanged.connect(lambda v: self.pace_value.setText(str(v)))
        self.spin_slider.valueChanged.connect(lambda v: self.spin_value.setText(str(v)))
        self.bounce_slider.valueChanged.connect(lambda v: self.bounce_value.setText(str(v)))
        
        pitch_group.setLayout(pitch_layout)
        setup_layout.addWidget(pitch_group)
        
        setup_group.setLayout(setup_layout)
        layout.addWidget(setup_group)
        
        # Control buttons
        self.start_button = QPushButton("🏏 Start Match")
        self.start_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: white;
                border: none;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['success_dark']};
            }}
            QPushButton:disabled {{
                background-color: {COLORS['text_secondary']};
            }}
        """)
        self.start_button.clicked.connect(self.start_match)
        layout.addWidget(self.start_button)
        
        self.quick_sim_button = QPushButton("⚡ Quick Simulate")
        self.quick_sim_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['secondary']};
                color: white;
                border: none;
                padding: 12px;
                font-size: 14px;
                font-weight: 600;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['secondary_dark']};
            }}
        """)
        self.quick_sim_button.clicked.connect(self.quick_simulate)
        layout.addWidget(self.quick_sim_button)
        
        layout.addStretch()
        left_panel.setLayout(layout)
        
        return left_panel
    
    def create_right_panel(self):
        """Create right display panel"""
        right_panel = QFrame()
        right_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_primary']};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Match status
        self.status_label = QLabel("Ready to start match")
        self.status_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {COLORS['text_primary']};
            padding: 15px;
            background-color: {COLORS['bg_tertiary']};
            border-radius: 8px;
            border: 2px solid {COLORS['border']};
        """)
        layout.addWidget(self.status_label)
        
        # Score display
        self.score_display = QLabel("No match in progress")
        self.score_display.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {COLORS['primary']};
            padding: 20px;
            background-color: #111827;
            border-radius: 8px;
            border: 2px solid {COLORS['border']};
        """)
        self.score_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.score_display)
        
        # Commentary
        commentary_group = QGroupBox("Live Commentary")
        commentary_group.setStyleSheet(f"""
            QGroupBox {{
                font-size: 16px;
                font-weight: bold;
                color: {COLORS['text_primary']};
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                margin-top: 16px;
                padding-top: 20px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 6px 16px;
                color: white;
                background-color: {COLORS['primary']};
                border-radius: 6px;
                margin-left: 12px;
            }}
        """)
        
        commentary_layout = QVBoxLayout()
        
        self.commentary_text = QTextEdit()
        self.commentary_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: #111827;
                border: 1px solid {COLORS['border_light']};
                border-radius: 6px;
                padding: 10px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }}
        """)
        self.commentary_text.setReadOnly(True)
        self.commentary_text.setMaximumHeight(200)
        commentary_layout.addWidget(self.commentary_text)
        
        commentary_group.setLayout(commentary_layout)
        layout.addWidget(commentary_group)
        
        # Match stats tabs
        self.stats_tabs = QTabWidget()
        self.stats_tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background-color: {COLORS['bg_primary']};
            }}
            QTabBar::tab {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_primary']};
                padding: 10px 20px;
                margin-right: 4px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 14px;
                font-weight: 600;
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS['primary']};
                color: white;
            }}
        """)
        
        # Batting stats tab
        self.batting_table = self.create_stats_table(['Player', 'Runs', 'Balls', 'SR', '4s', '6s', 'Dismissal'])
        self.stats_tabs.addTab(self.batting_table, "🏏 Batting")
        
        # Bowling stats tab
        self.bowling_table = self.create_stats_table(['Player', 'Overs', 'Runs', 'Wickets', 'Econ', 'Maidens'])
        self.stats_tabs.addTab(self.bowling_table, "⚾ Bowling")
        
        layout.addWidget(self.stats_tabs)
        
        right_panel.setLayout(layout)
        
        return right_panel
    
    def create_team_combo(self):
        """Create team selection combo box"""
        from PyQt6.QtWidgets import QComboBox
        
        combo = QComboBox()
        combo.setStyleSheet(f"""
            QComboBox {{
                padding: 10px;
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
                font-size: 14px;
                background-color: #111827;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {COLORS['text_secondary']};
            }}
        """)
        
        if self.game_engine:
            for team in self.game_engine.all_teams:
                combo.addItem(team.name, team)
        
        return combo
    
    def create_format_combo(self):
        """Create format selection combo box"""
        from PyQt6.QtWidgets import QComboBox
        
        combo = QComboBox()
        combo.addItems(['T20', 'ODI', 'Test'])
        combo.setStyleSheet(f"""
            QComboBox {{
                padding: 10px;
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
                font-size: 14px;
                background-color: #111827;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {COLORS['text_secondary']};
            }}
        """)
        
        return combo
    
    def create_stats_table(self, headers):
        """Create statistics table"""
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setStyleSheet(f"""
            QTableWidget {{
                border: none;
                background-color: #111827;
                gridline-color: {COLORS['border_light']};
                font-size: 12px;
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {COLORS['border_light']};
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['highlight_blue']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['primary']};
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 12px;
            }}
        """)
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        return table
    
    def start_match(self):
        """Start interactive match simulation"""
        if not self.validate_selection():
            return
        
        team1 = self.team1_combo.currentData()
        team2 = self.team2_combo.currentData()
        match_format = self.format_combo.currentText()
        
        self.status_label.setText(f"Starting {match_format} match...")
        self.add_commentary(f"🏏 {match_format} Match: {team1.name} vs {team2.name}")
        self.add_commentary("Match simulation in progress...")
        
        # Disable buttons during match
        self.start_button.setEnabled(False)
        self.quick_sim_button.setEnabled(False)
        
        # Start simulation thread
        self.match_thread = MatchSimulatorThread(match_format, team1, team2, match_format)
        self.match_thread.finished_signal.connect(self.on_match_finished)
        self.match_thread.start()
    
    def quick_simulate(self):
        """Quick simulate match without interactive elements"""
        if not self.validate_selection():
            return
        
        team1 = self.team1_combo.currentData()
        team2 = self.team2_combo.currentData()
        match_format = self.format_combo.currentText()
        
        self.status_label.setText(f"Quick simulating {match_format} match...")
        self.add_commentary(f"⚡ Quick Simulating {match_format}: {team1.name} vs {team2.name}")
        
        # Disable buttons during simulation
        self.start_button.setEnabled(False)
        self.quick_sim_button.setEnabled(False)
        
        # Start quick simulation thread
        self.match_thread = MatchSimulatorThread(match_format, team1, team2, match_format)
        self.match_thread.finished_signal.connect(self.on_match_finished)
        self.match_thread.start()
    
    def validate_selection(self):
        """Validate team selection"""
        team1 = self.team1_combo.currentData()
        team2 = self.team2_combo.currentData()
        
        if not team1 or not team2:
            QMessageBox.warning(self, "Selection Error", "Please select both teams")
            return False
        
        if team1.name == team2.name:
            QMessageBox.warning(self, "Selection Error", "Please select different teams")
            return False
        
        return True
    
    def on_match_finished(self, result):
        """Handle match completion"""
        # Re-enable buttons
        self.start_button.setEnabled(True)
        self.quick_sim_button.setEnabled(True)
        
        if 'error' in result:
            self.status_label.setText("Simulation Error")
            self.add_commentary(f"❌ Error: {result['error']}")
            return
        
        # Display results
        if 'winner' in result:
            winner = result['winner']
            if winner:
                self.status_label.setText(f"🏆 Winner: {winner}")
                self.add_commentary(f"🎉 {winner} wins the match!")
            else:
                self.status_label.setText("Match Drawn")
                self.add_commentary("🤝 Match ended in a draw")
        
        # Update score display
        if 'team1_score' in result and 'team2_score' in result:
            team1 = self.team1_combo.currentData()
            team2 = self.team2_combo.currentData()
            self.score_display.setText(
                f"{team1.name}: {result['team1_score']}\n"
                f"{team2.name}: {result['team2_score']}"
            )
        
        # Update stats tables
        if 'match_stats' in result:
            self.update_stats_tables(result['match_stats'])
        
        self.add_commentary("✅ Match simulation complete!")
    
    def update_stats_tables(self, match_stats):
        """Update batting and bowling statistics tables"""
        # Clear existing data
        self.batting_table.setRowCount(0)
        self.bowling_table.setRowCount(0)
        
        batting_row = 0
        bowling_row = 0
        
        for player_name, stats in match_stats.items():
            # Batting stats
            if stats['batting']['balls'] > 0:
                self.batting_table.insertRow(batting_row)
                
                batting_data = stats['batting']
                sr = (batting_data['runs'] / batting_data['balls'] * 100) if batting_data['balls'] > 0 else 0
                
                self.batting_table.setItem(batting_row, 0, QTableWidgetItem(player_name))
                self.batting_table.setItem(batting_row, 1, QTableWidgetItem(str(batting_data['runs'])))
                self.batting_table.setItem(batting_row, 2, QTableWidgetItem(str(batting_data['balls'])))
                self.batting_table.setItem(batting_row, 3, QTableWidgetItem(f"{sr:.1f}"))
                self.batting_table.setItem(batting_row, 4, QTableWidgetItem(str(batting_data['fours'])))
                self.batting_table.setItem(batting_row, 5, QTableWidgetItem(str(batting_data['sixes'])))
                self.batting_table.setItem(batting_row, 6, QTableWidgetItem(batting_data['dismissal'] or "Not out"))
                
                batting_row += 1
            
            # Bowling stats
            if stats['bowling']['balls'] > 0:
                self.bowling_table.insertRow(bowling_row)
                
                bowling_data = stats['bowling']
                overs = bowling_data['balls'] // 6
                balls = bowling_data['balls'] % 6
                econ = (bowling_data['runs'] / (bowling_data['balls'] / 6)) if bowling_data['balls'] > 0 else 0
                
                self.bowling_table.setItem(bowling_row, 0, QTableWidgetItem(player_name))
                self.bowling_table.setItem(bowling_row, 1, QTableWidgetItem(f"{overs}.{balls}"))
                self.bowling_table.setItem(bowling_row, 2, QTableWidgetItem(str(bowling_data['runs'])))
                self.bowling_table.setItem(bowling_row, 3, QTableWidgetItem(str(bowling_data['wickets'])))
                self.bowling_table.setItem(bowling_row, 4, QTableWidgetItem(f"{econ:.2f}"))
                self.bowling_table.setItem(bowling_row, 5, QTableWidgetItem(str(bowling_data['maidens'])))
                
                bowling_row += 1
    
    def add_commentary(self, text):
        """Add commentary text"""
        self.commentary_text.append(text)
        # Auto-scroll to bottom
        scrollbar = self.commentary_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def refresh_data(self):
        """Refresh the match simulator"""
        # Update team lists
        self.team1_combo.clear()
        self.team2_combo.clear()
        
        if self.game_engine:
            for team in self.game_engine.all_teams:
                self.team1_combo.addItem(team.name, team)
                self.team2_combo.addItem(team.name, team)
