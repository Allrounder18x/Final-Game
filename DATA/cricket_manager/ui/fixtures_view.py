"""
Fixtures Screen - Calendar-style month view with ICC FTP series grouping
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QFrame,
    QHeaderView, QMessageBox, QScrollArea, QGridLayout, QSizePolicy,
    QApplication,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

import os
import calendar

from cricket_manager.ui.styles import COLORS, MAIN_STYLESHEET
from cricket_manager.ui.screen_manager import BaseScreen

MONTH_NAMES = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]

# Cricket nation / team colors (primary brand/flag colors) for fixture tiles
TEAM_COLORS = {
    'India': '#0A2647',           # dark blue
    'Australia': '#00843D',       # green
    'England': '#C8102E',         # red
    'Pakistan': '#006629',       # green
    'South Africa': '#007749',   # green
    'New Zealand': '#00247D',    # black/dark blue
    'West Indies': '#FCD116',    # maroon/gold
    'Sri Lanka': '#FFBE00',      # gold/maroon
    'Bangladesh': '#006A4E',     # green
    'Afghanistan': '#000000',    # black
    'Ireland': '#169B62',        # green
    'Zimbabwe': '#FFD700',       # gold
    'Scotland': '#0065BF',       # blue
    'Netherlands': '#FF6600',    # orange
    'UAE': '#FF0000',            # red
    'Oman': '#CD0000',           # red
    'Nepal': '#DC143C',          # crimson
    'PNG': '#000000',            # black
    'Namibia': '#0033A0',        # blue
    'USA': '#3C3B6E',            # blue
    'Canada': '#FF0000',         # red
    'Kenya': '#006600',          # green
    'Hong Kong': '#E60012',      # red
    'Singapore': '#ED2939',      # red
    'Malaysia': '#010066',       # blue
    'Thailand': '#A51931',       # red
    'Kuwait': '#007A3D',         # green
    'Bahrain': '#C8102E',        # red
    'Qatar': '#8B1538',          # maroon
    'Saudi Arabia': '#006C35',   # green
    'Maldives': '#D21034',       # red
    'Bermuda': '#E4002B',        # red
    'Germany': '#000000',        # black
    'Italy': '#009246',          # green
    'Jersey': '#F9DD16',        # yellow
    'Argentina': '#75AADB',     # light blue
    'France': '#0055A4',        # blue
}
DEFAULT_TEAM_COLOR = '#5C6BC0'


class FixturesScreen(BaseScreen):
    """Calendar-style fixtures screen with series grouping and play functionality"""
    
    def __init__(self, screen_manager=None, game_engine=None):
        super().__init__(screen_manager)
        self.setStyleSheet(MAIN_STYLESHEET)
        self.game_engine = game_engine
        self.current_format = "All"  # Default to showing all formats
        self.current_tier = 0  # 0 = All tiers
        self._match_cards = {}
        self._sim_queue = []
        self._sim_queue_total = 0
        self._sim_queue_done = 0
        self._current_month_index = 0  # 0-11, month to display (one month full screen)
        self.show_domestic = False  # False = International fixtures, True = Domestic (top 10 nations)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI with calendar-style month view"""
        if self.layout() is not None:
            return
        
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = self._create_header()
        layout.addWidget(header)
        
        # Filters
        filters = self._create_filters()
        layout.addWidget(filters)
        
        # Fixed month navigation row (stays visible while calendar grid scrolls)
        month_nav = self._create_month_nav_bar()
        layout.addWidget(month_nav)
        
        # Single-month calendar inside scroll area to avoid huge window geometry
        self.calendar_widget = QWidget()
        self.calendar_layout = QVBoxLayout()
        self.calendar_layout.setSpacing(8)
        # Remove horizontal gutters so month row/background is consistent edge-to-edge.
        self.calendar_layout.setContentsMargins(0, 12, 0, 12)
        self.calendar_widget.setLayout(self.calendar_layout)
        bg0 = COLORS.get('bg_primary') or '#10141d'
        bg1 = COLORS.get('bg_secondary') or '#172131'
        self.calendar_widget.setStyleSheet(
            "QWidget { background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 %s, stop:1 %s); }"
            % (bg0, bg1)
        )
        
        scroll = QScrollArea()
        self.calendar_scroll = scroll
        scroll.setWidget(self.calendar_widget)
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(320)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
            "QScrollArea > QWidget > QWidget { background: #10141d; }"
            "QScrollBar:vertical { width: 12px; background: #111827; margin: 0; border-radius: 6px; }"
            "QScrollBar::handle:vertical { background: #2f3a50; min-height: 26px; border-radius: 6px; }"
            "QScrollBar::handle:vertical:hover { background: #44506b; }"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }"
        )
        scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.calendar_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        layout.addWidget(scroll, 1)
        
        self.setLayout(layout)
        self.load_fixtures()

    def _create_month_nav_bar(self):
        """Create fixed month navigation controls outside the scroll area."""
        prim = COLORS.get('primary') or '#2E7D32'
        nav_frame = QFrame()
        nav_frame.setStyleSheet(
            "QFrame { background-color: #0F1726; border: 1px solid #253247; border-radius: 4px; }"
        )
        nav_row = QHBoxLayout()
        nav_row.setSpacing(10)
        nav_row.setContentsMargins(6, 4, 6, 4)

        nav_style = (
            "QPushButton { background-color: #111827; color: #EAF1FF; padding: 6px 10px; "
            "border: 1px solid #334155; border-radius: 4px; font-weight: 800; font-size: 12px; min-width: 34px; } "
            "QPushButton:hover { background-color: #1F2937; border-color: #4B5563; } "
            "QPushButton:disabled { background-color: #0B1220; color: #6B7280; border-color: #1F2937; }"
        )
        self.month_prev_btn = QPushButton("◀")
        self.month_prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.month_prev_btn.setStyleSheet(nav_style)
        self.month_prev_btn.clicked.connect(self._go_prev_month)

        self.month_combo = QComboBox()
        self.month_combo.addItems(MONTH_NAMES)
        self.month_combo.setMinimumWidth(180)
        self.month_combo.setMaximumWidth(220)
        self.month_combo.setStyleSheet(
            "QComboBox { padding: 6px 10px; font-size: 12px; font-weight: 800; color: #FFFFFF; "
            "background-color: #111827; border: 1px solid #334155; border-radius: 4px; } "
            "QComboBox::drop-down { border: none; width: 20px; background: #0f1726; } "
            "QComboBox::down-arrow { image: none; border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 7px solid #dbe8ff; margin-right: 4px; } "
            "QComboBox QAbstractItemView { background-color: #111827; color: #FFFFFF; border: 1px solid #2b3850; selection-background-color: %s; selection-color: #FFFFFF; outline: 0; } "
            "QComboBox QAbstractItemView::item { background-color: #111827; color: #FFFFFF; min-height: 22px; } "
            "QComboBox QAbstractItemView::item:selected { background-color: %s; color: #FFFFFF; }"
            % (prim, prim)
        )
        self.month_combo.currentIndexChanged.connect(self._on_month_selected)

        self.month_year_lbl = QLabel("")
        self.month_year_lbl.setStyleSheet("color: rgba(255,255,255,0.92); font-size: 12px; font-weight: 800; padding: 0 4px;")

        self.month_next_btn = QPushButton("▶")
        self.month_next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.month_next_btn.setStyleSheet(nav_style)
        self.month_next_btn.clicked.connect(self._go_next_month)

        nav_row.addStretch(1)
        nav_row.addWidget(self.month_prev_btn)
        nav_row.addWidget(self.month_combo)
        nav_row.addWidget(self.month_year_lbl)
        nav_row.addWidget(self.month_next_btn)
        nav_row.addStretch(1)
        nav_frame.setLayout(nav_row)
        return nav_frame

    def _clear_layout_items(self, layout):
        """Recursively clear widgets and nested layouts to avoid visual overlap artifacts."""
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
                continue
            child_layout = item.layout()
            if child_layout is not None:
                self._clear_layout_items(child_layout)
    
    def _create_header(self):
        """Create minimal header: single row, compact, more space for calendar."""
        header = QFrame()
        prim = COLORS.get('primary') or '#2E7D32'
        sec = COLORS.get('secondary') or '#1976D2'
        header.setStyleSheet(
            "QFrame { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 %s, stop:1 %s); padding: 4px 12px; }"
            % (prim, sec)
        )
        layout = QHBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(0, 2, 0, 2)
        title = QLabel("Fixtures")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        layout.addWidget(title)
        season_text = f"Season {self.game_engine.current_season} | Year {self.game_engine.current_year}" if self.game_engine else "Current Season"
        subtitle = QLabel(" · " + season_text + " — ICC FTP")
        subtitle.setStyleSheet("font-size: 11px; color: rgba(255,255,255,0.95);")
        layout.addWidget(subtitle)
        layout.addStretch()
        header.setLayout(layout)
        return header
    
    def refresh_fixtures(self):
        """Refresh fixtures display (call after season change)"""
        self.load_fixtures()
        self.init_ui()
    
    def refresh_data(self):
        """Alias for refresh_fixtures for auto-refresh compatibility"""
        self.refresh_fixtures()
    
    def _create_filters(self):
        """Create filter section with format, tier, team selectors and NBA 2K24-style date range simulation"""
        filters = QFrame()
        bdr = COLORS.get('border_light') or COLORS.get('border') or '#E8ECF0'
        filters.setStyleSheet(f"""
            QFrame {{
                background: {COLORS.get('bg_secondary', '#FFFFFF')};
                border-bottom: 1px solid {bdr};
                padding: 6px 16px;
            }}
        """)
        outer_layout = QVBoxLayout()
        outer_layout.setSpacing(6)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- Row 1: Existing filters ---
        layout = QHBoxLayout()
        
        # Format selector
        layout.addWidget(QLabel("Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(['All', 'T20', 'ODI', 'Test'])
        self.format_combo.setCurrentText(self.current_format)
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        self.format_combo.setStyleSheet(f"""
            QComboBox {{ padding: 8px 15px; border: 1px solid {COLORS['border_light']}; border-radius: 5px; min-width: 80px; }}
        """)
        layout.addWidget(self.format_combo)
        
        layout.addSpacing(15)
        
        # Tier selector
        layout.addWidget(QLabel("Tier:"))
        self.tier_combo = QComboBox()
        self.tier_combo.addItems(['All Tiers', 'Tier 1', 'Tier 2', 'Tier 3', 'Tier 4', 'Tier 5 (U21)', 'World Cup'])
        self.tier_combo.currentIndexChanged.connect(self.on_tier_changed)
        self.tier_combo.setStyleSheet(f"""
            QComboBox {{ padding: 8px 15px; border: 1px solid {COLORS['border_light']}; border-radius: 5px; min-width: 100px; }}
        """)
        layout.addWidget(self.tier_combo)
        
        layout.addSpacing(15)
        
        # View: International vs Domestic
        layout.addWidget(QLabel("View:"))
        self.view_combo = QComboBox()
        self.view_combo.addItems(["International", "Domestic"])
        self.view_combo.currentTextChanged.connect(self.on_view_changed)
        self.view_combo.setStyleSheet(f"""
            QComboBox {{ padding: 8px 15px; border: 1px solid {COLORS['border_light']}; border-radius: 5px; min-width: 120px; }}
        """)
        layout.addWidget(self.view_combo)
        
        layout.addSpacing(15)
        
        # Team filter
        layout.addWidget(QLabel("Team:"))
        self.team_combo = QComboBox()
        self._refresh_team_combo()
        self.team_combo.currentTextChanged.connect(self.on_team_changed)
        self.team_combo.setStyleSheet(f"""
            QComboBox {{ padding: 8px 15px; border: 1px solid {COLORS['border_light']}; border-radius: 5px; min-width: 140px; }}
        """)
        layout.addWidget(self.team_combo)
        
        layout.addSpacing(15)
        
        # World Cup button
        self.wc_btn = QPushButton("World Cup")
        self.wc_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.wc_btn.clicked.connect(self._go_to_world_cup)
        self.wc_btn.setStyleSheet(f"""
            QPushButton {{ background-color: {COLORS['gold']}; color: white; padding: 10px 18px; border: none; border-radius: 5px; font-weight: bold; font-size: 13px; }}
            QPushButton:hover {{ background-color: {COLORS['warning']}; }}
        """)
        layout.addWidget(self.wc_btn)
        
        layout.addStretch()
        
        # WC Stats button (hidden by default)
        self.wc_stats_btn = QPushButton("WC Stats")
        self.wc_stats_btn.clicked.connect(self.show_world_cup_stats)
        self.wc_stats_btn.setStyleSheet(f"""
            QPushButton {{ background-color: {COLORS['secondary']}; color: white; padding: 10px 18px; border: none; border-radius: 5px; font-weight: bold; font-size: 13px; }}
            QPushButton:hover {{ background-color: {COLORS['primary']}; }}
        """)
        self.wc_stats_btn.setVisible(False)
        layout.addWidget(self.wc_stats_btn)
        
        # Simulate All button
        self.sim_all_btn = QPushButton("Sim All Visible")
        self.sim_all_btn.clicked.connect(self.simulate_all_matches)
        self.sim_all_btn.setStyleSheet(f"""
            QPushButton {{ background-color: {COLORS['warning']}; color: white; padding: 10px 18px; border: none; border-radius: 5px; font-weight: bold; font-size: 13px; }}
            QPushButton:hover {{ background-color: {COLORS['danger']}; }}
        """)
        layout.addWidget(self.sim_all_btn)
        
        # Simulate Entire Season button
        self.sim_season_btn = QPushButton("Sim Season")
        self.sim_season_btn.clicked.connect(self.simulate_season)
        self.sim_season_btn.setStyleSheet(f"""
            QPushButton {{ background-color: {COLORS['success']}; color: white; padding: 10px 18px; border: none; border-radius: 5px; font-weight: bold; font-size: 13px; }}
            QPushButton:hover {{ background-color: {COLORS['secondary']}; }}
        """)
        layout.addWidget(self.sim_season_btn)
        
        outer_layout.addLayout(layout)
        
        # --- Row 2: NBA 2K24-style Date Range Simulation ---
        range_row = QHBoxLayout()
        range_row.setSpacing(8)
        
        sim_icon = QLabel("🗓️")
        sim_icon.setStyleSheet("font-size: 16px;")
        range_row.addWidget(sim_icon)
        
        sim_label = QLabel("Simulate To:")
        sim_label.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {COLORS['primary']};")
        range_row.addWidget(sim_label)
        
        range_row.addSpacing(5)
        
        combo_style = f"""
            QComboBox {{ padding: 6px 10px; border: 2px solid {COLORS['primary']}; border-radius: 5px; 
                         min-width: 55px; font-weight: bold; background: #111827; }}
            QComboBox:hover {{ border-color: {COLORS['secondary']}; }}
        """
        
        from_lbl = QLabel("From:")
        from_lbl.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']};")
        range_row.addWidget(from_lbl)
        
        self.from_month_combo = QComboBox()
        self.from_month_combo.addItems([m[:3] for m in MONTH_NAMES])
        self.from_month_combo.setCurrentIndex(0)
        self.from_month_combo.setStyleSheet(combo_style)
        range_row.addWidget(self.from_month_combo)
        
        self.from_day_combo = QComboBox()
        self.from_day_combo.addItems([str(d) for d in range(1, 29)])
        self.from_day_combo.setStyleSheet(combo_style)
        range_row.addWidget(self.from_day_combo)
        
        range_row.addSpacing(10)
        
        to_lbl = QLabel("To:")
        to_lbl.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']};")
        range_row.addWidget(to_lbl)
        
        self.to_month_combo = QComboBox()
        self.to_month_combo.addItems([m[:3] for m in MONTH_NAMES])
        self.to_month_combo.setCurrentIndex(11)
        self.to_month_combo.setStyleSheet(combo_style)
        range_row.addWidget(self.to_month_combo)
        
        self.to_day_combo = QComboBox()
        self.to_day_combo.addItems([str(d) for d in range(1, 29)])
        self.to_day_combo.setCurrentIndex(27)
        self.to_day_combo.setStyleSheet(combo_style)
        range_row.addWidget(self.to_day_combo)
        
        range_row.addSpacing(15)
        
        self.sim_range_btn = QPushButton("Simulate Range")
        self.sim_range_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sim_range_btn.clicked.connect(self.simulate_date_range)
        self.sim_range_btn.setStyleSheet(f"""
            QPushButton {{ 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary']}, stop:1 {COLORS['secondary']});
                color: white; padding: 8px 22px; border: none; border-radius: 5px; 
                font-weight: bold; font-size: 13px;
            }}
            QPushButton:hover {{ 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['secondary']}, stop:1 {COLORS['primary']});
            }}
            QPushButton:disabled {{
                background: {COLORS['border']}; color: {COLORS['text_disabled']}; font-size: 13px;
            }}
        """)
        range_row.addWidget(self.sim_range_btn)
        
        self.series_results_btn = QPushButton("Series Results")
        self.series_results_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.series_results_btn.clicked.connect(self._open_series_results_dialog)
        self.series_results_btn.setStyleSheet(f"""
            QPushButton {{ background: {COLORS.get('info', '#2196F3')}; color: white; padding: 8px 18px; border: none; border-radius: 5px; font-weight: bold; font-size: 13px; }}
            QPushButton:hover {{ background: {COLORS.get('primary', '#2E7D32')}; }}
        """)
        range_row.addWidget(self.series_results_btn)
        
        range_row.addSpacing(10)
        
        self.sim_progress_label = QLabel("")
        self.sim_progress_label.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']}; font-weight: bold;")
        range_row.addWidget(self.sim_progress_label)
        
        range_row.addStretch()
        
        outer_layout.addLayout(range_row)
        
        filters.setLayout(outer_layout)
        return filters
    
    def _open_series_results_dialog(self):
        """Open dialog to select a team and a completed series, then show series stats (top batters, bowlers, match summaries)."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QComboBox, QListWidget, QListWidgetItem, QPushButton, QLabel, QMessageBox
        
        if not self.game_engine:
            QMessageBox.information(self, "Series Results", "No game data loaded.")
            return
        
        # Gather all completed fixtures (all formats, all tiers, no team filter)
        all_fixtures = []
        for fmt in ['T20', 'ODI', 'Test']:
            for f in self.game_engine.fixtures.get(fmt, []):
                if f.get('completed'):
                    all_fixtures.append(f)
        
        # Group by series_id / tour_id
        series_groups = {}
        for f in all_fixtures:
            sid = f.get('series_id') or f.get('tour_id')
            if sid:
                if sid not in series_groups:
                    series_groups[sid] = []
                series_groups[sid].append(f)
        
        # Build list of (series_fixtures, series_name, format)
        series_list = []
        team_names = set()
        for sid, flist in series_groups.items():
            flist.sort(key=lambda x: x.get('match_number', 0))
            first = flist[0]
            tour_name = first.get('tour_name', '') or first.get('series_name', '')
            fmt = first.get('format', '')
            home_team = first.get('home_team')
            away_team = first.get('away_team')
            home_name = home_team.name if hasattr(home_team, 'name') else first.get('home', str(home_team or ''))
            away_name = away_team.name if hasattr(away_team, 'name') else first.get('away', str(away_team or ''))
            if not tour_name and (home_name or away_name):
                tour_name = f"{home_name} vs {away_name}"
            team_names.add(home_name)
            team_names.add(away_name)
            total = len(flist)
            win_counts = {}
            for f in flist:
                w = f.get('winner', '')
                if w and w not in ('Draw', 'Tie', 'N/A'):
                    win_counts[w] = win_counts.get(w, 0) + 1
            winner_text = "Drawn"
            if win_counts:
                sw = max(win_counts, key=win_counts.get)
                best = win_counts[sw]
                counts_list = sorted(win_counts.values(), reverse=True)
                if len(counts_list) > 1 and counts_list[0] == counts_list[1]:
                    winner_text = "Drawn"
                else:
                    winner_text = f"{sw} {best}-{total - best}"
            series_list.append({
                'fixtures': flist,
                'name': tour_name or f"Series {sid}",
                'format': fmt,
                'display': f"{tour_name} — {fmt}, {total} match(es) — {winner_text}",
                'home': home_name,
                'away': away_name,
            })
        
        if not series_list:
            QMessageBox.information(self, "Series Results", "No completed series found.")
            return
        
        team_names = sorted([t for t in team_names if t])
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Series Results — Select team and series")
        dialog.setMinimumSize(560, 420)
        dlayout = QVBoxLayout()
        
        row = QHBoxLayout()
        row.addWidget(QLabel("Team:"))
        team_combo = QComboBox()
        team_combo.addItem("All Teams")
        for t in team_names:
            team_combo.addItem(t)
        team_combo.setStyleSheet(f"""
            QComboBox {{ min-width: 140px; padding: 6px; border: 1px solid {COLORS.get('border', '#ccc')}; border-radius: 4px; }}
        """)
        row.addWidget(team_combo)
        row.addStretch()
        dlayout.addLayout(row)
        
        dlayout.addWidget(QLabel("Completed series (double-click or select and click View):"))
        list_widget = QListWidget()
        list_widget.setStyleSheet(f"""
            QListWidget {{ border: 1px solid {COLORS.get('border', '#ccc')}; border-radius: 4px; padding: 4px; }}
        """)
        
        def populate_series():
            list_widget.clear()
            list_widget._series_data = []
            sel_team = team_combo.currentText()
            for s in series_list:
                if sel_team != "All Teams" and sel_team != s['home'] and sel_team != s['away']:
                    continue
                item = QListWidgetItem(s['display'])
                list_widget.addItem(item)
                list_widget._series_data.append(s)
        
        def on_view():
            row_idx = list_widget.currentRow()
            if row_idx < 0 or not getattr(list_widget, '_series_data', None) or row_idx >= len(list_widget._series_data):
                QMessageBox.information(self, "Series Results", "Please select a series first.")
                return
            s = list_widget._series_data[row_idx]
            dialog.accept()
            self.show_series_stats(s['fixtures'], s['name'], s['format'])
        
        team_combo.currentTextChanged.connect(lambda: populate_series())
        list_widget.doubleClicked.connect(on_view)
        populate_series()
        
        dlayout.addWidget(list_widget)
        
        btn_row = QHBoxLayout()
        view_btn = QPushButton("View series stats")
        view_btn.clicked.connect(on_view)
        view_btn.setStyleSheet(f"""
            QPushButton {{ background: {COLORS.get('primary', '#2E7D32')}; color: white; padding: 8px 20px; border: none; border-radius: 5px; font-weight: bold; }}
            QPushButton:hover {{ background: {COLORS.get('secondary', '#1B5E20')}; }}
        """)
        btn_row.addWidget(view_btn)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.reject)
        btn_row.addWidget(close_btn)
        dlayout.addLayout(btn_row)
        
        dialog.setLayout(dlayout)
        dialog.exec()
    
    # ========================================================================
    # WORLD CUP HELPERS (unchanged logic)
    # ========================================================================
    
    def _get_wc_fixtures_all_formats(self):
        """Get all World Cup fixtures across all formats"""
        for fmt in ['T20', 'ODI', 'Test']:
            all_fmt = self.game_engine.fixtures.get(fmt, [])
            wc = [f for f in all_fmt if f.get('is_world_cup', False)]
            if wc:
                return wc, fmt
        return [], None
    
    def _get_wc_phase(self, wc_fixtures):
        """Determine current WC phase (supports group-stage WCs and knockout-only Associate WC)"""
        group_fixtures = [f for f in wc_fixtures if f.get('round', '').startswith('Group')]
        ko_rounds = ['Round of 32', 'Round of 16', 'Quarter-Final', 'Semi-Final', 'Final']
        ko_fixtures = [f for f in wc_fixtures if f.get('round') in ko_rounds]
        final_fixtures = [f for f in wc_fixtures if f.get('round') == 'Final']
        
        # Check if this is a knockout-only tournament (Associate WC)
        is_knockout_only = len(group_fixtures) == 0 and len(ko_fixtures) > 0
        
        if is_knockout_only:
            if final_fixtures and all(f.get('completed') for f in final_fixtures):
                return 'completed'
            unplayed_ko = [f for f in ko_fixtures if not f.get('completed')]
            if unplayed_ko:
                return 'associate_knockout'
            # All current round done but no next round yet
            return 'associate_knockout_advance'
        
        # Standard group-stage WC
        unplayed_groups = [f for f in group_fixtures if not f.get('completed')]
        if unplayed_groups:
            return 'groups'
        if final_fixtures and all(f.get('completed') for f in final_fixtures):
            return 'completed'
        semi_fixtures = [f for f in wc_fixtures if f.get('round') == 'Semi-Final']
        if semi_fixtures or final_fixtures:
            return 'knockouts'
        return 'groups_done'
    
    def _generate_wc_knockouts(self, wc_fixtures, wc_format):
        """Generate semi-final and final fixtures based on group standings"""
        group_a = [f for f in wc_fixtures if f.get('round') == 'Group A' and f.get('completed')]
        group_b = [f for f in wc_fixtures if f.get('round') == 'Group B' and f.get('completed')]
        
        def build_standings(matches):
            standings = {}
            for m in matches:
                for team_name in [m.get('home', ''), m.get('away', '')]:
                    if team_name and team_name not in standings:
                        standings[team_name] = {'points': 0, 'nrr': 0.0, 'runs_for': 0, 'runs_against': 0, 'overs_batted': 0, 'overs_bowled': 0}
                sc = m.get('scorecard', {})
                home = m.get('home', '')
                away = m.get('away', '')
                winner = m.get('winner', '')
                if home in standings and away in standings:
                    if winner == home:
                        standings[home]['points'] += 2
                    elif winner == away:
                        standings[away]['points'] += 2
                    elif winner and winner != 'Tie':
                        pass
                    else:
                        standings[home]['points'] += 1
                        standings[away]['points'] += 1
                    if sc and 'innings' in sc and len(sc['innings']) >= 2:
                        inn1 = sc['innings'][0]
                        inn2 = sc['innings'][1]
                        standings[home]['runs_for'] += inn1.get('total_runs', 0)
                        standings[home]['runs_against'] += inn2.get('total_runs', 0)
                        standings[home]['overs_batted'] += inn1.get('overs', 1)
                        standings[home]['overs_bowled'] += inn2.get('overs', 1)
                        standings[away]['runs_for'] += inn2.get('total_runs', 0)
                        standings[away]['runs_against'] += inn1.get('total_runs', 0)
                        standings[away]['overs_batted'] += inn2.get('overs', 1)
                        standings[away]['overs_bowled'] += inn1.get('overs', 1)
            for name, s in standings.items():
                if s['overs_batted'] > 0 and s['overs_bowled'] > 0:
                    s['nrr'] = round(s['runs_for'] / s['overs_batted'] - s['runs_against'] / s['overs_bowled'], 3)
            return sorted(standings.items(), key=lambda x: (x[1]['points'], x[1]['nrr']), reverse=True)
        
        a_standings = build_standings(group_a)
        b_standings = build_standings(group_b)
        if len(a_standings) < 2 or len(b_standings) < 2:
            return
        a1_name, a2_name = a_standings[0][0], a_standings[1][0]
        b1_name, b2_name = b_standings[0][0], b_standings[1][0]
        a1 = self.game_engine.get_team_by_name(a1_name)
        a2 = self.game_engine.get_team_by_name(a2_name)
        b1 = self.game_engine.get_team_by_name(b1_name)
        b2 = self.game_engine.get_team_by_name(b2_name)
        if not all([a1, a2, b1, b2]):
            return
        existing_ko = [f for f in self.game_engine.fixtures.get(wc_format, [])
                      if f.get('is_world_cup') and f.get('round') in ('Semi-Final', 'Final')]
        if existing_ko:
            return
        wc_month = self.game_engine._get_wc_month(self.game_engine.current_season) if self.game_engine else 5
        self.game_engine.fixtures[wc_format].append({
            'team1': a1, 'team2': b2, 'home': a1.name, 'away': b2.name,
            'format': wc_format, 'tier': 0, 'is_world_cup': True, 'round': 'Semi-Final',
            'wc_tournament': getattr(self.game_engine, 'wc_name', 'World Cup'),
            'completed': False, 'status': 'Scheduled', 'winner': None, 'margin': '', 'scorecard': {},
            'month': wc_month if wc_month is not None else 5, 'day': 25,
        })
        self.game_engine.fixtures[wc_format].append({
            'team1': b1, 'team2': a2, 'home': b1.name, 'away': a2.name,
            'format': wc_format, 'tier': 0, 'is_world_cup': True, 'round': 'Semi-Final',
            'wc_tournament': getattr(self.game_engine, 'wc_name', 'World Cup'),
            'completed': False, 'status': 'Scheduled', 'winner': None, 'margin': '', 'scorecard': {},
            'month': wc_month if wc_month is not None else 5, 'day': 26,
        })
    
    def _generate_wc_final(self, wc_fixtures, wc_format):
        """Generate the final fixture after both semis are done"""
        semis = [f for f in wc_fixtures if f.get('round') == 'Semi-Final' and f.get('completed')]
        if len(semis) < 2:
            return
        existing_final = [f for f in self.game_engine.fixtures.get(wc_format, [])
                         if f.get('is_world_cup') and f.get('round') == 'Final']
        if existing_final:
            return
        w1_name = semis[0].get('winner', '')
        w2_name = semis[1].get('winner', '')
        w1 = self.game_engine.get_team_by_name(w1_name)
        w2 = self.game_engine.get_team_by_name(w2_name)
        if not w1 or not w2:
            return
        wc_month = self.game_engine._get_wc_month(self.game_engine.current_season) if self.game_engine else 5
        self.game_engine.fixtures[wc_format].append({
            'team1': w1, 'team2': w2, 'home': w1.name, 'away': w2.name,
            'format': wc_format, 'tier': 0, 'is_world_cup': True, 'round': 'Final',
            'wc_tournament': getattr(self.game_engine, 'wc_name', 'World Cup'),
            'completed': False, 'status': 'Scheduled', 'winner': None, 'margin': '', 'scorecard': {},
            'month': wc_month if wc_month is not None else 5, 'day': 28,
        })
    
    def _generate_associate_next_round(self, wc_fixtures, wc_format):
        """Generate next knockout round for Associate WC from winners of the completed round."""
        round_order = ['Round of 32', 'Round of 16', 'Quarter-Final', 'Semi-Final', 'Final']
        
        # Find the latest completed round
        completed_rounds = set()
        for f in wc_fixtures:
            if f.get('completed') and f.get('round') in round_order:
                completed_rounds.add(f['round'])
        
        if not completed_rounds:
            return
        
        # Get the latest completed round in order
        latest_idx = max(round_order.index(r) for r in completed_rounds)
        latest_round = round_order[latest_idx]
        
        # Check if next round already exists
        if latest_idx + 1 >= len(round_order):
            return
        next_round = round_order[latest_idx + 1]
        
        existing_next = [f for f in wc_fixtures if f.get('round') == next_round]
        if existing_next:
            return
        
        # Collect winners from the latest round
        round_fixtures = [f for f in wc_fixtures if f.get('round') == latest_round and f.get('completed')]
        winners = []
        for f in round_fixtures:
            w_name = f.get('winner', '')
            if w_name and w_name != 'Tie':
                w = self.game_engine.get_team_by_name(w_name)
                if w:
                    winners.append(w)
        
        if len(winners) < 2:
            return
        
        wc_month = self.game_engine._get_wc_month(self.game_engine.current_season) if self.game_engine else 9
        wc_tournament = getattr(self.game_engine, 'wc_name', 'Associate World Cup')
        day_counter = 1
        
        for i in range(0, len(winners) - 1, 2):
            t1 = winners[i]
            t2 = winners[i + 1]
            self.game_engine.fixtures[wc_format].append({
                'team1': t1, 'team2': t2, 'home': t1.name, 'away': t2.name,
                'format': wc_format, 'tier': 0, 'is_world_cup': True, 'round': next_round,
                'wc_tournament': wc_tournament,
                'completed': False, 'status': 'Scheduled', 'winner': None, 'margin': '', 'scorecard': {},
                'month': wc_month if wc_month is not None else 9, 'day': min(day_counter, 28),
            })
            day_counter += 1
        
        # Handle odd winner (bye)
        if len(winners) % 2 == 1:
            bye = winners[-1]
            # Auto-advance bye team to next-next round (or just note it)
            print(f"[Associate WC] {bye.name} gets a bye to {next_round}")
        
        print(f"[Associate WC] Generated {len(winners) // 2} {next_round} fixtures")
    
    # ========================================================================
    # CALENDAR VIEW - LOAD & RENDER
    # ========================================================================
    
    def _gather_all_fixtures(self):
        """Gather fixtures across all formats based on current filters (International or Domestic)."""
        if not self.game_engine:
            return []
        
        selected_team = self.team_combo.currentText() if hasattr(self, 'team_combo') else 'All Teams'
        team_filter = selected_team if selected_team != 'All Teams' else None
        
        if self.current_format == 'All':
            formats = ['T20', 'ODI', 'Test']
        else:
            formats = [self.current_format]
        
        all_fixtures = []
        seen_keys = set()

        def _key_for_fixture(f):
            home = f.get('team1') or f.get('home_team')
            away = f.get('team2') or f.get('away_team')
            home_name = home.name if hasattr(home, 'name') else f.get('home', str(home) if home else '')
            away_name = away.name if hasattr(away, 'name') else f.get('away', str(away) if away else '')
            return (
                f.get('format'),
                f.get('tier'),
                f.get('month'),
                f.get('day'),
                home_name,
                away_name,
                bool(f.get('is_u21', False)),
                bool(f.get('is_world_cup', False)),
            )
        source = getattr(self.game_engine, 'domestic_fixtures', None) if self.show_domestic else None
        if self.show_domestic and source:
            for fmt in formats:
                for f in source.get(fmt, []):
                    if team_filter:
                        home = f.get('team1') or f.get('home_team')
                        away = f.get('team2') or f.get('away_team')
                        home_name = home.name if hasattr(home, 'name') else f.get('home', str(home) if home else '')
                        away_name = away.name if hasattr(away, 'name') else f.get('away', str(away) if away else '')
                        if home_name != team_filter and away_name != team_filter:
                            continue
                    k = _key_for_fixture(f)
                    if k in seen_keys:
                        continue
                    seen_keys.add(k)
                    all_fixtures.append(f)
            return all_fixtures
        
        for fmt in formats:
            for f in self.game_engine.fixtures.get(fmt, []):
                if self.current_tier == 6:
                    if not f.get('is_world_cup', False) and f.get('tier') != 0:
                        continue
                elif self.current_tier > 0:
                    if f.get('tier') != self.current_tier and not f.get('is_world_cup', False):
                        continue
                if team_filter:
                    home = f.get('team1') or f.get('home_team')
                    away = f.get('team2') or f.get('away_team')
                    home_name = home.name if hasattr(home, 'name') else f.get('home', str(home) if home else '')
                    away_name = away.name if hasattr(away, 'name') else f.get('away', str(away) if away else '')
                    if home_name != team_filter and away_name != team_filter:
                        continue
                k = _key_for_fixture(f)
                if k in seen_keys:
                    continue
                seen_keys.add(k)
                all_fixtures.append(f)
        # Final hard filter guard (prevents ghost fixtures when stale renders existed).
        if team_filter:
            filtered = []
            for f in all_fixtures:
                home = f.get('team1') or f.get('home_team')
                away = f.get('team2') or f.get('away_team')
                home_name = home.name if hasattr(home, 'name') else f.get('home', str(home) if home else '')
                away_name = away.name if hasattr(away, 'name') else f.get('away', str(away) if away else '')
                if home_name == team_filter or away_name == team_filter:
                    filtered.append(f)
            all_fixtures = filtered
        return all_fixtures
    
    def _days_in_month(self, month_idx):
        """Days in month (0-11)."""
        if month_idx in (0, 2, 4, 6, 7, 9, 11):
            return 31
        if month_idx in (3, 5, 8, 10):
            return 30
        return 28
    
    def load_fixtures(self):
        """Load and render one month only: full-screen grid of day tiles (1-30/31), each showing that day's matches."""
        if not self.game_engine:
            return
        
        self.sim_all_btn.setEnabled(True)
        self.sim_all_btn.setText("Sim All Visible")
        self.wc_stats_btn.setVisible(False)
        
        wc_name = getattr(self.game_engine, 'wc_name', 'World Cup')
        wc_host = getattr(self.game_engine, 'wc_host', '')
        if wc_host:
            self.wc_btn.setText(f"World Cup (Host: {wc_host})")
        else:
            self.wc_btn.setText("World Cup")
        
        if self.current_tier == 6:
            wc_fixtures, wc_format = self._get_wc_fixtures_all_formats()
            if wc_fixtures:
                phase = self._get_wc_phase(wc_fixtures)
                if phase == 'groups_done':
                    self._generate_wc_knockouts(wc_fixtures, wc_format)
                elif phase == 'knockouts':
                    semis = [f for f in wc_fixtures if f.get('round') == 'Semi-Final']
                    if semis and all(f.get('completed') for f in semis):
                        finals = [f for f in wc_fixtures if f.get('round') == 'Final']
                        if not finals:
                            self._generate_wc_final(wc_fixtures, wc_format)
                elif phase == 'completed':
                    self.wc_stats_btn.setVisible(True)
        
        self._check_multi_nation_finals()
        
        all_fixtures = self._gather_all_fixtures()
        
        # Do NOT auto-advance month when current month is complete: user must use Prev/Next or month dropdown.
        # This allows viewing previous months and opening scorecards of simulated games after simulating forward.
        
        # Clear calendar and day-tile refs (for simulate-tile highlighting)
        self._day_tile_widgets = {}
        self._clear_layout_items(self.calendar_layout)
        
        month_idx = self._current_month_index
        month_name = MONTH_NAMES[month_idx]
        days_count = self._days_in_month(month_idx)
        
        # Fixtures for this month only (and any without month go to month 0 for display)
        this_month = [f for f in all_fixtures if f.get('month') == month_idx]
        no_month = [f for f in all_fixtures if f.get('month') is None or f.get('month') < 0]
        if no_month and month_idx == 0:
            this_month = this_month + no_month
        
        # Group by day
        by_day = {}
        for f in this_month:
            d = f.get('day', 1)
            if 1 <= d <= days_count:
                by_day.setdefault(d, []).append(f)
        
        # Update fixed month navigation controls.
        year = getattr(self.game_engine, 'current_year', 2025)
        if hasattr(self, 'month_combo'):
            self.month_combo.blockSignals(True)
            self.month_combo.setCurrentIndex(month_idx)
            self.month_combo.blockSignals(False)
        if hasattr(self, 'month_prev_btn'):
            self.month_prev_btn.setEnabled(month_idx > 0)
        if hasattr(self, 'month_next_btn'):
            self.month_next_btn.setEnabled(month_idx < 11)
        if hasattr(self, 'month_year_lbl'):
            self.month_year_lbl.setText(str(year))
        
        # Single grid: one cell per day, even spacing so no tiles are cut
        grid = QGridLayout()
        grid.setSpacing(4)
        grid.setContentsMargins(0, 4, 0, 8)
        
        try:
            weekday_py = calendar.weekday(year, month_idx + 1, 1)
            # Python calendar.weekday: Mon=0..Sun=6; our header is MON..SUN.
            start_col = weekday_py
        except Exception:
            start_col = 0
        
        self._match_cards = {}
        self._day_tile_widgets = {}
        day_tiles = {}
        for day in range(1, days_count + 1):
            day_tile = self._create_day_tile(day, month_name, by_day.get(day, []))
            day_tiles[day] = day_tile
            self._day_tile_widgets[(month_idx, day)] = day_tile
        
        for day in range(1, days_count + 1):
            cell_index = (day - 1) + start_col
            row = cell_index // 7
            col = cell_index % 7
            grid.addWidget(day_tiles[day], row, col)
        
        for c in range(start_col):
            empty = self._create_empty_day_cell()
            grid.addWidget(empty, 0, c)
        
        last_cell = (days_count - 1) + start_col
        last_row = last_cell // 7
        cells_after = 7 - (last_cell % 7 + 1)
        for c in range(7 - cells_after, 7):
            empty = self._create_empty_day_cell()
            grid.addWidget(empty, last_row, c)
        
        # Columns share width equally; rows use minimum height from tiles so nothing is cut
        for col in range(7):
            grid.setColumnStretch(col, 1)
        for r in range(0, last_row + 1):
            grid.setRowStretch(r, 0)
        
        self.calendar_layout.addLayout(grid, 1)
        # Ensure content is tall enough to require scrolling for lower rows.
        self.calendar_widget.setMinimumHeight(220 + (last_row + 1) * 120)
    
    def _go_prev_month(self):
        if self._current_month_index > 0:
            self._current_month_index -= 1
            self.load_fixtures()
    
    def _go_next_month(self):
        if self._current_month_index < 11:
            self._current_month_index += 1
            self.load_fixtures()
    
    def _on_month_selected(self, index):
        """Jump to selected month (1–12) so user can view any month."""
        if 0 <= index <= 11 and index != self._current_month_index:
            self._current_month_index = index
            self.load_fixtures()
    
    def _create_empty_day_cell(self):
        """Single-panel placeholder for slots before/after month – no inner tile, same surface as grid."""
        empty = QFrame()
        border_c = '#7A2331'
        bg = '#151c29'
        empty.setStyleSheet(
            "QFrame { background-color: %s; border: 1px solid %s; border-radius: 2px; }" % (bg, border_c)
        )
        empty.setMinimumHeight(80)
        return empty
    
    def _team_color(self, team_name):
        """Return hex color for team/country; fallback to default."""
        if not team_name:
            return DEFAULT_TEAM_COLOR
        name = (team_name.replace(" U21", "").strip() if isinstance(team_name, str) else "") or ""
        return TEAM_COLORS.get(name, TEAM_COLORS.get(team_name, DEFAULT_TEAM_COLOR))
    
    def _highlight_day_tile(self, month, day, on=True):
        """Highlight or unhighlight the day tile at (month, day) during simulate-till-date or range sim."""
        widget = getattr(self, '_day_tile_widgets', {}).get((month, day))
        if not widget:
            return
        prim = COLORS.get('primary') or '#2E7D32'
        success = COLORS.get('success') or '#4CAF50'
        border_c = COLORS.get('border_light') or '#2a3446'
        bg = COLORS.get('bg_secondary') or '#111827'
        if on:
            widget.setStyleSheet(
                "QFrame { background-color: rgba(20,45,30,0.92); border: 2px solid %s; border-radius: 3px; } "
                "QLabel { background: transparent; } QPushButton { background: transparent; }"
                % success
            )
        else:
            widget.setStyleSheet(
                "QFrame { background-color: %s; border: 1px solid %s; border-radius: 3px; } "
                "QLabel { background: transparent; } QPushButton { background: transparent; }"
                % (bg, border_c)
            )
        QApplication.processEvents()
    
    def _shorten_team_name(self, name, max_len=10):
        """Abbreviate long names so tile text fits."""
        if not name or len(name) <= max_len:
            return name or ""
        parts = name.split()
        if len(parts) >= 2:
            return parts[0][:4] + "." + parts[-1][:4] if len(parts[-1]) >= 2 else name[:max_len]
        return name[:max_len - 1] + "."
    
    def _create_day_tile(self, day, month_name, fixtures):
        """Single-panel day cell: no tile-in-tile. No-match days = one flat panel; match days = country-colored border."""
        tile = QFrame()
        border_c = '#7A2331'
        txt_pri = '#EAF1FF'
        fmt_t20 = COLORS.get('accent') or '#E74C3C'
        fmt_odi = COLORS.get('secondary') or '#1976D2'
        fmt_test = COLORS.get('success') or '#2E7D32'
        
        if not fixtures:
            # No match: dark board-style panel
            bg = '#192235'
            tile.setStyleSheet(
                "QFrame { background-color: %s; border: 1px solid %s; border-radius: 2px; }" % (bg, border_c)
            )
            layout = QVBoxLayout()
            layout.setSpacing(0)
            layout.setContentsMargins(8, 8, 8, 8)
            day_lbl = QLabel(str(day))
            day_lbl.setStyleSheet(
                "font-size: 18px; font-weight: 900; color: rgba(234, 241, 255, 0.45); background: transparent; border: none;"
            )
            day_lbl.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
            layout.addWidget(day_lbl, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
            date_lbl = QLabel(f"{day} {month_name[:3]}")
            date_lbl.setStyleSheet("font-size: 11px; font-weight: 700; color: rgba(232,241,255,0.82); background: transparent; border: none;")
            layout.addWidget(date_lbl, 0, Qt.AlignmentFlag.AlignLeft)
            tile.setLayout(layout)
            tile.setMinimumHeight(80)
            return tile
        
        # Match day: panel with format-colored left border and team colors
        home_team = fixtures[0].get('team1') or fixtures[0].get('home_team')
        away_team = fixtures[0].get('team2') or fixtures[0].get('away_team')
        home_name = home_team.name if hasattr(home_team, 'name') else fixtures[0].get('home', '')
        away_name = away_team.name if hasattr(away_team, 'name') else fixtures[0].get('away', '')
        bg = '#111827'
        tile.setStyleSheet(
            "QFrame { background-color: %s; border: 1px solid %s; border-radius: 2px; } "
            "QLabel { background: transparent; color: white; }"
            % (bg, border_c)
        )
        layout = QVBoxLayout()
        layout.setSpacing(3)
        layout.setContentsMargins(8, 8, 8, 8)
        
        day_lbl = QLabel(str(day))
        day_lbl.setStyleSheet(
            "font-size: 17px; font-weight: 900; color: rgba(255, 255, 255, 0.92); background: transparent; border: none;"
        )
        day_lbl.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        layout.addWidget(day_lbl, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        date_lbl = QLabel(f"{day} {month_name[:3]}")
        date_lbl.setStyleSheet("font-size: 11px; font-weight: 700; color: rgba(232,241,255,0.95); background: transparent; border: none;")
        layout.addWidget(date_lbl, 0, Qt.AlignmentFlag.AlignLeft)
        
        for f in fixtures:
            home_team = f.get('team1') or f.get('home_team')
            away_team = f.get('team2') or f.get('away_team')
            home_name = home_team.name if hasattr(home_team, 'name') else f.get('home', 'TBD')
            away_name = away_team.name if hasattr(away_team, 'name') else f.get('away', 'TBD')
            fmt = (f.get('format') or '').strip().upper()
            is_done = f.get('completed', False)
            winner = f.get('winner', '')
            margin = f.get('margin', '') or ''
            fmt_color = fmt_test if fmt == 'TEST' else (fmt_odi if fmt == 'ODI' else fmt_t20)
            
            h = self._shorten_team_name(home_name, 12)
            a = self._shorten_team_name(away_name, 12)
            teams_text = "%s v %s" % (h, a)
            if fmt:
                # Show format without brackets for a cleaner look
                teams_text += " " + fmt
            
            match_btn = QPushButton(teams_text)
            match_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            match_btn.setFlat(True)
            match_btn.setMinimumHeight(32)
            match_btn.setStyleSheet(
                "QPushButton { text-align: left; font-size: 10px; font-weight: 700; color: %s; "
                "border: 1px solid rgba(255,255,255,0.18); background: rgba(255,255,255,0.08); "
                "padding: 4px 6px; border-left: 4px solid %s; border-radius: 2px; margin-left: 0px; } "
                "QPushButton:hover { background-color: rgba(255,255,255,0.18); color: #ffffff; }"
                % (txt_pri, fmt_color)
            )
            match_btn.setToolTip("%s vs %s (%s) - Click to %s" % (
                home_name, away_name, fmt or "?", "view scorecard" if is_done else "Simulate or Play"
            ))
            match_btn.clicked.connect(lambda checked, fix=f: self._on_match_tile_clicked(fix))
            layout.addWidget(match_btn)
            
            if is_done and (winner or margin):
                result_text = winner if winner else margin
                if margin and winner:
                    result_text = "%s (%s)" % (winner, margin)
                if len(result_text) > 28:
                    result_text = result_text[:25] + "…"
                res_lbl = QLabel(result_text)
                res_lbl.setStyleSheet(
                    "font-size: 10px; color: rgba(220,240,255,0.95); font-weight: 700; background: transparent; border: none;"
                )
                res_lbl.setWordWrap(True)
                layout.addWidget(res_lbl)
                # Additional match summary line for completed fixtures
                sc = f.get('scorecard') or {}
                inns = sc.get('innings', []) if isinstance(sc, dict) else []
                if len(inns) >= 2:
                    h_runs = inns[0].get('total_runs', 0)
                    h_wk = inns[0].get('wickets_fallen', 0)
                    a_runs = inns[1].get('total_runs', 0)
                    a_wk = inns[1].get('wickets_fallen', 0)
                    summ = f"{h}:{h_runs}/{h_wk}  {a}:{a_runs}/{a_wk}"
                    if len(summ) > 36:
                        summ = summ[:33] + "…"
                    sum_lbl = QLabel(summ)
                    sum_lbl.setStyleSheet(
                        "font-size: 8px; color: rgba(200,220,255,0.86); background: transparent; border: none;"
                    )
                    sum_lbl.setWordWrap(True)
                    layout.addWidget(sum_lbl)
        
        tile.setLayout(layout)
        tile.setMinimumHeight(max(80, 56 + len(fixtures) * 40))
        return tile
    
    def _create_month_card(self, month_name, fixtures, is_wc_month=False):
        """Create a calendar month card with series-grouped fixtures."""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #111827;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
        """)
        card_layout = QVBoxLayout()
        card_layout.setSpacing(8)
        card_layout.setContentsMargins(15, 12, 15, 12)
        
        # Month header
        header_color = COLORS['gold'] if is_wc_month else COLORS['primary']
        wc_tag = " 🏆 World Cup Month" if is_wc_month else ""
        header = QLabel(f"📅 {month_name}{wc_tag}")
        header.setStyleSheet(f"""
            font-size: 18px; font-weight: bold; color: {header_color};
            padding: 8px 0; border-bottom: 2px solid {header_color};
        """)
        card_layout.addWidget(header)
        
        # Group fixtures by series_id (or tour_id), falling back to individual
        series_groups = {}
        ungrouped = []
        for f in fixtures:
            sid = f.get('series_id') or f.get('tour_id')
            if sid:
                if sid not in series_groups:
                    series_groups[sid] = []
                series_groups[sid].append(f)
            else:
                ungrouped.append(f)
        
        # Render series groups
        for sid, series_fixtures in series_groups.items():
            series_fixtures.sort(key=lambda x: x.get('match_number', 0))
            first = series_fixtures[0]
            tour_name = first.get('tour_name', '')
            series_name = first.get('series_name', tour_name)
            fmt = first.get('format', '')
            total = first.get('total_matches', len(series_fixtures))
            
            # Determine host name
            host_team = first.get('home_team')
            host_name = host_team.name if hasattr(host_team, 'name') else first.get('home', '')
            
            # Check if series is complete
            all_completed = all(f.get('completed', False) for f in series_fixtures)
            
            # Build display text
            fmt_colors = {'T20': '#E91E63', 'ODI': '#1976D2', 'Test': '#2E7D32'}
            fmt_color = fmt_colors.get(fmt, COLORS['text_primary'])
            
            if all_completed:
                # Calculate series winner from match results
                win_counts = {}
                for f in series_fixtures:
                    w = f.get('winner', '')
                    if w and w not in ('Draw', 'Tie', 'N/A'):
                        win_counts[w] = win_counts.get(w, 0) + 1
                if win_counts:
                    series_winner = max(win_counts, key=win_counts.get)
                    best = win_counts[series_winner]
                    # Check for drawn series
                    counts_list = sorted(win_counts.values(), reverse=True)
                    if len(counts_list) > 1 and counts_list[0] == counts_list[1]:
                        winner_text = "Series Drawn"
                    else:
                        winner_text = f"Winner: {series_winner} {best}-{total - best}"
                else:
                    winner_text = "Series Drawn"
                
                header_text = f"  🏏 {tour_name} — {total}-match {fmt} Series (🏆 {winner_text})"
                
                # Clickable label for completed series
                series_header = QPushButton(header_text)
                series_header.setStyleSheet(f"""
                    QPushButton {{
                        font-size: 14px; font-weight: bold; color: {fmt_color};
                        padding: 6px 4px 2px 4px; text-align: left; border: none;
                        background: transparent;
                    }}
                    QPushButton:hover {{
                        color: {COLORS['primary']}; text-decoration: underline;
                    }}
                """)
                series_header.setCursor(Qt.CursorShape.PointingHandCursor)
                series_header.clicked.connect(
                    lambda checked, sf=list(series_fixtures), sn=tour_name, f=fmt: self.show_series_stats(sf, sn, f)
                )
            else:
                header_text = f"  🏏 {tour_name} — {total}-match {fmt} Series (Host: {host_name})"
                series_header = QLabel(header_text)
                series_header.setStyleSheet(f"""
                    font-size: 14px; font-weight: bold; color: {fmt_color};
                    padding: 6px 0 2px 0;
                """)
            
            card_layout.addWidget(series_header)
            
            # Individual matches in the series
            for f in series_fixtures:
                match_row = self._create_match_row(f)
                card_layout.addWidget(match_row)
        
        # Render ungrouped fixtures (WC matches, legacy)
        for f in ungrouped:
            match_row = self._create_match_row(f)
            card_layout.addWidget(match_row)
        
        card.setLayout(card_layout)
        return card
    
    def _create_match_row(self, fixture):
        """Create a single match row widget with play/sim buttons."""
        row = QFrame()
        row.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_primary']};
                border-radius: 5px;
                padding: 4px;
            }}
            QFrame:hover {{
                background-color: {COLORS['bg_hover']};
            }}
        """)
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(8)
        
        # Match number / day + date
        match_num = fixture.get('match_number', '')
        total = fixture.get('total_matches', '')
        day = fixture.get('day', '')
        month_name = fixture.get('month_name', '')
        wc_round = fixture.get('round', '')
        
        # Build date string (e.g. "12 Jan")
        month_abbr = month_name[:3] if month_name else ''
        date_str = f"{day} {month_abbr}" if day and month_abbr else ''
        
        if wc_round:
            date_text = f"{wc_round}  {date_str}" if date_str else wc_round
        elif match_num and total:
            date_text = f"Match {match_num}/{total}  {date_str}" if date_str else f"Match {match_num}/{total}"
        elif date_str:
            date_text = date_str
        else:
            date_text = ""
        
        date_label = QLabel(date_text)
        date_label.setFixedWidth(150)
        date_label.setStyleSheet(f"font-size: 11px; color: {COLORS['text_secondary']}; font-weight: bold;")
        layout.addWidget(date_label)
        
        # Home team
        home_team = fixture.get('team1') or fixture.get('home_team')
        home_name = home_team.name if hasattr(home_team, 'name') else fixture.get('home', str(home_team) if home_team else 'TBD')
        home_label = QLabel(f"🏠 {home_name}")
        home_label.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {COLORS['text_primary']};")
        home_label.setFixedWidth(160)
        layout.addWidget(home_label)
        
        # VS
        vs_label = QLabel("vs")
        vs_label.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']}; font-weight: bold;")
        vs_label.setFixedWidth(25)
        vs_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(vs_label)
        
        # Away team
        away_team = fixture.get('team2') or fixture.get('away_team')
        away_name = away_team.name if hasattr(away_team, 'name') else fixture.get('away', str(away_team) if away_team else 'TBD')
        away_label = QLabel(away_name)
        away_label.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {COLORS['text_primary']};")
        away_label.setFixedWidth(160)
        layout.addWidget(away_label)
        
        # Format badge
        fmt = fixture.get('format', '')
        fmt_colors = {'T20': '#E91E63', 'ODI': '#1976D2', 'Test': '#2E7D32'}
        fmt_bg = fmt_colors.get(fmt, COLORS['text_secondary'])
        fmt_label = QLabel(fmt)
        fmt_label.setFixedWidth(45)
        fmt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fmt_label.setStyleSheet(f"""
            background-color: {fmt_bg}; color: white; border-radius: 3px;
            padding: 3px 6px; font-size: 11px; font-weight: bold;
        """)
        layout.addWidget(fmt_label)
        
        # Status
        is_completed = fixture.get('completed', False)
        status_text = fixture.get('status', 'Scheduled')
        winner = fixture.get('winner', '')
        if is_completed and winner:
            status_text = f"Won: {winner}"
        
        status_label = QLabel(status_text)
        status_label.setFixedWidth(140)
        status_color = COLORS['success'] if is_completed else COLORS['text_secondary']
        status_label.setStyleSheet(f"font-size: 11px; color: {status_color};")
        layout.addWidget(status_label)
        
        layout.addStretch()
        
        # Action buttons
        btn_style_play = f"""
            QPushButton {{ background-color: {COLORS['success']}; color: white; padding: 5px 12px; border: none; border-radius: 4px; font-weight: bold; font-size: 11px; }}
            QPushButton:hover {{ background-color: {COLORS['secondary']}; }}
        """
        btn_style_sim = f"""
            QPushButton {{ background-color: {COLORS['info']}; color: white; padding: 5px 12px; border: none; border-radius: 4px; font-weight: bold; font-size: 11px; }}
            QPushButton:hover {{ background-color: {COLORS['primary']}; }}
        """
        btn_style_done = f"""
            QPushButton {{ background-color: {COLORS['primary']}; color: white; padding: 5px 12px; border: none; border-radius: 4px; font-weight: bold; font-size: 11px; }}
            QPushButton:hover {{ background-color: {COLORS['secondary']}; }}
        """
        
        if is_completed:
            if fixture.get('scorecard'):
                sc_btn = QPushButton("📋 Scorecard")
                sc_btn.setStyleSheet(btn_style_done)
                sc_btn.clicked.connect(lambda checked, f=fixture: self.show_scorecard_dialog(f['scorecard']))
                layout.addWidget(sc_btn)
            else:
                done_btn = QPushButton("✅ Done")
                done_btn.setEnabled(False)
                done_btn.setStyleSheet(f"QPushButton {{ background-color: #bbb; color: white; padding: 5px 12px; border: none; border-radius: 4px; }}")
                layout.addWidget(done_btn)
        else:
            # Play button
            is_u21 = fixture.get('is_u21', False) or (fixture.get('team1') is None and fixture.get('team2') is None)
            play_btn = QPushButton("🎮 Play U21" if is_u21 else "🎮 Play")
            play_btn.setStyleSheet(btn_style_play)
            if is_u21:
                play_btn.clicked.connect(lambda checked, f=fixture: self.play_u21_match(f))
            else:
                play_btn.clicked.connect(lambda checked, f=fixture: self.play_match(f))
            layout.addWidget(play_btn)
            
            # Quick Sim button
            sim_btn = QPushButton("⚡ Sim")
            sim_btn.setStyleSheet(btn_style_sim)
            sim_btn.clicked.connect(lambda checked, f=fixture: self.quick_sim_match(f))
            layout.addWidget(sim_btn)
        
        row.setLayout(layout)
        return row
    
    # ========================================================================
    # NBA 2K24-STYLE HORIZONTAL CALENDAR RENDERING
    # ========================================================================
    
    def _create_month_strip(self, month_name, fixtures, is_wc_month=False, month_idx=0):
        """Create a horizontal month strip with match cards in NBA 2K24 style."""
        strip = QFrame()
        strip.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
                margin: 2px 0;
            }}
        """)
        strip_layout = QVBoxLayout()
        strip_layout.setSpacing(6)
        strip_layout.setContentsMargins(12, 8, 12, 8)
        
        # Month header row
        header_row = QHBoxLayout()
        
        header_color = COLORS['gold'] if is_wc_month else COLORS['primary']
        wc_tag = "  🏆" if is_wc_month else ""
        
        month_label = QLabel(f"📅 {month_name}{wc_tag}")
        month_label.setStyleSheet(f"""
            font-size: 16px; font-weight: bold; color: {header_color};
        """)
        header_row.addWidget(month_label)
        
        completed = sum(1 for f in fixtures if f.get('completed'))
        total = len(fixtures)
        count_label = QLabel(f"{completed}/{total} played")
        count_color = COLORS['success'] if completed == total else COLORS['text_secondary']
        count_label.setStyleSheet(f"font-size: 12px; color: {count_color}; font-weight: bold;")
        header_row.addStretch()
        header_row.addWidget(count_label)
        
        strip_layout.addLayout(header_row)
        
        # Thin progress bar for this month
        month_bar = QFrame()
        month_bar.setFixedHeight(4)
        pct = int((completed / total) * 100) if total > 0 else 0
        month_bar.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['success']}, stop:{pct/100.0} {COLORS['success']},
                    stop:{min(pct/100.0 + 0.01, 1.0)} {COLORS['border']}, stop:1 {COLORS['border']});
                border-radius: 2px;
            }}
        """)
        strip_layout.addWidget(month_bar)
        
        # Horizontal scroll area with match cards
        h_scroll = QScrollArea()
        h_scroll.setWidgetResizable(True)
        h_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        h_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        h_scroll.setFixedHeight(195)
        h_scroll.setStyleSheet(f"""
            QScrollArea {{ border: none; background: transparent; }}
            QScrollBar:horizontal {{ 
                height: 8px; background: {COLORS['bg_primary']}; border-radius: 4px;
            }}
            QScrollBar::handle:horizontal {{ 
                background: {COLORS['primary']}; border-radius: 4px; min-width: 30px;
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
        """)
        
        cards_container = QWidget()
        cards_container.setStyleSheet("background: transparent;")
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(10)
        cards_layout.setContentsMargins(5, 2, 5, 2)
        
        # Group fixtures by series for display, maintaining chronological order
        fixtures.sort(key=lambda f: (f.get('day', 1), f.get('match_number', 0)))
        
        for fixture in fixtures:
            card = self._create_match_card(fixture)
            cards_layout.addWidget(card)
            fix_id = id(fixture)
            self._match_cards[fix_id] = card
        
        cards_layout.addStretch()
        cards_container.setLayout(cards_layout)
        h_scroll.setWidget(cards_container)
        
        strip_layout.addWidget(h_scroll)
        
        strip.setLayout(strip_layout)
        return strip
    
    def _create_match_card(self, fixture):
        """Create a compact match card for the NBA 2K24-style horizontal calendar.
        Clicking the tile simulates all fixtures till this match date, then offers Play or Quick Sim."""
        card = QFrame()
        card.setFixedSize(175, 170)
        
        is_completed = fixture.get('completed', False)
        fmt = fixture.get('format', '')
        fmt_colors = {'T20': '#E91E63', 'ODI': '#1976D2', 'Test': '#2E7D32'}
        fmt_color = fmt_colors.get(fmt, COLORS['text_secondary'])
        
        wc_round = fixture.get('round', '')
        is_wc = fixture.get('is_world_cup', False)
        is_final = wc_round in ('Final', 'Semi-Final')
        
        if is_completed:
            bg_color = '#E8F5E9'
            border_color = COLORS['success']
        elif is_final or is_wc:
            bg_color = '#FFF8E1'
            border_color = COLORS['gold']
        else:
            bg_color = COLORS['bg_secondary']
            border_color = fmt_color
        
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 2px solid {border_color};
                border-radius: 10px;
            }}
            QFrame:hover {{
                border: 2px solid {COLORS['secondary']};
                background-color: {COLORS['bg_hover']};
            }}
        """)
        
        card_layout = QVBoxLayout()
        card_layout.setSpacing(3)
        card_layout.setContentsMargins(8, 6, 8, 6)
        
        # Clickable tile area: simulates all till this match, then offers Play / Quick Sim
        tile_btn = QPushButton()
        tile_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        tile_btn.setFlat(True)
        tile_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; border: none; border-radius: 6px;
                text-align: center; padding: 4px 2px;
            }}
            QPushButton:hover {{ background-color: rgba(0,0,0,0.06); }}
            QPushButton:pressed {{ background-color: rgba(0,0,0,0.1); }}
        """)
        tile_btn.setToolTip("Click: simulate all matches till this date (including previous months), then Play or Quick Sim")
        
        tile_inner = QVBoxLayout()
        tile_inner.setSpacing(2)
        tile_inner.setContentsMargins(4, 2, 4, 2)
        
        day = fixture.get('day', '')
        month_name = fixture.get('month_name', '')
        month_abbr = month_name[:3] if month_name else ''
        date_str = f"{day} {month_abbr}" if day and month_abbr else ''
        if wc_round:
            date_str = wc_round
        
        date_label = QLabel(date_str)
        date_label.setStyleSheet(f"font-size: 10px; color: {COLORS['text_secondary']}; font-weight: bold;")
        date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tile_inner.addWidget(date_label)
        
        fmt_badge = QLabel(fmt)
        fmt_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fmt_badge.setStyleSheet(f"""
            background-color: {fmt_color}; color: white; border-radius: 3px;
            padding: 1px 4px; font-size: 9px; font-weight: bold;
        """)
        tile_inner.addWidget(fmt_badge, alignment=Qt.AlignmentFlag.AlignCenter)
        
        series_name = fixture.get('tour_name', fixture.get('series_name', ''))
        if series_name:
            series_label = QLabel(series_name[:22] + ".." if len(series_name) > 22 else series_name)
            series_label.setStyleSheet(f"font-size: 8px; color: {fmt_color}; font-weight: bold;")
            series_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tile_inner.addWidget(series_label)
        
        home_team = fixture.get('team1') or fixture.get('home_team')
        home_name = home_team.name if hasattr(home_team, 'name') else fixture.get('home', str(home_team) if home_team else 'TBD')
        home_label = QLabel(f"🏠 {home_name}")
        home_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        home_label.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {COLORS['text_primary']};")
        tile_inner.addWidget(home_label)
        
        vs_label = QLabel("vs")
        vs_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vs_label.setStyleSheet(f"font-size: 9px; color: {COLORS['text_secondary']};")
        tile_inner.addWidget(vs_label)
        
        away_team = fixture.get('team2') or fixture.get('away_team')
        away_name = away_team.name if hasattr(away_team, 'name') else fixture.get('away', str(away_team) if away_team else 'TBD')
        away_label = QLabel(away_name)
        away_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        away_label.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {COLORS['text_primary']};")
        tile_inner.addWidget(away_label)
        
        tile_btn.setLayout(tile_inner)
        tile_btn.clicked.connect(lambda checked, f=fixture: self._on_match_tile_clicked(f))
        card_layout.addWidget(tile_btn)
        
        # Status / Result row
        if is_completed:
            winner = fixture.get('winner', '')
            result_text = f"✅ {winner}" if winner and winner not in ('Draw', 'Tie') else "🤝 Draw"
            result_label = QLabel(result_text)
            result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            result_label.setStyleSheet(f"font-size: 9px; color: {COLORS['success']}; font-weight: bold;")
            card_layout.addWidget(result_label)
            
            if fixture.get('scorecard'):
                sc_btn = QPushButton("📋")
                sc_btn.setFixedSize(30, 22)
                sc_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                sc_btn.setStyleSheet(f"""
                    QPushButton {{ background: {COLORS['primary']}; color: white; border: none; border-radius: 4px; font-size: 10px; }}
                    QPushButton:hover {{ background: {COLORS['secondary']}; }}
                """)
                sc_btn.clicked.connect(lambda checked, f=fixture: self.show_scorecard_dialog(f['scorecard']))
                btn_row = QHBoxLayout()
                btn_row.addStretch()
                btn_row.addWidget(sc_btn)
                btn_row.addStretch()
                card_layout.addLayout(btn_row)
        else:
            # Play + Sim buttons (direct action on this match only)
            btn_row = QHBoxLayout()
            btn_row.setSpacing(4)
            
            is_u21 = fixture.get('is_u21', False) or (fixture.get('team1') is None and fixture.get('team2') is None)
            
            play_btn = QPushButton("🎮")
            play_btn.setFixedSize(35, 24)
            play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            play_btn.setToolTip("Play Match")
            play_btn.setStyleSheet(f"""
                QPushButton {{ background: {COLORS['success']}; color: white; border: none; border-radius: 4px; font-size: 11px; }}
                QPushButton:hover {{ background: {COLORS['secondary']}; }}
            """)
            if is_u21:
                play_btn.clicked.connect(lambda checked, f=fixture: self.play_u21_match(f))
            else:
                play_btn.clicked.connect(lambda checked, f=fixture: self.play_match(f))
            
            sim_btn = QPushButton("⚡")
            sim_btn.setFixedSize(35, 24)
            sim_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            sim_btn.setToolTip("Quick Simulate")
            sim_btn.setStyleSheet(f"""
                QPushButton {{ background: {COLORS['info']}; color: white; border: none; border-radius: 4px; font-size: 11px; }}
                QPushButton:hover {{ background: {COLORS['primary']}; }}
            """)
            sim_btn.clicked.connect(lambda checked, f=fixture: self.quick_sim_match(f))
            
            btn_row.addStretch()
            btn_row.addWidget(play_btn)
            btn_row.addWidget(sim_btn)
            btn_row.addStretch()
            card_layout.addLayout(btn_row)
        
        card.setLayout(card_layout)
        return card
    
    def _fixture_before(self, f, target):
        """True if fixture f is strictly before target in chronological order."""
        m_f, d_f = f.get('month', -1), f.get('day', 1)
        m_t, d_t = target.get('month', -1), target.get('day', 1)
        if m_f < 0 or m_t < 0:
            return False
        key_f = (m_f, d_f, f.get('match_number', 0), id(f))
        key_t = (m_t, d_t, target.get('match_number', 0), id(target))
        return key_f < key_t
    
    def _on_match_tile_clicked(self, fixture):
        """If completed: show scorecard. Else: show Simulate/Play dialog; on Play/Sim run all matches 1st to (day-1) then action."""
        if fixture.get('completed', False):
            sc = fixture.get('scorecard')
            if not sc:
                same = self._find_same_fixture(fixture)
                if same and same.get('scorecard'):
                    sc = same['scorecard']
            if sc:
                self.show_scorecard_dialog(sc)
            return
        
        self._show_play_or_sim_dialog(fixture)
    
    def _find_same_fixture(self, fixture):
        """Return the fixture from engine that matches (month, day, teams) for scorecard lookup."""
        all_fixtures = self._gather_all_fixtures()
        m, d = fixture.get('month'), fixture.get('day')
        t1 = fixture.get('team1') or fixture.get('home_team')
        t2 = fixture.get('team2') or fixture.get('away_team')
        for x in all_fixtures:
            if x.get('month') != m or x.get('day') != d:
                continue
            xt1 = x.get('team1') or x.get('home_team')
            xt2 = x.get('team2') or x.get('away_team')
            if (xt1 == t1 and xt2 == t2) or (getattr(xt1, 'name', None) == getattr(t1, 'name', None) and getattr(xt2, 'name', None) == getattr(t2, 'name', None)):
                return x
        return None
    
    def _show_play_or_sim_dialog(self, fixture):
        """Show dialog: Simulate or Play. When user picks Play or Sim: simulate all matches from 1st to (this day - 1), then play/sim this match."""
        if fixture.get('completed', False):
            if fixture.get('scorecard'):
                self.show_scorecard_dialog(fixture['scorecard'])
            return
        
        home_team = fixture.get('team1') or fixture.get('home_team')
        away_team = fixture.get('team2') or fixture.get('away_team')
        home_name = home_team.name if hasattr(home_team, 'name') else fixture.get('home', 'TBD')
        away_name = away_team.name if hasattr(away_team, 'name') else fixture.get('away', 'TBD')
        
        dialog = QMessageBox(self)
        dialog.setWindowTitle("This match")
        dialog.setText(f"{home_name} vs {away_name}\n\nSimulate or Play this match? (All matches before this date, including in previous months, will be simulated first.)")
        dialog.setIcon(QMessageBox.Icon.Question)
        
        play_btn = dialog.addButton("Play", QMessageBox.ButtonRole.ActionRole)
        sim_btn = dialog.addButton("Quick Sim", QMessageBox.ButtonRole.ActionRole)
        cancel_btn = dialog.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        
        dialog.exec()
        clicked = dialog.clickedButton()
        
        if clicked == cancel_btn or clicked is None:
            return
        
        # Simulate all unplayed matches from 1st of month up to (but not including) this match's date; tile selection moves left to right
        all_fixtures = self._gather_all_fixtures()
        all_fixtures.sort(key=lambda f: (f.get('month', 0), f.get('day', 1), f.get('match_number', 0)))
        before = [f for f in all_fixtures if not f.get('completed') and self._fixture_before(f, fixture)]
        
        from cricket_manager.core.fast_match_simulator import FastMatchSimulator
        for f in before:
            m, d = f.get('month'), f.get('day')
            self._highlight_day_tile(m, d, True)
            try:
                if f.get('team1') is None and f.get('team2') is None:
                    self.simulate_u21_match(f)
                else:
                    self._sim_fixture(f, FastMatchSimulator)
                self._check_multi_nation_finals()
            except Exception as e:
                print(f"[Fixtures] Error simulating match before tile: {e}")
            self._highlight_day_tile(m, d, False)
        
        if before:
            self.load_fixtures()
            self.refresh_leagues_screen()
            if self.screen_manager:
                stats_screen = self.screen_manager.screens.get("Statistics")
                if stats_screen and hasattr(stats_screen, 'refresh_data'):
                    stats_screen.refresh_data()
        
        # Use engine fixture so completed/scorecard updates persist (same object Statistics uses)
        target = self._find_same_fixture(fixture) or fixture
        
        if clicked == play_btn:
            if target.get('completed'):
                if target.get('scorecard'):
                    self.show_scorecard_dialog(target['scorecard'])
            elif target.get('is_u21', False) or (target.get('team1') is None and target.get('team2') is None):
                self.play_u21_match(target)
            else:
                self.play_match(target)
        elif clicked == sim_btn:
            if not target.get('completed'):
                self.quick_sim_match(target)
        
        self.load_fixtures()
        self.refresh_leagues_screen()
    
    # ========================================================================
    # DATE RANGE SIMULATION (NBA 2K24-style left-to-right)
    # ========================================================================
    
    def _fixture_in_date_range(self, fixture, from_month, from_day, to_month, to_day):
        """Check if a fixture falls within the given date range."""
        f_month = fixture.get('month', -1)
        f_day = fixture.get('day', 1)
        
        if f_month < 0:
            return False
        
        f_val = f_month * 100 + f_day
        from_val = from_month * 100 + from_day
        to_val = to_month * 100 + to_day
        
        return from_val <= f_val <= to_val
    
    def simulate_date_range(self):
        """Simulate all matches in the selected date range, progressing left to right (NBA 2K24 style)."""
        from_month = self.from_month_combo.currentIndex()
        from_day = int(self.from_day_combo.currentText())
        to_month = self.to_month_combo.currentIndex()
        to_day = int(self.to_day_combo.currentText())
        
        all_fixtures = self._gather_all_fixtures()
        
        in_range = [f for f in all_fixtures
                    if not f.get('completed') and self._fixture_in_date_range(f, from_month, from_day, to_month, to_day)]
        
        in_range.sort(key=lambda f: (f.get('month', 0), f.get('day', 1)))
        
        if not in_range:
            QMessageBox.information(self, "No Matches",
                                   "No unplayed matches found in the selected date range.")
            return
        
        from_name = MONTH_NAMES[from_month][:3]
        to_name = MONTH_NAMES[to_month][:3]
        reply = QMessageBox.question(
            self, "Simulate Range",
            f"Simulate {len(in_range)} matches from {from_day} {from_name} to {to_day} {to_name}?\n\n"
            f"Matches will be simulated from left to right.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        self._sim_queue = list(in_range)
        self._sim_queue_total = len(in_range)
        self._sim_queue_done = 0
        
        self.sim_range_btn.setEnabled(False)
        self.sim_range_btn.setText("Simulating...")
        
        from PyQt6.QtCore import QTimer
        self._range_sim_timer = QTimer()
        self._range_sim_timer.setInterval(200)
        self._range_sim_timer.timeout.connect(self._simulate_next_in_range)
        self._range_sim_timer.start()
    
    def _simulate_next_in_range(self):
        """Simulate the next match in the date range queue with visual progression."""
        if not self._sim_queue:
            if hasattr(self, '_range_sim_timer'):
                self._range_sim_timer.stop()
            self.sim_range_btn.setEnabled(True)
            self.sim_range_btn.setText("Simulate Range")
            self.sim_progress_label.setText(f"✅ Done! {self._sim_queue_done} matches simulated")
            
            self._check_multi_nation_finals()
            self.load_fixtures()
            self.refresh_leagues_screen()
            # Refresh Statistics tab so new stats from simulated matches are visible
            if self.screen_manager:
                stats_screen = self.screen_manager.screens.get("Statistics")
                if stats_screen and hasattr(stats_screen, 'refresh_data'):
                    stats_screen.refresh_data()
            
            QMessageBox.information(self, "Simulation Complete",
                                   f"Simulated {self._sim_queue_done} matches!")
            self.sim_progress_label.setText("")
            return
        
        fixture = self._sim_queue.pop(0)
        self._sim_queue_done += 1
        
        self.sim_progress_label.setText(
            f"▶ {self._sim_queue_done}/{self._sim_queue_total}"
        )
        
        m, d = fixture.get('month'), fixture.get('day')
        self._highlight_day_tile(m, d, True)
        
        from cricket_manager.core.fast_match_simulator import FastMatchSimulator
        
        try:
            if fixture.get('team1') is None and fixture.get('team2') is None:
                self.simulate_u21_match(fixture)
            else:
                self._sim_fixture(fixture, FastMatchSimulator)
                self._check_multi_nation_finals()
        except Exception as e:
            print(f"[DateRangeSim] Error simulating match: {e}")
        
        self._highlight_day_tile(m, d, False)
    
    # ========================================================================
    # MULTI-NATION SERIES FINALS (Tri-Nations / Quad-Nations)
    # ========================================================================
    
    def _check_multi_nation_finals(self):
        """After group matches complete, update Tri/Quad Nations final teams from standings."""
        if not self.game_engine:
            return
        
        for fmt in ['T20', 'ODI']:
            fixtures_list = self.game_engine.fixtures.get(fmt, [])
            
            for fixture in fixtures_list:
                if not fixture.get('needs_team_update'):
                    continue
                if fixture.get('completed'):
                    continue
                
                series_id = fixture.get('series_id')
                if not series_id:
                    continue
                
                group_matches = [f for f in fixtures_list
                                if f.get('series_id') == series_id
                                and f.get('round') == 'Group']
                
                if not group_matches or not all(g.get('completed') for g in group_matches):
                    continue
                
                standings = self._calculate_multi_nation_standings(group_matches)
                
                if len(standings) < 2:
                    continue
                
                top1_name = standings[0][0]
                top2_name = standings[1][0]
                top1 = self.game_engine.get_team_by_name(top1_name)
                top2 = self.game_engine.get_team_by_name(top2_name)
                
                if top1 and top2:
                    fixture['team1'] = top1
                    fixture['team2'] = top2
                    fixture['home'] = top1.name
                    fixture['away'] = top2.name
                    fixture['home_team'] = top1
                    fixture['needs_team_update'] = False
                    
                    mn_type = fixture.get('multi_nation_type', 'unknown')
                    print(f"[MultiNation] Updated {mn_type} Final: {top1.name} vs {top2.name} "
                          f"(from standings: {', '.join(s[0] for s in standings)})")
    
    def _calculate_multi_nation_standings(self, group_matches):
        """Calculate standings from group matches of a multi-nation series."""
        standings = {}
        
        for match in group_matches:
            home = match.get('home', '')
            away = match.get('away', '')
            winner = match.get('winner', '')
            
            for team_name in [home, away]:
                if team_name and team_name not in standings:
                    standings[team_name] = {
                        'points': 0, 'wins': 0, 'losses': 0,
                        'nrr': 0.0, 'runs_for': 0, 'runs_against': 0,
                        'overs_batted': 0, 'overs_bowled': 0
                    }
            
            if not home or not away:
                continue
            
            if winner == home:
                standings[home]['points'] += 2
                standings[home]['wins'] += 1
                standings[away]['losses'] += 1
            elif winner == away:
                standings[away]['points'] += 2
                standings[away]['wins'] += 1
                standings[home]['losses'] += 1
            elif winner and winner not in ('Draw', 'Tie', 'N/A'):
                pass
            else:
                standings.get(home, {})['points'] = standings.get(home, {}).get('points', 0) + 1
                standings.get(away, {})['points'] = standings.get(away, {}).get('points', 0) + 1
            
            sc = match.get('scorecard', {})
            if sc and 'innings' in sc and len(sc['innings']) >= 2:
                inn1 = sc['innings'][0]
                inn2 = sc['innings'][1]
                if home in standings and away in standings:
                    standings[home]['runs_for'] += inn1.get('total_runs', 0)
                    standings[home]['runs_against'] += inn2.get('total_runs', 0)
                    standings[home]['overs_batted'] += inn1.get('overs', 1)
                    standings[home]['overs_bowled'] += inn2.get('overs', 1)
                    standings[away]['runs_for'] += inn2.get('total_runs', 0)
                    standings[away]['runs_against'] += inn1.get('total_runs', 0)
                    standings[away]['overs_batted'] += inn2.get('overs', 1)
                    standings[away]['overs_bowled'] += inn1.get('overs', 1)
        
        for name, s in standings.items():
            if s['overs_batted'] > 0 and s['overs_bowled'] > 0:
                s['nrr'] = round(s['runs_for'] / s['overs_batted'] - s['runs_against'] / s['overs_bowled'], 3)
        
        sorted_standings = sorted(
            standings.items(),
            key=lambda x: (x[1]['points'], x[1]['nrr'], x[1]['wins']),
            reverse=True
        )
        
        return sorted_standings
    
    # ========================================================================
    # FILTER HANDLERS
    # ========================================================================
    
    def _refresh_team_combo(self):
        """Populate team combo with international or domestic teams depending on view."""
        self.team_combo.blockSignals(True)
        self.team_combo.clear()
        self.team_combo.addItem("All Teams")
        if self.game_engine:
            if self.show_domestic and getattr(self.game_engine, 'domestic_teams', None):
                names = sorted(set(t.name for t in self.game_engine.domestic_teams))
                self.team_combo.addItems(names)
            else:
                names = sorted([t.name for t in self.game_engine.all_teams])
                self.team_combo.addItems(names)
        self.team_combo.blockSignals(False)
    
    def on_view_changed(self, view_text):
        """Switch between International and Domestic fixture view."""
        self.show_domestic = (view_text == "Domestic")
        self._refresh_team_combo()
        self.load_fixtures()
    
    def on_format_changed(self, format_type):
        """Handle format change"""
        self.current_format = format_type
        self.sim_all_btn.setEnabled(True)
        self.load_fixtures()
    
    def _go_to_world_cup(self):
        """Switch to World Cup view"""
        self.tier_combo.setCurrentIndex(6)  # World Cup index
    
    def on_tier_changed(self, index):
        """Handle tier change"""
        # index: 0=All, 1=Tier1, 2=Tier2, 3=Tier3, 4=Tier4, 5=Tier5(U21), 6=WorldCup
        if index == 6:
            self.current_tier = 6  # World Cup
        elif index == 0:
            self.current_tier = 0  # All tiers
        else:
            self.current_tier = index  # Tier 1-5
        self.sim_all_btn.setEnabled(True)
        self.load_fixtures()
    
    def on_team_changed(self, team_name):
        """Handle team filter change"""
        self.load_fixtures()
    
    def play_match(self, fixture):
        """Play match using new professional match simulator"""
        # Check if already completed
        if fixture.get('completed', False):
            QMessageBox.information(self, "Match Completed", 
                                   "This match has already been played.")
            return
        
        # Get team objects
        home_team = fixture.get('team1') or fixture.get('home_team')
        away_team = fixture.get('team2') or fixture.get('away_team')
        
        if not home_team or not away_team:
            QMessageBox.warning(self, "Error", "Could not find teams")
            return
        
        # Launch original match simulator directly
        from cricket_manager.ui.match_launcher import launch_t20_match, launch_test_match
        
        # Extract pitch conditions from fixture for the simulator
        pitch_cond = self._get_fixture_pitch(fixture)
        
        try:
            match_format = fixture.get('format', 'T20')
            launch_result = None
            
            if match_format in ['T20', 'ODI']:
                launch_result = launch_t20_match(home_team, away_team, match_format, pitch_conditions=pitch_cond)
                if launch_result:
                    print(f"[Fixtures] Launched {match_format} match: {home_team.name} vs {away_team.name} (pitch: {fixture.get('pitch_region', 'random')})")
                else:
                    print(f"[Fixtures] Failed to launch {match_format} match")
                    
            elif match_format == 'Test':
                launch_result = launch_test_match(home_team, away_team, pitch_conditions=pitch_cond)
                if launch_result:
                    print(f"[Fixtures] Launched Test match: {home_team.name} vs {away_team.name} (pitch: {fixture.get('pitch_region', 'random')})")
                else:
                    print(f"[Fixtures] Failed to launch Test match")
            
            if launch_result:
                # For T20/ODI, launch_result is (process, result_file_path)
                if isinstance(launch_result, tuple):
                    process, result_file = launch_result
                    # Wait for the match process in a background thread, then read result
                    import threading
                    def wait_and_read():
                        process.wait()
                        print(f"[Fixtures] Match process finished, reading result from {result_file}")
                        self._pending_match_result = {'fixture': fixture, 'result_file': result_file, 'home_team': home_team, 'away_team': away_team, 'format': match_format}
                    
                    thread = threading.Thread(target=wait_and_read, daemon=True)
                    thread.start()
                    
                    # Poll for result using QTimer
                    from PyQt6.QtCore import QTimer
                    self._match_poll_timer = QTimer()
                    self._match_poll_timer.setInterval(1000)
                    self._match_poll_timer.timeout.connect(lambda: self._check_match_result())
                    self._match_poll_timer.start()
                else:
                    # Test match or other format - fallback to quick sim
                    self._fallback_quick_sim(fixture, home_team, away_team, match_format)
                
        except Exception as e:
            print(f"[Fixtures] Error launching match: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "Error", f"Failed to launch match simulator: {e}")
    
    def _check_match_result(self):
        """Poll for match result file after interactive match finishes"""
        import pickle
        import traceback
        if not hasattr(self, '_pending_match_result') or not self._pending_match_result:
            return
        
        pending = self._pending_match_result
        result_file = pending['result_file']
        
        if not os.path.exists(result_file):
            return
        
        # Stop polling
        if hasattr(self, '_match_poll_timer'):
            self._match_poll_timer.stop()
        
        try:
            with open(result_file, 'rb') as f:
                match_result = pickle.load(f)
            
            print(f"[Fixtures] Read match result: {match_result.get('result', 'Unknown')}")
            
            fixture = pending['fixture']
            home_team = pending['home_team']
            away_team = pending['away_team']
            
            # Build scorecard from actual match data
            t1_score = f"{match_result['team1_score']}/{match_result['team1_wickets']}"
            t2_score = f"{match_result['team2_score']}/{match_result['team2_wickets']}"
            
            # Determine winner name
            result_text = match_result.get('result', '')
            winner_name = 'Tie'
            if home_team.name in result_text and ('won' in result_text or 'wins' in result_text):
                winner_name = home_team.name
            elif away_team.name in result_text and ('won' in result_text or 'wins' in result_text):
                winner_name = away_team.name
            
            # Build a scorecard dict from match_stats for the scorecard dialog
            match_stats = match_result.get('match_stats', {})
            scorecard = self._build_scorecard_from_match_stats(
                match_stats, home_team, away_team, match_result, pending['format']
            )
            
            # NEW: Update core career/season statistics using StatisticsManager
            # This ensures that interactive matches played via t20oversimulation.py
            # and test_match_enhanced.py (when they write match_stats) correctly
            # update the main GameEngine stats used by Statistics/Player Profile UIs.
            try:
                self._update_stats_from_match_result(match_result, home_team, away_team)
            except Exception as e:
                print(f"[Fixtures] Error updating stats from match result: {e}")
                traceback.print_exc()
            
            # Mark fixture as completed with actual match data
            fixture['completed'] = True
            fixture['status'] = 'Completed'
            fixture['winner'] = winner_name
            fixture['margin'] = result_text
            fixture['scorecard'] = scorecard
            fixture['man_of_the_match'] = scorecard.get('man_of_the_match', '')
            fixture['result'] = {
                'winner': winner_name,
                'team1_score': t1_score,
                'team2_score': t2_score,
            }
            
            # Clean up result file
            try:
                os.remove(result_file)
            except:
                pass
            
            self._pending_match_result = None
            self.load_fixtures()
            self.refresh_leagues_screen()
            # Refresh Statistics and Players screens so updated stats show immediately
            if hasattr(self, 'screen_manager') and self.screen_manager:
                for name in ('Statistics', 'Players'):
                    if name in self.screen_manager.screens:
                        screen = self.screen_manager.screens[name]
                        if hasattr(screen, 'refresh_data'):
                            screen.refresh_data()
                        elif hasattr(screen, 'refresh_all_stats'):
                            screen.refresh_all_stats()
            print(f"[Fixtures] Match result applied: {result_text}")
            
        except Exception as e:
            print(f"[Fixtures] Error reading match result: {e}")
            traceback.print_exc()
            self._pending_match_result = None
    
    def _update_stats_from_match_result(self, match_result, home_team, away_team):
        """
        Bridge external simulators back into the core statistics system.
        
        This uses StatisticsManager.update_player_stats_from_match() on the
        main GameEngine teams, based on the match_stats dictionary saved by
        t20oversimulation.py / test_match_enhanced.py.
        """
        from cricket_manager.core.statistics_manager import StatisticsManager
        
        # Require a game engine and match_stats payload
        if not self.game_engine:
            print("[Fixtures] No game_engine available - skipping stats update")
            return
        
        match_stats = match_result.get('match_stats')
        if not match_stats:
            print("[Fixtures] No match_stats found in result - skipping stats update")
            return
        
        # Determine match format (fallback to pending format or T20)
        match_format = match_result.get('match_format') or match_result.get('format') or 'T20'
        
        # Lightweight match wrapper expected by StatisticsManager
        class _TempMatch:
            pass
        
        temp_match = _TempMatch()
        temp_match.match_stats = match_stats
        temp_match.stats_updated = False
        
        # Provide parent_app-style context for current_year inference, if needed
        setattr(temp_match, 'parent_app', None)
        
        stats_manager = StatisticsManager()
        current_year = getattr(self.game_engine, 'current_year', None)
        
        print(f"[Fixtures] Updating player stats from interactive match ({match_format})...")
        stats_manager.update_player_stats_from_match(
            match=temp_match,
            match_format=match_format,
            teams=[home_team, away_team],
            current_year=current_year
        )
        print("[Fixtures] Player stats updated successfully from interactive match")
    
    def _build_scorecard_from_match_stats(self, match_stats, home_team, away_team, match_result, match_format):
        """Build a scorecard dict from T20Match match_stats for the scorecard dialog"""
        import random
        
        def build_innings(batting_team_name, bowling_team_name, batting_players, bowling_players, total_runs, total_wickets):
            batting_data = []
            for p_name in batting_players:
                if p_name in match_stats:
                    stats = match_stats[p_name]['batting']
                    if stats['balls'] > 0:
                        sr = (stats['runs'] * 100) / stats['balls'] if stats['balls'] > 0 else 0
                        batting_data.append({
                            'name': p_name,
                            'runs': stats['runs'],
                            'balls': stats['balls'],
                            'fours': stats.get('fours', 0),
                            'sixes': stats.get('sixes', 0),
                            'strike_rate': round(sr, 1),
                            'dismissal': stats.get('dismissal', 'Not Out')
                        })
            
            bowling_data = []
            for p_name in bowling_players:
                if p_name in match_stats:
                    stats = match_stats[p_name]['bowling']
                    if stats['balls'] > 0:
                        overs = stats['balls'] // 6 + (stats['balls'] % 6) / 10
                        econ = (stats['runs'] * 6) / stats['balls'] if stats['balls'] > 0 else 0
                        bowling_data.append({
                            'name': p_name,
                            'overs': round(overs, 1),
                            'maidens': stats.get('maidens', 0),
                            'runs': stats['runs'],
                            'wickets': stats['wickets'],
                            'economy': round(econ, 1)
                        })
            
            return {
                'batting_team': batting_team_name,
                'bowling_team': bowling_team_name,
                'total_runs': total_runs,
                'wickets_fallen': total_wickets,
                'overs': 0,
                'batting_card': batting_data,
                'bowling_card': bowling_data
            }
        
        home_player_names = [p.name for p in home_team.players]
        away_player_names = [p.name for p in away_team.players]
        
        innings1 = build_innings(
            home_team.name, away_team.name,
            home_player_names, away_player_names,
            match_result['team1_score'], match_result['team1_wickets']
        )
        innings2 = build_innings(
            away_team.name, home_team.name,
            away_player_names, home_player_names,
            match_result['team2_score'], match_result['team2_wickets']
        )
        
        # Determine winner
        result_text = match_result.get('result', '')
        winner = 'Tie'
        if home_team.name in result_text and ('won' in result_text or 'wins' in result_text):
            winner = home_team.name
        elif away_team.name in result_text and ('won' in result_text or 'wins' in result_text):
            winner = away_team.name
        
        return {
            'team1': home_team.name,
            'team2': away_team.name,
            'innings': [innings1, innings2],
            'winner': winner,
            'margin': result_text,
            'man_of_the_match': '',
            'format': match_format
        }
    
    def _get_fixture_pitch(self, fixture):
        """Extract pitch conditions dict from a fixture, or None."""
        if fixture.get('pitch_bounce') is not None:
            return {
                'pitch_bounce': fixture['pitch_bounce'],
                'pitch_spin': fixture.get('pitch_spin', 5),
                'pitch_pace': fixture.get('pitch_pace', 5),
            }
        return None
    
    def _fallback_quick_sim(self, fixture, home_team, away_team, match_format):
        """Fallback: use FastMatchSimulator when actual result is not available"""
        from cricket_manager.core.fast_match_simulator import FastMatchSimulator
        sim = FastMatchSimulator(home_team, away_team, match_format, pitch_conditions=self._get_fixture_pitch(fixture))
        sim.simulate()
        scorecard = sim.get_scorecard()
        
        winner_name = scorecard.get('winner', 'Tie')
        innings = scorecard.get('innings', [])
        t1_score = f"{innings[0]['total_runs']}/{innings[0]['wickets_fallen']}" if len(innings) > 0 else "0/0"
        t2_score = f"{innings[1]['total_runs']}/{innings[1]['wickets_fallen']}" if len(innings) > 1 else "0/0"
        
        fixture['completed'] = True
        fixture['status'] = 'Completed'
        fixture['winner'] = winner_name
        fixture['margin'] = scorecard.get('margin', '')
        fixture['scorecard'] = scorecard
        fixture['man_of_the_match'] = scorecard.get('man_of_the_match', '')
        fixture['result'] = {
            'winner': winner_name,
            'team1_score': t1_score,
            'team2_score': t2_score,
        }
        self.load_fixtures()
        self.refresh_leagues_screen()
    
    def play_u21_match(self, fixture):
        """Play U21 match using full match simulator (t20oversimulation.py or test_match_enhanced.py)"""
        # Check if already completed
        if fixture.get('completed', False):
            QMessageBox.information(self, "Match Completed", 
                                   "This match has already been played.")
            return
        
        # Extract team names from fixture
        home_name = fixture.get('home', '')
        away_name = fixture.get('away', '')
        
        # Get base team names (remove " U21" suffix)
        home_base_name = home_name.replace(' U21', '')
        away_base_name = away_name.replace(' U21', '')
        
        # Find the parent teams
        home_parent = self.game_engine.get_team_by_name(home_base_name)
        away_parent = self.game_engine.get_team_by_name(away_base_name)
        
        if not home_parent or not away_parent:
            QMessageBox.warning(self, "Error", "Could not find parent teams for U21 match")
            return
        
        # Check if U21 squads exist and have enough players
        if not hasattr(home_parent, 'u21_squad') or len(home_parent.u21_squad) < 11:
            QMessageBox.warning(self, "Error", f"{home_base_name} U21 squad has insufficient players")
            return
        if not hasattr(away_parent, 'u21_squad') or len(away_parent.u21_squad) < 11:
            QMessageBox.warning(self, "Error", f"{away_base_name} U21 squad has insufficient players")
            return
        
        # Create temporary U21 teams for the match
        from cricket_manager.core.team import Team
        
        u21_home = Team(name=home_name, tier=5)
        u21_home.players = list(home_parent.u21_squad[:15])  # Use up to 15 players
        
        u21_away = Team(name=away_name, tier=5)
        u21_away.players = list(away_parent.u21_squad[:15])
        
        # Launch original match simulator
        from cricket_manager.ui.match_launcher import launch_t20_match, launch_test_match
        
        try:
            match_format = fixture.get('format', 'T20')
            launch_result = None
            
            if match_format in ['T20', 'ODI']:
                launch_result = launch_t20_match(u21_home, u21_away, match_format)
                if launch_result:
                    print(f"[Fixtures] Launched U21 {match_format} match: {home_name} vs {away_name}")
                else:
                    print(f"[Fixtures] Failed to launch U21 {match_format} match")
                    
            elif match_format == 'Test':
                launch_result = launch_test_match(u21_home, u21_away)
                if launch_result:
                    print(f"[Fixtures] Launched U21 Test match: {home_name} vs {away_name}")
                else:
                    print(f"[Fixtures] Failed to launch U21 Test match")
            
            if launch_result:
                if isinstance(launch_result, tuple):
                    process, result_file = launch_result
                    import threading
                    def wait_and_read():
                        process.wait()
                        print(f"[Fixtures] U21 match process finished, reading result from {result_file}")
                        self._pending_match_result = {'fixture': fixture, 'result_file': result_file, 'home_team': u21_home, 'away_team': u21_away, 'format': match_format}
                    
                    thread = threading.Thread(target=wait_and_read, daemon=True)
                    thread.start()
                    
                    from PyQt6.QtCore import QTimer
                    self._match_poll_timer = QTimer()
                    self._match_poll_timer.setInterval(1000)
                    self._match_poll_timer.timeout.connect(lambda: self._check_match_result())
                    self._match_poll_timer.start()
                else:
                    self._fallback_quick_sim(fixture, u21_home, u21_away, match_format)
                
        except Exception as e:
            print(f"[Fixtures] Error launching U21 match: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "Error", f"Failed to launch U21 match simulator: {e}")
        
        # Reload fixtures to show updated status
        self.load_fixtures()
        # Refresh leagues screen
        self.refresh_leagues_screen()
    
    def quick_sim_match(self, fixture):
        """Quick simulate match"""
        # Check if already completed
        if fixture.get('completed', False):
            QMessageBox.information(self, "Match Completed", 
                                   "This match has already been played.")
            return
        
        if not self.game_engine:
            return
        
        try:
            # Check if this is a U21 match (tier youth fixtures always set is_u21)
            if fixture.get('is_u21') or (fixture.get('team1') is None and fixture.get('team2') is None):
                # This is a U21 match - simulate using youth system
                self.simulate_u21_match(fixture)
                return
            
            # Get teams from fixture (they're already Team objects)
            home_team = fixture.get('team1') or fixture.get('home_team')
            away_team = fixture.get('team2') or fixture.get('away_team')
            
            if not home_team or not away_team:
                QMessageBox.warning(self, "Error", "Could not find teams")
                return
            
            # Simulate match
            from cricket_manager.core.fast_match_simulator import FastMatchSimulator
            simulator = FastMatchSimulator(home_team, away_team, fixture['format'], pitch_conditions=self._get_fixture_pitch(fixture))
            winner = simulator.simulate()  # Returns Team object
            
            # Get scorecard
            scorecard = simulator.get_scorecard()
            
            # Mark fixture as completed
            fixture['completed'] = True
            fixture['status'] = 'Completed'
            fixture['winner'] = winner.name if winner else 'Draw'
            fixture['margin'] = simulator.margin
            fixture['scorecard'] = scorecard
            fixture['man_of_the_match'] = scorecard.get('man_of_the_match', '')
            innings = scorecard.get('innings', [])
            t1_score = f"{innings[0]['total_runs']}/{innings[0]['wickets_fallen']}" if len(innings) > 0 else "0/0"
            t2_score = f"{innings[1]['total_runs']}/{innings[1]['wickets_fallen']}" if len(innings) > 1 else "0/0"
            fixture['result'] = {
                'team1_score': t1_score,
                'team2_score': t2_score,
                'winner': winner.name if winner else 'Tie'
            }
            
            # Update stats and store scorecard so Statistics tab reflects this match
            if self.game_engine and scorecard:
                fmt = fixture.get('format', 'T20')
                result = {
                    'winner': winner.name if winner else 'Draw',
                    'team1': home_team.name,
                    'team2': away_team.name,
                    'format': fmt,
                    'margin': simulator.margin,
                    'scorecard': scorecard,
                }
                scorecard_key = (home_team.name, away_team.name, self.game_engine.current_season, fmt)
                self.game_engine.match_scorecards[scorecard_key] = scorecard
                self.game_engine.update_team_stats(home_team, away_team, result, fmt)
                self.game_engine._update_player_career_stats(scorecard, home_team, away_team, fmt)
            
            # Show detailed scorecard dialog
            self.show_scorecard_dialog(scorecard)
            
            # Reload fixtures
            self.load_fixtures()
            
            # Refresh leagues screen
            self.refresh_leagues_screen()
            
            # Refresh statistics screen so new stats are visible
            if self.screen_manager:
                stats_screen = self.screen_manager.screens.get("Statistics")
                if stats_screen and hasattr(stats_screen, 'refresh_data'):
                    stats_screen.refresh_data()
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to simulate match: {str(e)}")
    
    def simulate_u21_match(self, fixture):
        """Simulate a U21 match"""
        try:
            # Extract team names from fixture
            home_name = fixture.get('home', '')
            away_name = fixture.get('away', '')
            
            # Get base team names (remove " U21" suffix)
            home_base_name = home_name.replace(' U21', '')
            away_base_name = away_name.replace(' U21', '')
            
            # Find the parent teams
            home_parent = self.game_engine.get_team_by_name(home_base_name)
            away_parent = self.game_engine.get_team_by_name(away_base_name)
            
            if not home_parent or not away_parent:
                QMessageBox.warning(self, "Error", "Could not find parent teams for U21 match")
                return
            
            # Check if U21 squads exist and have enough players
            if not hasattr(home_parent, 'u21_squad') or len(home_parent.u21_squad) < 11:
                QMessageBox.warning(self, "Error", f"{home_base_name} U21 squad has insufficient players")
                return
            if not hasattr(away_parent, 'u21_squad') or len(away_parent.u21_squad) < 11:
                QMessageBox.warning(self, "Error", f"{away_base_name} U21 squad has insufficient players")
                return
            
            # Create temporary U21 teams
            from cricket_manager.core.team import Team
            from cricket_manager.core.fast_match_simulator import FastMatchSimulator
            
            u21_home = Team(name=home_name, tier=5)
            u21_home.players = list(home_parent.u21_squad[:11])
            
            u21_away = Team(name=away_name, tier=5)
            u21_away.players = list(away_parent.u21_squad[:11])
            
            # Simulate match
            simulator = FastMatchSimulator(u21_home, u21_away, fixture['format'], pitch_conditions=self._get_fixture_pitch(fixture))
            winner = simulator.simulate()
            
            # Get scorecard to extract scores
            scorecard = simulator.get_scorecard()
            
            # Extract scores from innings_data
            team1_score = "0/0"
            team2_score = "0/0"
            if scorecard and 'innings' in scorecard and len(scorecard['innings']) >= 2:
                inn1 = scorecard['innings'][0]
                inn2 = scorecard['innings'][1]
                team1_score = f"{inn1.get('total_runs', 0)}/{inn1.get('wickets_fallen', 0)}"
                team2_score = f"{inn2.get('total_runs', 0)}/{inn2.get('wickets_fallen', 0)}"
            
            # Mark fixture as completed
            fixture['completed'] = True
            fixture['status'] = 'Completed'
            fixture['winner'] = winner.name if winner else 'Draw'
            fixture['margin'] = getattr(simulator, 'margin', '')
            fixture['result'] = {
                'team1_score': team1_score,
                'team2_score': team2_score,
                'winner': winner.name if winner else 'Tie'
            }
            
            # Show detailed scorecard dialog
            self.show_scorecard_dialog(scorecard)
            
            # Reload fixtures
            self.load_fixtures()
            
            # Refresh leagues screen
            self.refresh_leagues_screen()
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to simulate U21 match: {str(e)}")
    
    def simulate_season(self):
        """Shortcut to Leagues screen's simulate_season - no duplication"""
        if self.screen_manager:
            leagues_screen = self.screen_manager.screens.get("Leagues")
            if leagues_screen and hasattr(leagues_screen, 'simulate_season'):
                leagues_screen.simulate_season()
                # Refresh fixtures + rebuild UI (including WC button name)
                self.refresh_fixtures()
                return
        QMessageBox.warning(self, "Error", "Could not find Leagues screen to simulate season.")
    
    def _sim_fixture(self, fixture, FastMatchSimulator):
        """Helper: simulate a single fixture and mark it completed. Returns True on success."""
        try:
            home_team = fixture.get('team1') or fixture.get('home_team')
            away_team = fixture.get('team2') or fixture.get('away_team')
            if not home_team or not away_team:
                return False
            sim = FastMatchSimulator(home_team, away_team, fixture['format'],
                                     pitch_conditions=self._get_fixture_pitch(fixture))
            winner = sim.simulate()
            sc = sim.get_scorecard()
            fixture['completed'] = True
            fixture['status'] = 'Completed'
            fixture['winner'] = winner.name if winner else 'Draw'
            fixture['margin'] = sim.margin
            fixture['scorecard'] = sc
            fixture['man_of_the_match'] = sc.get('man_of_the_match', '')
            # Update stats and store scorecard so Statistics tab reflects this match
            if self.game_engine and sc:
                fmt = fixture.get('format', 'T20')
                result = {
                    'winner': winner.name if winner else 'Draw',
                    'team1': home_team.name,
                    'team2': away_team.name,
                    'format': fmt,
                    'margin': sim.margin,
                    'scorecard': sc,
                }
                scorecard_key = (home_team.name, away_team.name, self.game_engine.current_season, fmt)
                self.game_engine.match_scorecards[scorecard_key] = sc
                self.game_engine.update_team_stats(home_team, away_team, result, fmt)
                self.game_engine._update_player_career_stats(sc, home_team, away_team, fmt)
            return True
        except Exception as e:
            print(f"Error simulating match: {e}")
            return False

    def _sim_entire_wc(self, FastMatchSimulator):
        """Simulate ALL remaining World Cup matches (groups → semis → final)."""
        simulated = 0
        # 1. Simulate all unplayed WC group/round fixtures
        wc_fixtures, wc_format = self._get_wc_fixtures_all_formats()
        if not wc_fixtures or not wc_format:
            return 0
        for f in [fx for fx in wc_fixtures if not fx.get('completed')]:
            if self._sim_fixture(f, FastMatchSimulator):
                simulated += 1
        # 2. Advance phases until WC is done
        for _ in range(10):  # safety cap
            wc_fixtures = [f for f in self.game_engine.fixtures.get(wc_format, []) if f.get('is_world_cup')]
            phase = self._get_wc_phase(wc_fixtures)
            if phase == 'completed':
                break
            elif phase == 'groups_done':
                self._generate_wc_knockouts(wc_fixtures, wc_format)
            elif phase == 'knockouts':
                semis = [f for f in wc_fixtures if f.get('round') == 'Semi-Final']
                if semis and all(f.get('completed') for f in semis):
                    finals = [f for f in wc_fixtures if f.get('round') == 'Final']
                    if not finals:
                        self._generate_wc_final(wc_fixtures, wc_format)
            elif phase == 'associate_knockout_advance':
                self._generate_associate_next_round(wc_fixtures, wc_format)
            elif phase == 'associate_knockout':
                pass  # just sim unplayed below
            else:
                break
            # Simulate any newly generated unplayed WC fixtures
            fresh = [f for f in self.game_engine.fixtures.get(wc_format, [])
                     if f.get('is_world_cup') and not f.get('completed')]
            for f in fresh:
                if self._sim_fixture(f, FastMatchSimulator):
                    simulated += 1
        return simulated

    def simulate_all_matches(self):
        """Simulate all remaining visible matches.
        If World Cup fixtures exist, asks user whether to include them.
        YES  → simulates regular matches + entire World Cup (groups, semis, final).
        NO   → simulates only regular (non-WC) matches.
        """
        if self.current_tier == 6:
            self._simulate_wc_matches()
            return
        
        # Gather all visible unplayed fixtures
        all_visible = self._gather_all_fixtures()
        unplayed = [f for f in all_visible 
                   if not f.get('completed') and f.get('status') != 'Completed']
        
        if not unplayed:
            QMessageBox.information(self, "No Matches", "No unplayed matches to simulate.")
            return
        
        # Check if there are any WC fixtures at all (even outside visible)
        wc_exist = any(f.get('is_world_cup', False) for f in unplayed)
        # Also check engine-level WC fixtures
        if not wc_exist:
            for fmt in ['T20', 'ODI', 'Test']:
                if any(f.get('is_world_cup') and not f.get('completed')
                       for f in self.game_engine.fixtures.get(fmt, [])):
                    wc_exist = True
                    break
        
        include_wc = False
        regular = [f for f in unplayed if not f.get('is_world_cup', False)]
        
        if wc_exist:
            wc_name = getattr(self.game_engine, 'wc_name', 'World Cup')
            reply = QMessageBox.question(
                self,
                "World Cup",
                f"Do you also want to simulate the entire {wc_name}\n"
                f"(including semi-finals and final)?\n\n"
                f"YES = Simulate {len(regular)} regular matches + full World Cup\n"
                f"NO  = Simulate {len(regular)} regular matches only",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            include_wc = (reply == QMessageBox.StandardButton.Yes)
        else:
            reply = QMessageBox.question(
                self,
                "Simulate All",
                f"Simulate {len(regular)} remaining matches?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        from cricket_manager.core.fast_match_simulator import FastMatchSimulator
        simulated = 0
        
        # Simulate regular (non-WC) matches
        for fixture in regular:
            if self._sim_fixture(fixture, FastMatchSimulator):
                simulated += 1
        
        # Simulate entire WC if user chose YES
        if include_wc:
            simulated += self._sim_entire_wc(FastMatchSimulator)
        
        QMessageBox.information(self, "Complete", f"Simulated {simulated} matches!")
        self.load_fixtures()
        self.refresh_leagues_screen()
    
    def _simulate_wc_matches(self):
        """Simulate remaining World Cup matches based on current phase"""
        # Find WC fixtures
        wc_fixtures = []
        wc_format = None
        for fmt in ['T20', 'ODI', 'Test']:
            all_fmt = self.game_engine.fixtures.get(fmt, [])
            wc = [f for f in all_fmt if f.get('is_world_cup', False)]
            if wc:
                wc_fixtures = wc
                wc_format = fmt
                break
        
        if not wc_fixtures or not wc_format:
            QMessageBox.information(self, "No World Cup", "No World Cup matches found.")
            return
        
        phase = self._get_wc_phase(wc_fixtures)
        
        if phase == 'groups':
            unplayed = [f for f in wc_fixtures if f.get('round', '').startswith('Group') and not f.get('completed')]
            msg = f"Simulate {len(unplayed)} remaining group stage matches?"
        elif phase == 'groups_done':
            self._generate_wc_knockouts(wc_fixtures, wc_format)
            wc_fixtures = [f for f in self.game_engine.fixtures.get(wc_format, []) if f.get('is_world_cup', False)]
            unplayed = [f for f in wc_fixtures if f.get('round') in ('Semi-Final', 'Final') and not f.get('completed')]
            msg = f"Simulate {len(unplayed)} remaining knockout matches?"
        elif phase == 'knockouts':
            semis = [f for f in wc_fixtures if f.get('round') == 'Semi-Final']
            if semis and all(f.get('completed') for f in semis):
                finals = [f for f in wc_fixtures if f.get('round') == 'Final']
                if not finals:
                    self._generate_wc_final(wc_fixtures, wc_format)
                    wc_fixtures = [f for f in self.game_engine.fixtures.get(wc_format, []) if f.get('is_world_cup', False)]
            unplayed = [f for f in wc_fixtures if f.get('round') in ('Semi-Final', 'Final') and not f.get('completed')]
            msg = f"Simulate {len(unplayed)} remaining knockout matches?"
        elif phase in ('associate_knockout', 'associate_knockout_advance'):
            # Associate WC: knockout-only format
            if phase == 'associate_knockout_advance':
                self._generate_associate_next_round(wc_fixtures, wc_format)
                wc_fixtures = [f for f in self.game_engine.fixtures.get(wc_format, []) if f.get('is_world_cup', False)]
            unplayed = [f for f in wc_fixtures if not f.get('completed')]
            if not unplayed:
                QMessageBox.information(self, "World Cup", "Associate World Cup is already completed!")
                return
            msg = f"Simulate {len(unplayed)} remaining Associate World Cup matches?"
        elif phase == 'completed':
            QMessageBox.information(self, "World Cup", "World Cup is already completed!")
            return
        else:
            return
        
        reply = QMessageBox.question(self, "Simulate World Cup", msg,
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        from cricket_manager.core.fast_match_simulator import FastMatchSimulator
        
        simulated = 0
        for fixture in unplayed:
            try:
                home_team = fixture.get('team1')
                away_team = fixture.get('team2')
                if not home_team or not away_team:
                    continue
                
                simulator = FastMatchSimulator(home_team, away_team, fixture['format'], pitch_conditions=self._get_fixture_pitch(fixture))
                winner = simulator.simulate()
                scorecard = simulator.get_scorecard()
                fixture['completed'] = True
                fixture['status'] = 'Completed'
                fixture['winner'] = winner.name if winner else 'Tie'
                fixture['margin'] = simulator.margin
                fixture['scorecard'] = scorecard
                fixture['man_of_the_match'] = scorecard.get('man_of_the_match', '')
                simulated += 1
            except Exception as e:
                print(f"Error simulating WC match: {e}")
        
        if simulated > 0:
            QMessageBox.information(self, "Complete", f"Simulated {simulated} World Cup matches!")
        
        # After simulation, advance to next phase
        wc_fixtures = [f for f in self.game_engine.fixtures.get(wc_format, []) if f.get('is_world_cup', False)]
        new_phase = self._get_wc_phase(wc_fixtures)
        
        if new_phase == 'groups_done':
            self._generate_wc_knockouts(wc_fixtures, wc_format)
        elif new_phase == 'knockouts':
            semis = [f for f in wc_fixtures if f.get('round') == 'Semi-Final']
            if semis and all(f.get('completed') for f in semis):
                finals = [f for f in wc_fixtures if f.get('round') == 'Final']
                if not finals:
                    self._generate_wc_final(wc_fixtures, wc_format)
        elif new_phase == 'associate_knockout_advance':
            self._generate_associate_next_round(wc_fixtures, wc_format)
        
        self.load_fixtures()
        self.refresh_leagues_screen()
    
    def refresh_leagues_screen(self):
        """Refresh the leagues screen to show updated standings"""
        if self.screen_manager:
            leagues_screen = self.screen_manager.screens.get("Leagues")
            if leagues_screen and hasattr(leagues_screen, 'refresh_standings'):
                leagues_screen.refresh_standings()
    
    def show_series_stats(self, series_fixtures, series_name, fmt):
        """Show top 5 batters and bowlers from a completed series in a popup dialog."""
        from PyQt6.QtWidgets import QDialog, QTabWidget
        
        if not series_fixtures:
            return
        
        # Extract player stats from all series scorecards
        player_stats = {}
        match_keys_seen = {}
        
        for fix in series_fixtures:
            sc = fix.get('scorecard', {})
            if not sc or 'innings' not in sc:
                continue
            fix_key = f"{fix.get('home','')}_{fix.get('away','')}_{fix.get('match_number','')}"
            for innings in sc.get('innings', []):
                batting_team = innings.get('batting_team', innings.get('team', ''))
                bowling_team = innings.get('bowling_team', '')
                for bat in innings.get('batting', innings.get('batting_card', [])):
                    name = bat.get('name', bat.get('player', ''))
                    if not name:
                        continue
                    if name not in player_stats:
                        player_stats[name] = {
                            'team': batting_team, 'matches': 0,
                            'runs': 0, 'balls': 0, 'fours': 0, 'sixes': 0,
                            'highest': 0, 'fifties': 0, 'hundreds': 0,
                            'not_outs': 0, 'dismissals': 0,
                            'wickets': 0, 'runs_conceded': 0, 'balls_bowled': 0,
                            'overs_bowled': 0, 'four_wkt': 0, 'five_wkt': 0,
                        }
                    runs = bat.get('runs', 0)
                    balls = bat.get('balls', bat.get('balls_faced', 0))
                    player_stats[name]['runs'] += runs
                    player_stats[name]['balls'] += balls
                    player_stats[name]['fours'] += bat.get('fours', 0)
                    player_stats[name]['sixes'] += bat.get('sixes', 0)
                    if runs > player_stats[name]['highest']:
                        player_stats[name]['highest'] = runs
                    if runs >= 100:
                        player_stats[name]['hundreds'] += 1
                    elif runs >= 50:
                        player_stats[name]['fifties'] += 1
                    dismissal = bat.get('dismissal', bat.get('how_out', ''))
                    if dismissal and dismissal.lower() not in ('not out', 'not_out', ''):
                        player_stats[name]['dismissals'] += 1
                    else:
                        player_stats[name]['not_outs'] += 1
                    # Count matches
                    pkey = f"{name}_{fix_key}"
                    if pkey not in match_keys_seen:
                        match_keys_seen[pkey] = True
                        player_stats[name]['matches'] += 1
                
                for bowl in innings.get('bowling', innings.get('bowling_card', [])):
                    name = bowl.get('name', bowl.get('player', ''))
                    if not name:
                        continue
                    if name not in player_stats:
                        player_stats[name] = {
                            'team': bowling_team, 'matches': 0,
                            'runs': 0, 'balls': 0, 'fours': 0, 'sixes': 0,
                            'highest': 0, 'fifties': 0, 'hundreds': 0,
                            'not_outs': 0, 'dismissals': 0,
                            'wickets': 0, 'runs_conceded': 0, 'balls_bowled': 0,
                            'overs_bowled': 0, 'four_wkt': 0, 'five_wkt': 0,
                        }
                    wkts = bowl.get('wickets', 0)
                    player_stats[name]['wickets'] += wkts
                    player_stats[name]['runs_conceded'] += bowl.get('runs', bowl.get('runs_conceded', 0))
                    player_stats[name]['overs_bowled'] += bowl.get('overs', 0)
                    player_stats[name]['balls_bowled'] += bowl.get('balls', bowl.get('balls_bowled', 0))
                    if wkts >= 5:
                        player_stats[name]['five_wkt'] += 1
                    elif wkts >= 4:
                        player_stats[name]['four_wkt'] += 1
        
        # Top 5 batters by runs
        batters = [(n, s) for n, s in player_stats.items() if s['runs'] > 0]
        batters.sort(key=lambda x: x[1]['runs'], reverse=True)
        top_batters = batters[:5]
        
        # Top 5 bowlers by wickets
        bowlers = [(n, s) for n, s in player_stats.items() if s['wickets'] > 0]
        bowlers.sort(key=lambda x: x[1]['wickets'], reverse=True)
        top_bowlers = bowlers[:5]
        
        # Series winner
        win_counts = {}
        for f in series_fixtures:
            w = f.get('winner', '')
            if w and w not in ('Draw', 'Tie', 'N/A'):
                win_counts[w] = win_counts.get(w, 0) + 1
        if win_counts:
            sw = max(win_counts, key=win_counts.get)
            counts_list = sorted(win_counts.values(), reverse=True)
            if len(counts_list) > 1 and counts_list[0] == counts_list[1]:
                winner_line = "Series Drawn"
            else:
                winner_line = f"Winner: {sw} ({win_counts[sw]}-{len(series_fixtures) - win_counts[sw]})"
        else:
            winner_line = "Series Drawn"
        
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"{series_name} — Series Stats")
        dialog.setMinimumSize(750, 420)
        dlayout = QVBoxLayout()
        
        title_lbl = QLabel(f"🏏 {series_name} — {fmt}\n🏆 {winner_line}")
        title_lbl.setStyleSheet(f"font-size: 17px; font-weight: bold; color: {COLORS['primary']}; padding: 10px;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dlayout.addWidget(title_lbl)
        
        tabs = QTabWidget()
        
        # --- Match summaries ---
        summaries = []
        for i, f in enumerate(series_fixtures):
            home = f.get('home') or (f.get('home_team').name if hasattr(f.get('home_team'), 'name') else str(f.get('home_team', '')))
            away = f.get('away') or (f.get('away_team').name if hasattr(f.get('away_team'), 'name') else str(f.get('away_team', '')))
            winner = f.get('winner', '')
            margin = f.get('margin', '') or ''
            mn = f.get('match_number', i + 1)
            if winner and winner not in ('Draw', 'Tie', 'N/A'):
                other = away if winner == home else home
                line = f"Match {mn}: {winner} beat {other} — {margin}" if margin else f"Match {mn}: {winner} won"
            elif winner == 'Tie':
                line = f"Match {mn}: {home} vs {away} — Tie"
            else:
                line = f"Match {mn}: {home} vs {away} — Draw" if winner == 'Draw' else f"Match {mn}: {home} vs {away} — {margin or 'Completed'}"
            summaries.append((mn, home, away, line))
        sum_table = QTableWidget()
        sum_table.setColumnCount(4)
        sum_table.setHorizontalHeaderLabels(['#', 'Home', 'Away', 'Result'])
        sum_table.setRowCount(len(summaries))
        sum_table.verticalHeader().setVisible(False)
        sum_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        for i, (mn, home, away, line) in enumerate(summaries):
            sum_table.setItem(i, 0, QTableWidgetItem(str(mn)))
            sum_table.setItem(i, 1, QTableWidgetItem(home))
            sum_table.setItem(i, 2, QTableWidgetItem(away))
            sum_table.setItem(i, 3, QTableWidgetItem(line))
        sh = sum_table.horizontalHeader()
        for col in range(4):
            sh.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch if col == 3 else QHeaderView.ResizeMode.ResizeToContents)
        sum_table.setStyleSheet(f"""
            QTableWidget {{ border: none; background: #111827; gridline-color: #334155; }}
            QTableWidget::item {{ padding: 6px; }}
            QHeaderView::section {{ background: {COLORS['primary']}; color: white; padding: 8px; font-weight: bold; border: none; }}
        """)
        tabs.addTab(sum_table, "📋 Match summaries")
        
        # --- Top 5 Batters ---
        bat_table = QTableWidget()
        bat_table.setColumnCount(9)
        bat_table.setHorizontalHeaderLabels(['#', 'Player', 'Team', 'Runs', 'Balls', 'Avg', 'SR', 'HS', '50/100'])
        bat_table.setRowCount(len(top_batters))
        bat_table.verticalHeader().setVisible(False)
        bat_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        bh = bat_table.horizontalHeader()
        for col in range(9):
            bh.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch if col == 1 else QHeaderView.ResizeMode.ResizeToContents)
        bat_table.setStyleSheet(f"""
            QTableWidget {{ border: none; background: #111827; gridline-color: #334155; }}
            QTableWidget::item {{ padding: 6px; }}
            QHeaderView::section {{ background: {COLORS['primary']}; color: white; padding: 8px; font-weight: bold; border: none; }}
        """)
        for i, (name, s) in enumerate(top_batters):
            sr = f"{(s['runs']/s['balls']*100):.1f}" if s['balls'] > 0 else "0.0"
            avg = f"{(s['runs']/s['dismissals']):.2f}" if s['dismissals'] > 0 else "N/A"
            items = [str(i+1), name, s.get('team',''), str(s['runs']), str(s['balls']),
                     avg, sr, str(s['highest']), f"{s['fifties']}/{s['hundreds']}"]
            for col, val in enumerate(items):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter if col != 1 else Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                bat_table.setItem(i, col, item)
        tabs.addTab(bat_table, "🏏 Top 5 Batters")
        
        # --- Top 5 Bowlers ---
        bowl_table = QTableWidget()
        bowl_table.setColumnCount(8)
        bowl_table.setHorizontalHeaderLabels(['#', 'Player', 'Team', 'Wkts', 'Overs', 'Runs', 'Avg', 'Econ'])
        bowl_table.setRowCount(len(top_bowlers))
        bowl_table.verticalHeader().setVisible(False)
        bowl_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        bwh = bowl_table.horizontalHeader()
        for col in range(8):
            bwh.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch if col == 1 else QHeaderView.ResizeMode.ResizeToContents)
        bowl_table.setStyleSheet(f"""
            QTableWidget {{ border: none; background: #111827; gridline-color: #334155; }}
            QTableWidget::item {{ padding: 6px; }}
            QHeaderView::section {{ background: {COLORS['primary']}; color: white; padding: 8px; font-weight: bold; border: none; }}
        """)
        for i, (name, s) in enumerate(top_bowlers):
            overs = s.get('overs_bowled', 0)
            if overs == 0 and s['balls_bowled'] > 0:
                overs = s['balls_bowled'] / 6
            econ = f"{(s['runs_conceded']/overs):.2f}" if overs > 0 else "0.00"
            bowl_avg = f"{(s['runs_conceded']/s['wickets']):.2f}" if s['wickets'] > 0 else "N/A"
            items = [str(i+1), name, s.get('team',''), str(s['wickets']),
                     f"{overs:.1f}", str(s['runs_conceded']), bowl_avg, econ]
            for col, val in enumerate(items):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter if col != 1 else Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                bowl_table.setItem(i, col, item)
        tabs.addTab(bowl_table, "🎳 Top 5 Bowlers")
        
        dlayout.addWidget(tabs)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        close_btn.setStyleSheet(f"""
            QPushButton {{ background-color: {COLORS['primary']}; color: white; padding: 8px 25px; border: none; border-radius: 5px; font-weight: bold; }}
            QPushButton:hover {{ background-color: {COLORS['secondary']}; }}
        """)
        dlayout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        dialog.setLayout(dlayout)
        dialog.exec()
    
    def show_world_cup_stats(self):
        """Show World Cup stats dialog with top 20 batters and bowlers"""
        from PyQt6.QtWidgets import QDialog, QTabWidget, QScrollArea
        
        # Collect all completed WC fixtures
        wc_fixtures = []
        wc_format = None
        wc_name = getattr(self.game_engine, 'wc_name', 'World Cup')
        for fmt in ['T20', 'ODI', 'Test']:
            all_fmt = self.game_engine.fixtures.get(fmt, [])
            wc = [f for f in all_fmt if f.get('is_world_cup', False) and f.get('completed')]
            if wc:
                wc_fixtures = wc
                wc_format = fmt
                break
        
        if not wc_fixtures:
            QMessageBox.information(self, "No Stats", "No completed World Cup matches found.")
            return
        
        # Extract player stats from all WC scorecards
        player_stats = {}
        for fix in wc_fixtures:
            sc = fix.get('scorecard', {})
            if not sc or 'innings' not in sc:
                continue
            for innings in sc.get('innings', []):
                batting_team = innings.get('batting_team', innings.get('team', ''))
                bowling_team = innings.get('bowling_team', '')
                for bat in innings.get('batting', innings.get('batting_card', [])):
                    name = bat.get('name', bat.get('player', ''))
                    if not name:
                        continue
                    if name not in player_stats:
                        player_stats[name] = {
                            'team': batting_team, 'matches': 0,
                            'runs': 0, 'balls': 0, 'fours': 0, 'sixes': 0,
                            'highest': 0, 'fifties': 0, 'hundreds': 0, 'not_outs': 0, 'dismissals': 0,
                            'wickets': 0, 'runs_conceded': 0, 'balls_bowled': 0,
                            'overs_bowled': 0, 'four_wkt': 0, 'five_wkt': 0,
                        }
                    elif not player_stats[name]['team'] and batting_team:
                        player_stats[name]['team'] = batting_team
                    runs = bat.get('runs', 0)
                    balls = bat.get('balls', bat.get('balls_faced', 0))
                    player_stats[name]['runs'] += runs
                    player_stats[name]['balls'] += balls
                    player_stats[name]['fours'] += bat.get('fours', 0)
                    player_stats[name]['sixes'] += bat.get('sixes', 0)
                    if runs > player_stats[name]['highest']:
                        player_stats[name]['highest'] = runs
                    if runs >= 100:
                        player_stats[name]['hundreds'] += 1
                    elif runs >= 50:
                        player_stats[name]['fifties'] += 1
                    dismissal = bat.get('dismissal', bat.get('how_out', ''))
                    if dismissal and dismissal.lower() not in ('not out', 'not_out', ''):
                        player_stats[name]['dismissals'] += 1
                    else:
                        player_stats[name]['not_outs'] += 1
                
                for bowl in innings.get('bowling', innings.get('bowling_card', [])):
                    name = bowl.get('name', bowl.get('player', ''))
                    if not name:
                        continue
                    if name not in player_stats:
                        player_stats[name] = {
                            'team': bowling_team, 'matches': 0,
                            'runs': 0, 'balls': 0, 'fours': 0, 'sixes': 0,
                            'highest': 0, 'fifties': 0, 'hundreds': 0, 'not_outs': 0, 'dismissals': 0,
                            'wickets': 0, 'runs_conceded': 0, 'balls_bowled': 0,
                            'overs_bowled': 0, 'four_wkt': 0, 'five_wkt': 0,
                        }
                    elif not player_stats[name]['team'] and bowling_team:
                        player_stats[name]['team'] = bowling_team
                    wkts = bowl.get('wickets', 0)
                    player_stats[name]['wickets'] += wkts
                    player_stats[name]['runs_conceded'] += bowl.get('runs', bowl.get('runs_conceded', 0))
                    player_stats[name]['overs_bowled'] += bowl.get('overs', 0)
                    player_stats[name]['balls_bowled'] += bowl.get('balls', bowl.get('balls_bowled', 0))
                    if wkts >= 5:
                        player_stats[name]['five_wkt'] += 1
                    elif wkts >= 4:
                        player_stats[name]['four_wkt'] += 1
        
        # Count matches per player
        match_teams = {}
        for fix in wc_fixtures:
            sc = fix.get('scorecard', {})
            if not sc:
                continue
            for innings in sc.get('innings', []):
                for bat in innings.get('batting', innings.get('batting_card', [])):
                    name = bat.get('name', bat.get('player', ''))
                    if name:
                        key = f"{name}_{fix.get('home','')}_{fix.get('away','')}"
                        if key not in match_teams:
                            match_teams[key] = True
                            player_stats.get(name, {})['matches'] = player_stats.get(name, {}).get('matches', 0) + 1
        
        # Build top 20 batters
        batters = [(n, s) for n, s in player_stats.items() if s['runs'] > 0]
        batters.sort(key=lambda x: x[1]['runs'], reverse=True)
        top_batters = batters[:20]
        
        # Build top 20 bowlers
        bowlers = [(n, s) for n, s in player_stats.items() if s['wickets'] > 0]
        bowlers.sort(key=lambda x: x[1]['wickets'], reverse=True)
        top_bowlers = bowlers[:20]
        
        # Find champion
        final = [f for f in wc_fixtures if f.get('round') == 'Final']
        champion = final[0].get('winner', 'N/A') if final else 'N/A'
        
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"{wc_name} - Statistics")
        dialog.setMinimumSize(900, 650)
        
        dlayout = QVBoxLayout()
        
        # Title
        title_lbl = QLabel(f"🏆 {wc_name} - Champion: {champion}")
        title_lbl.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {COLORS['primary']}; padding: 10px;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dlayout.addWidget(title_lbl)
        
        tabs = QTabWidget()
        
        # --- Top Batters Tab ---
        bat_table = QTableWidget()
        bat_table.setColumnCount(12)
        bat_table.setHorizontalHeaderLabels(['#', 'Player', 'Team', 'Mat', 'Runs', 'Balls', 'Avg', 'SR', 'HS', '50s', '100s', '4s/6s'])
        bat_table.setRowCount(len(top_batters))
        bat_table.verticalHeader().setVisible(False)
        bat_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        bat_header = bat_table.horizontalHeader()
        for col in range(12):
            bat_header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch if col == 1 else QHeaderView.ResizeMode.ResizeToContents)
        bat_table.setStyleSheet(f"""
            QTableWidget {{ border: none; background: #111827; gridline-color: #334155; }}
            QTableWidget::item {{ padding: 6px; }}
            QHeaderView::section {{ background: {COLORS['primary']}; color: white; padding: 8px; font-weight: bold; border: none; }}
        """)
        
        for i, (name, s) in enumerate(top_batters):
            sr = f"{(s['runs']/s['balls']*100):.1f}" if s['balls'] > 0 else "0.0"
            avg = f"{(s['runs']/s['dismissals']):.2f}" if s['dismissals'] > 0 else "N/A"
            items = [
                str(i+1), name, s.get('team', ''), str(s.get('matches', 0)),
                str(s['runs']), str(s['balls']),
                avg, sr, str(s['highest']), str(s['fifties']), str(s['hundreds']),
                f"{s['fours']}/{s['sixes']}"
            ]
            for col, val in enumerate(items):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter if col != 1 else Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                bat_table.setItem(i, col, item)
        
        tabs.addTab(bat_table, "🏏 Top 20 Batters")
        
        # --- Top Bowlers Tab ---
        bowl_table = QTableWidget()
        bowl_table.setColumnCount(11)
        bowl_table.setHorizontalHeaderLabels(['#', 'Player', 'Team', 'Mat', 'Wickets', 'Overs', 'Runs', 'Avg', 'Econ', '4W', '5W'])
        bowl_table.setRowCount(len(top_bowlers))
        bowl_table.verticalHeader().setVisible(False)
        bowl_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        bowl_header = bowl_table.horizontalHeader()
        for col in range(11):
            bowl_header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch if col == 1 else QHeaderView.ResizeMode.ResizeToContents)
        bowl_table.setStyleSheet(f"""
            QTableWidget {{ border: none; background: #111827; gridline-color: #334155; }}
            QTableWidget::item {{ padding: 6px; }}
            QHeaderView::section {{ background: {COLORS['primary']}; color: white; padding: 8px; font-weight: bold; border: none; }}
        """)
        
        for i, (name, s) in enumerate(top_bowlers):
            overs = s.get('overs_bowled', 0)
            if overs == 0 and s['balls_bowled'] > 0:
                overs = s['balls_bowled'] / 6
            econ = f"{(s['runs_conceded']/overs):.2f}" if overs > 0 else "0.00"
            bowl_avg = f"{(s['runs_conceded']/s['wickets']):.2f}" if s['wickets'] > 0 else "N/A"
            items = [
                str(i+1), name, s.get('team', ''), str(s.get('matches', 0)),
                str(s['wickets']),
                f"{overs:.1f}", str(s['runs_conceded']), bowl_avg, econ,
                str(s['four_wkt']), str(s['five_wkt'])
            ]
            for col, val in enumerate(items):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter if col != 1 else Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                bowl_table.setItem(i, col, item)
        
        tabs.addTab(bowl_table, "🎳 Top 20 Bowlers")
        
        dlayout.addWidget(tabs)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                padding: 10px 30px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{ background-color: {COLORS['secondary']}; }}
        """)
        dlayout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        dialog.setLayout(dlayout)
        dialog.exec()
    
    def show_scorecard_dialog(self, scorecard):
        """Show detailed scorecard in a dialog"""
        from PyQt6.QtWidgets import QDialog, QTextEdit
        
        dialog = QDialog(self)
        team1_name = scorecard.get('team1', '')
        team2_name = scorecard.get('team2', '')
        if not team1_name or not team2_name:
            innings = scorecard.get('innings', [])
            if len(innings) > 0:
                team1_name = team1_name or innings[0].get('batting_team', 'Team 1')
            if len(innings) > 1:
                team2_name = team2_name or innings[1].get('batting_team', 'Team 2')
        dialog.setWindowTitle(f"{team1_name} vs {team2_name} - Scorecard")
        dialog.setMinimumSize(800, 600)
        
        layout = QVBoxLayout()
        
        # Create scorecard text
        scorecard_text = self.format_scorecard(scorecard)
        
        # Text display
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(scorecard_text)
        text_edit.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New', monospace;
                font-size: 12px;
                background-color: #111827;
                border: 1px solid #334155;
            }
        """)
        layout.addWidget(text_edit)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['secondary']};
            }}
        """)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def format_scorecard(self, scorecard):
        """Format scorecard as text"""
        text = []
        
        # Get team names robustly
        team1_name = scorecard.get('team1', '')
        team2_name = scorecard.get('team2', '')
        innings_list = scorecard.get('innings', [])
        if not team1_name and len(innings_list) > 0:
            team1_name = innings_list[0].get('batting_team', 'Team 1')
        if not team2_name and len(innings_list) > 1:
            team2_name = innings_list[1].get('batting_team', 'Team 2')
        
        text.append("=" * 80)
        text.append(f"{team1_name} vs {team2_name}")
        text.append(f"Format: {scorecard.get('format', 'Unknown')}")
        text.append("=" * 80)
        text.append("")
        
        # Result
        winner = scorecard.get('winner', 'Unknown')
        margin = scorecard.get('margin', '')
        if margin and winner and winner != 'Tie':
            text.append(f"Result: {margin}")
        else:
            text.append(f"Result: {winner}")
        text.append("")
        text.append("=" * 80)
        
        # Innings
        for i, innings in enumerate(innings_list, 1):
            text.append("")
            text.append(f"INNINGS {i}: {innings.get('batting_team', 'Team')}")
            text.append("-" * 80)
            text.append(f"Total: {innings.get('total_runs', 0)}/{innings.get('wickets_fallen', innings.get('wickets', 0))} ({innings.get('overs', 0)} overs)")
            text.append("")
            
            # Batting card - handle both key names
            text.append("BATTING")
            text.append(f"{'Player':<25} {'Runs':<8} {'Balls':<8} {'4s':<6} {'6s':<6} {'SR':<8}")
            text.append("-" * 80)
            
            batting_card = innings.get('batting_card', innings.get('batting', []))
            for bat in batting_card:
                player_name = bat.get('name', bat.get('player', 'Unknown'))[:24]
                runs = bat.get('runs', 0)
                balls = bat.get('balls', 0)
                fours = bat.get('fours', 0)
                sixes = bat.get('sixes', 0)
                sr = f"{(runs/balls*100):.1f}" if balls > 0 else "0.0"
                
                text.append(f"{player_name:<25} {runs:<8} {balls:<8} {fours:<6} {sixes:<6} {sr:<8}")
            
            text.append("")
            
            # Bowling card - handle both key names
            text.append("BOWLING")
            text.append(f"{'Player':<25} {'Overs':<8} {'Runs':<8} {'Wkts':<6} {'Econ':<8}")
            text.append("-" * 80)
            
            bowling_card = innings.get('bowling_card', innings.get('bowling', []))
            for bowl in bowling_card:
                player_name = bowl.get('name', bowl.get('player', 'Unknown'))[:24]
                overs = bowl.get('overs', 0)
                runs = bowl.get('runs', 0)
                wickets = bowl.get('wickets', 0)
                econ = f"{bowl.get('economy', 0):.2f}"
                
                text.append(f"{player_name:<25} {overs:<8} {runs:<8} {wickets:<6} {econ:<8}")
            
            text.append("")
        
        text.append("=" * 80)
        
        return "\n".join(text)
