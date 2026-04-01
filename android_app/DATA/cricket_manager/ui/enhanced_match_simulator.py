"""
Enhanced Match Simulator - Step 1: Basic Structure
Exact replica of t20oversimulation.py and test_match_enhanced.py GUI
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QFrame, QHeaderView,
    QScrollArea, QTextEdit, QSlider, QGroupBox, QGridLayout,
    QMessageBox, QProgressBar, QTabWidget, QSplitter,
    QComboBox
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap

from cricket_manager.ui.styles import COLORS, MAIN_STYLESHEET
from .enhanced_match_simulator_thread import EnhancedMatchSimulatorThread

class EnhancedMatchSimulator(QDialog):
    """Enhanced match simulator with exact replica GUI from t20oversimulation.py and test_match_enhanced.py"""
    
    def __init__(self, parent=None, team1=None, team2=None, match_format='T20', game_engine=None):
        super().__init__(parent)
        self.setStyleSheet(MAIN_STYLESHEET)
        self.team1 = team1
        self.team2 = team2
        self.match_format = match_format
        self.game_engine = game_engine
        # Bridge back to main window screens (for stats / profiles refresh)
        # This allows t20oversimulation.T20Match (Tkinter) to call back into
        # the Qt statistics and players views via self.screen_manager.
        self.screen_manager = getattr(parent, "screen_manager", None)
        
        # Match state
        self.is_playing = False
        self.current_over = 0
        self.current_ball = 0
        self.total_runs = 0
        self.total_wickets = 0
        self.striker = None
        self.non_striker = None
        self.current_bowler = None
        self.target = None
        
        # Control values
        self.batting_aggression = 50
        self.bowling_aggression = 50
        self.pace_rating = 5
        self.spin_rating = 5
        self.bounce_rating = 5
        self.bowling_line = 'Good Length'
        self.field_setting = 'Balanced'
        
        # Match statistics
        self.batting_stats = {}
        self.bowling_stats = {}
        self.fall_of_wickets = []
        
        # Thread for simulation
        self.match_thread = None
        
        # Test match specific state
        self.current_day = 1
        self.current_session = 1
        self.current_innings = 1
        self.sessions_per_day = 3
        
        # Pitch controls state
        self.pitch_controls_enabled = True
        
        # Setup window
        self.setup_window()
        
    def setup_window(self):
        """Setup the match window exactly like t20oversimulation.py"""
        self.setWindowTitle(f"{self.match_format} Match Simulator")
        self.setGeometry(100, 100, 1400, 900)
        
        # Main frames layout (exact replica)
        main_layout = QHBoxLayout()
        
        # Left frame (controls) - 400px width
        left_frame = QFrame()
        left_frame.setStyleSheet("background-color: #111827; border-right: 2px solid #334155;")
        left_frame.setFixedWidth(400)
        
        # Right frame (match display)
        right_frame = QFrame()
        right_frame.setStyleSheet("background-color: #0B1220;")
        
        main_layout.addWidget(left_frame)
        main_layout.addWidget(right_frame)
        
        self.setLayout(main_layout)
        
        # Setup left frame controls (exact replica)
        self.setup_left_frame(left_frame)
        
        # Setup right frame display
        self.setup_right_frame(right_frame)
        
        # Initialize match
        self.initialize_match()
    
    def setup_left_frame(self, left_frame):
        """Setup left frame with exact replica of t20oversimulation.py controls"""
        layout = QVBoxLayout()
        layout.setSpacing(5)
        
        # Control panel
        control_panel = QGroupBox("Match Controls")
        control_panel.setStyleSheet("""
            QGroupBox {
                font-size: 12px;
                font-weight: bold;
                border: 2px solid #334155;
                border-radius: 4px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: #1F2937;
                border-radius: 2px;
            }
        """)
        
        control_layout = QVBoxLayout()
        
        # Batting Aggression
        batting_label = QLabel("Batting Aggression:")
        batting_label.setStyleSheet("font-size: 11px;")
        control_layout.addWidget(batting_label)
        
        self.batting_slider = QSlider(Qt.Orientation.Horizontal)
        self.batting_slider.setRange(0, 100)
        self.batting_slider.setValue(50)
        self.batting_slider.valueChanged.connect(self.on_batting_aggression_change)
        control_layout.addWidget(self.batting_slider)
        
        control_layout.addSpacing(10)
        
        # Pitch Conditions frame
        pitch_frame = QGroupBox("Pitch Conditions")
        pitch_frame.setStyleSheet("""
            QGroupBox {
                font-size: 12px;
                font-weight: bold;
                border: 2px solid #334155;
                border-radius: 4px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: #1F2937;
                border-radius: 2px;
            }
        """)
        
        pitch_layout = QGridLayout()
        
        # Pace Bowler Assistance
        pace_label = QLabel("Pace Bowler Assistance:")
        pace_label.setStyleSheet("font-size: 11px;")
        pitch_layout.addWidget(pace_label, 0, 0)
        
        self.pace_slider = QSlider(Qt.Orientation.Horizontal)
        self.pace_slider.setRange(1, 10)
        self.pace_slider.setValue(self.pace_rating)
        self.pace_slider.valueChanged.connect(self.on_pitch_slider_change)
        pitch_layout.addWidget(self.pace_slider, 0, 1)
        
        # Spin Bowler Assistance
        spin_label = QLabel("Spin Bowler Assistance:")
        spin_label.setStyleSheet("font-size: 11px;")
        pitch_layout.addWidget(spin_label, 1, 0)
        
        self.spin_slider = QSlider(Qt.Orientation.Horizontal)
        self.spin_slider.setRange(1, 10)
        self.spin_slider.setValue(self.spin_rating)
        self.spin_slider.valueChanged.connect(self.on_pitch_slider_change)
        pitch_layout.addWidget(self.spin_slider, 1, 1)
        
        # Pitch Bounce
        bounce_label = QLabel("Pitch Bounce:")
        bounce_label.setStyleSheet("font-size: 11px;")
        pitch_layout.addWidget(bounce_label, 2, 0)
        
        self.bounce_slider = QSlider(Qt.Orientation.Horizontal)
        self.bounce_slider.setRange(1, 10)
        self.bounce_slider.setValue(self.bounce_rating)
        self.bounce_slider.valueChanged.connect(self.on_pitch_slider_change)
        pitch_layout.addWidget(self.bounce_slider, 2, 1)
        
        pitch_layout.setColumnStretch(1, 1)
        control_layout.addLayout(pitch_layout)
        
        # Pitch description
        self.pitch_description = QLabel(self.get_pitch_description())
        self.pitch_description.setStyleSheet("font-size: 10px; padding: 5px;")
        self.pitch_description.setWordWrap(True)
        control_layout.addWidget(self.pitch_description)
        
        control_layout.addSpacing(10)
        
        # Start button
        self.start_button = QPushButton(f"Start {self.match_format} Match")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.start_button.clicked.connect(self.start_match)
        control_layout.addWidget(self.start_button)
        
        control_panel.setLayout(control_layout)
        layout.addWidget(control_panel)
        
        # Bowling Controls
        bowling_frame = QGroupBox("Bowling Controls")
        bowling_frame.setStyleSheet("""
            QGroupBox {
                font-size: 12px;
                font-weight: bold;
                border: 2px solid #334155;
                border-radius: 4px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: #1F2937;
                border-radius: 2px;
            }
        """)
        
        bowling_layout = QVBoxLayout()
        
        # Bowling Aggression
        bowling_label = QLabel("Bowling Aggression:")
        bowling_label.setStyleSheet("font-size: 11px;")
        bowling_layout.addWidget(bowling_label)
        
        self.bowling_slider = QSlider(Qt.Orientation.Horizontal)
        self.bowling_slider.setRange(0, 100)
        self.bowling_slider.setValue(50)
        self.bowling_slider.valueChanged.connect(self.on_bowling_aggression_change)
        bowling_layout.addWidget(self.bowling_slider)
        
        bowling_layout.addSpacing(10)
        
        # Bowling Line
        line_label = QLabel("Bowling Line:")
        line_label.setStyleSheet("font-size: 11px;")
        bowling_layout.addWidget(line_label)
        
        self.bowling_line_combo = QComboBox()
        self.bowling_line_combo.addItems(['Short', 'Good Length', 'Full'])
        self.bowling_line_combo.setCurrentText(self.bowling_line)
        self.bowling_line_combo.currentTextChanged.connect(self.on_bowling_line_change)
        bowling_layout.addWidget(self.bowling_line_combo)
        
        bowling_layout.addSpacing(10)
        
        # Field Setting
        field_label = QLabel("Field Setting:")
        field_label.setStyleSheet("font-size: 11px;")
        bowling_layout.addWidget(field_label)
        
        self.field_setting_combo = QComboBox()
        self.field_setting_combo.addItems(['Aggressive', 'Balanced', 'Defensive'])
        self.field_setting_combo.setCurrentText(self.field_setting)
        self.field_setting_combo.currentTextChanged.connect(self.on_field_setting_change)
        bowling_layout.addWidget(self.field_setting_combo)
        
        bowling_frame.setLayout(bowling_layout)
        layout.addWidget(bowling_frame)
        
        # Score Display
        score_frame = QGroupBox("Match Status")
        score_frame.setStyleSheet("""
            QGroupBox {
                font-size: 12px;
                font-weight: bold;
                border: 2px solid #334155;
                border-radius: 4px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: #1F2937;
                border-radius: 2px;
            }
        """)
        
        score_layout = QVBoxLayout()
        
        self.score_label = QLabel("0/0 (0.0)")
        self.score_label.setStyleSheet("font-size: 16px; font-weight: bold; font-family: Arial;")
        score_layout.addWidget(self.score_label)
        
        self.target_label = QLabel("")
        self.target_label.setStyleSheet("font-size: 12px; font-family: Arial;")
        self.target_label.setWordWrap(True)
        score_layout.addWidget(self.target_label)
        
        score_frame.setLayout(score_layout)
        layout.addWidget(score_frame)
        
        # Current Batsmen
        batsmen_frame = QGroupBox("Current Batsmen")
        batsmen_frame.setStyleSheet("""
            QGroupBox {
                font-size: 12px;
                font-weight: bold;
                border: 2px solid #334155;
                border-radius: 4px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: #1F2937;
                border-radius: 2px;
            }
        """)
        
        batsmen_layout = QVBoxLayout()
        
        self.striker_label = QLabel("")
        self.striker_label.setStyleSheet("font-size: 12px; font-family: Arial;")
        batsmen_layout.addWidget(self.striker_label)
        
        self.non_striker_label = QLabel("")
        self.non_striker_label.setStyleSheet("font-size: 12px; font-family: Arial;")
        batsmen_layout.addWidget(self.non_striker_label)
        
        batsmen_frame.setLayout(batsmen_layout)
        layout.addWidget(batsmen_frame)
        
        # Current Bowler
        bowler_frame = QGroupBox("Current Bowler")
        bowler_frame.setStyleSheet("""
            QGroupBox {
                font-size: 12px;
                font-weight: bold;
                border: 2px solid #334155;
                border-radius: 4px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: #1F2937;
                border-radius: 2px;
            }
        """)
        
        bowler_layout = QVBoxLayout()
        
        self.bowler_label = QLabel("")
        self.bowler_label.setStyleSheet("font-size: 12px; font-family: Arial;")
        bowler_layout.addWidget(self.bowler_label)
        
        bowler_frame.setLayout(bowler_layout)
        layout.addWidget(bowler_frame)
        
        # Control Buttons
        control_frame = QGroupBox("Controls")
        control_frame.setStyleSheet("""
            QGroupBox {
                font-size: 12px;
                font-weight: bold;
                border: 2px solid #334155;
                border-radius: 4px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: #1F2937;
                border-radius: 2px;
            }
        """)
        
        control_layout = QVBoxLayout()
        
        # Row 1: Basic controls
        basic_controls_layout = QHBoxLayout()
        
        self.bowl_button = QPushButton("Bowl")
        self.bowl_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.bowl_button.clicked.connect(self.bowl_delivery)
        basic_controls_layout.addWidget(self.bowl_button)
        
        self.bowl_over_button = QPushButton("Bowl Over")
        self.bowl_over_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        self.bowl_over_button.clicked.connect(self.bowl_over)
        basic_controls_layout.addWidget(self.bowl_over_button)
        
        control_layout.addLayout(basic_controls_layout)
        
        # Row 2: Test match specific controls (only visible for Test matches)
        if self.match_format == 'Test':
            test_controls_layout = QHBoxLayout()
            
            self.sim_session_button = QPushButton("Simulate to Session")
            self.sim_session_button.setStyleSheet("""
                QPushButton {
                    background-color: #9C27B0;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    font-size: 12px;
                    font-weight: bold;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #7B1FA2;
                }
            """)
            self.sim_session_button.clicked.connect(self.simulate_to_session)
            test_controls_layout.addWidget(self.sim_session_button)
            
            self.sim_day_button = QPushButton("Simulate to Day")
            self.sim_day_button.setStyleSheet("""
                QPushButton {
                    background-color: #673AB7;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    font-size: 12px;
                    font-weight: bold;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #512DA8;
                }
            """)
            self.sim_day_button.clicked.connect(self.simulate_to_day)
            test_controls_layout.addWidget(self.sim_day_button)
            
            self.sim_innings_button = QPushButton("Simulate Innings")
            self.sim_innings_button.setStyleSheet("""
                QPushButton {
                    background-color: #3F51B5;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    font-size: 12px;
                    font-weight: bold;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #303F9F;
                }
            """)
            self.sim_innings_button.clicked.connect(self.simulate_innings)
            test_controls_layout.addWidget(self.sim_innings_button)
            
            control_layout.addLayout(test_controls_layout)
        
        # Row 3: Session/Day display (Test matches only)
        if self.match_format == 'Test':
            session_frame = QGroupBox("Match Progress")
            session_frame.setStyleSheet("""
                QGroupBox {
                    font-size: 12px;
                    font-weight: bold;
                    border: 2px solid #334155;
                    border-radius: 4px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    padding: 0 5px;
                    background-color: #1F2937;
                    border-radius: 2px;
                }
            """)
            
            session_layout = QHBoxLayout()
            
            self.current_session_label = QLabel("Session: 1.1")
            self.current_session_label.setStyleSheet("font-size: 11px; font-weight: bold;")
            session_layout.addWidget(self.current_session_label)
            
            self.current_day_label = QLabel("Day: 1")
            self.current_day_label.setStyleSheet("font-size: 11px; font-weight: bold;")
            session_layout.addWidget(self.current_day_label)
            
            self.current_innings_label = QLabel("Innings: 1")
            self.current_innings_label.setStyleSheet("font-size: 11px; font-weight: bold;")
            session_layout.addWidget(self.current_innings_label)
            
            session_layout.addStretch()
            
            session_frame.setLayout(session_layout)
            control_layout.addWidget(session_frame)
        
        control_frame.setLayout(control_layout)
        layout.addWidget(control_frame)
        
        left_frame.setLayout(layout)
    
    def setup_right_frame(self, right_frame):
        """Setup right frame with match display"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Commentary area
        commentary_frame = QGroupBox("Live Commentary")
        commentary_frame.setStyleSheet("""
            QGroupBox {
                font-size: 12px;
                font-weight: bold;
                border: 2px solid #334155;
                border-radius: 4px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: #1F2937;
                border-radius: 2px;
            }
        """)
        
        commentary_layout = QVBoxLayout()
        
        self.commentary_text = QTextEdit()
        self.commentary_text.setStyleSheet("""
            QTextEdit {
                background-color: #111827;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 10px;
                font-family: 'Consolas', monospace;
                font-size: 11px;
            }
        """)
        self.commentary_text.setReadOnly(True)
        self.commentary_text.setMaximumHeight(150)
        commentary_layout.addWidget(self.commentary_text)
        
        commentary_frame.setLayout(commentary_layout)
        layout.addWidget(commentary_frame)
        
        # Scorecard tabs
        self.scorecard_tabs = QTabWidget()
        self.scorecard_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #0B1220;
            }
            QTabBar::tab {
                background-color: #111827;
                color: #B8C3D9;
                padding: 8px 16px;
                margin-right: 4px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 12px;
                font-weight: 600;
            }
            QTabBar::tab:selected {
                background-color: #1976D2;
                color: white;
            }
        """)
        
        # Batting Scorecard
        self.batting_table = self.create_scorecard_table(['Player', 'R', 'B', '4s', '6s', 'SR', 'Dismissal'])
        self.scorecard_tabs.addTab(self.batting_table, "🏏 Batting Scorecard")
        
        # Bowling Scorecard
        self.bowling_table = self.create_scorecard_table(['Player', 'Overs', 'Runs', 'Wkts', 'Econ', 'Maidens'])
        self.scorecard_tabs.addTab(self.bowling_table, "⚾ Bowling Scorecard")
        
        # Fall of Wickets
        self.fow_table = self.create_fow_table()
        self.scorecard_tabs.addTab(self.fow_table, "📉 Fall of Wickets")
        
        layout.addWidget(self.scorecard_tabs, 1)
        
        right_frame.setLayout(layout)
    
    def create_scorecard_table(self, headers):
        """Create a scorecard table"""
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setStyleSheet("""
            QTableWidget {
                border: none;
                background-color: #111827;
                gridline-color: #111827;
                font-size: 11px;
            }
            QTableWidget::item {
                padding: 6px;
                border-bottom: 1px solid #111827;
            }
            QTableWidget::item:selected {
                background-color: #1E293B;
            }
            QHeaderView::section {
                background-color: #2196F3;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: 11px;
            }
        """)
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        return table
    
    def create_fow_table(self):
        """Create fall of wickets table"""
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(['Over', 'Score', 'Wicket', 'Player'])
        table.setStyleSheet("""
            QTableWidget {
                border: none;
                background-color: #111827;
                gridline-color: #111827;
                font-size: 11px;
            }
            QTableWidget::item {
                padding: 6px;
                border-bottom: 1px solid #111827;
            }
            QTableWidget::item:selected {
                background-color: #1E293B;
            }
            QHeaderView::section {
                background-color: #2196F3;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: 11px;
            }
        """)
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        return table
    
    def initialize_match(self):
        """Initialize match state"""
        if self.match_format in ['T20', 'ODI']:
            self.max_overs = 20 if self.match_format == 'T20' else 50
        else:  # Test match
            self.max_overs = None
        
        # Reset match state
        self.current_over = 0
        self.current_ball = 0
        self.total_runs = 0
        self.total_wickets = 0
        self.target = None
        
        # Set initial players
        if self.team1 and self.team2:
            self.striker = self.team1.players[0] if self.team1.players else None
            self.non_striker = self.team1.players[1] if len(self.team1.players) > 1 else self.striker
            self.current_bowler = self.team2.players[0] if self.team2.players else None
            
            # Add initial commentary
            self.add_commentary(f"Match: {self.team1.name} vs {self.team2.name}")
            self.add_commentary(f"Format: {self.match_format}")
            self.add_commentary(f"Pitch: {self.get_pitch_description()}")
    
    def on_pitch_slider_change(self, value):
        """Handle pitch slider changes"""
        self.pace_rating = self.pace_slider.value()
        self.spin_rating = self.spin_slider.value()
        self.bounce_rating = self.bounce_slider.value()
        self.pitch_description.setText(self.get_pitch_description())
    
    def get_pitch_description(self):
        """Get pitch description based on current ratings"""
        pace_desc = {
            1: "Very slow pitch - difficult for batting",
            2: "Slow pitch - helps bowlers",
            3: "Medium pace - balanced",
            4: "Fast pitch - helps batters",
            5: "Very fast pitch - batting paradise",
            6: "Extremely fast - batting paradise",
            7: "Extremely fast - batting paradise",
            8: "Extremely fast - batting paradise",
            9: "Extremely fast - batting paradise",
            10: "Extremely fast - batting paradise"
        }
        
        spin_desc = {
            1: "Very helpful for spinners",
            2: "Helpful for spinners",
            3: "Balanced for spin and pace",
            4: "Slightly favors batters",
            5: "Slightly favors batters",
            6: "Favors batters",
            7: "Strongly favors batters",
            8: "Strongly favors batters",
            9: "Extremely favors batters",
            10: "Extremely favors batters"
        }
        
        bounce_desc = {
            1: "Low bounce - difficult timing",
            2: "Low bounce - difficult timing",
            3: "Normal bounce",
            4: "Good bounce",
            5: "Good bounce",
            6: "High bounce",
            7: "Very high bounce",
            8: "Very high bounce",
            9: "Extremely high bounce",
            10: "Extremely high bounce"
        }
        
        pace_desc_text = pace_desc.get(self.pace_rating, "Unknown")
        spin_desc_text = spin_desc.get(self.spin_rating, "Unknown")
        bounce_desc_text = bounce_desc.get(self.bounce_rating, "Unknown")
        
        return f"Pace: {pace_desc_text}, Spin: {spin_desc_text}, Bounce: {bounce_desc_text}"
    
    def on_batting_aggression_change(self, value):
        """Handle batting aggression slider change"""
        self.batting_aggression = value
    
    def on_bowling_aggression_change(self, value):
        """Handle bowling aggression slider change"""
        self.bowling_aggression = value
    
    def on_bowling_line_change(self, value):
        """Handle bowling line change"""
        self.bowling_line = value
    
    def on_field_setting_change(self, value):
        """Handle field setting change"""
        self.field_setting = value
    
    def update_display(self):
        """Update score display"""
        if self.match_format in ['T20', 'ODI']:
            score_text = f"{self.total_runs}/{self.total_wickets} ({self.get_run_rate():.2f})"
            target_text = f"Target: {self.target}" if self.target else ""
        else:  # Test match
            score_text = f"{self.total_runs}/{self.total_wickets} ({self.get_run_rate():.2f})"
            target_text = f"Lead: {self.get_lead()}" if hasattr(self, 'get_lead') else ""
        
        self.score_label.setText(score_text)
        self.target_label.setText(target_text)
        
        # Update batsmen display
        if self.striker:
            striker_text = f"* {self.striker.name}* ({self.striker.batting} runs)"
        else:
            striker_text = "No striker"
        self.striker_label.setText(striker_text)
        
        if self.non_striker:
            non_striker_text = f"* {self.non_striker.name}* ({self.non_striker.batting} runs)"
        else:
            non_striker_text = "No non-striker"
        self.non_striker_label.setText(non_striker_text)
        
        # Update bowler display
        if self.current_bowler:
            bowler_text = f"* {self.current_bowler.name}* ({self.current_bowler.bowling})"
        else:
            bowler_text = "No bowler"
        self.bowler_label.setText(bowler_text)
        
        # Update commentary
        self.add_commentary(f"Overs {self.current_over}.{self.current_ball} - {score_text}")
        
        # Update scorecards
        self.update_scorecards()
    
    def update_scorecards(self):
        """Update all scorecard tables"""
        self.update_batting_scorecard()
        self.update_bowling_scorecard()
        self.update_fall_of_wickets()
    
    def update_batting_scorecard(self):
        """Update batting scorecard table"""
        if not self.team1:
            return
        
        # Clear existing data
        self.batting_table.setRowCount(0)
        
        # Get batting players
        batting_players = []
        if self.team1.players:
            batting_players = self.team1.players[:11]  # First 11 players
        
        row = 0
        for player in batting_players:
            # Get or initialize stats
            if player.name not in self.batting_stats:
                self.batting_stats[player.name] = {
                    'runs': 0,
                    'balls': 0,
                    'fours': 0,
                    'sixes': 0,
                    'dismissal': 'Not out'
                }
            
            stats = self.batting_stats[player.name]
            
            # Add row
            self.batting_table.insertRow(row)
            
            # Calculate strike rate
            sr = (stats['runs'] / stats['balls'] * 100) if stats['balls'] > 0 else 0
            
            self.batting_table.setItem(row, 0, QTableWidgetItem(player.name))
            self.batting_table.setItem(row, 1, QTableWidgetItem(str(stats['runs'])))
            self.batting_table.setItem(row, 2, QTableWidgetItem(str(stats['balls'])))
            self.batting_table.setItem(row, 3, QTableWidgetItem(str(stats['fours'])))
            self.batting_table.setItem(row, 4, QTableWidgetItem(str(stats['sixes'])))
            self.batting_table.setItem(row, 5, QTableWidgetItem(f"{sr:.1f}"))
            self.batting_table.setItem(row, 6, QTableWidgetItem(stats['dismissal']))
            
            row += 1
    
    def update_bowling_scorecard(self):
        """Update bowling scorecard table"""
        if not self.team2:
            return
        
        # Clear existing data
        self.bowling_table.setRowCount(0)
        
        # Get bowling players
        bowling_players = []
        if self.team2.players:
            bowling_players = [p for p in self.team2.players if 'Bowler' in p.role or 'Spinner' in p.role or 'Pacer' in p.role]
        
        row = 0
        for player in bowling_players:
            # Get or initialize stats
            if player.name not in self.bowling_stats:
                self.bowling_stats[player.name] = {
                    'balls': 0,
                    'runs': 0,
                    'wickets': 0,
                    'maidens': 0
                }
            
            stats = self.bowling_stats[player.name]
            
            # Add row
            self.bowling_table.insertRow(row)
            
            # Calculate overs and economy
            overs = stats['balls'] // 6
            balls = stats['balls'] % 6
            econ = (stats['runs'] / (stats['balls'] / 6)) if stats['balls'] > 0 else 0
            
            self.bowling_table.setItem(row, 0, QTableWidgetItem(player.name))
            self.bowling_table.setItem(row, 1, QTableWidgetItem(f"{overs}.{balls}"))
            self.bowling_table.setItem(row, 2, QTableWidgetItem(str(stats['runs'])))
            self.bowling_table.setItem(row, 3, QTableWidgetItem(str(stats['wickets'])))
            self.bowling_table.setItem(row, 4, QTableWidgetItem(f"{econ:.2f}"))
            self.bowling_table.setItem(row, 5, QTableWidgetItem(str(stats['maidens'])))
            
            row += 1
    
    def update_fall_of_wickets(self):
        """Update fall of wickets table"""
        # Clear existing data
        self.fow_table.setRowCount(0)
        
        row = 0
        for fow in self.fall_of_wickets:
            self.fow_table.insertRow(row)
            self.fow_table.setItem(row, 0, QTableWidgetItem(str(fow['over'])))
            self.fow_table.setItem(row, 1, QTableWidgetItem(str(fow['score'])))
            self.fow_table.setItem(row, 2, QTableWidgetItem(str(fow['wicket'])))
            self.fow_table.setItem(row, 3, QTableWidgetItem(fow['player']))
            row += 1
    
    def get_run_rate(self):
        """Calculate current run rate"""
        total_balls = self.current_over * 6 + self.current_ball
        if total_balls > 0:
            return (self.total_runs / total_balls) * 100
        return 0.0
    
    def get_lead(self):
        """Calculate lead (for Test matches)"""
        return self.total_runs
    
    def bowl_delivery(self):
        """Bowl one delivery - now works with thread simulation"""
        if not self.is_playing:
            self.add_commentary("Match not started yet!")
            return
        
        if self.match_thread and self.match_thread.isRunning():
            self.add_commentary("Simulation running in background...")
            return
        
        # If thread is not running, use local simulation (fallback)
        self.current_ball += 1
        
        # Simple simulation
        import random
        runs = random.randint(0, 6)
        self.total_runs += runs
        
        # Update striker stats
        if self.striker and self.striker.name not in self.batting_stats:
            self.batting_stats[self.striker.name] = {
                'runs': 0,
                'balls': 0,
                'fours': 0,
                'sixes': 0,
                'dismissal': 'Not out'
            }
        
        striker_stats = self.batting_stats[self.striker.name]
        striker_stats['runs'] += runs
        striker_stats['balls'] += 1
        
        if runs == 4:
            striker_stats['fours'] += 1
            self.add_commentary(f"FOUR! Excellent shot")
        elif runs == 6:
            striker_stats['sixes'] += 1
            self.add_commentary(f"SIX! Maximum!")
        elif runs == 0:
            self.add_commentary(f"Dot ball")
        else:
            self.add_commentary(f"{runs} runs")
        
        # Update bowler stats
        if self.current_bowler and self.current_bowler.name not in self.bowling_stats:
            self.bowling_stats[self.current_bowler.name] = {
                'balls': 0,
                'runs': 0,
                'wickets': 0,
                'maidens': 0
            }
        
        bowler_stats = self.bowling_stats[self.current_bowler.name]
        bowler_stats['balls'] += 1
        bowler_stats['runs'] += runs
        
        # Check for over
        if self.current_ball >= 6:
            self.current_over += 1
            self.current_ball = 0
            
            # Check for maiden
            if bowler_stats['runs'] == 0:
                bowler_stats['maidens'] += 1
            
            self.add_commentary(f"Over {self.current_over} completed")
            self.change_bowler()
        
        # Check for innings end
        if self.total_wickets >= 10 or (self.max_overs and self.current_over >= self.max_overs):
            self.end_innings()
        
        self.update_display()
    
    def bowl_over(self):
        """Bowl an over - now works with thread simulation"""
        if not self.is_playing:
            self.add_commentary("Match not started yet!")
            return
        
        self.current_over += 1
        self.current_ball = 0
        
        # Simulate over
        import random
        over_runs = random.randint(0, 20)
        self.total_runs += over_runs
        wickets = random.randint(0, 2)
        self.total_wickets += wickets
        
        self.add_commentary(f"Over {self.current_over}: {over_runs} runs, {wickets} wickets")
        
        # Check for innings end
        if self.total_wickets >= 10 or (self.max_overs and self.current_over >= self.max_overs):
            self.end_innings()
        
        self.update_display()
    
    def end_innings(self):
        """End current innings"""
        self.add_commentary("Innings completed!")
        self.is_playing = False
        
        # Show result
        QMessageBox.information(self, "Innings Complete", 
                               f"Final Score: {self.total_runs}/{self.total_wickets}")
    
    def add_commentary(self, text):
        """Add commentary text"""
        self.commentary_text.append(text)
        # Auto-scroll to bottom
        scrollbar = self.commentary_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def start_match(self):
        """Start the match simulation using original backends"""
        if not self.team1 or not self.team2:
            QMessageBox.warning(self, "Error", "Teams not properly set")
            return
        
        if self.is_playing:
            QMessageBox.information(self, "Match Already Started", "Match is already in progress")
            return
        
        self.is_playing = True
        self.pitch_controls_enabled = True
        
        # Disable pitch controls after first over (like original)
        self.pace_slider.setEnabled(False)
        self.spin_slider.setEnabled(False)
        self.bounce_slider.setEnabled(False)
        
        self.add_commentary("Launching original match simulator...")
        self.add_commentary(f"Format: {self.match_format}")
        self.add_commentary(f"{self.team1.name} vs {self.team2.name}")
        
        try:
            if self.match_format in ['T20', 'ODI']:
                # Launch T20/ODI match
                from .match_launcher import launch_t20_match
                
                success = launch_t20_match(self.team1, self.team2, self.match_format)
                if success:
                    self.add_commentary("T20/ODI match simulator launched successfully!")
                    self.add_commentary("Use the original match window for over-by-over simulation")
                else:
                    self.add_commentary("Failed to launch T20/ODI match simulator")
                    QMessageBox.critical(self, "Error", "Failed to launch T20/ODI match simulator")
                
            else:  # Test match
                # Launch Test match
                from .match_launcher import launch_test_match
                
                success = launch_test_match(self.team1, self.team2)
                if success:
                    self.add_commentary("Test match simulator launched successfully!")
                    self.add_commentary("Use the original match window for session-by-session simulation")
                else:
                    self.add_commentary("Failed to launch Test match simulator")
                    QMessageBox.critical(self, "Error", "Failed to launch Test match simulator")
                
        except Exception as e:
            self.add_commentary(f"Error launching simulator: {e}")
            QMessageBox.critical(self, "Error", f"Failed to launch match simulator: {e}")
        
        # Update display
        self.update_display()
        
        # Close this dialog after launching original simulator
        self.accept()
    
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
    
    def on_match_update(self, data):
        """Handle match update from simulation thread"""
        if data.get('status') == 'creating_match':
            # Create the match in the main thread
            try:
                from t20oversimulation import T20Match
                
                # IMPORTANT:
                # Pass self as master so that T20Match can:
                # - Access self.game_engine for StatisticsManager updates
                # - Access self.screen_manager for refreshing Qt UI screens
                #   (Statistics screen, Players screen, etc.) via its
                #   _complete_ui_updates() callback.
                self.match_instance = T20Match(
                    self,
                    data['team1_data'],
                    data['team2_data'],
                    data['match_format'],
                    headless=False
                )
                
                # Set all the parameters
                self.match_instance.batting_slider.set(data['batting_aggression'])
                self.match_instance.bowling_slider.set(data['bowling_aggression'])
                self.match_instance.pace_pitch_slider.set(data['pace_rating'])
                self.match_instance.spin_pitch_slider.set(data['spin_rating'])
                self.match_instance.bounce_pitch_slider.set(data['bounce_rating'])
                self.match_instance.bowling_line_var.set(data['bowling_line'])
                self.match_instance.field_setting_var.set(data['field_setting'])
                
                # Start the match
                self.match_instance.setup_match()
                
                self.add_commentary("Match created successfully!")
                self.add_commentary("Use the original match window for over-by-over simulation")
                
                # Show the original match window
                if hasattr(self.match_instance, 'match_window'):
                    self.match_instance.match_window.lift()
                    self.match_instance.match_window.focus_force()
                
            except Exception as e:
                self.add_commentary(f"Error creating match: {e}")
                print(f"Match creation error: {e}")
                
        elif 'total_runs' in data:
            self.total_runs = data['total_runs']
            self.total_wickets = data.get('total_wickets', self.total_wickets)
            self.current_over = data.get('current_over', self.current_over)
            self.current_ball = data.get('current_ball', self.current_ball)
            
            # Update striker and non-striker if provided
            if 'striker' in data:
                self.striker = data['striker']
            if 'non_striker' in data:
                self.non_striker = data['non_striker']
            if 'current_bowler' in data:
                self.current_bowler = data['current_bowler']
            
            # Update commentary if provided
            if 'commentary' in data:
                self.add_commentary(data['commentary'])
            
            # Update scorecards
            self.update_scorecards()
            
            # Update display
            self.update_display()
    
    def on_match_finished(self, result):
        """Handle match completion from simulation thread"""
        self.is_playing = False
        
        if 'error' in result:
            self.add_commentary(f"❌ Error: {result['error']}")
            QMessageBox.critical(self, "Simulation Error", f"Match simulation failed: {result['error']}")
            return
        
        # Store result for parent
        self.match_result = result
        
        # Display final result
        self.add_commentary("🏁 MATCH COMPLETE!")
        
        if 'winner' in result:
            winner = result['winner']
            if winner and winner != 'Unknown':
                self.add_commentary(f"🏆 Winner: {winner}")
            else:
                self.add_commentary("🤝 Match ended in a draw")
        
        if 'team1_score' in result:
            self.add_commentary(f"{self.team1.name}: {result['team1_score']}")
        if 'team2_score' in result:
            self.add_commentary(f"{self.team2.name}: {result['team2_score']}")
        
        # Update final scorecards if available
        if 'final_scorecard' in result and result['final_scorecard']:
            self.add_commentary("Final scorecard available")
        
        # Show result dialog
        result_text = "Match Complete!\n\n"
        if 'winner' in result:
            result_text += f"🏆 Winner: {result['winner']}\n"
        if 'team1_score' in result:
            result_text += f"{self.team1.name}: {result['team1_score']}\n"
        if 'team2_score' in result:
            result_text += f"{self.team2.name}: {result['team2_score']}\n"
        if 'margin' in result:
            result_text += f"Margin: {result['margin']}"
        
        QMessageBox.information(self, "Match Complete", result_text)
        
        # Accept dialog to indicate match was played
        self.accept()
    
    def simulate_to_session(self):
        """Simulate to next session (Test match specific)"""
        if self.match_format != 'Test':
            self.add_commentary("This feature is only available for Test matches")
            return
        
        if not self.is_playing:
            self.add_commentary("Match not started yet!")
            return
        
        self.add_commentary(f"Simulating to end of Session {self.current_session}.{self.current_day}")
        
        # Simulate remaining balls in current session (30 overs per session)
        overs_in_session = 30
        balls_remaining = (overs_in_session * 6) - (self.current_over * 6 + self.current_ball)
        
        import random
        for _ in range(balls_remaining):
            runs = random.randint(0, 6)
            self.total_runs += runs
            
            # Random wicket chance
            if random.random() < 0.03:  # 3% chance per ball
                self.total_wickets += 1
                self.add_commentary(f"Wicket falls! Total: {self.total_wickets}")
            
            self.current_ball += 1
            if self.current_ball >= 6:
                self.current_over += 1
                self.current_ball = 0
        
        # Move to next session
        self.current_session += 1
        if self.current_session > self.sessions_per_day:
            self.current_session = 1
            self.current_day += 1
        
        self.update_test_match_display()
        self.add_commentary(f"Session complete. Now: Day {self.current_day}, Session {self.current_session}")
        
        # Check for match end
        if self.total_wickets >= 10 or self.current_day > 5:
            self.end_innings()
        
        self.update_display()
    
    def simulate_to_day(self):
        """Simulate to end of current day (Test match specific)"""
        if self.match_format != 'Test':
            self.add_commentary("This feature is only available for Test matches")
            return
        
        if not self.is_playing:
            self.add_commentary("Match not started yet!")
            return
        
        self.add_commentary(f"Simulating to end of Day {self.current_day}")
        
        # Simulate remaining sessions in current day
        sessions_remaining = self.sessions_per_day - self.current_session + 1
        
        for _ in range(sessions_remaining):
            self.simulate_to_session()
        
        self.add_commentary(f"Day {self.current_day-1} complete!")
        self.update_display()
    
    def simulate_innings(self):
        """Simulate entire innings (Test match specific)"""
        if self.match_format != 'Test':
            self.add_commentary("This feature is only available for Test matches")
            return
        
        if not self.is_playing:
            self.add_commentary("Match not started yet!")
            return
        
        self.add_commentary("Simulating entire innings...")
        
        # Simulate until 10 wickets or reasonable overs (90 overs max)
        max_overs = 90
        while self.total_wickets < 10 and self.current_over < max_overs:
            import random
            runs = random.randint(0, 6)
            self.total_runs += runs
            
            # Higher wicket chance in Test matches
            if random.random() < 0.04:  # 4% chance per ball
                self.total_wickets += 1
                self.add_commentary(f"Wicket falls! Total: {self.total_wickets}")
            
            self.current_ball += 1
            if self.current_ball >= 6:
                self.current_over += 1
                self.current_ball = 0
                
                # Update session progress
                if self.current_over % 30 == 0:
                    self.current_session += 1
                    if self.current_session > self.sessions_per_day:
                        self.current_session = 1
                        self.current_day += 1
        
        self.add_commentary(f"Innings complete! {self.total_runs}/{self.total_wickets}")
        self.end_innings()
        self.update_display()
    
    def update_test_match_display(self):
        """Update Test match specific display elements"""
        if self.match_format == 'Test':
            self.current_session_label.setText(f"Session: {self.current_session}.{self.current_day}")
            self.current_day_label.setText(f"Day: {self.current_day}")
            self.current_innings_label.setText(f"Innings: {self.current_innings}")
    
    def update_display(self):
        """Update score display with Test match support"""
        if self.match_format in ['T20', 'ODI']:
            score_text = f"{self.total_runs}/{self.total_wickets} ({self.get_run_rate():.2f})"
            target_text = f"Target: {self.target}" if self.target else ""
        else:  # Test match
            score_text = f"{self.total_runs}/{self.total_wickets} ({self.get_run_rate():.2f})"
            target_text = f"Lead: {self.get_lead()}" if hasattr(self, 'get_lead') else ""
        
        self.score_label.setText(score_text)
        self.target_label.setText(target_text)
        
        # Update batsmen display
        if self.striker:
            striker_text = f"* {self.striker.name}* ({self.striker.batting} runs)"
        else:
            striker_text = "No striker"
        self.striker_label.setText(striker_text)
        
        if self.non_striker:
            non_striker_text = f"* {self.non_striker.name}* ({self.non_striker.batting} runs)"
        else:
            non_striker_text = "No non-striker"
        self.non_striker_label.setText(non_striker_text)
        
        # Update bowler display
        if self.current_bowler:
            bowler_text = f"* {self.current_bowler.name}* ({self.current_bowler.bowling})"
        else:
            bowler_text = "No bowler"
        self.bowler_label.setText(bowler_text)
        
        # Update Test match specific display
        self.update_test_match_display()
        
        # Update commentary
        self.add_commentary(f"Overs {self.current_over}.{self.current_ball} - {score_text}")
        
        # Update scorecards
        self.update_scorecards()
