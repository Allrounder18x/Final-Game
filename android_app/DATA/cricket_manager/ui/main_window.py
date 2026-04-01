"""
Main Window - Central hub for the Cricket Manager game
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QGridLayout, QScrollArea, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from cricket_manager.ui.styles import COLORS, MAIN_STYLESHEET, apply_windows_dark_title_bar
from cricket_manager.ui.screen_manager import ScreenManager
from cricket_manager.core.game_engine import GameEngine


class MainWindow(QMainWindow):
    """Main application window with Football Manager style layout"""
    
    def __init__(self, game_engine=None):
        super().__init__()
        self.setWindowTitle("Cricket Manager")
        self.setGeometry(100, 50, 1400, 900)
        
        # Apply sports theme
        self.setStyleSheet(MAIN_STYLESHEET)
        apply_windows_dark_title_bar(self)
        
        # Initialize or use provided game engine
        if game_engine is None:
            print("[MainWindow] Initializing Game Engine...")
            self.game_engine = GameEngine()
            print("[MainWindow] Game Engine initialized!")
        else:
            print("[MainWindow] Using provided Game Engine...")
            self.game_engine = game_engine
        
        # Create main widget
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Sidebar
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Main content area with top bar
        content_area = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Top bar
        self.top_bar = self.create_top_bar()
        content_layout.addWidget(self.top_bar)
        
        # Screen manager for content
        self.screen_manager = ScreenManager()
        content_layout.addWidget(self.screen_manager, 1)
        
        content_area.setLayout(content_layout)
        main_layout.addWidget(content_area, 1)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Hide sidebar and top bar until team is selected
        self.sidebar.setVisible(False)
        self.top_bar.setVisible(False)
        
        # Show team selection screen first
        self._show_team_selection()
        
        # Status bar
        self.statusBar().showMessage("Select your team to begin")
    
    def create_sidebar(self):
        """Create Football Manager style sidebar"""
        sidebar = QFrame()
        sidebar.setFixedWidth(170)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: #1a1a1a;
                border-right: 1px solid #333;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Logo/Title area
        logo_area = QFrame()
        logo_area.setFixedHeight(100)
        logo_area.setStyleSheet("background-color: #0d0d0d;")
        logo_layout = QVBoxLayout()
        logo_layout.setContentsMargins(20, 20, 20, 20)
        logo_layout.setSpacing(5)
        
        title = QLabel("Cricket Manager")
        title.setStyleSheet("""
            font-size: 15px;
            font-weight: 700;
            color: white;
            letter-spacing: 0px;
            background: transparent;
        """)
        title.setWordWrap(True)
        title.setMaximumWidth(180)
        logo_layout.addWidget(title)
        
        subtitle = QLabel("Professional Edition")
        subtitle.setStyleSheet("""
            font-size: 9px;
            color: #888;
            letter-spacing: 0px;
            background: transparent;
        """)
        subtitle.setWordWrap(True)
        subtitle.setMaximumWidth(180)
        logo_layout.addWidget(subtitle)
        
        logo_area.setLayout(logo_layout)
        layout.addWidget(logo_area)
        
        # Navigation menu
        nav_scroll = QScrollArea()
        nav_scroll.setWidgetResizable(True)
        nav_scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        nav_widget = QWidget()
        nav_layout = QVBoxLayout()
        nav_layout.setSpacing(2)
        nav_layout.setContentsMargins(0, 10, 0, 10)
        
        # Menu sections
        self.add_nav_section(nav_layout, "CORE", [
            ("🏠", "Dashboard"),
            ("🏏", "Players"),
            ("🏆", "Leagues"),
            ("📅", "Fixtures"),
            ("📈", "Statistics"),
        ])
        
        self.add_nav_section(nav_layout, "COMPETITION", [
            ("📊", "Rankings"),
            ("🌍", "World Cups"),
        ])
        
        self.add_nav_section(nav_layout, "DEVELOPMENT", [
            ("🎯", "Training"),
        ])
        
        self.add_nav_section(nav_layout, "SYSTEM", [
            ("⚙️", "Settings"),
            ("💾", "Save/Load"),
            ("❓", "Help"),
        ])
        
        nav_layout.addStretch()
        nav_widget.setLayout(nav_layout)
        nav_scroll.setWidget(nav_widget)
        layout.addWidget(nav_scroll, 1)
        
        sidebar.setLayout(layout)
        return sidebar
    
    def add_nav_section(self, layout, title, items):
        """Add a navigation section"""
        # Section title
        section_title = QLabel(title)
        section_title.setStyleSheet("""
            font-size: 10px;
            font-weight: 700;
            color: #666;
            padding: 15px 20px 8px 20px;
            letter-spacing: 1px;
        """)
        layout.addWidget(section_title)
        
        # Section items
        for icon, name in items:
            btn = self.create_nav_button(icon, name)
            layout.addWidget(btn)
    
    def create_nav_button(self, icon, name):
        """Create a navigation button"""
        btn = QPushButton(f"{icon}  {name}")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ccc;
                text-align: left;
                padding: 12px 20px;
                border: none;
                border-left: 3px solid transparent;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #252525;
                color: white;
                border-left: 3px solid #4CAF50;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
        """)
        btn.clicked.connect(lambda: self.on_nav_click(name))
        return btn
    
    def create_top_bar(self):
        """Create top bar with breadcrumbs and actions"""
        top_bar = QFrame()
        top_bar.setFixedHeight(60)
        top_bar.setStyleSheet(f"""
            QFrame {{
                background-color: #111827;
                border-bottom: 1px solid {COLORS['border']};
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(30, 0, 30, 0)
        
        # Breadcrumb / Current screen
        self.breadcrumb = QLabel("Dashboard")
        self.breadcrumb.setStyleSheet("""
            font-size: 20px;
            font-weight: 700;
            color: #EAF1FF;
        """)
        layout.addWidget(self.breadcrumb)
        
        layout.addStretch()
        
        # Quick stats in top bar
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(30)
        
        # Season info
        self.season_label = QLabel("Season: 1 | Year: 2025")
        self.season_label.setStyleSheet("font-size: 12px; color: #666; font-weight: 600;")
        stats_layout.addWidget(self.season_label)
        
        # User team info
        self.team_label = QLabel("Team: India")
        self.team_label.setStyleSheet("font-size: 12px; color: #666; font-weight: 600;")
        stats_layout.addWidget(self.team_label)
        
        # Credits
        self.credits_label = QLabel("Credits: 0")
        self.credits_label.setStyleSheet(f"font-size: 12px; color: {COLORS['success']}; font-weight: 700;")
        stats_layout.addWidget(self.credits_label)
        
        # Select XI button (manual team selection)
        self.select_xi_btn = QPushButton("Select XI")
        self.select_xi_btn.setStyleSheet(f"""
            QPushButton {{ background-color: {COLORS['primary']}; color: white; padding: 8px 16px; border-radius: 4px; font-weight: 600; }}
            QPushButton:hover {{ background-color: {COLORS['primary_light']}; }}
        """)
        self.select_xi_btn.clicked.connect(self._on_select_xi)
        stats_layout.addWidget(self.select_xi_btn)
        
        layout.addLayout(stats_layout)
        
        top_bar.setLayout(layout)
        return top_bar
    
    def _on_select_xi(self):
        """Open Select XI dialog for user team."""
        if not getattr(self.game_engine, 'user_team', None):
            return
        from cricket_manager.ui.select_xi_dialog import SelectXIDialog
        d = SelectXIDialog(self.game_engine.user_team, self)
        d.exec()
    
    def _show_team_selection(self):
        """Show the team selection screen as the first screen (International + Domestic)."""
        from cricket_manager.ui.team_selection_screen import TeamSelectionScreen
        domestic = getattr(self.game_engine, 'domestic_teams', []) or []
        self.team_selection = TeamSelectionScreen(self.game_engine.all_teams, domestic_teams=domestic)
        self.team_selection.team_selected.connect(self._on_team_selected)
        self.screen_manager.add_screen("TeamSelection", self.team_selection)
        self.screen_manager.show_screen("TeamSelection")
    
    def _on_team_selected(self, team):
        """Called when user picks a team on the selection screen (international or domestic)."""
        is_domestic = getattr(team, 'is_domestic', False)
        if is_domestic:
            nation = getattr(team, 'parent_nation', None)
            self.game_engine.user_team = self.game_engine.get_team_by_name(nation) if nation else self.game_engine.all_teams[0]
            self.game_engine.user_domestic_team = team
            print(f"[MainWindow] User selected domestic team: {team.name} ({nation})")
            display = f"{team.name} ({nation})"
        else:
            self.game_engine.user_team = team
            self.game_engine.user_domestic_team = None
            print(f"[MainWindow] User selected international team: {team.name} (Tier {team.format_tiers.get('T20', 1)})")
            display = team.name
        
        # Remove selection screen
        self.screen_manager.removeWidget(self.team_selection)
        self.team_selection.deleteLater()
        del self.screen_manager.screens["TeamSelection"]
        
        # Show sidebar and top bar
        self.sidebar.setVisible(True)
        self.top_bar.setVisible(True)
        
        # Initialize all game screens
        self.init_screens()
        
        # Navigate to Fixtures
        self.screen_manager.show_screen("Fixtures")
        self.breadcrumb.setText("Fixtures")
        fixtures_screen = self.screen_manager.screens.get("Fixtures")
        if fixtures_screen:
            if hasattr(fixtures_screen, 'team_combo'):
                idx = fixtures_screen.team_combo.findText(self.game_engine.user_team.name)
                if idx >= 0:
                    fixtures_screen.team_combo.setCurrentIndex(idx)
            user_tier = self.game_engine.user_team.format_tiers.get('T20', 1)
            if hasattr(fixtures_screen, 'tier_combo'):
                fixtures_screen.tier_combo.setCurrentIndex(user_tier)
        
        self.statusBar().showMessage(f"Welcome! Managing {display}")
    
    def init_screens(self):
        """Initialize screens with game engine"""
        # Import screen classes
        from cricket_manager.ui.teams_view import TeamsScreen
        from cricket_manager.ui.players_view import PlayersScreen
        from cricket_manager.ui.leagues_view_new import LeaguesScreen
        from cricket_manager.ui.fixtures_view import FixturesScreen
        from cricket_manager.ui.statistics_view import StatisticsScreen
        from cricket_manager.ui.rankings_view import RankingsScreen
        from cricket_manager.ui.settings_view import SettingsScreen
        from cricket_manager.ui.world_cup_view import WorldCupResultsScreen
        from cricket_manager.ui.youth_management_view import YouthManagementScreen
        from cricket_manager.ui.training_view import TrainingScreen
        from cricket_manager.ui.loot_pack_view import LootPackScreen
        from cricket_manager.ui.match_simulator_view import MatchSimulatorView
        
        # Create dashboard with game engine
        dashboard = DashboardScreen(self.screen_manager, self.game_engine, self)
        self.screen_manager.add_screen("Dashboard", dashboard)
        
        # Create teams screen with game engine
        teams_screen = TeamsScreen(self.screen_manager, self.game_engine)
        self.screen_manager.add_screen("Teams", teams_screen)
        
        # Create players screen with game engine
        players_screen = PlayersScreen(self.screen_manager, self.game_engine)
        self.screen_manager.add_screen("Players", players_screen)
        
        # Create leagues screen with game engine
        leagues_screen = LeaguesScreen(self.screen_manager, self.game_engine)
        self.screen_manager.add_screen("Leagues", leagues_screen)
        
        # Create fixtures screen with game engine
        fixtures_screen = FixturesScreen(self.screen_manager, self.game_engine)
        self.screen_manager.add_screen("Fixtures", fixtures_screen)
        
        # Create statistics screen with game engine
        self.statistics_view = StatisticsScreen(self.screen_manager, self.game_engine)
        self.screen_manager.add_screen("Statistics", self.statistics_view)
        
        # Create rankings screen with game engine
        rankings_screen = RankingsScreen(self.screen_manager, self.game_engine)
        self.screen_manager.add_screen("Rankings", rankings_screen)
        
        # Create World Cup screen
        world_cup_screen = WorldCupResultsScreen(self.screen_manager, self.game_engine)
        self.screen_manager.add_screen("World Cups", world_cup_screen)
        
        # Create Youth screen
        youth_screen = YouthManagementScreen(self.screen_manager, self.game_engine)
        self.screen_manager.add_screen("Youth", youth_screen)
        
        # Create Training screen
        training_screen = TrainingScreen(self.screen_manager, self.game_engine)
        self.screen_manager.add_screen("Training", training_screen)
        
        # Create Loot Pack screen
        loot_pack_screen = LootPackScreen(self.screen_manager, self.game_engine)
        self.screen_manager.add_screen("Loot Packs", loot_pack_screen)
        
        # Create Match Simulator screen
        match_simulator_screen = MatchSimulatorView(self.screen_manager, self.game_engine)
        self.screen_manager.add_screen("Match Simulator", match_simulator_screen)
        
        # Create settings screen
        settings_screen = SettingsScreen(self.screen_manager)
        self.screen_manager.add_screen("Settings", settings_screen)
        
        # Update top bar
        self.update_top_bar()
    
    def on_nav_click(self, screen_name):
        """Handle navigation click"""
        print(f"[Navigation] Clicked: {screen_name}")
        self.breadcrumb.setText(screen_name)
        
        # Handle special screens
        if screen_name == "Save/Load":
            self.show_save_load_dialog()
        elif screen_name == "Help":
            self.show_help_dialog()
        elif screen_name in self.screen_manager.screens:
            self.screen_manager.show_screen(screen_name)
            self.update_top_bar()
            
            # Auto-refresh data for certain screens
            screen = self.screen_manager.screens[screen_name]
            if screen_name in ["Players", "Statistics", "Rankings", "Fixtures", "World Cups", "Training"] and hasattr(screen, 'refresh_data'):
                print(f"[Navigation] Auto-refreshing {screen_name}")
                screen.refresh_data()
            
            # Pre-select user team in Statistics filter
            if screen_name == "Statistics" and self.game_engine.user_team:
                if hasattr(screen, 'team_combo'):
                    idx = screen.team_combo.findText(self.game_engine.user_team.name)
                    if idx >= 0:
                        screen.team_combo.setCurrentIndex(idx)
        else:
            # Show placeholder for unimplemented screens
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                screen_name,
                f"{screen_name} screen is not yet implemented.",
                QMessageBox.StandardButton.Ok
            )
    
    def update_top_bar(self):
        """Update top bar with current game state"""
        if hasattr(self, 'game_engine'):
            self.season_label.setText(f"Season: {self.game_engine.current_season} | Year: {self.game_engine.current_year}")
            if self.game_engine.user_team:
                ut = self.game_engine.user_team
                ud = getattr(self.game_engine, 'user_domestic_team', None)
                if ud:
                    self.team_label.setText(f"Team: {ut.name} ({ud.name})")
                else:
                    self.team_label.setText(f"Team: {ut.name}")
                self.credits_label.setText(f"Credits: {ut.credits:,}")
    
    def show_save_load_dialog(self):
        """Show save/load dialog"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QFileDialog, QMessageBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Save / Load Game")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Save section
        save_label = QLabel("Save Game")
        save_label.setStyleSheet("font-size: 16px; font-weight: 700;")
        layout.addWidget(save_label)
        
        save_layout = QHBoxLayout()
        self.save_input = QLineEdit()
        self.save_input.setPlaceholderText("Enter save name...")
        self.save_input.setText(f"save_season_{self.game_engine.current_season}.pkl")
        save_layout.addWidget(self.save_input)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(lambda: self.save_game(dialog))
        save_layout.addWidget(save_btn)
        layout.addLayout(save_layout)
        
        # Load section
        load_label = QLabel("Load Game")
        load_label.setStyleSheet("font-size: 16px; font-weight: 700;")
        layout.addWidget(load_label)
        
        load_btn = QPushButton("Browse and Load...")
        load_btn.clicked.connect(lambda: self.load_game(dialog))
        layout.addWidget(load_btn)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def save_game(self, dialog):
        """Save game to file"""
        filename = self.save_input.text()
        if not filename:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", "Please enter a filename")
            return
        
        try:
            self.game_engine.save_game(filename)
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Success", f"Game saved to {filename}")
            dialog.close()
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to save game: {str(e)}")
    
    def load_game(self, dialog):
        """Load game from file"""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Load Game",
            "",
            "Save Files (*.pkl);;All Files (*)"
        )
        
        if filename:
            try:
                self.game_engine.load_game(filename)
                self.update_top_bar()
                # Refresh all screens
                for screen in self.screen_manager.screens.values():
                    if hasattr(screen, 'refresh_data'):
                        screen.refresh_data()
                QMessageBox.information(self, "Success", f"Game loaded from {filename}")
                dialog.close()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load game: {str(e)}")
    
    def show_help_dialog(self):
        """Show help dialog"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Cricket Manager - Help",
            "Cricket Manager - Professional Edition\n\n"
            "Features:\n"
            "• Manage 76 teams across 5 tiers\n"
            "• 3 formats: T20, ODI, Test\n"
            "• Season simulation with fast match engine\n"
            "• World Cup tournaments every 2 years\n"
            "• Player development and traits\n"
            "• Youth academy system\n"
            "• Training and loot packs\n\n"
            "Navigation:\n"
            "• Use the sidebar to navigate between screens\n"
            "• Dashboard shows quick overview\n"
            "• Teams/Players screens show all data\n"
            "• Leagues screen to simulate seasons\n\n"
            "Tips:\n"
            "• Save your game regularly\n"
            "• Train players to improve skills\n"
            "• Promote youth players when ready\n"
            "• Watch for World Cups in even seasons",
            QMessageBox.StandardButton.Ok
        )


class DashboardScreen(QWidget):
    """Dashboard content area"""
    
    def __init__(self, screen_manager=None, game_engine=None, main_window=None):
        super().__init__()
        self.screen_manager = screen_manager
        self.game_engine = game_engine
        self.main_window = main_window
        self.init_ui()
    
    def init_ui(self):
        """Initialize dashboard UI"""
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"border: none; background-color: {COLORS['bg_primary']};")
        
        # Content
        content = QWidget()
        content.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
        content_layout = QVBoxLayout()
        content_layout.setSpacing(25)
        content_layout.setContentsMargins(30, 30, 30, 30)
        
        # Quick overview cards
        overview = self.create_overview_cards()
        content_layout.addWidget(overview)
        
        # Generate Fake Database button
        fake_db_btn = QPushButton("GENERATE FAKE DATABASE")
        fake_db_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        fake_db_btn.setMinimumHeight(50)
        fake_db_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['danger']};
                color: white;
                font-size: 16px;
                font-weight: 700;
                border: none;
                border-radius: 8px;
                padding: 12px 30px;
            }}
            QPushButton:hover {{
                background-color: #b71c1c;
            }}
            QPushButton:pressed {{
                background-color: #880e0e;
            }}
        """)
        fake_db_btn.clicked.connect(self.on_generate_fake_database)
        content_layout.addWidget(fake_db_btn)
        
        # Hide batting/bowling abilities toggle (same row as fake DB)
        self.hide_ratings_btn = QPushButton("HIDE PLAYERS BATTING AND BOWLING ABILITIES")
        self.hide_ratings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.hide_ratings_btn.setCheckable(True)
        self.hide_ratings_btn.setChecked(getattr(self.game_engine, 'hide_batting_bowling_ratings', False))
        self.hide_ratings_btn.setMinimumHeight(50)
        self._update_hide_ratings_button_text()
        self.hide_ratings_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['warning']};
                color: white;
                font-size: 14px;
                font-weight: 700;
                border: none;
                border-radius: 8px;
                padding: 12px 30px;
            }}
            QPushButton:hover {{
                background-color: #E65100;
            }}
            QPushButton:checked {{
                background-color: #2E7D32;
            }}
        """)
        self.hide_ratings_btn.clicked.connect(self.on_toggle_hide_ratings)
        content_layout.addWidget(self.hide_ratings_btn)
        
        content_layout.addStretch()
        content.setLayout(content_layout)
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)
        
        self.setLayout(layout)
    
    def create_overview_cards(self):
        """Create overview cards"""
        container = QWidget()
        layout = QGridLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Get real data from game engine
        if self.game_engine:
            total_teams = len(self.game_engine.all_teams)
            total_players = sum(len(team.players) for team in self.game_engine.all_teams)
            user_credits = self.game_engine.user_team.credits if self.game_engine.user_team else 0
            current_season = self.game_engine.current_season
        else:
            total_teams = 76
            total_players = 1140
            user_credits = 0
            current_season = 1
        
        # Cards data
        cards = [
            (str(total_teams), "Total Teams", "Across all tiers", COLORS['primary']),
            (f"{total_players:,}", "Total Players", "15 per team", COLORS['info']),
            (f"Season {current_season}", "Current Season", f"Year {2024 + current_season}", COLORS['success']),
            (f"{user_credits:,}", "Your Credits", "Team budget", COLORS['warning']),
        ]
        
        for i, (value, title, subtitle, color) in enumerate(cards):
            card = self.create_info_card(value, title, subtitle, color)
            layout.addWidget(card, 0, i)
        
        container.setLayout(layout)
        return container
    
    def create_info_card(self, value, title, subtitle, color):
        """Create an info card"""
        card = QFrame()
        card.setMinimumHeight(150)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #111827;
                border-radius: 8px;
                border: 1px solid {COLORS['border']};
                padding: 25px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Value
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            font-size: 36px;
            font-weight: 700;
            color: {color};
            background: transparent;
        """)
        value_label.setWordWrap(False)
        layout.addWidget(value_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 15px;
            font-weight: 600;
            color: #EAF1FF;
            background: transparent;
        """)
        title_label.setWordWrap(False)
        layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("""
            font-size: 12px;
            color: #888;
            background: transparent;
        """)
        subtitle_label.setWordWrap(True)
        layout.addWidget(subtitle_label)
        
        layout.addStretch()
        
        card.setLayout(layout)
        return card
    
    def create_quick_actions(self):
        """Create quick actions section"""
        container = QFrame()
        container.setStyleSheet(f"""
            background-color: #111827;
            border-radius: 8px;
            border: 1px solid {COLORS['border']};
            padding: 25px;
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Section title
        title = QLabel("Quick Actions")
        title.setStyleSheet("""
            font-size: 16px;
            font-weight: 700;
            color: #EAF1FF;
        """)
        layout.addWidget(title)
        
        # Actions grid
        actions_grid = QGridLayout()
        actions_grid.setSpacing(15)
        
        actions = [
            ("🏏", "View Players", "Browse all players", COLORS['info'], "Players"),
            ("📅", "Fixtures", "Upcoming matches", COLORS['warning'], "Fixtures"),
            ("🏆", "Simulate Season", "Run full season", COLORS['success'], "Leagues"),
            ("🎁", "Loot Packs", "Open rewards", COLORS['accent'], "Loot Packs"),
            ("⭐", "Youth", "Manage U21", COLORS['info'], "Youth"),
            ("🌍", "World Cups", "Tournaments", COLORS['gold'], "World Cups"),
        ]
        
        for i, (icon, title, desc, color, screen) in enumerate(actions):
            btn = self.create_action_button(icon, title, desc, color, screen)
            row = i // 3
            col = i % 3
            actions_grid.addWidget(btn, row, col)
        
        layout.addLayout(actions_grid)
        container.setLayout(layout)
        return container
    
    def create_action_button(self, icon, title, description, color, screen_name):
        """Create an action button"""
        btn = QPushButton()
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setMinimumHeight(80)
        
        # Create a frame to hold content
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
                border: none;
            }}
        """)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        btn_layout.setContentsMargins(15, 10, 15, 10)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 28px; color: {color}; background: transparent;")
        icon_label.setFixedWidth(35)
        btn_layout.addWidget(icon_label)
        
        # Text
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 13px;
            font-weight: 700;
            color: #EAF1FF;
            background: transparent;
        """)
        text_layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            font-size: 11px;
            color: #888;
            background: transparent;
        """)
        text_layout.addWidget(desc_label)
        
        btn_layout.addLayout(text_layout)
        btn_layout.addStretch()
        
        frame.setLayout(btn_layout)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(frame)
        btn.setLayout(main_layout)
        
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #111827;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_tertiary']};
                border: 2px solid {color};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['bg_hover']};
            }}
        """)
        
        btn.clicked.connect(lambda: self.on_action_click(screen_name))
        return btn
    
    def on_action_click(self, screen_name):
        """Handle quick action button clicks"""
        print(f"[Dashboard] Action: {screen_name}")
        if self.screen_manager and screen_name in self.screen_manager.screens:
            self.screen_manager.show_screen(screen_name)
            if self.main_window:
                self.main_window.update_top_bar()
    
    def on_generate_fake_database(self):
        """Handle Generate Fake Database button click"""
        from PyQt6.QtWidgets import QMessageBox
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Generate Fake Database")
        msg.setText(
            "This will REPLACE ALL players in every international team and every domestic club "
            "with randomly generated players (custom domestic roster files are ignored for this rebuild).\n\n"
            "All career stats, traits, and history will be reset.\n\n"
            "Are you sure?"
        )
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        
        if msg.exec() != QMessageBox.StandardButton.Yes:
            return
        if not self.game_engine:
            return
        
        msg2 = QMessageBox(self)
        msg2.setWindowTitle("Generate Fake Database")
        msg2.setText(
            "Generate synthetic career statistics (matches, runs, wickets, etc.) for all players?\n\n"
            "Choose \"Without stats\" to leave career totals at zero for everyone."
        )
        msg2.setIcon(QMessageBox.Icon.Question)
        btn_with = msg2.addButton("With stats", QMessageBox.ButtonRole.AcceptRole)
        btn_without = msg2.addButton("Without stats", QMessageBox.ButtonRole.ActionRole)
        msg2.exec()
        clicked = msg2.clickedButton()
        if clicked is None:
            return
        if clicked == btn_with:
            with_stats = True
        elif clicked == btn_without:
            with_stats = False
        else:
            return
        
        total = self.game_engine.generate_fake_database(with_stats=with_stats)
        nd = len(getattr(self.game_engine, "domestic_teams", []) or [])
        dcount = sum(
            len(getattr(t, "players", []) or [])
            for t in (getattr(self.game_engine, "domestic_teams", None) or [])
        )
        stats_line = (
            "Synthetic career statistics were generated for players."
            if with_stats
            else "Career statistics were left at zero (no synthetic totals)."
        )
        QMessageBox.information(
            self, "Fake Database Generated",
            f"Successfully generated {total} new international players "
            f"({len(self.game_engine.all_teams)} teams) and {dcount} domestic club players "
            f"({nd} clubs).\n\n"
            f"{stats_line}\n\n"
            "All player data has been reset.",
        )
        
        # Refresh all screens
        if self.screen_manager:
            for name, screen in self.screen_manager.screens.items():
                if name == "Dashboard" and hasattr(screen, '_update_hide_ratings_button_text'):
                    screen._update_hide_ratings_button_text()
                if hasattr(screen, 'refresh_data'):
                    screen.refresh_data()
    
    def _update_hide_ratings_button_text(self):
        """Update the hide ratings button label to reflect current state."""
        if not hasattr(self, 'hide_ratings_btn'):
            return
        hide = getattr(self.game_engine, 'hide_batting_bowling_ratings', False)
        self.hide_ratings_btn.setText("SHOW PLAYERS BATTING AND BOWLING ABILITIES" if hide else "HIDE PLAYERS BATTING AND BOWLING ABILITIES")
        self.hide_ratings_btn.setChecked(hide)
    
    def on_toggle_hide_ratings(self):
        """Toggle hide batting/bowling ratings and refresh screens that show them."""
        if not self.game_engine:
            return
        self.game_engine.hide_batting_bowling_ratings = self.hide_ratings_btn.isChecked()
        self._update_hide_ratings_button_text()
        if self.screen_manager:
            for name, screen in self.screen_manager.screens.items():
                if hasattr(screen, 'refresh_data'):
                    screen.refresh_data()
    
    def refresh_data(self):
        """Refresh dashboard data (e.g. after loading a game)."""
        self._update_hide_ratings_button_text()
