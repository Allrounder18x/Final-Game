"""
World Cup History Screen - Track all World Cup tournaments across seasons
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QFrame, QScrollArea,
    QHeaderView, QTabWidget, QGroupBox, QDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from collections import Counter

from cricket_manager.ui.styles import COLORS, MAIN_STYLESHEET
from cricket_manager.ui.screen_manager import BaseScreen


class WorldCupResultsScreen(BaseScreen):
    """World Cup History - Track all tournaments across seasons"""
    
    def __init__(self, screen_manager=None, game_engine=None):
        super().__init__(screen_manager)
        self.setStyleSheet(MAIN_STYLESHEET)
        self.game_engine = game_engine
        self._wc_history_data = []  # store for click handler
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI with World Cup history"""
        print("[WC View] init_ui called")
        
        # Use existing layout or create new one
        if self.layout() is not None:
            layout = self.layout()
        else:
            layout = QVBoxLayout()
            layout.setSpacing(0)
            layout.setContentsMargins(0, 0, 0, 0)
        
        # Compact header matching Stats tab gradient
        header_frame = QFrame()
        header_frame.setFixedHeight(50)
        header_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary']}, stop:1 {COLORS['secondary']});
                padding: 0px 20px;
            }}
        """)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(10, 0, 10, 0)
        
        title = QLabel("🏆 World Cup History")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        header_layout.addWidget(title)
        
        subtitle = QLabel("Click any row to view final scorecard & tournament stats")
        subtitle.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.8); margin-left: 10px;")
        header_layout.addWidget(subtitle)
        header_layout.addStretch()
        
        header_frame.setLayout(header_layout)
        layout.addWidget(header_frame)
        
        # Check if we have World Cup history
        wc_history = self.get_wc_history()
        
        if not wc_history:
            placeholder = QLabel("No World Cup results yet.\n\nWorld Cups rotate every 4 seasons:\n• T20 World Cup  •  ODI World Cup  •  U19 World Cup  •  Associate World Cup\n\nSimulate seasons to see results!")
            placeholder.setStyleSheet(f"font-size: 14px; color: {COLORS['text_secondary']}; padding: 40px;")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(placeholder, 1)
            self.setLayout(layout)
            return
        
        # Create tabs for different World Cup types
        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: none; background-color: {COLORS['bg_primary']}; }}
            QTabBar::tab {{
                background-color: {COLORS['bg_tertiary']}; color: #EAF1FF;
                padding: 10px 22px; margin-right: 3px;
                border-top-left-radius: 5px; border-top-right-radius: 5px;
                font-size: 13px; font-weight: 700;
            }}
            QTabBar::tab:selected {{ background-color: {COLORS['primary']}; color: white; }}
        """)
        
        tabs.addTab(self.create_history_tab(wc_history, 'T20'), "🏏 T20 World Cup")
        tabs.addTab(self.create_history_tab(wc_history, 'ODI'), "⚪ ODI World Cup")
        tabs.addTab(self.create_history_tab(wc_history, 'U19'), "⭐ U19 World Cup")
        tabs.addTab(self.create_history_tab(wc_history, 'Associate'), "🌍 Associate World Cup")
        
        layout.addWidget(tabs, 1)
        
        if self.layout() is None:
            self.setLayout(layout)
    
    def get_wc_history(self):
        if not self.game_engine:
            return []
        history = getattr(self.game_engine, 'world_cup_history', [])
        print(f"[WC View] Found {len(history)} World Cup records")
        return history
    
    def create_history_tab(self, wc_history, wc_type):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"border: none; background-color: {COLORS['bg_primary']};")
        
        content = QWidget()
        content.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 15, 20, 15)
        
        type_history = [h for h in wc_history if h.get('tournament', '').startswith(wc_type)]
        
        if not type_history:
            no_data = QLabel(f"No {wc_type} World Cup history yet.")
            no_data.setStyleSheet(f"font-size: 14px; color: {COLORS['text_secondary']}; padding: 40px;")
            no_data.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(no_data)
        else:
            type_history.sort(key=lambda x: x.get('season', 0), reverse=True)
            self._wc_history_data = type_history  # store for click handler
            
            table = QTableWidget()
            table.setColumnCount(6)
            table.setHorizontalHeaderLabels(['Season', 'Year', 'Winner', 'Runner-up', 'Final Score', 'Host'])
            table.setRowCount(len(type_history))
            table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            table.verticalHeader().setVisible(False)
            
            table.setStyleSheet(f"""
                QTableWidget {{ border: none; background-color: #111827; gridline-color: {COLORS['border_light']}; font-size: 13px; }}
                QTableWidget::item {{ padding: 10px 8px; border-bottom: 1px solid {COLORS['border_light']}; }}
                QTableWidget::item:selected {{ background-color: {COLORS['highlight_blue']}; }}
                QHeaderView::section {{ background-color: {COLORS['primary']}; color: white; padding: 10px 8px; border: none; font-weight: bold; font-size: 13px; }}
            """)
            
            header = table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
            table.setColumnWidth(0, 70)
            table.setColumnWidth(1, 70)
            table.setColumnWidth(5, 110)
            
            for row, wc in enumerate(type_history):
                season_item = QTableWidgetItem(str(wc.get('season', 'N/A')))
                season_item.setFont(QFont('Arial', 11, QFont.Weight.Bold))
                season_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row, 0, season_item)
                
                year_item = QTableWidgetItem(str(wc.get('year', 'N/A')))
                year_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row, 1, year_item)
                
                winner_item = QTableWidgetItem(f"🏆 {wc.get('winner', 'N/A')}")
                winner_item.setFont(QFont('Arial', 11, QFont.Weight.Bold))
                winner_item.setForeground(Qt.GlobalColor.darkGreen)
                table.setItem(row, 2, winner_item)
                
                runner_item = QTableWidgetItem(f"🥈 {wc.get('runner_up', 'N/A')}")
                runner_item.setForeground(Qt.GlobalColor.darkGray)
                table.setItem(row, 3, runner_item)
                
                final_score = wc.get('final_score', 'N/A') or 'N/A'
                table.setItem(row, 4, QTableWidgetItem(final_score))
                
                host_item = QTableWidgetItem(wc.get('host', 'Various'))
                host_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row, 5, host_item)
                
                table.setRowHeight(row, 44)
            
            # Make rows clickable
            table.cellDoubleClicked.connect(lambda r, c: self._on_wc_row_clicked(type_history, r))
            
            # Hint label
            hint = QLabel("💡 Double-click any row to view final scorecard and top 20 batters/bowlers")
            hint.setStyleSheet(f"font-size: 11px; color: {COLORS['text_secondary']}; padding: 4px 0;")
            layout.addWidget(hint)
            layout.addWidget(table)
            
            # Stats summary
            stats_frame = self.create_stats_summary(type_history, wc_type)
            layout.addWidget(stats_frame)
        
        layout.addStretch()
        content.setLayout(layout)
        scroll.setWidget(content)
        return scroll
    
    def _on_wc_row_clicked(self, history_list, row):
        """Show final scorecard + top 20 batters/bowlers for the clicked WC."""
        if row < 0 or row >= len(history_list):
            return
        wc = history_list[row]
        wc_name = wc.get('tournament', 'World Cup')
        winner = wc.get('winner', 'N/A')
        host = wc.get('host', 'Various')
        season = wc.get('season', '?')
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"{wc_name} - Season {season}")
        dialog.setMinimumSize(950, 700)
        dlayout = QVBoxLayout()
        
        # Title
        title_lbl = QLabel(f"🏆 {wc_name} (Season {season}) — Champion: {winner}  |  Host: {host}")
        title_lbl.setStyleSheet(f"font-size: 17px; font-weight: bold; color: {COLORS['primary']}; padding: 8px;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dlayout.addWidget(title_lbl)
        
        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabBar::tab {{ padding: 8px 18px; font-weight: bold; }}
            QTabBar::tab:selected {{ background: {COLORS['primary']}; color: white; }}
        """)
        
        # --- Tab 1: Final Scorecard ---
        final_sc = wc.get('final_scorecard', {})
        if final_sc and 'innings' in final_sc:
            sc_widget = self._build_scorecard_widget(final_sc)
            tabs.addTab(sc_widget, "📋 Final Scorecard")
        else:
            no_sc = QLabel("Final scorecard not available for this tournament.")
            no_sc.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_sc.setStyleSheet("padding: 30px; font-size: 14px; color: #888;")
            tabs.addTab(no_sc, "📋 Final Scorecard")
        
        # --- Extract player stats from all WC scorecards ---
        all_scorecards = wc.get('wc_scorecards', [])
        player_stats = self._extract_player_stats(all_scorecards)
        
        # --- Tab 2: Top 20 Batters ---
        batters = sorted([(n, s) for n, s in player_stats.items() if s['runs'] > 0],
                         key=lambda x: x[1]['runs'], reverse=True)[:20]
        bat_table = self._build_batters_table(batters)
        tabs.addTab(bat_table, "🏏 Top 20 Batters")
        
        # --- Tab 3: Top 20 Bowlers ---
        bowlers = sorted([(n, s) for n, s in player_stats.items() if s['wickets'] > 0],
                         key=lambda x: x[1]['wickets'], reverse=True)[:20]
        bowl_table = self._build_bowlers_table(bowlers)
        tabs.addTab(bowl_table, "🎳 Top 20 Bowlers")
        
        dlayout.addWidget(tabs, 1)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        close_btn.setStyleSheet(f"""
            QPushButton {{ background-color: {COLORS['primary']}; color: white; padding: 10px 30px; border: none; border-radius: 5px; font-weight: bold; font-size: 13px; }}
            QPushButton:hover {{ background-color: {COLORS['secondary']}; }}
        """)
        dlayout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        dialog.setLayout(dlayout)
        dialog.exec()
    
    def _build_scorecard_widget(self, scorecard):
        """Build a scrollable scorecard widget from innings data."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        container = QWidget()
        lay = QVBoxLayout()
        lay.setSpacing(12)
        lay.setContentsMargins(15, 10, 15, 10)
        
        for innings in scorecard.get('innings', []):
            team = innings.get('batting_team', innings.get('team', 'Unknown'))
            total = innings.get('total_runs', 0)
            wkts = innings.get('wickets_fallen', 0)
            overs = innings.get('overs', '')
            
            inn_label = QLabel(f"<b>{team}</b> — {total}/{wkts}" + (f" ({overs} ov)" if overs else ""))
            inn_label.setStyleSheet(f"font-size: 15px; color: {COLORS['primary']}; padding: 4px 0;")
            lay.addWidget(inn_label)
            
            # Batting card
            bat_data = innings.get('batting', innings.get('batting_card', []))
            if bat_data:
                bat_table = QTableWidget()
                bat_table.setColumnCount(6)
                bat_table.setHorizontalHeaderLabels(['Batter', 'Dismissal', 'Runs', 'Balls', '4s', '6s'])
                bat_table.setRowCount(len(bat_data))
                bat_table.verticalHeader().setVisible(False)
                bat_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
                bat_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
                bat_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
                for c in range(2, 6):
                    bat_table.horizontalHeader().setSectionResizeMode(c, QHeaderView.ResizeMode.ResizeToContents)
                bat_table.setStyleSheet(f"""
                    QTableWidget {{ border: 1px solid #334155; background: #111827; }}
                    QTableWidget::item {{ padding: 4px; }}
                    QHeaderView::section {{ background: {COLORS['primary']}; color: white; padding: 6px; border: none; font-weight: bold; }}
                """)
                for r, b in enumerate(bat_data):
                    name = b.get('name', b.get('player', ''))
                    dismissal = b.get('dismissal', b.get('how_out', ''))
                    bat_table.setItem(r, 0, QTableWidgetItem(name))
                    bat_table.setItem(r, 1, QTableWidgetItem(str(dismissal)))
                    for ci, key in enumerate(['runs', 'balls', 'fours', 'sixes'], 2):
                        val = b.get(key, b.get('balls_faced' if key == 'balls' else key, 0))
                        item = QTableWidgetItem(str(val))
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        bat_table.setItem(r, ci, item)
                    bat_table.setRowHeight(r, 28)
                bat_table.setMaximumHeight(min(30 + len(bat_data) * 30, 350))
                lay.addWidget(bat_table)
            
            # Bowling card
            bowl_data = innings.get('bowling', innings.get('bowling_card', []))
            if bowl_data:
                bowl_lbl = QLabel(f"<b>Bowling</b>")
                bowl_lbl.setStyleSheet("font-size: 12px; color: #555; padding-top: 4px;")
                lay.addWidget(bowl_lbl)
                bowl_table = QTableWidget()
                bowl_table.setColumnCount(5)
                bowl_table.setHorizontalHeaderLabels(['Bowler', 'Overs', 'Runs', 'Wickets', 'Econ'])
                bowl_table.setRowCount(len(bowl_data))
                bowl_table.verticalHeader().setVisible(False)
                bowl_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
                bowl_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
                for c in range(1, 5):
                    bowl_table.horizontalHeader().setSectionResizeMode(c, QHeaderView.ResizeMode.ResizeToContents)
                bowl_table.setStyleSheet(f"""
                    QTableWidget {{ border: 1px solid #334155; background: #111827; }}
                    QTableWidget::item {{ padding: 4px; }}
                    QHeaderView::section {{ background: #555; color: white; padding: 6px; border: none; font-weight: bold; }}
                """)
                for r, bw in enumerate(bowl_data):
                    name = bw.get('name', bw.get('player', ''))
                    overs_b = bw.get('overs', 0)
                    runs_c = bw.get('runs', bw.get('runs_conceded', 0))
                    wkts_b = bw.get('wickets', 0)
                    econ = f"{(runs_c / overs_b):.2f}" if overs_b > 0 else "0.00"
                    bowl_table.setItem(r, 0, QTableWidgetItem(name))
                    for ci, val in enumerate([str(overs_b), str(runs_c), str(wkts_b), econ], 1):
                        item = QTableWidgetItem(val)
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        bowl_table.setItem(r, ci, item)
                    bowl_table.setRowHeight(r, 28)
                bowl_table.setMaximumHeight(min(30 + len(bowl_data) * 30, 250))
                lay.addWidget(bowl_table)
        
        # MoM
        mom = scorecard.get('man_of_the_match', '')
        if mom:
            mom_lbl = QLabel(f"⭐ Man of the Match: <b>{mom}</b>")
            mom_lbl.setStyleSheet("font-size: 14px; color: #FFD700; padding: 6px 0;")
            lay.addWidget(mom_lbl)
        
        lay.addStretch()
        container.setLayout(lay)
        scroll.setWidget(container)
        return scroll
    
    def _extract_player_stats(self, scorecards):
        """Extract aggregated player stats from a list of scorecards."""
        stats = {}
        for sc in scorecards:
            if not sc or 'innings' not in sc:
                continue
            for innings in sc.get('innings', []):
                batting_team = innings.get('batting_team', innings.get('team', ''))
                bowling_team = innings.get('bowling_team', '')
                for bat in innings.get('batting', innings.get('batting_card', [])):
                    name = bat.get('name', bat.get('player', ''))
                    if not name:
                        continue
                    if name not in stats:
                        stats[name] = {'team': batting_team, 'runs': 0, 'balls': 0, 'fours': 0, 'sixes': 0,
                                       'highest': 0, 'fifties': 0, 'hundreds': 0, 'dismissals': 0, 'not_outs': 0,
                                       'wickets': 0, 'runs_conceded': 0, 'overs_bowled': 0, 'balls_bowled': 0,
                                       'four_wkt': 0, 'five_wkt': 0, 'matches': 0}
                    s = stats[name]
                    if not s['team'] and batting_team:
                        s['team'] = batting_team
                    runs = bat.get('runs', 0)
                    s['runs'] += runs
                    s['balls'] += bat.get('balls', bat.get('balls_faced', 0))
                    s['fours'] += bat.get('fours', 0)
                    s['sixes'] += bat.get('sixes', 0)
                    if runs > s['highest']:
                        s['highest'] = runs
                    if runs >= 100:
                        s['hundreds'] += 1
                    elif runs >= 50:
                        s['fifties'] += 1
                    dismissal = bat.get('dismissal', bat.get('how_out', ''))
                    if dismissal and dismissal.lower() not in ('not out', 'not_out', ''):
                        s['dismissals'] += 1
                    else:
                        s['not_outs'] += 1
                
                for bowl in innings.get('bowling', innings.get('bowling_card', [])):
                    name = bowl.get('name', bowl.get('player', ''))
                    if not name:
                        continue
                    if name not in stats:
                        stats[name] = {'team': bowling_team, 'runs': 0, 'balls': 0, 'fours': 0, 'sixes': 0,
                                       'highest': 0, 'fifties': 0, 'hundreds': 0, 'dismissals': 0, 'not_outs': 0,
                                       'wickets': 0, 'runs_conceded': 0, 'overs_bowled': 0, 'balls_bowled': 0,
                                       'four_wkt': 0, 'five_wkt': 0, 'matches': 0}
                    s = stats[name]
                    if not s['team'] and bowling_team:
                        s['team'] = bowling_team
                    wkts = bowl.get('wickets', 0)
                    s['wickets'] += wkts
                    s['runs_conceded'] += bowl.get('runs', bowl.get('runs_conceded', 0))
                    s['overs_bowled'] += bowl.get('overs', 0)
                    s['balls_bowled'] += bowl.get('balls', bowl.get('balls_bowled', 0))
                    if wkts >= 5:
                        s['five_wkt'] += 1
                    elif wkts >= 4:
                        s['four_wkt'] += 1
        return stats
    
    def _build_batters_table(self, batters):
        table = QTableWidget()
        table.setColumnCount(11)
        table.setHorizontalHeaderLabels(['#', 'Player', 'Team', 'Runs', 'Balls', 'Avg', 'SR', 'HS', '50s', '100s', '4s/6s'])
        table.setRowCount(len(batters))
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        h = table.horizontalHeader()
        for c in range(11):
            h.setSectionResizeMode(c, QHeaderView.ResizeMode.Stretch if c == 1 else QHeaderView.ResizeMode.ResizeToContents)
        table.setStyleSheet(f"""
            QTableWidget {{ border: none; background: #111827; gridline-color: #334155; }}
            QTableWidget::item {{ padding: 6px; }}
            QHeaderView::section {{ background: {COLORS['primary']}; color: white; padding: 8px; font-weight: bold; border: none; }}
        """)
        for i, (name, s) in enumerate(batters):
            sr = f"{(s['runs']/s['balls']*100):.1f}" if s['balls'] > 0 else "0.0"
            avg = f"{(s['runs']/s['dismissals']):.2f}" if s['dismissals'] > 0 else "N/A"
            items = [str(i+1), name, s.get('team',''), str(s['runs']), str(s['balls']),
                     avg, sr, str(s['highest']), str(s['fifties']), str(s['hundreds']),
                     f"{s['fours']}/{s['sixes']}"]
            for col, val in enumerate(items):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter if col != 1 else Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                table.setItem(i, col, item)
        return table
    
    def _build_bowlers_table(self, bowlers):
        table = QTableWidget()
        table.setColumnCount(9)
        table.setHorizontalHeaderLabels(['#', 'Player', 'Team', 'Wickets', 'Overs', 'Runs', 'Avg', 'Econ', '5W'])
        table.setRowCount(len(bowlers))
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        h = table.horizontalHeader()
        for c in range(9):
            h.setSectionResizeMode(c, QHeaderView.ResizeMode.Stretch if c == 1 else QHeaderView.ResizeMode.ResizeToContents)
        table.setStyleSheet(f"""
            QTableWidget {{ border: none; background: #111827; gridline-color: #334155; }}
            QTableWidget::item {{ padding: 6px; }}
            QHeaderView::section {{ background: {COLORS['primary']}; color: white; padding: 8px; font-weight: bold; border: none; }}
        """)
        for i, (name, s) in enumerate(bowlers):
            overs = s['overs_bowled']
            if overs == 0 and s['balls_bowled'] > 0:
                overs = s['balls_bowled'] / 6
            econ = f"{(s['runs_conceded']/overs):.2f}" if overs > 0 else "0.00"
            avg = f"{(s['runs_conceded']/s['wickets']):.2f}" if s['wickets'] > 0 else "N/A"
            items = [str(i+1), name, s.get('team',''), str(s['wickets']),
                     f"{overs:.1f}", str(s['runs_conceded']), avg, econ, str(s['five_wkt'])]
            for col, val in enumerate(items):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter if col != 1 else Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                table.setItem(i, col, item)
        return table
    
    def create_stats_summary(self, history, wc_type):
        stats_frame = QGroupBox(f"{wc_type} World Cup Statistics")
        stats_frame.setStyleSheet(f"""
            QGroupBox {{ font-size: 15px; font-weight: 700; color: #EAF1FF; border: 2px solid {COLORS['border']}; border-radius: 8px; margin-top: 12px; padding-top: 16px; }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 4px 12px; color: white; background-color: {COLORS['secondary']}; border-radius: 5px; margin-left: 10px; }}
        """)
        layout = QHBoxLayout()
        layout.setSpacing(25)
        
        total_label = QLabel(f"Total Tournaments: {len(history)}")
        total_label.setStyleSheet("font-size: 14px; font-weight: 600;")
        layout.addWidget(total_label)
        
        winners = [h.get('winner', 'Unknown') for h in history]
        if winners:
            winner_counts = Counter(winners)
            most = winner_counts.most_common(1)[0]
            layout.addWidget(QLabel(f"Most Successful: {most[0]} ({most[1]} titles)"))
        
        if history:
            latest = history[0]
            layout.addWidget(QLabel(f"Current Champion: {latest.get('winner', 'N/A')}"))
        
        layout.addStretch()
        stats_frame.setLayout(layout)
        return stats_frame
    
    def refresh_data(self):
        print("[WC View] refresh_data called")
        if self.layout() is not None:
            layout = self.layout()
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        self.init_ui()
