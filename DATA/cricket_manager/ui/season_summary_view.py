"""
Season Summary Screen - Clean, Simple, Working Design
Shows comprehensive end-of-season report with all tabs functional
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QFrame, QScrollArea,
    QHeaderView, QTabWidget, QDialog, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from cricket_manager.ui.styles import COLORS, MAIN_STYLESHEET
from cricket_manager.ui.match_scorecard_dialog import MatchScorecardDialog


class SeasonSummaryDialog(QDialog):
    """Clean, working season summary dialog"""
    
    def __init__(self, season_data, parent=None, game_engine=None):
        super().__init__(parent)
        self.setStyleSheet(MAIN_STYLESHEET)
        self.season_data = season_data
        self.game_engine = game_engine or (getattr(parent, 'game_engine', None) if parent else None)
        self.setWindowTitle(f"Season {season_data.get('season', 1)} Summary")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI with clean layout"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Continue button at TOP (prominent) — adds 5 training points for the new season
        continue_btn = QPushButton("Continue to Next Season")
        continue_btn.clicked.connect(self._on_continue_to_next_season)
        continue_btn.setMinimumHeight(50)
        continue_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                border: none;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_light']};
            }}
        """)
        layout.addWidget(continue_btn)
        
        # Tabs
        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {COLORS['border_light']};
                background: {COLORS['bg_primary']};
            }}
            QTabBar::tab {{
                background: {COLORS['bg_tertiary']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border_light']};
                padding: 8px 14px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background: {COLORS['primary']};
                color: #FFFFFF;
            }}
            QTabBar::tab:hover {{
                background: {COLORS['bg_hover']};
            }}
        """)
        tabs.addTab(self.create_overview_tab(), "Overview")
        tabs.addTab(self.create_matches_tab(), "Matches")
        tabs.addTab(self.create_retirements_tab(), "Retirements")
        tabs.addTab(self.create_promotions_tab(), "Youth Promotions")
        tabs.addTab(self.create_skill_changes_tab(), "Skill Changes")
        tabs.addTab(self.create_tier_changes_tab(), "Tier Changes")
        tabs.addTab(self.create_transfers_tab(), "Transfers")
        
        # Add World Cup tab if there was one
        if self.season_data.get('world_cup'):
            tabs.addTab(self.create_worldcup_tab(), "World Cup")
        
        tabs.addTab(self.create_role_conversions_tab(), "Role Conversions")
        
        layout.addWidget(tabs, 1)
        
        self.setLayout(layout)
    
    def _on_continue_to_next_season(self):
        """Add 5 training points for the new season (Training tab), then close the dialog."""
        if self.game_engine and getattr(self.game_engine, 'training_system', None) and getattr(self.game_engine, 'user_team', None):
            self.game_engine.training_system.reset_training_points(self.game_engine.user_team)
        self.accept()
    
    def create_header(self):
        """Create simple header"""
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['primary']};
                padding: 20px;
                border-radius: 5px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        title = QLabel(f"🏆 Season {self.season_data.get('season', 1)} Complete! 🏆")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel(f"Year {self.season_data.get('year', 2025)} • {self.season_data.get('format', 'All Formats')}")
        subtitle.setStyleSheet("font-size: 16px; color: white;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        header.setLayout(layout)
        return header
    
    def create_overview_tab(self):
        """Create overview with simple statistics"""
        # Create scroll area for overview
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Season summary stats
        stats_frame = QFrame()
        stats_frame.setMinimumHeight(180)
        stats_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-radius: 10px;
                padding: 20px;
            }}
        """)
        stats_layout = QVBoxLayout()
        
        stats_title = QLabel("Season Summary")
        stats_title.setStyleSheet("font-size: 20px; font-weight: bold;")
        stats_layout.addWidget(stats_title)
        
        # Key stats
        stats_grid = QHBoxLayout()
        
        def create_stat_box(value, label):
            box = QVBoxLayout()
            val_label = QLabel(str(value))
            val_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #2196F3;")
            val_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            box.addWidget(val_label)
            
            text_label = QLabel(label)
            text_label.setStyleSheet(f"font-size: 14px; color: {COLORS['text_secondary']};")
            text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            box.addWidget(text_label)
            
            return box
        
        stats_grid.addLayout(create_stat_box(
            self.season_data.get('total_matches', 0), 
            "Total Matches"
        ))
        stats_grid.addLayout(create_stat_box(
            len(self.season_data.get('retirements', [])), 
            "Retirements"
        ))
        stats_grid.addLayout(create_stat_box(
            len(self.season_data.get('promotions', [])), 
            "Youth Promotions"
        ))
        stats_grid.addLayout(create_stat_box(
            len(self.season_data.get('skill_changes', [])), 
            "Skill Changes"
        ))
        
        stats_layout.addLayout(stats_grid)
        stats_frame.setLayout(stats_layout)
        layout.addWidget(stats_frame)
        
        # Season awards (Batter, Bowler, Young Player of the season)
        awards = self.season_data.get('season_awards', {})
        if awards and (awards.get('batter') or awards.get('bowler') or awards.get('young_player')):
            awards_frame = QFrame()
            awards_frame.setStyleSheet(f"""
                QFrame {{ background-color: {COLORS['bg_secondary']}; border-radius: 10px; padding: 20px; }}
            """)
            awards_layout = QVBoxLayout()
            awards_title = QLabel("Season Awards")
            awards_title.setStyleSheet("font-size: 20px; font-weight: bold;")
            awards_layout.addWidget(awards_title)
            if awards.get('batter'):
                awards_layout.addWidget(QLabel(f"Batter of the Season: {awards['batter']}"))
            if awards.get('bowler'):
                awards_layout.addWidget(QLabel(f"Bowler of the Season: {awards['bowler']}"))
            if awards.get('young_player'):
                awards_layout.addWidget(QLabel(f"Young Player of the Season: {awards['young_player']}"))
            awards_frame.setLayout(awards_layout)
            layout.addWidget(awards_frame)
        
        # World Cup section
        if self.season_data.get('world_cup'):
            wc_data = self.season_data['world_cup']
            wc_frame = QFrame()
            wc_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['bg_secondary']};
                    border-radius: 10px;
                    padding: 20px;
                }}
            """)
            wc_layout = QVBoxLayout()
            
            wc_title = QLabel("🏆 World Cup Results 🏆")
            wc_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFD700;")
            wc_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            wc_layout.addWidget(wc_title)
            
            wc_info = QLabel(f"Winner: {wc_data.get('winner', 'N/A')}")
            wc_info.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50;")
            wc_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            wc_layout.addWidget(wc_info)
            
            runner_label = QLabel(f"Runner-up: {wc_data.get('runner_up', 'N/A')}")
            runner_label.setStyleSheet("font-size: 16px;")
            runner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            wc_layout.addWidget(runner_label)
            
            wc_frame.setLayout(wc_layout)
            layout.addWidget(wc_frame)
        
        layout.addStretch()
        widget.setLayout(layout)
        scroll.setWidget(widget)
        return scroll
    
    def create_matches_tab(self):
        """Create matches tab with clickable match cards and filters"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Store all matches
        self.all_matches = self.season_data.get('matches', [])
        
        if not self.all_matches:
            no_matches_label = QLabel("No matches played this season")
            no_matches_label.setStyleSheet(f"font-size: 18px; color: {COLORS['text_secondary']}; padding: 50px;")
            no_matches_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(no_matches_label)
        else:
            # Filters section
            filters_frame = QFrame()
            filters_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['bg_secondary']};
                    border-radius: 8px;
                    padding: 10px;
                }}
            """)
            filters_layout = QHBoxLayout()
            
            # Format filter
            filters_layout.addWidget(QLabel("Format:"))
            self.matches_format_filter = QComboBox()
            self.matches_format_filter.addItem("All Formats")
            self.matches_format_filter.addItems(["T20", "ODI", "Test"])
            self.matches_format_filter.currentTextChanged.connect(self.filter_matches)
            self.matches_format_filter.setStyleSheet("""
                QComboBox {
                    padding: 5px 10px;
                    min-width: 100px;
                }
            """)
            filters_layout.addWidget(self.matches_format_filter)
            
            filters_layout.addSpacing(20)
            
            # Team filter
            filters_layout.addWidget(QLabel("Team:"))
            self.matches_team_filter = QComboBox()
            self.matches_team_filter.addItem("All Teams")
            # Get unique teams from matches
            teams = set()
            for match in self.all_matches:
                teams.add(match.get('home', ''))
                teams.add(match.get('away', ''))
            for team in sorted(teams):
                if team:
                    self.matches_team_filter.addItem(team)
            self.matches_team_filter.currentTextChanged.connect(self.filter_matches)
            self.matches_team_filter.setStyleSheet("""
                QComboBox {
                    padding: 5px 10px;
                    min-width: 150px;
                }
            """)
            filters_layout.addWidget(self.matches_team_filter)
            
            filters_layout.addSpacing(20)
            
            # Tier filter
            filters_layout.addWidget(QLabel("Tier:"))
            self.matches_tier_filter = QComboBox()
            self.matches_tier_filter.addItem("All Tiers")
            self.matches_tier_filter.addItems(["Tier 1", "Tier 2", "Tier 3", "Tier 4", "Tier 5 (U21)", "World Cup"])
            self.matches_tier_filter.currentTextChanged.connect(self.filter_matches)
            self.matches_tier_filter.setStyleSheet("""
                QComboBox {
                    padding: 5px 10px;
                    min-width: 100px;
                }
            """)
            filters_layout.addWidget(self.matches_tier_filter)
            
            filters_layout.addStretch()
            filters_frame.setLayout(filters_layout)
            layout.addWidget(filters_frame)
            
            # Match count label
            self.matches_count_label = QLabel(f"{len(self.all_matches)} matches")
            self.matches_count_label.setStyleSheet(f"font-size: 14px; color: {COLORS['text_secondary']}; font-style: italic; padding: 10px;")
            layout.addWidget(self.matches_count_label)
            
            # Scroll area for matches
            self.matches_scroll = QScrollArea()
            self.matches_scroll.setWidgetResizable(True)
            self.matches_scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
            
            # Create container for match cards
            self.matches_container = QWidget()
            self.matches_layout = QVBoxLayout()
            self.matches_layout.setSpacing(10)
            self.matches_container.setLayout(self.matches_layout)
            
            self.matches_scroll.setWidget(self.matches_container)
            layout.addWidget(self.matches_scroll)
            
            # Initial display of all matches
            self.filter_matches()
        
        widget.setLayout(layout)
        return widget
    
    def filter_matches(self):
        """Filter matches based on selected filters"""
        format_filter = self.matches_format_filter.currentText() if hasattr(self, 'matches_format_filter') else "All Formats"
        team_filter = self.matches_team_filter.currentText() if hasattr(self, 'matches_team_filter') else "All Teams"
        tier_filter = self.matches_tier_filter.currentText() if hasattr(self, 'matches_tier_filter') else "All Tiers"
        
        # Filter matches
        filtered = self.all_matches
        
        if format_filter != "All Formats":
            filtered = [m for m in filtered if m.get('format') == format_filter]
        
        if team_filter != "All Teams":
            filtered = [m for m in filtered if team_filter in [m.get('home', ''), m.get('away', '')]]
        
        if tier_filter != "All Tiers":
            if tier_filter == "World Cup":
                # Show only World Cup matches
                filtered = [m for m in filtered if m.get('is_world_cup', False)]
            else:
                # Parse tier number from filter text (e.g., "Tier 5 (U21)" -> 5)
                tier_num = int(tier_filter.split()[1])
                # Filter by tier - matches now store their tier
                filtered = [m for m in filtered if m.get('tier') == tier_num]
        
        # Update count label
        if hasattr(self, 'matches_count_label'):
            self.matches_count_label.setText(f"{len(filtered)} matches shown")
        
        # Clear and rebuild match cards
        if hasattr(self, 'matches_layout'):
            # Clear existing widgets
            while self.matches_layout.count():
                item = self.matches_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # Add filtered matches
            for match in filtered:
                match_card = self.create_match_card(match)
                self.matches_layout.addWidget(match_card)
            
            self.matches_layout.addStretch()
    
    def create_match_card(self, match):
        """Create a clickable match card"""
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border: 2px solid {COLORS['border_light']};
                border-radius: 8px;
                padding: 15px;
            }}
            QFrame:hover {{
                background-color: {COLORS['bg_hover']};
                border: 2px solid {COLORS['primary']};
            }}
        """)
        
        layout = QHBoxLayout()
        
        # Match info
        info_layout = QVBoxLayout()
        
        teams = QLabel(f"{match.get('home', 'Home')} vs {match.get('away', 'Away')}")
        teams.setStyleSheet("font-size: 16px; font-weight: bold;")
        info_layout.addWidget(teams)
        
        # Match type display
        round_type = match.get('round', '')
        if round_type:
            match_type = f"🏆 World Cup - {round_type}"
        elif match.get('is_world_cup'):
            match_type = "🏆 World Cup Match"
        else:
            match_type = f"Tier {match.get('tier', 1)} Match"
        
        format_info = QLabel(f"{match.get('format', 'Unknown')} • {match_type}")
        format_info.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']};")
        info_layout.addWidget(format_info)
        
        # Man of the Match
        mom = match.get('man_of_the_match', '')
        if mom:
            mom_label = QLabel(f"⭐ Man of the Match: {mom}")
            mom_label.setStyleSheet("font-size: 12px; color: #FF9800; font-weight: bold;")
            info_layout.addWidget(mom_label)
        
        # Result
        result = match.get('result', {})
        winner = match.get('winner', result.get('winner', 'Unknown'))
        margin = match.get('margin', result.get('margin', ''))
        
        result_label = QLabel(f"🏆 {winner} won by {margin}")
        result_label.setStyleSheet("font-size: 14px; color: #4CAF50; font-weight: bold;")
        info_layout.addWidget(result_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # Click hint
        hint = QLabel("Click to view scorecard")
        hint.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']}; font-style: italic;")
        layout.addWidget(hint)
        
        widget.setLayout(layout)
        
        # Get scorecard from match data
        scorecard_data = match.get('scorecard')
        if not scorecard_data and 'result' in match:
            result = match.get('result', {})
            if isinstance(result, dict):
                scorecard_data = result.get('scorecard')
        
        # Make clickable
        widget.mousePressEvent = lambda event, sc=scorecard_data: self.show_match_scorecard(sc)
        
        return widget
    
    def show_match_scorecard(self, scorecard):
        """Show match scorecard dialog"""
        print(f"[SeasonSummary] Attempting to show scorecard: {scorecard is not None}")
        
        # Check if scorecard is in the result dictionary
        if isinstance(scorecard, dict) and 'innings' in scorecard:
            actual_scorecard = scorecard
        elif isinstance(scorecard, dict) and 'scorecard' in scorecard:
            actual_scorecard = scorecard.get('scorecard')
        else:
            actual_scorecard = None
        
        if actual_scorecard:
            try:
                print(f"[SeasonSummary] Scorecard data: {list(actual_scorecard.keys()) if isinstance(actual_scorecard, dict) else type(actual_scorecard)}")
                dialog = MatchScorecardDialog(actual_scorecard, self)
                dialog.exec()
            except Exception as e:
                print(f"[SeasonSummary] Error showing scorecard: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("[SeasonSummary] No scorecard data available")
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Scorecard", "No scorecard data available for this match.")
    
    def create_retirements_tab(self):
        """Create retirements tab"""
        return self.create_simple_table_tab(
            "Player Retirements",
            self.season_data.get('retirements', []),
            ["Player", "Team", "Age", "Role", "Batting", "Bowling"]
        )
    
    def create_promotions_tab(self):
        """Create youth promotions tab"""
        return self.create_simple_table_tab(
            "Youth Promotions",
            self.season_data.get('promotions', []),
            ["Player", "Team", "Age", "Role", "Batting", "Bowling"]
        )
    
    def create_skill_changes_tab(self):
        """Create skill changes tab with improved presentation"""
        changes = self.season_data.get('skill_changes', [])
        
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title header
        title_frame = QFrame()
        title_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['primary']};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        title_layout = QHBoxLayout()
        
        title_label = QLabel("📊 Skill & Trait Changes")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        title_layout.addWidget(title_label)
        
        count_label = QLabel(f"{len(changes)} changes")
        count_label.setStyleSheet("font-size: 14px; color: rgba(255,255,255,0.8);")
        title_layout.addStretch()
        title_layout.addWidget(count_label)
        
        title_frame.setLayout(title_layout)
        layout.addWidget(title_frame)
        
        # Info label
        info_label = QLabel("💡 Double-click on any card to view player profile")
        info_label.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']}; padding: 5px; font-style: italic;")
        layout.addWidget(info_label)
        
        if not changes:
            empty_frame = QFrame()
            empty_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['bg_secondary']};
                    border-radius: 8px;
                    padding: 50px;
                }}
            """)
            empty_layout = QVBoxLayout()
            empty_label = QLabel("No significant skill changes this season")
            empty_label.setStyleSheet(f"font-size: 18px; color: {COLORS['text_secondary']};")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_layout.addWidget(empty_label)
            empty_frame.setLayout(empty_layout)
            layout.addWidget(empty_frame)
        else:
            # Store changes for click handling
            self._skill_changes = changes
            
            # Scroll area
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("QScrollArea { border: none; }")
            
            content = QWidget()
            content_layout = QVBoxLayout()
            content_layout.setSpacing(10)
            
            for idx, change in enumerate(changes[:50]):  # Limit to 50
                change_widget = self.create_skill_change_card(change, idx)
                content_layout.addWidget(change_widget)
            
            content_layout.addStretch()
            content.setLayout(content_layout)
            scroll.setWidget(content)
            layout.addWidget(scroll)
        
        widget.setLayout(layout)
        return widget
    
    def create_skill_change_card(self, change, idx=0):
        """Create a skill change display card for both skill and trait changes"""
        change_type = change.get('type', 'skill_change')
        
        # Determine card color based on change type
        if change_type == 'trait_gained':
            bg_color = '#e8f5e9'  # Light green
            border_color = '#4caf50'
            icon = '✨'
        elif change_type == 'trait_lost':
            bg_color = '#ffebee'  # Light red
            border_color = '#f44336'
            icon = '❌'
        elif change_type == 'trait_level_up':
            bg_color = '#e3f2fd'  # Light blue
            border_color = '#2196f3'
            icon = '⬆️'
        elif change_type == 'trait_level_down':
            bg_color = '#fff3e0'  # Light orange
            border_color = '#ff9800'
            icon = '⬇️'
        else:
            bg_color = COLORS['bg_secondary']
            border_color = COLORS['border']
            icon = '📊'
        
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 8px;
                border-left: 4px solid {border_color};
                padding: 15px;
                margin: 5px;
            }}
            QFrame:hover {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-left: 4px solid {border_color};
            }}
        """)
        widget.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Store change data for click handling
        widget.change_data = change
        
        layout = QVBoxLayout()
        
        player = change.get('player', 'Unknown')
        team = change.get('team', 'Unknown')
        
        header = QLabel(f"{icon} {player} ({team})")
        header.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(header)
        
        # Import traits for display names and descriptions (from player_traits.py)
        from cricket_manager.systems.trait_assignment import ALL_PLAYER_TRAITS as ALL_TRAITS
        
        # Handle different change types
        if change_type == 'trait_gained':
            trait_key = change.get('trait', 'Unknown Trait')
            trait_info = ALL_TRAITS.get(trait_key, {})
            display_name = trait_info.get('name', trait_key.replace('_', ' ').title())
            description = trait_info.get('description', '')
            detail = QLabel(f"🎯 New Trait Earned: {display_name}")
            detail.setStyleSheet("font-size: 14px; color: #22C55E; font-weight: bold;")
            layout.addWidget(detail)
            if description:
                desc_label = QLabel(f"   {description}")
                desc_label.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']}; font-style: italic;")
                layout.addWidget(desc_label)
            
        elif change_type == 'trait_lost':
            trait_key = change.get('trait', 'Unknown Trait')
            trait_info = ALL_TRAITS.get(trait_key, {})
            display_name = trait_info.get('name', trait_key.replace('_', ' ').title())
            reason = change.get('reason', 'performance decline')
            detail = QLabel(f"Trait Lost: {display_name}")
            detail.setStyleSheet("font-size: 14px; color: #c62828; font-weight: bold;")
            layout.addWidget(detail)
            reason_label = QLabel(f"Reason: {reason}")
            reason_label.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']}; font-style: italic;")
            layout.addWidget(reason_label)
            
        elif change_type == 'trait_level_up':
            trait_key = change.get('trait', 'Unknown Trait')
            trait_info = ALL_TRAITS.get(trait_key, {})
            display_name = trait_info.get('name', trait_key.replace('_', ' ').title())
            description = trait_info.get('description', '')
            old_level = change.get('old_level', 1)
            new_level = change.get('new_level', 2)
            detail = QLabel(f"Trait Upgraded: {display_name} (Level {old_level} → {new_level})")
            detail.setStyleSheet("font-size: 14px; color: #60A5FA; font-weight: bold;")
            layout.addWidget(detail)
            if description:
                desc_label = QLabel(f"   {description}")
                desc_label.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']}; font-style: italic;")
                layout.addWidget(desc_label)
            
        elif change_type == 'trait_level_down':
            trait_key = change.get('trait', 'Unknown Trait')
            trait_info = ALL_TRAITS.get(trait_key, {})
            display_name = trait_info.get('name', trait_key.replace('_', ' ').title())
            old_level = change.get('old_level', 2)
            new_level = change.get('new_level', 1)
            detail = QLabel(f"Trait Downgraded: {display_name} (Level {old_level} → {new_level})")
            detail.setStyleSheet("font-size: 14px; color: #ef6c00; font-weight: bold;")
            layout.addWidget(detail)
            
        else:
            # Standard skill change
            changes_text = []
            if 'old_batting' in change and 'new_batting' in change:
                diff = change['new_batting'] - change['old_batting']
                if diff != 0:
                    color = '#22C55E' if diff > 0 else '#c62828'
                    changes_text.append(f"Batting: {change['old_batting']} → {change['new_batting']} (<span style='color:{color}'>{'+' if diff > 0 else ''}{diff}</span>)")
            
            if 'old_bowling' in change and 'new_bowling' in change:
                diff = change['new_bowling'] - change['old_bowling']
                if diff != 0:
                    color = '#22C55E' if diff > 0 else '#c62828'
                    changes_text.append(f"Bowling: {change['old_bowling']} → {change['new_bowling']} (<span style='color:{color}'>{'+' if diff > 0 else ''}{diff}</span>)")
            
            if changes_text:
                changes_label = QLabel(" • ".join(changes_text))
                changes_label.setTextFormat(Qt.TextFormat.RichText)
                changes_label.setStyleSheet(f"font-size: 13px; color: {COLORS['text_secondary']};")
                layout.addWidget(changes_label)
        
        widget.setLayout(layout)
        return widget
    
    def create_tier_changes_tab(self):
        """Create tier changes tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Promoted section
        promoted = self.season_data.get('tier_promoted', [])
        if promoted:
            promoted_title = QLabel("⬆️ Promoted to Higher Tier")
            promoted_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50;")
            layout.addWidget(promoted_title)
            
            for team, old_tier, new_tier in promoted:
                team_label = QLabel(f"  {team}: Tier {old_tier} → Tier {new_tier}")
                team_label.setStyleSheet("font-size: 14px; padding: 5px;")
                layout.addWidget(team_label)
        
        # Relegated section
        relegated = self.season_data.get('tier_relegated', [])
        if relegated:
            relegated_title = QLabel("⬇️ Relegated to Lower Tier")
            relegated_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #f44336;")
            layout.addWidget(relegated_title)
            
            for team, old_tier, new_tier in relegated:
                team_label = QLabel(f"  {team}: Tier {old_tier} → Tier {new_tier}")
                team_label.setStyleSheet("font-size: 14px; padding: 5px;")
                layout.addWidget(team_label)
        
        if not promoted and not relegated:
            empty_label = QLabel("No tier changes this season")
            empty_label.setStyleSheet(f"font-size: 18px; color: {COLORS['text_secondary']}; padding: 50px;")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(empty_label)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_transfers_tab(self):
        """Create Transfers tab: players moved from Test nations to associate nations (poor Test record)."""
        transfers = self.season_data.get('transfers', [])
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        
        title_frame = QFrame()
        title_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['primary']};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        title_layout = QHBoxLayout()
        title_label = QLabel("🔄 Transfers to Associate Nations")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        title_layout.addWidget(title_label)
        count_label = QLabel(f"{len(transfers)} players transferred (Test/T20 poor averages by role)")
        count_label.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.9);")
        title_layout.addStretch()
        title_layout.addWidget(count_label)
        title_frame.setLayout(title_layout)
        layout.addWidget(title_frame)
        
        if not transfers:
            empty_frame = QFrame()
            empty_frame.setStyleSheet(f"QFrame {{ background-color: {COLORS.get('bg_secondary', '#111827')}; border-radius: 8px; padding: 50px; }}")
            empty_layout = QVBoxLayout()
            empty_label = QLabel(
                "No transfers this season.\n\n"
                "Test: 20+ matches — batters bat avg < 20, bowlers ball avg > 50.\n"
                "T20: 40+ matches — non-bowlers bat avg < 15, non-batters ball avg > 40.\n"
                "Return to original team: Test bat > 42 & T20 bat > 32 (batters); Test ball < 28 & T20 ball < 24 (bowlers).\n"
                "Associate nations have no squad limit."
            )
            empty_label.setStyleSheet(f"font-size: 14px; color: {COLORS['text_secondary']};")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setWordWrap(True)
            empty_layout.addWidget(empty_label)
            empty_frame.setLayout(empty_layout)
            layout.addWidget(empty_frame)
        else:
            table = QTableWidget()
            table.setColumnCount(8)
            table.setHorizontalHeaderLabels(["Player", "Role", "From", "To", "Format", "Reason", "Bat Avg", "Ball Avg"])
            table.setRowCount(len(transfers))
            table.setStyleSheet(f"""
                QTableWidget {{ background-color: #111827; border: 1px solid {COLORS.get('border_light', '#ddd')}; border-radius: 8px; gridline-color: #334155; font-size: 13px; }}
                QHeaderView::section {{ background-color: {COLORS['primary']}; color: white; padding: 10px; font-weight: bold; border: none; }}
            """)
            table.verticalHeader().setVisible(False)
            table.setAlternatingRowColors(True)
            table.horizontalHeader().setStretchLastSection(True)
            for row, tr in enumerate(transfers):
                table.setItem(row, 0, QTableWidgetItem(tr.get('player', 'N/A')))
                table.setItem(row, 1, QTableWidgetItem(tr.get('role', '')))
                table.setItem(row, 2, QTableWidgetItem(tr.get('from_team', 'N/A')))
                table.setItem(row, 3, QTableWidgetItem(tr.get('to_team', 'N/A')))
                table.setItem(row, 4, QTableWidgetItem(tr.get('format', '')))
                table.setItem(row, 5, QTableWidgetItem(tr.get('reason', '')))
                bat_avg = tr.get('bat_avg')
                table.setItem(row, 6, QTableWidgetItem(f"{bat_avg:.1f}" if isinstance(bat_avg, (int, float)) else str(bat_avg or '')))
                ball_avg = tr.get('ball_avg')
                table.setItem(row, 7, QTableWidgetItem(f"{ball_avg:.1f}" if isinstance(ball_avg, (int, float)) else str(ball_avg or '')))
            layout.addWidget(table)
        
        widget.setLayout(layout)
        return widget
    
    def create_worldcup_tab(self):
        """Create World Cup results tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        wc_data = self.season_data.get('world_cup', {})
        
        # Champion
        champion_frame = QFrame()
        champion_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-radius: 10px;
                padding: 30px;
            }}
        """)
        champion_layout = QVBoxLayout()
        
        champion_title = QLabel("🏆 WORLD CUP CHAMPION 🏆")
        champion_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFD700;")
        champion_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        champion_layout.addWidget(champion_title)
        
        champion = wc_data.get('winner', 'N/A')
        champion_name = QLabel(champion)
        champion_name.setStyleSheet("font-size: 36px; font-weight: bold; color: #4CAF50;")
        champion_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        champion_layout.addWidget(champion_name)
        
        champion_frame.setLayout(champion_layout)
        layout.addWidget(champion_frame)
        
        # Runner-up
        runner_frame = QFrame()
        runner_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-radius: 10px;
                padding: 20px;
            }}
        """)
        runner_layout = QVBoxLayout()
        
        runner_title = QLabel("🥈 Runner-up")
        runner_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #C0C0C0;")
        runner_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        runner_layout.addWidget(runner_title)
        
        runner = wc_data.get('runner_up', 'N/A')
        runner_name = QLabel(runner)
        runner_name.setStyleSheet("font-size: 28px; font-weight: bold;")
        runner_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        runner_layout.addWidget(runner_name)
        
        runner_frame.setLayout(runner_layout)
        layout.addWidget(runner_frame)
        
        # Semi-finalists
        semi = wc_data.get('semi_finalists', [])
        if semi:
            semi_title = QLabel("Semi-Finalists")
            semi_title.setStyleSheet("font-size: 18px; font-weight: bold;")
            semi_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(semi_title)
            
            for team in semi:
                team_label = QLabel(team)
                team_label.setStyleSheet(f"font-size: 14px; color: {COLORS['text_secondary']};")
                team_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(team_label)
        
        # TOP PERFORMERS - Top 20 Batters and Bowlers
        format_type = self.season_data.get('format', 'T20')
        top_performers = self.get_world_cup_top_performers(format_type)
        
        if top_performers['batters'] or top_performers['bowlers']:
            performers_frame = QFrame()
            performers_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['bg_secondary']};
                    border-radius: 10px;
                    padding: 20px;
                }}
            """)
            performers_layout = QHBoxLayout()
            performers_layout.setSpacing(20)
            
            # Top 20 Batters
            if top_performers['batters']:
                batters_widget = self.create_top_performers_table(
                    "🏏 Top 20 Batters", 
                    top_performers['batters'],
                    ['Player', 'Team', 'Runs', 'Avg', 'SR']
                )
                performers_layout.addWidget(batters_widget, 1)
            
            # Top 20 Bowlers
            if top_performers['bowlers']:
                bowlers_widget = self.create_top_performers_table(
                    "⚾ Top 20 Bowlers", 
                    top_performers['bowlers'],
                    ['Player', 'Team', 'Wkts', 'Avg', 'Econ']
                )
                performers_layout.addWidget(bowlers_widget, 1)
            
            performers_frame.setLayout(performers_layout)
            layout.addWidget(performers_frame)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def get_world_cup_top_performers(self, format_type):
        """Get top 20 batters and bowlers from World Cup results"""
        wc_data = self.season_data.get('world_cup', {})
        
        # Get top batters from World Cup results
        batters = []
        for batter in wc_data.get('top_batters', []):
            batters.append([
                batter.get('name', ''),
                batter.get('team', ''),
                str(batter.get('runs', 0)),
                str(batter.get('avg', 0)),
                str(batter.get('sr', 0))
            ])
        
        # Get top bowlers from World Cup results
        bowlers = []
        for bowler in wc_data.get('top_bowlers', []):
            bowlers.append([
                bowler.get('name', ''),
                bowler.get('team', ''),
                str(bowler.get('wickets', 0)),
                str(bowler.get('avg', 0)),
                str(bowler.get('econ', 0))
            ])
        
        return {'batters': batters, 'bowlers': bowlers}
    
    def create_top_performers_table(self, title, data, columns):
        """Create a table for top performers"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #EAF1FF;")
        layout.addWidget(title_label)
        
        # Table
        table = QTableWidget()
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)
        table.setRowCount(min(len(data), 20))
        
        # Style
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: #111827;
                border: 1px solid {COLORS['border_light']};
                gridline-color: {COLORS['border_light']};
                font-size: 12px;
            }}
            QHeaderView::section {{
                background-color: {COLORS['primary']};
                color: white;
                padding: 8px;
                font-weight: bold;
                border: none;
            }}
        """)
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        
        # Populate
        for row, item in enumerate(data[:20]):
            for col, value in enumerate(item):
                table.setItem(row, col, QTableWidgetItem(str(value)))
            table.setRowHeight(row, 30)
        
        layout.addWidget(table)
        widget.setLayout(layout)
        return widget
    
    def create_role_conversions_tab(self):
        """Create role conversions tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        conversions = self.season_data.get('role_conversions', {})
        
        if not conversions:
            empty_label = QLabel("No role conversions this season")
            empty_label.setStyleSheet(f"font-size: 18px; color: {COLORS['text_secondary']}; padding: 50px;")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(empty_label)
        else:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            
            content = QWidget()
            content_layout = QVBoxLayout()
            
            for team, players in conversions.items():
                team_label = QLabel(f"{team}")
                team_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2196F3;")
                content_layout.addWidget(team_label)
                
                for player_data in players:
                    raw_player = player_data.get('player', 'Unknown')
                    if hasattr(raw_player, 'name'):
                        player_name = raw_player.name
                    else:
                        player_name = str(raw_player)
                    old_role = player_data.get('old_role', 'Unknown')
                    new_role = player_data.get('new_role', 'Unknown')
                    reason = player_data.get('reason', '')
                    
                    conversion_label = QLabel(f"  {player_name}: {old_role} → {new_role}")
                    conversion_label.setStyleSheet("font-size: 14px; padding: 5px;")
                    content_layout.addWidget(conversion_label)
                    
                    if reason:
                        reason_label = QLabel(f"    Reason: {reason}")
                        reason_label.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']}; padding-left: 10px;")
                        content_layout.addWidget(reason_label)
            
            content_layout.addStretch()
            content.setLayout(content_layout)
            scroll.setWidget(content)
            layout.addWidget(scroll)
        
        widget.setLayout(layout)
        return widget
    
    def create_simple_table_tab(self, title, data, columns):
        """Create an improved table tab with better styling and player profile click"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title with count
        title_frame = QFrame()
        title_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['primary']};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        title_layout = QHBoxLayout()
        
        title_label = QLabel(f"📋 {title}")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        title_layout.addWidget(title_label)
        
        count_label = QLabel(f"{len(data)} players")
        count_label.setStyleSheet("font-size: 14px; color: rgba(255,255,255,0.8);")
        title_layout.addStretch()
        title_layout.addWidget(count_label)
        
        title_frame.setLayout(title_layout)
        layout.addWidget(title_frame)
        
        # Info label
        info_label = QLabel("💡 Click on any player row to view their profile")
        info_label.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']}; padding: 5px; font-style: italic;")
        layout.addWidget(info_label)
        
        if not data:
            empty_frame = QFrame()
            empty_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['bg_secondary']};
                    border-radius: 8px;
                    padding: 50px;
                }}
            """)
            empty_layout = QVBoxLayout()
            empty_label = QLabel(f"No {title.lower()} this season")
            empty_label.setStyleSheet(f"font-size: 18px; color: {COLORS['text_secondary']};")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_layout.addWidget(empty_label)
            empty_frame.setLayout(empty_layout)
            layout.addWidget(empty_frame)
        else:
            # Table with improved styling
            table = QTableWidget()
            table.setColumnCount(len(columns))
            table.setHorizontalHeaderLabels(columns)
            table.setRowCount(len(data))
            
            # Enhanced style
            table.setStyleSheet(f"""
                QTableWidget {{
                    background-color: #111827;
                    alternate-background-color: {COLORS['bg_tertiary']};
                    border: 1px solid {COLORS['border_light']};
                    border-radius: 8px;
                    gridline-color: {COLORS['border_light']};
                    font-size: 13px;
                }}
                QTableWidget::item {{
                    padding: 10px;
                    border-bottom: 1px solid #eee;
                }}
                QTableWidget::item:selected {{
                    background-color: {COLORS['primary']};
                    color: white;
                }}
                QTableWidget::item:hover {{
                    background-color: {COLORS['bg_hover']};
                }}
                QHeaderView::section {{
                    background-color: {COLORS['primary']};
                    color: white;
                    padding: 12px 8px;
                    font-weight: bold;
                    font-size: 13px;
                    border: none;
                    border-right: 1px solid rgba(255,255,255,0.2);
                }}
            """)
            
            table.setAlternatingRowColors(True)
            table.horizontalHeader().setStretchLastSection(True)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            table.verticalHeader().setVisible(False)
            table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
            table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Disable editing
            
            # Store data for click handling
            self._table_data = data
            
            # Populate with colored skill values
            for row, item in enumerate(data):
                for col, col_name in enumerate(columns):
                    key = col_name.lower().replace(' ', '_')
                    if key == 'batting':
                        key = 'batting_rating'
                    elif key == 'bowling':
                        key = 'bowling_rating'
                    elif key == 'role':
                        key = 'best_role'
                    value = str(item.get(key, item.get(col_name, 'N/A')))
                    
                    cell = QTableWidgetItem(value)
                    cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    cell.setFlags(cell.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make cell non-editable
                    
                    # Color code skill values
                    if col_name in ['Batting', 'Bowling'] and value.isdigit():
                        skill_val = int(value)
                        if skill_val >= 80:
                            cell.setForeground(QColor('#22C55E'))  # Green for elite
                        elif skill_val >= 65:
                            cell.setForeground(QColor('#1976d2'))  # Blue for good
                        elif skill_val >= 50:
                            cell.setForeground(QColor('#f57c00'))  # Orange for average
                        else:
                            cell.setForeground(QColor('#c62828'))  # Red for low
                    
                    # Bold player name
                    if col_name == 'Player':
                        font = cell.font()
                        font.setBold(True)
                        cell.setFont(font)
                    
                    table.setItem(row, col, cell)
                table.setRowHeight(row, 45)
            
            # Connect double-click to open player profile
            table.cellDoubleClicked.connect(self._on_table_double_click)
            
            layout.addWidget(table)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _on_table_double_click(self, row, col):
        """Handle double-click on table row"""
        self.open_player_profile(row)
    
    def open_player_profile(self, row):
        """Open player profile dialog when row is clicked"""
        if not hasattr(self, '_table_data') or row >= len(self._table_data):
            return
        
        player_data = self._table_data[row]
        player_name = player_data.get('player', player_data.get('name', ''))
        team_name = player_data.get('team', '')
        
        if not player_name or not self.game_engine:
            return
        
        # Find the player and team
        player = None
        team = None
        for t in self.game_engine.all_teams:
            if t.name == team_name:
                team = t
                for p in t.players:
                    if p.name == player_name:
                        player = p
                        break
                # Also check U21 squad
                if not player and hasattr(t, 'u21_squad'):
                    for p in t.u21_squad:
                        if p.name == player_name:
                            player = p
                            break
            if player:
                break
        
        if player and team:
            from cricket_manager.ui.player_profile_dialog import PlayerProfileDialog
            dialog = PlayerProfileDialog(self, player, team, self.game_engine)
            dialog.exec()
