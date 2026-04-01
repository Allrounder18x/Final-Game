"""
Interactive Match Player - Complete Implementation
Based on t20oversimulation.py and test_match_enhanced.py
Features: Pitch conditions, aggression, bowling controls, speeds, proper innings handling
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QFrame, QTextEdit, QGroupBox, QGridLayout, QProgressBar,
    QComboBox, QButtonGroup, QRadioButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QTabWidget, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor
import random

from cricket_manager.ui.styles import COLORS, MAIN_STYLESHEET
from cricket_manager.core.match_simulator import MatchSimulator


class InteractiveMatchPlayerNew(QDialog):
    """
    Interactive match player with complete controls
    """
    
    match_completed = pyqtSignal(dict)
    
    def __init__(self, parent, fixture, game_engine):
        super().__init__(parent)
        self.setStyleSheet(MAIN_STYLESHEET)
        self.fixture = fixture
        self.game_engine = game_engine
        
        # Extract from fixture
        self.team1 = fixture['team1']
        self.team2 = fixture['team2']
        self.match_format = fixture['format']
        
        # Match state
        self.simulator = MatchSimulator(self.team1, self.team2, self.match_format, parent_app=game_engine)
        self.current_innings = 1
        self.current_over = 0
        self.current_ball = 0
        self.aggression = 50  # 0-100
        self.auto_play = False
        self.auto_timer = None
        self.match_started = False  # Track if match has started (to disable pitch sliders)
        
        # Pitch conditions (randomized)
        self.pitch_pace = random.randint(3, 9)
        self.pitch_spin = random.randint(3, 9)
        self.pitch_bounce = random.randint(3, 9)
        
        # Setup UI
        self.setWindowTitle(f"{self.team1.name} vs {self.team2.name} - {self.match_format}")
        self.setMinimumSize(1200, 800)
        self.init_ui()
        
        # Start match
        self.start_match()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Top: Match header
        header = self.create_header()
        layout.addWidget(header)
        
        # Middle: Main content (2 columns - Scorecard and Controls)
        content_layout = QHBoxLayout()
        
        # Left: Scorecard (larger, takes more space)
        scorecard = self.create_scorecard_panel()
        content_layout.addWidget(scorecard, 3)
        
        # Right: Controls
        controls = self.create_controls_panel()
        content_layout.addWidget(controls, 1)
        
        layout.addLayout(content_layout, 3)
        
        # Bottom: Commentary (with scrollbar)
        commentary = self.create_commentary_panel()
        layout.addWidget(commentary, 1)
        
        # Bottom: Action buttons
        actions = self.create_action_buttons()
        layout.addWidget(actions)
        
        self.setLayout(layout)
    
    def create_header(self):
        """Create match header"""
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['primary']};
                padding: 15px;
                border-radius: 8px;
            }}
        """)
        
        layout = QHBoxLayout()
        
        # Team 1
        team1_label = QLabel(self.team1.name)
        team1_label.setStyleSheet("font-size: 18px; font-weight: 700; color: white;")
        layout.addWidget(team1_label)
        
        self.team1_score = QLabel("0/0 (0.0)")
        self.team1_score.setStyleSheet("font-size: 16px; color: white;")
        layout.addWidget(self.team1_score)
        
        layout.addStretch()
        
        # Match info
        match_info = QLabel(f"{self.match_format} Match")
        match_info.setStyleSheet("font-size: 14px; color: white; font-weight: 600;")
        layout.addWidget(match_info)
        
        layout.addStretch()
        
        # Team 2
        self.team2_score = QLabel("0/0 (0.0)")
        self.team2_score.setStyleSheet("font-size: 16px; color: white;")
        layout.addWidget(self.team2_score)
        
        team2_label = QLabel(self.team2.name)
        team2_label.setStyleSheet("font-size: 18px; font-weight: 700; color: white;")
        layout.addWidget(team2_label)
        
        header.setLayout(layout)
        return header
    
    def create_scorecard_panel(self):
        """Create scorecard panel with TreeView tables like t20oversimulation.py"""
        panel = QFrame()
        layout = QVBoxLayout()
        
        # Batting scorecard
        batting_frame = QGroupBox(f"{self.team1.name} Batting Scorecard")
        batting_frame.setStyleSheet(f"""
            QGroupBox {{
                font-size: 14px;
                font-weight: 700;
                color: #EAF1FF;
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px;
                margin-top: 10px;
            }}
        """)
        batting_layout = QVBoxLayout()
        
        self.batting_tree = QTableWidget()
        self.batting_tree.setColumnCount(7)
        self.batting_tree.setHorizontalHeaderLabels(['Batsman', 'R', 'B', '4s', '6s', 'SR', 'Status'])
        
        # Set column widths
        header = self.batting_tree.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, 7):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        self.batting_tree.setStyleSheet("""
            QTableWidget {
                background-color: #111827;
                border: 1px solid #334155;
                gridline-color: #e0e0e0;
                font-size: 13px;
                color: #EAF1FF;
            }
            QTableWidget::item {
                padding: 8px;
                color: #EAF1FF;
            }
            QHeaderView::section {
                background-color: #0B1220;
                padding: 8px;
                border: none;
                font-weight: 700;
                font-size: 13px;
                color: #EAF1FF;
            }
        """)
        self.batting_tree.setMinimumHeight(350)
        batting_layout.addWidget(self.batting_tree)
        batting_frame.setLayout(batting_layout)
        layout.addWidget(batting_frame)
        
        # Bowling scorecard
        bowling_frame = QGroupBox(f"{self.team2.name} Bowling Scorecard")
        bowling_frame.setStyleSheet(f"""
            QGroupBox {{
                font-size: 14px;
                font-weight: 700;
                color: #EAF1FF;
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px;
                margin-top: 10px;
            }}
        """)
        bowling_layout = QVBoxLayout()
        
        self.bowling_tree = QTableWidget()
        self.bowling_tree.setColumnCount(8)
        self.bowling_tree.setHorizontalHeaderLabels(['Bowler', 'O', 'M', 'R', 'W', 'Econ', 'Avg Speed', 'Top Speed'])
        
        # Set column widths
        header = self.bowling_tree.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, 8):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        self.bowling_tree.setStyleSheet("""
            QTableWidget {
                background-color: #111827;
                border: 1px solid #334155;
                gridline-color: #e0e0e0;
                font-size: 13px;
                color: #EAF1FF;
            }
            QTableWidget::item {
                padding: 8px;
                color: #EAF1FF;
            }
            QHeaderView::section {
                background-color: #0B1220;
                padding: 8px;
                border: none;
                font-weight: 700;
                font-size: 13px;
                color: #EAF1FF;
            }
        """)
        self.bowling_tree.setMinimumHeight(300)
        bowling_layout.addWidget(self.bowling_tree)
        bowling_frame.setLayout(bowling_layout)
        layout.addWidget(bowling_frame)
        
        panel.setLayout(layout)
        return panel
    
    def create_commentary_panel(self):
        """Create commentary panel at bottom with scrollbar"""
        panel = QGroupBox("Live Commentary")
        panel.setStyleSheet(f"""
            QGroupBox {{
                font-size: 14px;
                font-weight: 700;
                color: #EAF1FF;
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px;
                margin-top: 10px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        self.commentary_text = QTextEdit()
        self.commentary_text.setReadOnly(True)
        self.commentary_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New', monospace;
                font-size: 12px;
                color: #EAF1FF;
                background-color: #0B1220;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        self.commentary_text.setMinimumHeight(150)
        self.commentary_text.setMaximumHeight(200)
        layout.addWidget(self.commentary_text)
        
        panel.setLayout(layout)
        return panel
    
    def create_controls_panel(self):
        """Create controls panel"""
        panel = QGroupBox("Match Controls")
        panel.setStyleSheet(f"""
            QGroupBox {{
                font-size: 14px;
                font-weight: 700;
                color: #EAF1FF;
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                padding: 15px;
                margin-top: 10px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Pitch conditions
        pitch_label = QLabel("Pitch Conditions")
        pitch_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #EAF1FF;")
        layout.addWidget(pitch_label)
        
        # Pace slider
        pace_lbl = QLabel(f"Pace: {self.pitch_pace}/10")
        pace_lbl.setStyleSheet("font-size: 11px; color: #EAF1FF;")
        layout.addWidget(pace_lbl)
        
        self.pace_slider = QSlider(Qt.Orientation.Horizontal)
        self.pace_slider.setMinimum(1)
        self.pace_slider.setMaximum(10)
        self.pace_slider.setValue(self.pitch_pace)
        self.pace_slider.valueChanged.connect(lambda v: self.on_pitch_changed('pace', v, pace_lbl))
        layout.addWidget(self.pace_slider)
        
        # Spin slider
        spin_lbl = QLabel(f"Spin: {self.pitch_spin}/10")
        spin_lbl.setStyleSheet("font-size: 11px; color: #EAF1FF;")
        layout.addWidget(spin_lbl)
        
        self.spin_slider = QSlider(Qt.Orientation.Horizontal)
        self.spin_slider.setMinimum(1)
        self.spin_slider.setMaximum(10)
        self.spin_slider.setValue(self.pitch_spin)
        self.spin_slider.valueChanged.connect(lambda v: self.on_pitch_changed('spin', v, spin_lbl))
        layout.addWidget(self.spin_slider)
        
        # Bounce slider
        bounce_lbl = QLabel(f"Bounce: {self.pitch_bounce}/10")
        bounce_lbl.setStyleSheet("font-size: 11px; color: #EAF1FF;")
        layout.addWidget(bounce_lbl)
        
        self.bounce_slider = QSlider(Qt.Orientation.Horizontal)
        self.bounce_slider.setMinimum(1)
        self.bounce_slider.setMaximum(10)
        self.bounce_slider.setValue(self.pitch_bounce)
        self.bounce_slider.valueChanged.connect(lambda v: self.on_pitch_changed('bounce', v, bounce_lbl))
        layout.addWidget(self.bounce_slider)
        
        # Aggression slider
        aggr_label = QLabel("Batting Aggression")
        aggr_label.setStyleSheet("font-size: 13px; font-weight: 600; margin-top: 10px; color: #EAF1FF;")
        layout.addWidget(aggr_label)
        
        self.aggression_slider = QSlider(Qt.Orientation.Horizontal)
        self.aggression_slider.setMinimum(0)
        self.aggression_slider.setMaximum(100)
        self.aggression_slider.setValue(50)
        self.aggression_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.aggression_slider.setTickInterval(25)
        self.aggression_slider.valueChanged.connect(self.on_aggression_changed)
        self.aggression_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                height: 8px;
                background: {COLORS['bg_tertiary']};
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {COLORS['primary']};
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }}
        """)
        layout.addWidget(self.aggression_slider)
        
        self.aggression_value = QLabel("Aggression: 50% (Balanced)")
        self.aggression_value.setStyleSheet("font-size: 11px; color: #EAF1FF;")
        layout.addWidget(self.aggression_value)
        
        # Bowling controls
        bowl_label = QLabel("Bowling Controls")
        bowl_label.setStyleSheet("font-size: 13px; font-weight: 600; margin-top: 10px; color: #EAF1FF;")
        layout.addWidget(bowl_label)
        
        self.bowling_combo = QComboBox()
        self.bowling_combo.addItems(["Auto Select", "Change Bowler"])
        self.bowling_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 8px;
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
                font-size: 12px;
                color: #EAF1FF;
                background-color: #111827;
            }}
        """)
        layout.addWidget(self.bowling_combo)
        
        layout.addStretch()
        panel.setLayout(layout)
        return panel
    
    def create_action_buttons(self):
        """Create action buttons"""
        frame = QFrame()
        layout = QHBoxLayout()
        
        # Play ball button
        self.play_btn = QPushButton("▶️ Play Ball")
        self.play_btn.setMinimumHeight(45)
        self.play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.play_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: white;
                font-size: 14px;
                font-weight: 700;
                border-radius: 6px;
                padding: 10px 30px;
            }}
            QPushButton:hover {{
                background-color: #45a049;
            }}
        """)
        self.play_btn.clicked.connect(lambda: self.play_ball())
        layout.addWidget(self.play_btn)
        
        # Bowl over button
        self.bowl_over_btn = QPushButton("🎯 Bowl Over")
        self.bowl_over_btn.setMinimumHeight(45)
        self.bowl_over_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.bowl_over_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                font-size: 14px;
                font-weight: 700;
                border-radius: 6px;
                padding: 10px 30px;
            }}
            QPushButton:hover {{
                background-color: #E91E63;
            }}
        """)
        self.bowl_over_btn.clicked.connect(self.bowl_over)
        layout.addWidget(self.bowl_over_btn)
        
        # Auto play toggle
        self.auto_btn = QPushButton("⚡ Auto Play")
        self.auto_btn.setCheckable(True)
        self.auto_btn.setMinimumHeight(45)
        self.auto_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.auto_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['info']};
                color: white;
                font-size: 14px;
                font-weight: 700;
                border-radius: 6px;
                padding: 10px 30px;
            }}
            QPushButton:checked {{
                background-color: {COLORS['warning']};
            }}
            QPushButton:hover {{
                background-color: #2196F3;
            }}
        """)
        self.auto_btn.clicked.connect(self.toggle_auto_play)
        layout.addWidget(self.auto_btn)
        
        # Close button
        close_btn = QPushButton("❌ Close")
        close_btn.setMinimumHeight(45)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['text_secondary']};
                color: white;
                font-size: 14px;
                font-weight: 700;
                border-radius: 6px;
                padding: 10px 30px;
            }}
            QPushButton:hover {{
                background-color: #757575;
            }}
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        frame.setLayout(layout)
        return frame
    
    def start_match(self):
        """Start the match"""
        self.add_commentary(f"🏏 {self.match_format} Match")
        self.add_commentary(f"{self.team1.name} vs {self.team2.name}")
        self.add_commentary(f"")
        self.add_commentary(f"Toss: {self.team1.name} won and elected to bat first")
        self.add_commentary(f"")
        
        # Initialize match state
        self.simulator.start_match()
        self.update_display()
    
    def play_ball(self, shot_type=None):
        """Play one ball"""
        if self.simulator.match_complete:
            return
        
        # Disable pitch sliders after first ball
        if not self.match_started:
            self.match_started = True
            self.pace_slider.setEnabled(False)
            self.spin_slider.setEnabled(False)
            self.bounce_slider.setEnabled(False)
        
        # Check if innings just completed
        was_innings_complete = self.simulator.innings_complete
        
        # Simulate ball with aggression and shot type
        result = self.simulator.simulate_ball_interactive(
            aggression=self.aggression / 100.0,
            shot_type=shot_type
        )
        
        # Update display
        self.update_display()
        
        # Add commentary
        self.add_ball_commentary(result)
        
        # Check if innings completed (transition from 1st to 2nd)
        if not was_innings_complete and self.simulator.innings_complete and self.simulator.current_innings == 1:
            self.handle_innings_complete()
        
        # Check if match complete
        if self.simulator.match_complete:
            self.handle_match_complete()
    
    def bowl_over(self):
        """Bowl complete over (6 balls)"""
        if self.simulator.match_complete:
            return
        
        # Calculate how many balls left in current over
        balls_in_over = self.simulator.current_ball
        balls_to_bowl = 6 - balls_in_over
        
        # If we're at the start of an over, bowl 6 balls
        if balls_in_over == 0:
            balls_to_bowl = 6
        
        # Bowl the balls
        for i in range(balls_to_bowl):
            if self.simulator.match_complete or self.simulator.innings_complete:
                break
            
            self.play_ball()
        
        # Add over summary commentary
        if not self.simulator.match_complete:
            self.add_commentary(f"--- End of over {int(self.simulator.current_innings_data['overs'])} ---")
            self.add_commentary("")
    
    def toggle_auto_play(self):
        """Toggle auto play mode"""
        self.auto_play = self.auto_btn.isChecked()
        
        if self.auto_play:
            # Start auto play timer
            self.auto_timer = QTimer()
            self.auto_timer.timeout.connect(self.auto_play_ball)
            self.auto_timer.start(500)  # Play ball every 0.5 seconds
            self.play_btn.setEnabled(False)
            self.bowl_over_btn.setEnabled(False)
            for btn in self.shot_buttons.values():
                btn.setEnabled(False)
        else:
            # Stop auto play
            if self.auto_timer:
                self.auto_timer.stop()
            self.play_btn.setEnabled(True)
            self.bowl_over_btn.setEnabled(True)
            for btn in self.shot_buttons.values():
                btn.setEnabled(True)
    
    def auto_play_ball(self):
        """Auto play one ball"""
        if not self.simulator.match_complete:
            self.play_ball()
        else:
            self.auto_btn.setChecked(False)
            self.toggle_auto_play()
    
    def on_pitch_changed(self, pitch_type, value, label):
        """Handle pitch condition change"""
        if pitch_type == 'pace':
            self.pitch_pace = value
            label.setText(f"Pace: {value}/10")
        elif pitch_type == 'spin':
            self.pitch_spin = value
            label.setText(f"Spin: {value}/10")
        elif pitch_type == 'bounce':
            self.pitch_bounce = value
            label.setText(f"Bounce: {value}/10")
    
    def on_aggression_changed(self, value):
        """Handle aggression slider change"""
        self.aggression = value
        
        if value < 25:
            style = "Defensive"
        elif value < 50:
            style = "Cautious"
        elif value < 75:
            style = "Balanced"
        else:
            style = "Aggressive"
        
        self.aggression_value.setText(f"Aggression: {value}% ({style})")
    
    def update_display(self):
        """Update all display elements"""
        # Update scores
        innings = self.simulator.current_innings_data
        if innings:
            # Fix overs display: show max overs when all out instead of ball where last wicket fell
            overs = innings['overs']
            if innings['wickets'] >= 10 and self.simulator.max_overs:
                # All out - show max overs
                overs = float(self.simulator.max_overs)
            
            score_text = f"{innings['runs']}/{innings['wickets']} ({overs:.1f})"
            
            if self.simulator.current_innings == 1:
                self.team1_score.setText(score_text)
            else:
                self.team2_score.setText(score_text)
        
        # Update batting scorecard (TreeView table)
        self.update_batting_scorecard()
        
        # Update bowling scorecard (TreeView table)
        self.update_bowling_scorecard()
    
    def update_batting_scorecard(self):
        """Update batting scorecard table"""
        self.batting_tree.setRowCount(0)
        
        if not hasattr(self.simulator, 'match_stats'):
            return
        
        # Get current batting team players
        batting_team_name = self.simulator.batting_team.name if hasattr(self.simulator, 'batting_team') else self.team1.name
        
        row = 0
        for player in self.simulator.batting_team.players if hasattr(self.simulator, 'batting_team') else self.team1.players:
            player_name = player.name
            if player_name in self.simulator.match_stats:
                batting_stats = self.simulator.match_stats[player_name]['batting']
                
                # Only show players who have batted or are currently batting
                if batting_stats.get('balls', 0) > 0 or batting_stats.get('runs', 0) > 0 or batting_stats.get('dismissal'):
                    self.batting_tree.insertRow(row)
                    
                    runs = batting_stats.get('runs', 0)
                    balls = batting_stats.get('balls', 0)
                    fours = batting_stats.get('fours', 0)
                    sixes = batting_stats.get('sixes', 0)
                    sr = (runs / balls * 100) if balls > 0 else 0.0
                    dismissal = batting_stats.get('dismissal', '')
                    
                    # Format status (how out or not out)
                    if dismissal and dismissal != 'not out':
                        status = dismissal
                    elif balls > 0:
                        status = 'not out'
                    else:
                        status = ''
                    
                    # Create items with black text
                    name_item = QTableWidgetItem(player_name)
                    name_item.setForeground(QColor('black'))
                    
                    runs_item = QTableWidgetItem(str(runs))
                    runs_item.setForeground(QColor('black'))
                    
                    balls_item = QTableWidgetItem(str(balls))
                    balls_item.setForeground(QColor('black'))
                    
                    fours_item = QTableWidgetItem(str(fours))
                    fours_item.setForeground(QColor('black'))
                    
                    sixes_item = QTableWidgetItem(str(sixes))
                    sixes_item.setForeground(QColor('black'))
                    
                    sr_item = QTableWidgetItem(f"{sr:.1f}")
                    sr_item.setForeground(QColor('black'))
                    
                    status_item = QTableWidgetItem(status)
                    status_item.setForeground(QColor('black'))
                    
                    self.batting_tree.setItem(row, 0, name_item)
                    self.batting_tree.setItem(row, 1, runs_item)
                    self.batting_tree.setItem(row, 2, balls_item)
                    self.batting_tree.setItem(row, 3, fours_item)
                    self.batting_tree.setItem(row, 4, sixes_item)
                    self.batting_tree.setItem(row, 5, sr_item)
                    self.batting_tree.setItem(row, 6, status_item)
                    
                    row += 1
    
    def update_bowling_scorecard(self):
        """Update bowling scorecard table"""
        self.bowling_tree.setRowCount(0)
        
        if not hasattr(self.simulator, 'match_stats'):
            return
        
        # Get current bowling team players
        bowling_team_name = self.simulator.bowling_team.name if hasattr(self.simulator, 'bowling_team') else self.team2.name
        
        row = 0
        # Show ALL bowlers who have bowled (even 1 ball)
        for player in self.simulator.bowling_team.players if hasattr(self.simulator, 'bowling_team') else self.team2.players:
            player_name = player.name
            if player_name in self.simulator.match_stats:
                bowling_stats = self.simulator.match_stats[player_name]['bowling']
                
                # Show bowlers who have bowled at least 1 ball
                if bowling_stats.get('balls', 0) > 0:
                    self.bowling_tree.insertRow(row)
                    
                    balls = bowling_stats.get('balls', 0)
                    overs = balls // 6
                    balls_in_over = balls % 6
                    overs_str = f"{overs}.{balls_in_over}"
                    
                    maidens = bowling_stats.get('maidens', 0)
                    runs = bowling_stats.get('runs', 0)
                    wickets = bowling_stats.get('wickets', 0)
                    economy = (runs / (balls / 6)) if balls > 0 else 0.0
                    
                    speeds = bowling_stats.get('speeds', [])
                    avg_speed = sum(speeds) / len(speeds) if speeds else 0
                    top_speed = max(speeds) if speeds else 0
                    
                    # Create items with black text
                    name_item = QTableWidgetItem(player_name)
                    name_item.setForeground(QColor('black'))
                    
                    overs_item = QTableWidgetItem(overs_str)
                    overs_item.setForeground(QColor('black'))
                    
                    maidens_item = QTableWidgetItem(str(maidens))
                    maidens_item.setForeground(QColor('black'))
                    
                    runs_item = QTableWidgetItem(str(runs))
                    runs_item.setForeground(QColor('black'))
                    
                    wickets_item = QTableWidgetItem(str(wickets))
                    wickets_item.setForeground(QColor('black'))
                    
                    econ_item = QTableWidgetItem(f"{economy:.2f}")
                    econ_item.setForeground(QColor('black'))
                    
                    avg_speed_item = QTableWidgetItem(f"{avg_speed:.1f}" if avg_speed > 0 else "-")
                    avg_speed_item.setForeground(QColor('black'))
                    
                    top_speed_item = QTableWidgetItem(f"{top_speed:.1f}" if top_speed > 0 else "-")
                    top_speed_item.setForeground(QColor('black'))
                    
                    self.bowling_tree.setItem(row, 0, name_item)
                    self.bowling_tree.setItem(row, 1, overs_item)
                    self.bowling_tree.setItem(row, 2, maidens_item)
                    self.bowling_tree.setItem(row, 3, runs_item)
                    self.bowling_tree.setItem(row, 4, wickets_item)
                    self.bowling_tree.setItem(row, 5, econ_item)
                    self.bowling_tree.setItem(row, 6, avg_speed_item)
                    self.bowling_tree.setItem(row, 7, top_speed_item)
                    
                    row += 1
    
    
    def add_commentary(self, text):
        """Add commentary line"""
        self.commentary_text.append(text)
        # Auto scroll to bottom
        self.commentary_text.verticalScrollBar().setValue(
            self.commentary_text.verticalScrollBar().maximum()
        )
    
    def add_ball_commentary(self, result):
        """Add ball-by-ball commentary"""
        over = result.get('over', 0)
        ball = result.get('ball', 0)
        runs = result.get('runs', 0)
        wicket = result.get('wicket', False)
        
        commentary = f"{over}.{ball} - "
        
        if wicket:
            commentary += f"🔴 WICKET! {result.get('batsman', 'Batsman')} out! "
        elif runs == 6:
            commentary += f"⚡ SIX! "
        elif runs == 4:
            commentary += f"💥 FOUR! "
        elif runs == 0:
            commentary += f"⚪ Dot ball. "
        else:
            commentary += f"{runs} run{'s' if runs > 1 else ''}. "
        
        commentary += result.get('description', '')
        
        self.add_commentary(commentary)
    
    def handle_innings_complete(self):
        """Handle innings completion"""
        innings = self.simulator.innings1_data if self.simulator.current_innings == 2 else self.simulator.current_innings_data
        
        # Fix overs display: show max overs when all out
        overs = innings['overs']
        if innings['wickets'] >= 10 and self.simulator.max_overs:
            overs = float(self.simulator.max_overs)
        
        self.add_commentary("")
        self.add_commentary(f"{'='*50}")
        self.add_commentary(f"END OF INNINGS 1")
        self.add_commentary(f"{innings['batting_team']}: {innings['runs']}/{innings['wickets']} ({overs:.1f} overs)")
        
        # Show last wicket if all out
        if innings['wickets'] >= 10:
            self.add_commentary(f"All out!")
        
        target = innings['runs'] + 1
        self.add_commentary(f"{self.simulator.bowling_team.name} need {target} runs to win")
        
        self.add_commentary(f"{'='*50}")
        self.add_commentary("")
        self.add_commentary(f"INNINGS 2 - {self.simulator.batting_team.name} batting")
        self.add_commentary("")
    
    def handle_match_complete(self):
        """Handle match completion"""
        self.add_commentary("")
        self.add_commentary(f"{'='*50}")
        self.add_commentary(f"MATCH COMPLETE!")
        self.add_commentary("")
        
        # Show both innings scores with correct overs
        if self.simulator.innings1_data:
            inn1 = self.simulator.innings1_data
            overs1 = inn1['overs']
            if inn1['wickets'] >= 10 and self.simulator.max_overs:
                overs1 = float(self.simulator.max_overs)
            self.add_commentary(f"{inn1['batting_team']}: {inn1['runs']}/{inn1['wickets']} ({overs1:.1f} overs)")
            if inn1['wickets'] >= 10:
                self.add_commentary(f"  All out")
        
        if self.simulator.innings2_data:
            inn2 = self.simulator.innings2_data
            overs2 = inn2['overs']
            if inn2['wickets'] >= 10 and self.simulator.max_overs:
                overs2 = float(self.simulator.max_overs)
            self.add_commentary(f"{inn2['batting_team']}: {inn2['runs']}/{inn2['wickets']} ({overs2:.1f} overs)")
            if inn2['wickets'] >= 10:
                self.add_commentary(f"  All out")
        
        self.add_commentary("")
        
        winner = self.simulator.get_winner()
        if winner:
            self.add_commentary(f"Winner: {winner.name}")
            margin = self.simulator.get_margin()
            self.add_commentary(f"Margin: {margin}")
        else:
            self.add_commentary(f"Match Tied!")
        
        self.add_commentary(f"{'='*50}")
        
        # Mark fixture as completed
        if self.game_engine and self.fixture:
            self.fixture['completed'] = True
            self.fixture['status'] = 'Completed'
            self.fixture['result'] = {
                'winner': winner.name if winner else 'Tie',
                'team1_score': f"{self.simulator.innings1_data['runs']}/{self.simulator.innings1_data['wickets']}",
                'team2_score': f"{self.simulator.innings2_data['runs']}/{self.simulator.innings2_data['wickets']}" if self.simulator.innings2_data else "DNB"
            }
        
        # Disable controls
        self.play_btn.setEnabled(False)
        self.bowl_over_btn.setEnabled(False)
        self.auto_btn.setEnabled(False)
        
        # Emit completion signal
        result = {
            'winner': winner.name if winner else 'Tie',
            'team1_score': f"{self.simulator.innings1_data['runs']}/{self.simulator.innings1_data['wickets']}",
            'team2_score': f"{self.simulator.innings2_data['runs']}/{self.simulator.innings2_data['wickets']}" if self.simulator.innings2_data else "DNB"
        }
        self.match_completed.emit(result)

