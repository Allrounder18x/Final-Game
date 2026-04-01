"""
Match Simulator Dialog - Professional match simulation dialog
Uses t20oversimulation.py and test_match_enhanced.py for accurate simulation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QFrame, QHeaderView,
    QScrollArea, QTextEdit, QSlider, QGroupBox, QGridLayout,
    QMessageBox, QProgressBar, QTabWidget, QSplitter
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from cricket_manager.ui.styles import COLORS, MAIN_STYLESHEET


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


class MatchSimulatorDialog(QDialog):
    """Professional match simulator dialog"""
    
    def __init__(self, parent=None, team1=None, team2=None, match_format='T20', game_engine=None):
        super().__init__(parent)
        self.team1 = team1
        self.team2 = team2
        self.match_format = match_format
        self.game_engine = game_engine
        self.match_thread = None
        self.match_result = None
        
        self.setWindowTitle(f"{match_format} Match Simulator")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['bg_primary']};
            }}
        """)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the dialog UI"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Main content
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Controls
        left_panel = self.create_control_panel()
        main_splitter.addWidget(left_panel)
        
        # Right panel - Match display
        right_panel = self.create_match_panel()
        main_splitter.addWidget(right_panel)
        
        main_splitter.setSizes([300, 700])
        layout.addWidget(main_splitter)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("🏏 Start Match")
        self.start_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['success_dark']};
            }}
            QPushButton:disabled {{
                background-color: {COLORS['text_secondary']};
            }}
        """)
        self.start_button.clicked.connect(self.start_match)
        button_layout.addWidget(self.start_button)
        
        self.quick_sim_button = QPushButton("⚡ Quick Sim")
        self.quick_sim_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['secondary']};
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['secondary_dark']};
            }}
            QPushButton:disabled {{
                background-color: {COLORS['text_secondary']};
            }}
        """)
        self.quick_sim_button.clicked.connect(self.quick_simulate)
        button_layout.addWidget(self.quick_sim_button)
        
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['text_secondary']};
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 14px;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['text_primary']};
            }}
        """)
        close_button.clicked.connect(self.reject)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def create_header(self):
        """Create header section"""
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary']}, stop:1 {COLORS['secondary']});
                padding: 15px;
                border-radius: 8px;
            }}
        """)
        
        layout = QHBoxLayout()
        
        title = QLabel(f"⚡ {self.match_format} Match")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        layout.addWidget(title)
        
        if self.team1 and self.team2:
            match_text = QLabel(f"{self.team1.name} vs {self.team2.name}")
            match_text.setStyleSheet("font-size: 16px; color: white;")
            layout.addWidget(match_text)
        
        layout.addStretch()
        
        header.setLayout(layout)
        return header
    
    def create_control_panel(self):
        """Create control panel"""
        control_panel = QFrame()
        control_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_tertiary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        # Match info
        info_group = QGroupBox("Match Information")
        info_group.setStyleSheet(f"""
            QGroupBox {{
                font-size: 14px;
                font-weight: bold;
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
                background-color: {COLORS['bg_primary']};
                border-radius: 4px;
                margin-left: 8px;
            }}
        """)
        
        info_layout = QVBoxLayout()
        
        if self.team1 and self.team2:
            team1_label = QLabel(f"Team 1: {self.team1.name}")
            team1_label.setStyleSheet("font-size: 12px; padding: 5px;")
            info_layout.addWidget(team1_label)
            
            team2_label = QLabel(f"Team 2: {self.team2.name}")
            team2_label.setStyleSheet("font-size: 12px; padding: 5px;")
            info_layout.addWidget(team2_label)
        
        format_label = QLabel(f"Format: {self.match_format}")
        format_label.setStyleSheet("font-size: 12px; padding: 5px;")
        info_layout.addWidget(format_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Pitch conditions
        pitch_group = QGroupBox("Pitch Conditions")
        pitch_group.setStyleSheet(info_group.styleSheet())
        
        pitch_layout = QGridLayout()
        
        # Pace slider
        pace_label = QLabel("Pace:")
        pace_label.setStyleSheet("font-size: 12px;")
        pitch_layout.addWidget(pace_label, 0, 0)
        
        self.pace_slider = QSlider(Qt.Orientation.Horizontal)
        self.pace_slider.setRange(1, 10)
        self.pace_slider.setValue(5)
        self.pace_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                height: 6px;
                background: {COLORS['bg_primary']};
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {COLORS['primary']};
                border: 2px solid white;
                width: 16px;
                height: 16px;
                border-radius: 8px;
            }}
        """)
        pitch_layout.addWidget(self.pace_slider, 0, 1)
        
        self.pace_value = QLabel("5")
        self.pace_value.setStyleSheet("font-size: 12px; font-weight: 600;")
        pitch_layout.addWidget(self.pace_value, 0, 2)
        
        # Spin slider
        spin_label = QLabel("Spin:")
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
        
        # Connect sliders
        self.pace_slider.valueChanged.connect(lambda v: self.pace_value.setText(str(v)))
        self.spin_slider.valueChanged.connect(lambda v: self.spin_value.setText(str(v)))
        
        pitch_group.setLayout(pitch_layout)
        layout.addWidget(pitch_group)
        
        # Status
        self.status_label = QLabel("Ready to start")
        self.status_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: bold;
            color: {COLORS['text_primary']};
            padding: 10px;
            background-color: {COLORS['bg_primary']};
            border-radius: 6px;
            border: 1px solid {COLORS['border']};
            text-align: center;
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        control_panel.setLayout(layout)
        
        return control_panel
    
    def create_match_panel(self):
        """Create match display panel"""
        match_panel = QFrame()
        match_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        # Score display
        self.score_display = QLabel("No match in progress")
        self.score_display.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {COLORS['primary']};
            padding: 15px;
            background-color: #111827;
            border-radius: 6px;
            border: 1px solid {COLORS['border']};
            text-align: center;
        """)
        self.score_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.score_display)
        
        # Commentary
        commentary_group = QGroupBox("Live Commentary")
        commentary_group.setStyleSheet(f"""
            QGroupBox {{
                font-size: 14px;
                font-weight: bold;
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 16px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 12px;
                color: white;
                background-color: {COLORS['primary']};
                border-radius: 4px;
                margin-left: 8px;
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
                font-size: 11px;
            }}
        """)
        self.commentary_text.setReadOnly(True)
        self.commentary_text.setMaximumHeight(150)
        commentary_layout.addWidget(self.commentary_text)
        
        commentary_group.setLayout(commentary_layout)
        layout.addWidget(commentary_group)
        
        # Stats tabs
        self.stats_tabs = QTabWidget()
        self.stats_tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background-color: {COLORS['bg_primary']};
            }}
            QTabBar::tab {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_primary']};
                padding: 8px 16px;
                margin-right: 4px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 12px;
                font-weight: 600;
            }}
            QTabBar::tab:selected {{
                background-color: {COLORS['primary']};
                color: white;
            }}
        """)
        
        # Batting stats
        self.batting_table = self.create_stats_table(['Player', 'Runs', 'Balls', 'SR', '4s', '6s'])
        self.stats_tabs.addTab(self.batting_table, "🏏 Batting")
        
        # Bowling stats
        self.bowling_table = self.create_stats_table(['Player', 'Overs', 'Runs', 'Wickets', 'Econ'])
        self.stats_tabs.addTab(self.bowling_table, "⚾ Bowling")
        
        layout.addWidget(self.stats_tabs)
        
        match_panel.setLayout(layout)
        
        return match_panel
    
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
                font-size: 11px;
            }}
            QTableWidget::item {{
                padding: 6px;
                border-bottom: 1px solid {COLORS['border_light']};
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['highlight_blue']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['primary']};
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: 11px;
            }}
        """)
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        return table
    
    def start_match(self):
        """Start interactive match simulation"""
        if not self.team1 or not self.team2:
            QMessageBox.warning(self, "Error", "Teams not properly set")
            return
        
        self.status_label.setText("Starting match...")
        self.add_commentary(f"🏏 {self.match_format} Match: {self.team1.name} vs {self.team2.name}")
        self.add_commentary("Match simulation in progress...")
        
        # Disable buttons during match
        self.start_button.setEnabled(False)
        self.quick_sim_button.setEnabled(False)
        
        # Start simulation thread
        self.match_thread = MatchSimulatorThread(self.match_format, self.team1, self.team2, self.match_format)
        self.match_thread.finished_signal.connect(self.on_match_finished)
        self.match_thread.start()
    
    def quick_simulate(self):
        """Quick simulate match"""
        if not self.team1 or not self.team2:
            QMessageBox.warning(self, "Error", "Teams not properly set")
            return
        
        self.status_label.setText("Quick simulating...")
        self.add_commentary(f"⚡ Quick Simulating {self.match_format}: {self.team1.name} vs {self.team2.name}")
        
        # Disable buttons during simulation
        self.start_button.setEnabled(False)
        self.quick_sim_button.setEnabled(False)
        
        # Start quick simulation thread
        self.match_thread = MatchSimulatorThread(self.match_format, self.team1, self.team2, self.match_format)
        self.match_thread.finished_signal.connect(self.on_match_finished)
        self.match_thread.start()
    
    def on_match_finished(self, result):
        """Handle match completion"""
        # Re-enable buttons
        self.start_button.setEnabled(True)
        self.quick_sim_button.setEnabled(True)
        
        if 'error' in result:
            self.status_label.setText("Simulation Error")
            self.add_commentary(f"❌ Error: {result['error']}")
            return
        
        # Store result for parent
        self.match_result = result
        
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
            self.score_display.setText(
                f"{self.team1.name}: {result['team1_score']}\n"
                f"{self.team2.name}: {result['team2_score']}"
            )
        
        # Update stats tables
        if 'match_stats' in result:
            self.update_stats_tables(result['match_stats'])
        
        self.add_commentary("✅ Match simulation complete!")
        
        # Accept dialog to indicate match was played
        self.accept()
    
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
                
                bowling_row += 1
    
    def add_commentary(self, text):
        """Add commentary text"""
        self.commentary_text.append(text)
        # Auto-scroll to bottom
        scrollbar = self.commentary_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
