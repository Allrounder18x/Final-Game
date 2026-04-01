"""
Leagues Screen - Modern redesign with standings and simulate season
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QFrame,
    QHeaderView, QMessageBox, QProgressDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from cricket_manager.ui.styles import COLORS, get_tier_color, MAIN_STYLESHEET, apply_windows_dark_title_bar
from cricket_manager.ui.screen_manager import BaseScreen


class LeaguesScreen(BaseScreen):
    """Modern leagues screen with standings"""
    
    def __init__(self, screen_manager=None, game_engine=None):
        super().__init__(screen_manager)
        self.setStyleSheet(MAIN_STYLESHEET)
        self.game_engine = game_engine
        self.current_format = "T20"
        self.current_tier = 1
        self.league_season_view_year = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Controls with tier selector at top
        controls = self.create_controls()
        layout.addWidget(controls)
        
        # Single tier standings table (12 teams)
        self.standings_table = self.create_standings_table()
        layout.addWidget(self.standings_table, 1)
        
        self.setLayout(layout)
        self._populate_league_season_combo()
        self.load_standings()
    
    def create_controls(self):
        """Create control section with tier selector"""
        controls = QFrame()
        controls.setObjectName("leagueControls")
        controls.setStyleSheet(f"""
            QFrame#leagueControls {{
                background: #111827;
                border-bottom: 2px solid {COLORS['border_light']};
                padding: 15px 20px;
            }}
        """)
        
        layout = QHBoxLayout()
        
        combo_style = f"""
            QComboBox {{
                padding: 8px 15px;
                border: 1px solid {COLORS['border_light']};
                border-radius: 5px;
                min-width: 120px;
                font-size: 13px;
                background: #111827;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 25px;
            }}
            QComboBox QAbstractItemView {{
                background: #111827;
                border: 1px solid {COLORS['border_light']};
                selection-background-color: {COLORS['primary']};
                selection-color: white;
                font-size: 13px;
                padding: 4px;
            }}
        """
        
        # Tier selector at top
        tier_label = QLabel("Tier:")
        tier_label.setStyleSheet("font-size: 13px; font-weight: bold;")
        layout.addWidget(tier_label)
        self.tier_combo = QComboBox()
        self.tier_combo.addItems(['Tier 1', 'Tier 2', 'Tier 3', 'Tier 4', 'Tier 5 (U21)'])
        self.tier_combo.setCurrentIndex(self.current_tier - 1)
        self.tier_combo.setStyleSheet(combo_style)
        self.tier_combo.currentIndexChanged.connect(self.on_tier_changed)
        layout.addWidget(self.tier_combo)
        
        layout.addSpacing(20)
        
        # Format selector
        format_label = QLabel("Format:")
        format_label.setStyleSheet("font-size: 13px; font-weight: bold;")
        layout.addWidget(format_label)
        self.format_combo = QComboBox()
        self.format_combo.addItems(['T20', 'ODI', 'Test'])
        self.format_combo.setCurrentText(self.current_format)
        self.format_combo.setStyleSheet(combo_style)
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        layout.addWidget(self.format_combo)
        
        layout.addSpacing(20)
        
        season_label = QLabel("Season:")
        season_label.setStyleSheet("font-size: 13px; font-weight: bold;")
        layout.addWidget(season_label)
        self.league_season_combo = QComboBox()
        self.league_season_combo.setStyleSheet(combo_style)
        self.league_season_combo.currentIndexChanged.connect(self.on_league_season_filter_changed)
        layout.addWidget(self.league_season_combo)
        
        layout.addStretch()
        
        # Simulate Season button
        sim_season_btn = QPushButton("⚡ Simulate Entire Season")
        sim_season_btn.clicked.connect(self.simulate_season)
        sim_season_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: white;
                padding: 12px 25px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['secondary']};
            }}
        """)
        layout.addWidget(sim_season_btn)
        
        controls.setLayout(layout)
        return controls
    
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
        
        # Title section
        title_layout = QVBoxLayout()
        title = QLabel("League Standings")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        title_layout.addWidget(title)
        
        if self.game_engine:
            self.header_subtitle = QLabel(
                f"Season {self.game_engine.current_season} • Year {self.game_engine.current_year}"
            )
            self.header_subtitle.setStyleSheet("font-size: 14px; color: white;")
            title_layout.addWidget(self.header_subtitle)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        header.setLayout(layout)
        return header
    
    def create_standings_table(self):
        """Create single standings table for selected tier (12 teams)"""
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
    
    def on_tier_changed(self, index):
        """Handle tier change"""
        self.current_tier = index + 1
        print(f"[Leagues] Tier filter changed to: Tier {self.current_tier}")
        self.load_standings()
    
    def on_format_changed(self, format_type):
        """Handle format change"""
        if not format_type:
            return
        self.current_format = format_type
        print(f"[Leagues] Format filter changed to: {self.current_format}")
        self.load_standings()
    
    def _populate_league_season_combo(self):
        """Fill season/year filter: current campaign plus completed years from snapshots."""
        if not hasattr(self, "league_season_combo"):
            return
        saved_year = self.league_season_view_year
        self.league_season_combo.blockSignals(True)
        self.league_season_combo.clear()
        self.league_season_combo.addItem("Current season", None)
        history = []
        if self.game_engine:
            history = list(getattr(self.game_engine, "league_standings_history", None) or [])
        years = sorted({e.get("year") for e in history if e.get("year") is not None}, reverse=True)
        for y in years:
            ent = next((e for e in history if e.get("year") == y), None)
            sn = ent.get("season", "?") if ent else "?"
            self.league_season_combo.addItem(f"{y} (Season {sn} ended)", y)
        idx = 0
        if saved_year is not None:
            for i in range(self.league_season_combo.count()):
                if self.league_season_combo.itemData(i) == saved_year:
                    idx = i
                    break
        else:
            # Default: last completed calendar year = current in-game year minus 1
            target = None
            if self.game_engine is not None:
                cy = getattr(self.game_engine, "current_year", None)
                if cy is not None and cy > 2000:
                    target = cy - 1
            if target is not None:
                for i in range(self.league_season_combo.count()):
                    if self.league_season_combo.itemData(i) == target:
                        idx = i
                        break
                else:
                    best_i = 0
                    best_y = None
                    for i in range(1, self.league_season_combo.count()):
                        y = self.league_season_combo.itemData(i)
                        if y is not None and y <= target:
                            if best_y is None or y > best_y:
                                best_y = y
                                best_i = i
                    if best_y is not None:
                        idx = best_i
                    elif self.league_season_combo.count() > 1:
                        idx = 1
            elif self.league_season_combo.count() > 1:
                idx = 1
        self.league_season_combo.setCurrentIndex(idx)
        self.league_season_view_year = self.league_season_combo.currentData()
        self.league_season_combo.blockSignals(False)
    
    def on_league_season_filter_changed(self, _index=None):
        """Reload table for selected calendar year or current in-progress campaign."""
        if not hasattr(self, "league_season_combo"):
            return
        self.league_season_view_year = self.league_season_combo.currentData()
        self.load_standings()
    
    def refresh_standings(self):
        """Refresh standings display (called externally after fixture changes)"""
        self.load_standings()
    
    def refresh_data(self):
        """Alias for refresh_standings for auto-refresh compatibility"""
        self._populate_league_season_combo()
        self.load_standings()
    
    def _update_league_header_subtitle(self):
        if not getattr(self, "header_subtitle", None) or not self.game_engine:
            return
        if self.league_season_view_year is None:
            self.header_subtitle.setText(
                f"Season {self.game_engine.current_season} • Year {self.game_engine.current_year}"
            )
        else:
            self.header_subtitle.setText(
                f"Year {self.league_season_view_year} — table shows that season's league totals (tiers as at year end)"
            )
    
    def load_standings(self):
        """Load standings for current tier; optional season filter for year-by-year totals."""
        if not self.game_engine:
            return
        
        if not hasattr(self, 'standings_table'):
            return
        
        from PyQt6.QtGui import QColor
        
        try:
            self._update_league_header_subtitle()
            yf = self.league_season_view_year
            print(f"[Leagues] Loading standings - Format: {self.current_format}, Tier: {self.current_tier}, Season filter: {yf}")
            
            self.standings_table.setHorizontalHeaderLabels([
                "Pos", "Team", "Played", "Won", "Lost", "Drawn", "Points", "NRR", "Form"
            ])
            
            getter = getattr(self.game_engine, "get_league_season_table_rows", None)
            if not getter:
                print("[Leagues] WARNING: game engine missing get_league_season_table_rows")
                self.standings_table.clearContents()
                self.standings_table.setRowCount(0)
                return
            
            rows = getter(self.current_format, self.current_tier, yf)
            print(f"[Leagues] {len(rows)} rows for {self.current_format} Tier {self.current_tier}")
            
            if len(rows) == 0:
                self.standings_table.clearContents()
                self.standings_table.setRowCount(0)
                return
            
            self.standings_table.clearContents()
            self.standings_table.setRowCount(len(rows))
            n_rows = len(rows)
            
            for row, r in enumerate(rows):
                name = r["team_name"]
                stats = r["stats"]
                is_u21_row = self.current_tier == 5
                display_name = f"{name} U21" if is_u21_row else name
                
                pos_item = QTableWidgetItem(str(row + 1))
                pos_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                pos_item.setFont(QFont('Arial', 12, QFont.Weight.Bold))
                
                if row == 0:
                    pos_item.setForeground(QColor('#FFD700'))
                elif row == 1:
                    pos_item.setForeground(QColor('#C0C0C0'))
                elif not is_u21_row and row <= 1 and self.current_tier > 1:
                    pos_item.setBackground(QColor('#d4edda'))
                elif not is_u21_row and row >= n_rows - 2 and self.current_tier < 4:
                    pos_item.setBackground(QColor('#f8d7da'))
                
                self.standings_table.setItem(row, 0, pos_item)
                
                team_item = QTableWidgetItem(display_name)
                team_item.setFont(QFont('Arial', 12))
                ut = getattr(self.game_engine, "user_team", None)
                if ut is not None and ut.name == name:
                    team_item.setBackground(QColor('#fff3cd'))
                self.standings_table.setItem(row, 1, team_item)
                
                self.standings_table.setItem(row, 2, self.create_center_item(str(stats.get('matches_played', 0))))
                
                won_item = self.create_center_item(str(stats.get('wins', 0)))
                won_item.setForeground(QColor('#27ae60'))
                self.standings_table.setItem(row, 3, won_item)
                
                lost_item = self.create_center_item(str(stats.get('losses', 0)))
                lost_item.setForeground(QColor('#e74c3c'))
                self.standings_table.setItem(row, 4, lost_item)
                
                self.standings_table.setItem(row, 5, self.create_center_item(str(stats.get('draws', 0))))
                
                points_item = self.create_center_item(str(stats.get('points', 0)))
                points_item.setFont(QFont('Arial', 12, QFont.Weight.Bold))
                points_item.setForeground(QColor(COLORS['primary']))
                self.standings_table.setItem(row, 6, points_item)
                
                nrr_val = stats.get('nrr')
                if nrr_val is None:
                    nrr_text = "—"
                    nrr_item = self.create_center_item(nrr_text)
                else:
                    nrr_text = f"+{nrr_val:.3f}" if nrr_val >= 0 else f"{nrr_val:.3f}"
                    nrr_item = self.create_center_item(nrr_text)
                    nrr_item.setForeground(QColor('#27ae60') if nrr_val >= 0 else QColor('#e74c3c'))
                self.standings_table.setItem(row, 7, nrr_item)
                
                if yf is not None:
                    form_item = QTableWidgetItem("—")
                else:
                    form_item = QTableWidgetItem(self.get_team_form(stats))
                form_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                form_item.setFont(QFont('Arial', 11, QFont.Weight.Bold))
                self.standings_table.setItem(row, 8, form_item)
                
                self.standings_table.setRowHeight(row, 45)
            
            self.standings_table.viewport().update()
            
        except Exception as e:
            print(f"[Leagues] ERROR loading standings: {e}")
            import traceback
            traceback.print_exc()
    
    def get_team_form(self, stats, _team_name=None):
        """Approximate recent form from win rate over the displayed match totals (current season view)."""
        # For now, generate based on win percentage
        matches = stats.get('matches_played', 0)
        if matches == 0:
            return "-"
        
        wins = stats.get('wins', 0)
        win_pct = wins / matches if matches > 0 else 0
        
        # Generate form string (W = Win, L = Loss, D = Draw)
        form_chars = []
        recent_matches = min(5, matches)
        
        for i in range(recent_matches):
            import random
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
    
    def simulate_season(self):
        """Simulate entire season for ALL formats"""
        # Count remaining matches for ALL formats
        total_remaining = 0
        format_details = []
        for fmt in ['T20', 'ODI', 'Test']:
            fixtures = self.game_engine.get_fixtures(fmt)
            remaining = sum(1 for f in fixtures if not f.get('completed', False))
            total_remaining += remaining
            format_details.append(f"{fmt}: {remaining}")
        
        reply = QMessageBox.question(
            self,
            "Simulate Season",
            f"Simulate entire season for ALL formats?\n\n"
            f"This will:\n"
            f"• Simulate {total_remaining} remaining matches across all formats\n"
            f"• {', '.join(format_details)}\n"
            f"• Skip matches already played\n"
            f"• Process player development\n"
            f"• Handle promotions/relegations\n"
            f"• Advance to next season\n\n"
            f"Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Show progress dialog
                progress = QProgressDialog("Simulating season...", "Cancel", 0, 100, self)
                progress.setWindowModality(Qt.WindowModality.WindowModal)
                progress.setMinimumDuration(0)
                progress.setValue(1)
                apply_windows_dark_title_bar(progress)
                
                # Calculate total matches across all formats
                total_all_formats = 0
                for fmt in ['T20', 'ODI', 'Test']:
                    fixtures = self.game_engine.get_fixtures(fmt)
                    remaining = sum(1 for f in fixtures if not f.get('completed', False))
                    total_all_formats += remaining
                
                # Track overall progress
                total_simulated = 0
                
                # Ensure all teams have full squads before simulating
                self._fill_u21_squads()
                for team in self.game_engine.all_teams:
                    if getattr(team, "is_domestic", False):
                        continue
                    if len(team.players) < 15:
                        self.game_engine.fill_national_squad_from_domestic_and_u21(team, 20)
                
                # Simulate all formats with progress callback
                all_summaries = {}
                for i, fmt in enumerate(['T20', 'ODI', 'Test']):
                    fixtures = self.game_engine.get_fixtures(fmt)
                    remaining = sum(1 for f in fixtures if not f.get('completed', False))
                    
                    def make_progress_callback(format_name, remaining_count, current_total):
                        def callback(message, percent):
                            nonlocal total_simulated
                            # Calculate overall progress (0-100)
                            overall_progress = int((current_total + (percent / 100) * remaining_count) / total_all_formats * 100)
                            progress.setLabelText(f"[{format_name}] {message}")
                            progress.setValue(max(1, min(99, overall_progress)))
                            # Process events to update UI
                            from PyQt6.QtCore import QCoreApplication
                            QCoreApplication.processEvents()
                        return callback
                    
                    progress_callback = make_progress_callback(fmt, remaining, total_simulated)
                    # Only age players on the final format (Test)
                    should_age = (i == 2)
                    summary = self.game_engine.simulate_season(fmt, headless=True, progress_callback=progress_callback, skip_aging=not should_age)
                    all_summaries[fmt] = summary
                    total_simulated += remaining
                    progress.setValue(int(total_simulated / total_all_formats * 100))
                
                # Simulate U21 matches
                progress.setLabelText("Simulating U21 matches...")
                progress.setValue(85)
                all_u21_matches = []
                for fmt in ['T20', 'ODI', 'Test']:
                    u21_matches = self.game_engine.simulate_youth_matches(fmt)
                    all_u21_matches.extend(u21_matches)
                progress.setValue(90)
                print(f"[Leagues] Simulated {len(all_u21_matches)} U21 matches")
                
                progress.setLabelText("Processing season completion...")
                progress.setValue(92)
                
                # Complete season for all formats
                all_completion_data = {}
                for i, fmt in enumerate(['T20', 'ODI', 'Test']):
                    should_increment = (i == 2)  # Only increment season on last format
                    should_develop = (i == 2)    # Only run development on last format (Test)
                    completion_data = self.game_engine.complete_season(fmt, increment_season=should_increment, skip_development=not should_develop)
                    all_completion_data[fmt] = completion_data
                
                progress.setValue(95)
                
                # Prepare season summary with matches from all formats
                all_matches = []
                total_matches = 0
                total_youth = len(all_u21_matches)  # Count U21 matches as youth matches
                
                for fmt, summary in all_summaries.items():
                    total_matches += summary.get('total_matches', 0)
                    all_matches.extend(summary.get('matches', []))
                
                # Add U21 matches to total matches count
                total_matches += len(all_u21_matches)
                
                # Role conversions run at end of each format's simulate_season; merge all three
                # so the summary is not empty when changes happened in T20/ODI only (summary was Test-only).
                merged_role_conversions = {}
                for _fmt in ('T20', 'ODI', 'Test'):
                    _s = all_summaries.get(_fmt) or {}
                    for team_name, convs in (_s.get('role_conversions') or {}).items():
                        merged_role_conversions.setdefault(team_name, []).extend(list(convs))
                
                last_sim_summary = all_summaries.get('Test') or {}
                season_summary = {
                    'season': self.game_engine.current_season - 1,
                    'year': self.game_engine.current_year - 1,
                    'format': 'All Formats',
                    'total_matches': total_matches,
                    'youth_matches': total_youth,
                    'retirements': self.game_engine.season_retirements,
                    'promotions': self.game_engine.season_promotions,
                    'skill_changes': self.game_engine.season_changes,
                    'role_conversions': merged_role_conversions,
                    'news_items': last_sim_summary.get('news_items', []),
                    'world_cup': last_sim_summary.get('world_cup'),
                    'tier_promoted': completion_data.get('tier_promoted', []),
                    'tier_relegated': completion_data.get('tier_relegated', []),
                    'transfers': getattr(self.game_engine, 'season_transfers', []),
                    'matches': []
                }
                
                # Collect matches with scorecards from all formats
                for match in all_matches:
                    # Add scorecard from match_scorecards if available
                    if 'result' in match:
                        scorecard_key = f"{match['home']}_vs_{match['away']}_{match['format']}_S{season_summary['season']}"
                        if scorecard_key in self.game_engine.match_scorecards:
                            match['scorecard'] = self.game_engine.match_scorecards[scorecard_key]
                        elif 'scorecard' in match['result']:
                            match['scorecard'] = match['result']['scorecard']
                    season_summary['matches'].append(match)
                
                # Add U21 matches to season summary
                for match in all_u21_matches:
                    season_summary['matches'].append(match)
                    season_summary['youth_matches'] += 1
                
                progress.setValue(100)
                progress.close()
                
                # Show season summary dialog (Continue to Next Season adds 5 training points)
                from cricket_manager.ui.season_summary_view import SeasonSummaryDialog
                summary_dialog = SeasonSummaryDialog(season_summary, self)
                summary_dialog.exec()
                
                # Refresh Training tab so the new 5 training points are shown
                if self.screen_manager:
                    training_screen = self.screen_manager.screens.get("Training")
                    if training_screen and hasattr(training_screen, 'refresh_data'):
                        training_screen.refresh_data()
                
                # Fill U21 squads to 16 players for all teams
                self._fill_u21_squads()
                
                # Reload standings (season list includes completed years)
                self._populate_league_season_combo()
                self.load_standings()
                
                # Refresh fixtures screen (use refresh_fixtures to rebuild UI including WC button name)
                if self.screen_manager:
                    fixtures_screen = self.screen_manager.screens.get("Fixtures")
                    if fixtures_screen and hasattr(fixtures_screen, 'refresh_fixtures'):
                        fixtures_screen.refresh_fixtures()
                    elif fixtures_screen and hasattr(fixtures_screen, 'load_fixtures'):
                        fixtures_screen.load_fixtures()
                
                # Refresh statistics view
                if self.screen_manager:
                    stats_screen = self.screen_manager.screens.get("Statistics")
                    if stats_screen and hasattr(stats_screen, 'load_statistics'):
                        stats_screen.load_statistics()
                
            except Exception as e:
                import traceback
                traceback.print_exc()
                QMessageBox.critical(self, "Error", f"Failed to simulate season: {str(e)}")
    
    def _fill_u21_squads(self):
        """Ensure every team has a full U21 squad (20, balanced roles) before simulating."""
        if not self.game_engine:
            return
        
        from cricket_manager.systems.youth_system import U21_SQUAD_TARGET
        print(f"[Leagues] Ensuring U21 squads are {U21_SQUAD_TARGET} players per team...")
        
        ys = self.game_engine.youth_system
        comps = getattr(self.game_engine.domestic_system, 'competitions_by_nation', None) or {}
        total_generated = 0
        for team in self.game_engine.all_teams:
            if not hasattr(team, 'u21_squad') or team.u21_squad is None:
                team.u21_squad = []
            added = ys.ensure_u21_squad_strength(team, U21_SQUAD_TARGET)
            total_generated += len(added)
            if added and comps:
                for np in added:
                    from cricket_manager.utils.domestic_affiliations import pick_affiliations_for_nation
                    t20, odi = pick_affiliations_for_nation(team.name, np.name, comps)
                    np.domestic_t20_club_name = t20
                    np.domestic_odi_fc_club_name = odi
            print(f"[Leagues] {team.name}: U21 count {len(team.u21_squad)}")
        
        print(f"[Leagues] Total U21 players added this fill: {total_generated}")
