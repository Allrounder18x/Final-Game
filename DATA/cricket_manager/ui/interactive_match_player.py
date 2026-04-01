"""
Interactive Match Player - Ball-by-ball match with GUI controls
Features: Aggression control, shot selection, bowling controls, live commentary
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QFrame, QTextEdit, QGroupBox, QGridLayout, QProgressBar,
    QComboBox, QButtonGroup, QRadioButton
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
import random

from cricket_manager.ui.styles import COLORS, MAIN_STYLESHEET
from cricket_manager.core.match_simulator import MatchSimulator


class InteractiveMatchPlayer(QDialog):
    """
    Interactive match player with ball-by-ball controls
    
    Features:
    - Aggression slider (0-100)
    - Shot selection buttons
    - Bowling controls
    - Live commentary
    - Real-time scorecard
    - Auto-play option
    """
    
    match_completed = pyqtSignal(dict)
    
    def __init__(self, parent, team1, team2, match_format='T20', game_engine=None):
        super().__init__(parent)
        self.setStyleSheet(MAIN_STYLESHEET)
        self.team1 = team1
        self.team2 = team2
        self.match_format = match_format
        self.game_engine = game_engine
        
        # Match state
        self.simulator = MatchSimulator(team1, team2, match_format)
        self.current_innings = 1
        self.current_over = 0
        self.current_ball = 0
        self.aggression = 50  # 0-100
        self.auto_play = False
        self.auto_timer = None
        
        # Setup UI
        self.setWindowTitle(f"{team1.name} vs {team2.name} - {match_format}")
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
        
        # Middle: Main content (3 columns)
        content_layout = QHBoxLayout()
        
        # Left: Scorecard
        scorecard = self.create_scorecard_panel()
        content_layout.addWidget(scorecard, 2)
        
        # Center: Commentary
        commentary = self.create_commentary_panel()
        content_layout.addWidget(commentary, 3)
        
        # Right: Controls
        controls = self.create_controls_panel()
        content_layout.addWidget(controls, 2)
        
        layout.addLayout(content_layout, 1)
        
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
        """Create scorecard panel"""
        panel = QGroupBox("Live Scorecard")
        panel.setStyleSheet(f"""
            QGroupBox {{
                font-size: 14px;
                font-weight: 700;
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                padding: 15px;
                margin-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        # Current partnership
        self.partnership_label = QLabel("Partnership: 0 runs (0 balls)")
        self.partnership_label.setStyleSheet("font-size: 12px; font-weight: 600; padding: 5px;")
        layout.addWidget(self.partnership_label)
        
        # Batsmen
        batsmen_frame = QFrame()
        batsmen_frame.setStyleSheet(f"background-color: {COLORS['bg_tertiary']}; padding: 10px; border-radius: 6px;")
        batsmen_layout = QVBoxLayout()
        
        self.striker_label = QLabel("Striker: -")
        self.striker_label.setStyleSheet("font-size: 13px; font-weight: 600;")
        batsmen_layout.addWidget(self.striker_label)
        
        self.non_striker_label = QLabel("Non-Striker: -")
        self.non_striker_label.setStyleSheet("font-size: 13px;")
        batsmen_layout.addWidget(self.non_striker_label)
        
        batsmen_frame.setLayout(batsmen_layout)
        layout.addWidget(batsmen_frame)
        
        # Current bowler
        bowler_frame = QFrame()
        bowler_frame.setStyleSheet(f"background-color: {COLORS['bg_tertiary']}; padding: 10px; border-radius: 6px;")
        bowler_layout = QVBoxLayout()
        
        self.bowler_label = QLabel("Bowler: -")
        self.bowler_label.setStyleSheet("font-size: 13px; font-weight: 600;")
        bowler_layout.addWidget(self.bowler_label)
        
        self.bowler_stats = QLabel("0-0 (0.0 overs)")
        self.bowler_stats.setStyleSheet("font-size: 12px;")
        bowler_layout.addWidget(self.bowler_stats)
        
        bowler_frame.setLayout(bowler_layout)
        layout.addWidget(bowler_frame)
        
        # Recent balls
        self.recent_balls = QLabel("This Over: ")
        self.recent_balls.setStyleSheet("font-size: 12px; padding: 10px;")
        self.recent_balls.setWordWrap(True)
        layout.addWidget(self.recent_balls)
        
        # Required run rate (for chase)
        self.req_rr_label = QLabel("")
        self.req_rr_label.setStyleSheet("font-size: 12px; font-weight: 600; color: #d32f2f;")
        layout.addWidget(self.req_rr_label)
        
        layout.addStretch()
        panel.setLayout(layout)
        return panel
    
    def create_commentary_panel(self):
        """Create commentary panel"""
        panel = QGroupBox("Live Commentary")
        panel.setStyleSheet(f"""
            QGroupBox {{
                font-size: 14px;
                font-weight: 700;
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                padding: 15px;
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
                background-color: #0B1220;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 10px;
            }
        """)
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
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                padding: 15px;
                margin-top: 10px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Aggression slider
        aggr_label = QLabel("Batting Aggression")
        aggr_label.setStyleSheet("font-size: 13px; font-weight: 600;")
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
        self.aggression_value.setStyleSheet("font-size: 11px; color: #666;")
        layout.addWidget(self.aggression_value)
        
        # Shot selection
        shot_label = QLabel("Shot Selection")
        shot_label.setStyleSheet("font-size: 13px; font-weight: 600; margin-top: 10px;")
        layout.addWidget(shot_label)
        
        shot_grid = QGridLayout()
        shot_grid.setSpacing(8)
        
        shots = [
            ("Defend", 0, 0), ("Push", 0, 1),
            ("Drive", 1, 0), ("Cut", 1, 1),
            ("Pull", 2, 0), ("Sweep", 2, 1),
            ("Loft", 3, 0), ("Slog", 3, 1)
        ]
        
        self.shot_buttons = {}
        for shot_name, row, col in shots:
            btn = QPushButton(shot_name)
            btn.setMinimumHeight(35)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #111827;
                    border: 2px solid {COLORS['border']};
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['primary']};
                    color: white;
                    border-color: {COLORS['primary']};
                }}
            """)
            btn.clicked.connect(lambda checked, s=shot_name: self.play_ball(shot_type=s))
            shot_grid.addWidget(btn, row, col)
            self.shot_buttons[shot_name] = btn
        
        layout.addLayout(shot_grid)
        
        # Bowling controls
        bowl_label = QLabel("Bowling Controls")
        bowl_label.setStyleSheet("font-size: 13px; font-weight: 600; margin-top: 10px;")
        layout.addWidget(bowl_label)
        
        self.bowling_combo = QComboBox()
        self.bowling_combo.addItems(["Auto Select", "Change Bowler"])
        self.bowling_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 8px;
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
                font-size: 12px;
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
            score_text = f"{innings['runs']}/{innings['wickets']} ({innings['overs']:.1f})"
            
            if self.simulator.current_innings == 1:
                self.team1_score.setText(score_text)
            else:
                self.team2_score.setText(score_text)
        
        # Update batsmen
        if self.simulator.striker:
            striker_text = f"⭐ {self.simulator.striker.name}: {self.simulator.striker_runs}({self.simulator.striker_balls})"
            self.striker_label.setText(striker_text)
        
        if self.simulator.non_striker:
            non_striker_text = f"   {self.simulator.non_striker.name}: {self.simulator.non_striker_runs}({self.simulator.non_striker_balls})"
            self.non_striker_label.setText(non_striker_text)
        
        # Update bowler
        if self.simulator.current_bowler:
            bowler_text = f"🎯 {self.simulator.current_bowler.name}"
            self.bowler_label.setText(bowler_text)
            
            bowler_stats = f"{self.simulator.bowler_wickets}-{self.simulator.bowler_runs} ({self.simulator.bowler_overs:.1f} overs)"
            self.bowler_stats.setText(bowler_stats)
        
        # Update recent balls
        if hasattr(self.simulator, 'current_over_balls'):
            balls_text = "This Over: " + " ".join(self.simulator.current_over_balls[-6:])
            self.recent_balls.setText(balls_text)
        
        # Update required run rate (if chasing)
        if self.simulator.current_innings == 2 and innings:
            target = self.simulator.target
            needed = target - innings['runs']
            balls_left = (self.simulator.max_overs * 6) - (innings['balls'])
            
            if balls_left > 0:
                req_rr = (needed * 6) / balls_left
                self.req_rr_label.setText(f"Need {needed} runs from {balls_left} balls (RR: {req_rr:.2f})")
            else:
                self.req_rr_label.setText("")
    
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
        self.add_commentary("")
        self.add_commentary(f"{'='*50}")
        self.add_commentary(f"END OF INNINGS 1")
        self.add_commentary(f"{innings['batting_team']}: {innings['runs']}/{innings['wickets']} ({innings['overs']:.1f} overs)")
        
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
        self.add_commentary(f"🏆 MATCH COMPLETE!")
        
        winner = self.simulator.get_winner()
        if winner:
            self.add_commentary(f"Winner: {winner.name}")
            margin = self.simulator.get_margin()
            self.add_commentary(f"Margin: {margin}")
        else:
            self.add_commentary(f"Match Tied!")
        
        self.add_commentary(f"{'='*50}")
        
        # Disable controls
        self.play_btn.setEnabled(False)
        self.bowl_over_btn.setEnabled(False)
        self.auto_btn.setEnabled(False)
        for btn in self.shot_buttons.values():
            btn.setEnabled(False)
        
        # Emit completion signal
        result = {
            'winner': winner.name if winner else 'Tie',
            'team1_score': f"{self.simulator.innings1_data['runs']}/{self.simulator.innings1_data['wickets']}",
            'team2_score': f"{self.simulator.innings2_data['runs']}/{self.simulator.innings2_data['wickets']}" if self.simulator.innings2_data else "DNB"
        }
        self.match_completed.emit(result)
