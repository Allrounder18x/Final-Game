"""
Youth Management Screen - Single scrollable view for U21 squad management
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QGroupBox, QFrame, QScrollArea,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from cricket_manager.ui.styles import COLORS, MAIN_STYLESHEET
from cricket_manager.ui.screen_manager import BaseScreen
from cricket_manager.utils.constants import MAX_SQUAD_SIZE


class YouthManagementScreen(BaseScreen):
    """Full-screen view for youth player management with single scroll"""
    
    back_clicked = pyqtSignal()
    
    def __init__(self, screen_manager=None, game_engine=None):
        super().__init__(screen_manager)
        self.setStyleSheet(MAIN_STYLESHEET)
        self.game_engine = game_engine
        self.team = game_engine.user_team if game_engine else None
        self.youth_system = game_engine.youth_system if game_engine else None
        self.match_format = 'T20'
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header (fixed at top)
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            background-color: {COLORS['primary']};
            padding: 20px;
        """)
        header_layout = QHBoxLayout()
        
        # Back button
        back_btn = QPushButton("← Back")
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary_dark']};
                color: white;
                font-size: 14px;
                font-weight: 600;
                padding: 10px 20px;
                border-radius: 6px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #1B5E20;
            }}
        """)
        back_btn.clicked.connect(self.on_back)
        header_layout.addWidget(back_btn)
        
        # Title
        title_layout = QVBoxLayout()
        title = QLabel(f"⭐ {self.team.name} U21 Squad")
        title.setStyleSheet("font-size: 28px; font-weight: 700; color: white;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(title)
        
        subtitle = QLabel("Youth Player Management")
        subtitle.setStyleSheet("font-size: 14px; color: white;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(subtitle)
        
        header_layout.addLayout(title_layout, 1)
        header_layout.addWidget(QLabel(""))  # Spacer for symmetry
        
        header_frame.setLayout(header_layout)
        layout.addWidget(header_frame)
        
        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"border: none; background-color: {COLORS['bg_primary']};")
        
        # Content widget
        content = QWidget()
        content.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
        content_layout = QVBoxLayout()
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(30, 30, 30, 30)
        
        # Squad summary
        summary_frame = self.create_summary_frame()
        content_layout.addWidget(summary_frame)
        
        # Promotion requirements info
        requirements_frame = self.create_requirements_frame()
        content_layout.addWidget(requirements_frame)
        
        # Youth players table
        players_frame = self.create_players_table()
        content_layout.addWidget(players_frame)
        
        content.setLayout(content_layout)
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)
        
        self.setLayout(layout)
    
    def create_summary_frame(self):
        """Create squad summary frame"""
        frame = QFrame()
        frame.setStyleSheet(f"""
            background-color: #111827;
            border-radius: 10px;
            padding: 20px;
        """)
        
        layout = QHBoxLayout()
        layout.setSpacing(30)
        
        # Total players
        total_card = self.create_stat_card(
            "Total Players",
            str(len(self.team.u21_squad)) if hasattr(self.team, 'u21_squad') else "0",
            COLORS['info']
        )
        layout.addWidget(total_card)
        
        # Eligible for promotion
        eligible_count = 0
        if hasattr(self.team, 'u21_squad'):
            for player in self.team.u21_squad:
                is_eligible, _ = self.youth_system.is_eligible_for_promotion(player, self.match_format)
                if is_eligible:
                    eligible_count += 1
        
        eligible_card = self.create_stat_card(
            "Eligible for Promotion",
            str(eligible_count),
            COLORS['success']
        )
        layout.addWidget(eligible_card)
        
        # Average age
        avg_age = 0
        if hasattr(self.team, 'u21_squad') and len(self.team.u21_squad) > 0:
            avg_age = sum(p.age for p in self.team.u21_squad) / len(self.team.u21_squad)
        
        age_card = self.create_stat_card(
            "Average Age",
            f"{avg_age:.1f}",
            COLORS['secondary']
        )
        layout.addWidget(age_card)
        
        frame.setLayout(layout)
        return frame
    
    def create_stat_card(self, title, value, color):
        """Create a stat card"""
        card = QFrame()
        card.setStyleSheet(f"""
            background-color: {COLORS['bg_tertiary']};
            border-left: 5px solid {color};
            border-radius: 8px;
            padding: 20px;
        """)
        
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 13px; color: {COLORS['text_secondary']}; font-weight: 600;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 32px; font-weight: 700; color: {color};")
        layout.addWidget(value_label)
        
        card.setLayout(layout)
        return card
    
    def create_requirements_frame(self):
        """Create promotion requirements info frame"""
        frame = QGroupBox("📋 Promotion Requirements")
        frame.setStyleSheet(f"""
            QGroupBox {{
                font-size: 16px;
                font-weight: 700;
                color: #EAF1FF;
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                margin-top: 16px;
                padding-top: 20px;
                background-color: #111827;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 6px 16px;
                color: white;
                background-color: {COLORS['secondary']};
                border-radius: 6px;
                margin-left: 12px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        requirements_text = """
<b>Simple Promotion Criteria:</b>

• <b>Minimum Age:</b> 15 years
• <b>Skill Requirement:</b> Batting > 60 OR Bowling > 60

<i>Players meeting these criteria can be promoted to the senior team.</i>
        """
        
        info_label = QLabel(requirements_text)
        info_label.setStyleSheet("font-size: 14px; color: #B8C3D9; padding: 10px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        frame.setLayout(layout)
        return frame
    
    def create_players_table(self):
        """Create youth players table"""
        frame = QGroupBox("👥 U21 Squad Players")
        frame.setStyleSheet(f"""
            QGroupBox {{
                font-size: 16px;
                font-weight: 700;
                color: #EAF1FF;
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                margin-top: 16px;
                padding-top: 20px;
                background-color: #111827;
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
        
        layout = QVBoxLayout()
        
        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(12)
        self.table.setHorizontalHeaderLabels([
            'Name', 'Age', 'Role', 'BAT', 'BOWL', 'FIELD', 
            'POT', 'Matches', 'Runs', 'Wickets', 'Eligible', 'Action'
        ])
        
        # Set column widths
        self.table.setColumnWidth(0, 150)  # Name
        self.table.setColumnWidth(1, 50)   # Age
        self.table.setColumnWidth(2, 150)  # Role
        self.table.setColumnWidth(3, 60)   # BAT
        self.table.setColumnWidth(4, 60)   # BOWL
        self.table.setColumnWidth(5, 60)   # FIELD
        self.table.setColumnWidth(6, 60)   # POT
        self.table.setColumnWidth(7, 70)   # Matches
        self.table.setColumnWidth(8, 70)   # Runs
        self.table.setColumnWidth(9, 80)   # Wickets
        self.table.setColumnWidth(10, 100) # Eligible
        self.table.setColumnWidth(11, 100) # Action
        
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setMinimumHeight(400)
        
        # Populate table
        self.populate_table()
        
        layout.addWidget(self.table)
        frame.setLayout(layout)
        return frame
    
    def populate_table(self):
        """Populate the youth players table"""
        if not hasattr(self.team, 'u21_squad'):
            self.table.setRowCount(0)
            return
        
        self.table.setRowCount(len(self.team.u21_squad))
        
        for i, player in enumerate(self.team.u21_squad):
            # Get stats
            season_stats = player.season_stats.get(self.match_format, {})
            matches = season_stats.get('matches', 0)
            runs = season_stats.get('runs', 0)
            wickets = season_stats.get('wickets', 0)
            
            # Check eligibility
            is_eligible, reason = self.youth_system.is_eligible_for_promotion(player, self.match_format)
            
            # Name
            name_item = QTableWidgetItem(player.name)
            name_item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            self.table.setItem(i, 0, name_item)
            
            # Age
            age_item = QTableWidgetItem(str(player.age))
            age_item.setFont(QFont("Arial", 11))
            age_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 1, age_item)
            
            # Role
            role_item = QTableWidgetItem(player.role)
            role_item.setFont(QFont("Arial", 11))
            self.table.setItem(i, 2, role_item)
            
            # Skills (hide batting/bowling when setting is on)
            hide_bat_bowl = getattr(self.game_engine, 'hide_batting_bowling_ratings', False) if self.game_engine else False
            bat_item = QTableWidgetItem("—" if hide_bat_bowl else str(player.batting))
            bat_item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            bat_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 3, bat_item)
            
            bowl_item = QTableWidgetItem("—" if hide_bat_bowl else str(player.bowling))
            bowl_item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            bowl_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 4, bowl_item)
            
            field_item = QTableWidgetItem(str(player.fielding))
            field_item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            field_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 5, field_item)
            
            # Potential
            pot_item = QTableWidgetItem(str(player.potential))
            pot_item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            pot_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            pot_item.setForeground(QColor(COLORS['gold']))
            self.table.setItem(i, 6, pot_item)
            
            # Stats
            matches_item = QTableWidgetItem(str(matches))
            matches_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 7, matches_item)
            
            runs_item = QTableWidgetItem(str(runs))
            runs_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 8, runs_item)
            
            wickets_item = QTableWidgetItem(str(wickets))
            wickets_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 9, wickets_item)
            
            # Eligibility
            eligible_text = "✓ Eligible" if is_eligible else "✗ Not Eligible"
            eligible_item = QTableWidgetItem(eligible_text)
            eligible_item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            eligible_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if is_eligible:
                eligible_item.setForeground(QColor(COLORS['success']))
                # Color the entire row green
                for col in range(11):
                    if self.table.item(i, col):
                        self.table.item(i, col).setBackground(QColor('#E8F5E9'))
            else:
                eligible_item.setForeground(QColor(COLORS['danger']))
            self.table.setItem(i, 10, eligible_item)
            
            # Promote button
            promote_btn = QPushButton("Promote" if is_eligible else "View")
            if is_eligible:
                promote_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLORS['success']};
                        color: white;
                        font-size: 12px;
                        font-weight: 600;
                        padding: 8px 16px;
                        border-radius: 6px;
                        border: none;
                    }}
                    QPushButton:hover {{
                        background-color: #66BB6A;
                    }}
                """)
            else:
                promote_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLORS['border']};
                        color: {COLORS['text_secondary']};
                        font-size: 12px;
                        font-weight: 600;
                        padding: 8px 16px;
                        border-radius: 6px;
                        border: none;
                    }}
                    QPushButton:hover {{
                        background-color: #BDBDBD;
                    }}
                """)
            
            promote_btn.clicked.connect(lambda checked, p=player, eligible=is_eligible, r=reason: 
                                       self.on_promote_clicked(p, eligible, r))
            self.table.setCellWidget(i, 11, promote_btn)
            
            # Set row height
            self.table.setRowHeight(i, 50)
    
    def on_promote_clicked(self, player, is_eligible, reason):
        """Handle promote button click"""
        if not is_eligible:
            # Show reason why not eligible
            QMessageBox.information(
                self,
                "Not Eligible",
                f"{player.name} is not eligible for promotion:\n\n{reason}",
                QMessageBox.StandardButton.Ok
            )
            return
        
        # Check if senior squad has space
        if len(self.team.players) >= MAX_SQUAD_SIZE:
            QMessageBox.warning(
                self,
                "Squad Full",
                f"Senior squad is full (maximum {MAX_SQUAD_SIZE} players).\nPlease release a player first.",
                QMessageBox.StandardButton.Ok
            )
            return
        
        # Confirm promotion
        reply = QMessageBox.question(
            self,
            "Confirm Promotion",
            f"Promote {player.name} ({player.role}, Age {player.age}) to the senior team?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Snapshot U21 career and reset senior stats before promotion
            if hasattr(player, 'snapshot_u21_and_reset_senior_career'):
                player.snapshot_u21_and_reset_senior_career()
            # Promote player from U21 to senior
            if hasattr(self.team, 'u21_squad') and player in self.team.u21_squad:
                self.team.u21_squad.remove(player)
            player.is_youth_player = False
            self.team.add_player(player)
            
            QMessageBox.information(
                self,
                "Success",
                f"{player.name} has been promoted to the senior team!",
                QMessageBox.StandardButton.Ok
            )
            
            # Refresh table only
            self.populate_table()
    
    def on_back(self):
        """Handle back button click"""
        print("[YouthManagementScreen] Back clicked")
        self.back_clicked.emit()
