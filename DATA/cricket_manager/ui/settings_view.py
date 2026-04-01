"""
Settings Screen - Game configuration and preferences
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QFrame, QScrollArea, QGridLayout, QCheckBox,
    QSpinBox, QGroupBox, QLineEdit, QMessageBox, QSlider
)
from PyQt6.QtCore import Qt

from cricket_manager.ui.styles import COLORS, MAIN_STYLESHEET
from cricket_manager.ui.screen_manager import BaseScreen


class SettingsScreen(BaseScreen):
    """Settings and configuration screen"""
    
    def __init__(self, screen_manager=None, game_engine=None):
        super().__init__(screen_manager)
        self.setStyleSheet(MAIN_STYLESHEET)
        self.game_engine = game_engine
        self.settings = self.load_default_settings()
        # Load simulation settings from game engine if available
        self.load_settings_from_engine()
        self.init_ui()
    
    def load_settings_from_engine(self):
        """Load simulation settings from game engine (for save/load support)"""
        if self.game_engine and hasattr(self.game_engine, 'simulation_settings'):
            sim_settings = self.game_engine.simulation_settings
            if sim_settings:
                # Update settings with values from game engine
                for key in sim_settings:
                    if key in self.settings:
                        self.settings[key] = sim_settings[key]
                print(f"[Settings] Loaded simulation settings from game engine")
            if hasattr(self.game_engine, 'difficulty'):
                d = self.game_engine.difficulty
                self.settings['difficulty'] = 'Medium' if d == 'Normal' else d
    
    def load_default_settings(self):
        """Load default settings"""
        return {
            'game_speed': 'Normal',
            'auto_save': True,
            'auto_save_interval': 5,
            'show_animations': True,
            'sound_enabled': True,
            'music_volume': 70,
            'sfx_volume': 80,
            'difficulty': 'Medium',
            'simulation_detail': 'Medium',
            'player_name': 'Manager',
            'favorite_team': 'India',
            'starting_credits': 1000,
            'starting_training_points': 5,
            # Simulation probability adjustments (-100 to +100)
            't20_dot_adj': 0,
            't20_single_adj': 0,
            't20_double_adj': 0,
            't20_triple_adj': 0,
            't20_boundary_adj': 0,
            't20_wicket_adj': 0,
            'odi_dot_adj': 0,
            'odi_single_adj': 0,
            'odi_double_adj': 0,
            'odi_triple_adj': 0,
            'odi_boundary_adj': 0,
            'odi_wicket_adj': 0,
            'test_dot_adj': 0,
            'test_single_adj': 0,
            'test_double_adj': 0,
            'test_triple_adj': 0,
            'test_boundary_adj': 0,
            'test_wicket_adj': 0,
        }
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Main scroll area - SINGLE SCROLL BAR
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"border: none; background-color: {COLORS['bg_primary']};")
        
        # Content
        content = QWidget()
        content.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
        content_layout = QVBoxLayout()
        content_layout.setSpacing(25)
        content_layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header = self.create_header()
        content_layout.addWidget(header)
        
        # Manager Profile (includes managed team selection)
        manager_profile = self.create_manager_profile()
        content_layout.addWidget(manager_profile)
        
        # Simulation Tuning
        simulation_tuning = self.create_simulation_tuning()
        content_layout.addWidget(simulation_tuning)
        
        # Action buttons
        actions = self.create_action_buttons()
        content_layout.addWidget(actions)
        
        content_layout.addStretch()
        content.setLayout(content_layout)
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)
        
        self.setLayout(layout)
    
    def create_header(self):
        """Create header section"""
        container = QFrame()
        container.setStyleSheet(f"""
            background-color: #111827;
            border-radius: 8px;
            border: 1px solid {COLORS['border']};
            padding: 20px;
        """)
        
        layout = QHBoxLayout()
        
        title = QLabel("⚙️ Game Settings")
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: 700;
            color: #EAF1FF;
        """)
        layout.addWidget(title)
        
        layout.addStretch()
        
        info = QLabel("Configure your game preferences")
        info.setStyleSheet("""
            font-size: 13px;
            color: #666;
        """)
        layout.addWidget(info)
        
        container.setLayout(layout)
        return container
    
    def create_game_settings(self):
        """Create game settings section"""
        container = QFrame()
        container.setStyleSheet(f"""
            background-color: #111827;
            border-radius: 8px;
            border: 1px solid {COLORS['border']};
            padding: 20px;
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Section title
        title = QLabel("Game Settings")
        title.setStyleSheet("""
            font-size: 16px;
            font-weight: 700;
            color: #EAF1FF;
        """)
        layout.addWidget(title)
        
        # Settings grid
        grid = QGridLayout()
        grid.setSpacing(15)
        
        # Game Speed
        grid.addWidget(QLabel("Game Speed:"), 0, 0)
        self.game_speed_combo = QComboBox()
        self.game_speed_combo.addItems(['Slow', 'Normal', 'Fast', 'Very Fast'])
        self.game_speed_combo.setCurrentText(self.settings['game_speed'])
        self.game_speed_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: #111827;
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                min-width: 150px;
            }}
        """)
        grid.addWidget(self.game_speed_combo, 0, 1)
        
        # Auto Save
        self.auto_save_check = QCheckBox("Enable Auto-Save")
        self.auto_save_check.setChecked(self.settings['auto_save'])
        self.auto_save_check.setStyleSheet("font-size: 13px;")
        grid.addWidget(self.auto_save_check, 1, 0)
        
        # Auto Save Interval
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Every"))
        self.auto_save_interval = QSpinBox()
        self.auto_save_interval.setRange(1, 30)
        self.auto_save_interval.setValue(self.settings['auto_save_interval'])
        self.auto_save_interval.setSuffix(" minutes")
        interval_layout.addWidget(self.auto_save_interval)
        interval_layout.addStretch()
        grid.addLayout(interval_layout, 1, 1)
        
        # Show Animations
        self.animations_check = QCheckBox("Show Animations")
        self.animations_check.setChecked(self.settings['show_animations'])
        self.animations_check.setStyleSheet("font-size: 13px;")
        grid.addWidget(self.animations_check, 2, 0)
        
        layout.addLayout(grid)
        container.setLayout(layout)
        return container
    
    def create_audio_settings(self):
        """Create audio settings section"""
        container = QFrame()
        container.setStyleSheet(f"""
            background-color: #111827;
            border-radius: 8px;
            border: 1px solid {COLORS['border']};
            padding: 20px;
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Section title
        title = QLabel("Audio Settings")
        title.setStyleSheet("""
            font-size: 16px;
            font-weight: 700;
            color: #EAF1FF;
        """)
        layout.addWidget(title)
        
        # Settings grid
        grid = QGridLayout()
        grid.setSpacing(15)
        
        # Sound Enabled
        self.sound_check = QCheckBox("Enable Sound")
        self.sound_check.setChecked(self.settings['sound_enabled'])
        self.sound_check.setStyleSheet("font-size: 13px;")
        grid.addWidget(self.sound_check, 0, 0)
        
        # Music Volume
        grid.addWidget(QLabel("Music Volume:"), 1, 0)
        self.music_volume = QSpinBox()
        self.music_volume.setRange(0, 100)
        self.music_volume.setValue(self.settings['music_volume'])
        self.music_volume.setSuffix("%")
        grid.addWidget(self.music_volume, 1, 1)
        
        # SFX Volume
        grid.addWidget(QLabel("Sound Effects:"), 2, 0)
        self.sfx_volume = QSpinBox()
        self.sfx_volume.setRange(0, 100)
        self.sfx_volume.setValue(self.settings['sfx_volume'])
        self.sfx_volume.setSuffix("%")
        grid.addWidget(self.sfx_volume, 2, 1)
        
        layout.addLayout(grid)
        container.setLayout(layout)
        return container
    
    def create_gameplay_settings(self):
        """Create gameplay settings section"""
        container = QFrame()
        container.setStyleSheet(f"""
            background-color: #111827;
            border-radius: 8px;
            border: 1px solid {COLORS['border']};
            padding: 20px;
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Section title
        title = QLabel("Gameplay Settings")
        title.setStyleSheet("""
            font-size: 16px;
            font-weight: 700;
            color: #EAF1FF;
        """)
        layout.addWidget(title)
        
        # Settings grid
        grid = QGridLayout()
        grid.setSpacing(15)
        
        # Difficulty
        grid.addWidget(QLabel("Difficulty:"), 0, 0)
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(['Easy', 'Medium', 'Hard', 'Expert'])
        self.difficulty_combo.setCurrentText(self.settings['difficulty'])
        self.difficulty_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: #111827;
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                min-width: 150px;
            }}
        """)
        grid.addWidget(self.difficulty_combo, 0, 1)
        
        # Simulation Detail
        grid.addWidget(QLabel("Simulation Detail:"), 1, 0)
        self.sim_detail_combo = QComboBox()
        self.sim_detail_combo.addItems(['Low', 'Medium', 'High', 'Very High'])
        self.sim_detail_combo.setCurrentText(self.settings['simulation_detail'])
        self.sim_detail_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: #111827;
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                min-width: 150px;
            }}
        """)
        grid.addWidget(self.sim_detail_combo, 1, 1)
        
        # Starting Credits
        grid.addWidget(QLabel("Starting Credits:"), 2, 0)
        self.starting_credits = QSpinBox()
        self.starting_credits.setRange(0, 10000)
        self.starting_credits.setSingleStep(100)
        self.starting_credits.setValue(self.settings['starting_credits'])
        grid.addWidget(self.starting_credits, 2, 1)
        
        # Starting Training Points
        grid.addWidget(QLabel("Starting Training Points:"), 3, 0)
        self.starting_training = QSpinBox()
        self.starting_training.setRange(0, 20)
        self.starting_training.setValue(self.settings['starting_training_points'])
        grid.addWidget(self.starting_training, 3, 1)
        
        layout.addLayout(grid)
        container.setLayout(layout)
        return container
    
    def create_manager_profile(self):
        """Create manager profile section with managed team selection"""
        container = QFrame()
        container.setStyleSheet(f"""
            background-color: #111827;
            border-radius: 8px;
            border: 1px solid {COLORS['border']};
            padding: 20px;
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Section title
        title = QLabel("Manager Profile")
        title.setStyleSheet("""
            font-size: 16px;
            font-weight: 700;
            color: #EAF1FF;
        """)
        layout.addWidget(title)
        
        # Settings grid
        grid = QGridLayout()
        grid.setSpacing(15)
        
        # Manager Name
        grid.addWidget(QLabel("Manager Name:"), 0, 0)
        self.manager_name = QLineEdit()
        self.manager_name.setText(self.settings['player_name'])
        self.manager_name.setStyleSheet(f"""
            QLineEdit {{
                background-color: #111827;
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
            }}
        """)
        grid.addWidget(self.manager_name, 0, 1)
        
        # Managed Team - populate from game engine with tier organization
        grid.addWidget(QLabel("Managed Team:"), 1, 0)
        self.managed_team_combo = QComboBox()
        
        # Get all teams from game engine organized by tier
        if self.game_engine and hasattr(self.game_engine, 'all_teams'):
            # Organize teams by tier
            tier1_teams = []
            tier2_teams = []
            tier3_teams = []
            tier4_teams = []
            
            for team in self.game_engine.all_teams:
                tier = getattr(team, 'tier', 1)
                if tier == 1:
                    tier1_teams.append(team.name)
                elif tier == 2:
                    tier2_teams.append(team.name)
                elif tier == 3:
                    tier3_teams.append(team.name)
                else:
                    tier4_teams.append(team.name)
            
            # Add teams grouped by category
            if tier1_teams:
                self.managed_team_combo.addItem("── International (Test Nations) ──")
                for name in sorted(tier1_teams):
                    self.managed_team_combo.addItem(f"  {name}")
            if tier2_teams:
                self.managed_team_combo.addItem("── Associate (Tier 2) ──")
                for name in sorted(tier2_teams):
                    self.managed_team_combo.addItem(f"  {name}")
            if tier3_teams:
                self.managed_team_combo.addItem("── Associate (Tier 3) ──")
                for name in sorted(tier3_teams):
                    self.managed_team_combo.addItem(f"  {name}")
            if tier4_teams:
                self.managed_team_combo.addItem("── Associate (Tier 4) ──")
                for name in sorted(tier4_teams):
                    self.managed_team_combo.addItem(f"  {name}")
            
            # Set current team
            if self.game_engine.user_team:
                # Find the item with the team name (with leading spaces)
                for i in range(self.managed_team_combo.count()):
                    if self.game_engine.user_team.name in self.managed_team_combo.itemText(i):
                        self.managed_team_combo.setCurrentIndex(i)
                        break
        else:
            # Fallback list
            teams = ['India', 'Australia', 'England', 'Pakistan', 'South Africa', 
                    'New Zealand', 'West Indies', 'Sri Lanka', 'Bangladesh', 'Afghanistan']
            self.managed_team_combo.addItems(teams)
            self.managed_team_combo.setCurrentText(self.settings['favorite_team'])
        
        self.managed_team_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: #111827;
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                min-width: 200px;
            }}
        """)
        self.managed_team_combo.currentTextChanged.connect(self._on_managed_team_changed)
        grid.addWidget(self.managed_team_combo, 1, 1)
        
        # Info label
        info_label = QLabel("Changing managed team will update Training tab and main GUI")
        info_label.setStyleSheet("font-size: 11px; color: #666; font-style: italic;")
        grid.addWidget(info_label, 2, 0, 1, 2)
        
        layout.addLayout(grid)
        container.setLayout(layout)
        return container
    
    def _on_managed_team_changed(self, text):
        """Immediately update managed team when combo box changes"""
        team_name = text.strip()
        # Skip category headers
        if not team_name or team_name.startswith("──"):
            return
        if not self.game_engine:
            return
        new_team = self.game_engine.get_team_by_name(team_name)
        if new_team and new_team != self.game_engine.user_team:
            old_name = self.game_engine.user_team.name if self.game_engine.user_team else "None"
            self.game_engine.user_team = new_team
            print(f"[Settings] Managed team changed: {old_name} → {new_team.name}")
            
            # Update main window top bar
            if self.screen_manager:
                main_window = self.screen_manager.parent()
                while main_window and not hasattr(main_window, 'update_top_bar'):
                    main_window = main_window.parent() if hasattr(main_window, 'parent') else None
                if main_window and hasattr(main_window, 'update_top_bar'):
                    main_window.update_top_bar()
            
            # Refresh training screen
            if self.screen_manager and hasattr(self.screen_manager, 'screens'):
                training_screen = self.screen_manager.screens.get('Training')
                if training_screen and hasattr(training_screen, 'refresh_data'):
                    training_screen.refresh_data()
    
    def create_simulation_tuning(self):
        """Create simulation probability tuning section"""
        container = QFrame()
        container.setStyleSheet(f"""
            background-color: #111827;
            border-radius: 8px;
            border: 1px solid {COLORS['border']};
            padding: 20px;
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Section title
        title = QLabel("Simulation Tuning")
        title.setStyleSheet("""
            font-size: 16px;
            font-weight: 700;
            color: #EAF1FF;
        """)
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Adjust simulation probabilities (-100% to +100%). 0% = default values.")
        desc.setStyleSheet("font-size: 12px; color: #666;")
        layout.addWidget(desc)
        
        # T20 Settings
        t20_group = QGroupBox("T20 Adjustments")
        t20_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        t20_layout = QGridLayout()
        t20_layout.setSpacing(10)
        
        # T20 Dot Ball (0s)
        t20_dot_lbl = QLabel("Dot Balls / 0s (+ = more dots):")
        t20_dot_lbl.setStyleSheet("font-size: 12px;")
        t20_layout.addWidget(t20_dot_lbl, 0, 0)
        self.t20_dot_slider = self.create_adjustment_slider('t20_dot_adj')
        t20_layout.addWidget(self.t20_dot_slider, 0, 1)
        self.t20_dot_label = QLabel(f"{self.settings['t20_dot_adj']}%")
        self.t20_dot_label.setMinimumWidth(50)
        t20_layout.addWidget(self.t20_dot_label, 0, 2)
        self.t20_dot_slider.valueChanged.connect(lambda v: self.update_slider_realtime('t20_dot_adj', v, self.t20_dot_label))
        
        # T20 Singles (1s)
        t20_single_lbl = QLabel("Singles / 1s (+ = more singles):")
        t20_single_lbl.setStyleSheet("font-size: 12px;")
        t20_layout.addWidget(t20_single_lbl, 1, 0)
        self.t20_single_slider = self.create_adjustment_slider('t20_single_adj')
        t20_layout.addWidget(self.t20_single_slider, 1, 1)
        self.t20_single_label = QLabel(f"{self.settings['t20_single_adj']}%")
        self.t20_single_label.setMinimumWidth(50)
        t20_layout.addWidget(self.t20_single_label, 1, 2)
        self.t20_single_slider.valueChanged.connect(lambda v: self.update_slider_realtime('t20_single_adj', v, self.t20_single_label))
        
        # T20 Doubles (2s)
        t20_double_lbl = QLabel("Doubles / 2s (+ = more doubles):")
        t20_double_lbl.setStyleSheet("font-size: 12px;")
        t20_layout.addWidget(t20_double_lbl, 2, 0)
        self.t20_double_slider = self.create_adjustment_slider('t20_double_adj')
        t20_layout.addWidget(self.t20_double_slider, 2, 1)
        self.t20_double_label = QLabel(f"{self.settings['t20_double_adj']}%")
        self.t20_double_label.setMinimumWidth(50)
        t20_layout.addWidget(self.t20_double_label, 2, 2)
        self.t20_double_slider.valueChanged.connect(lambda v: self.update_slider_realtime('t20_double_adj', v, self.t20_double_label))
        
        # T20 Triples (3s)
        t20_triple_lbl = QLabel("Triples / 3s (+ = more triples):")
        t20_triple_lbl.setStyleSheet("font-size: 12px;")
        t20_layout.addWidget(t20_triple_lbl, 3, 0)
        self.t20_triple_slider = self.create_adjustment_slider('t20_triple_adj')
        t20_layout.addWidget(self.t20_triple_slider, 3, 1)
        self.t20_triple_label = QLabel(f"{self.settings['t20_triple_adj']}%")
        self.t20_triple_label.setMinimumWidth(50)
        t20_layout.addWidget(self.t20_triple_label, 3, 2)
        self.t20_triple_slider.valueChanged.connect(lambda v: self.update_slider_realtime('t20_triple_adj', v, self.t20_triple_label))
        
        # T20 Boundary
        t20_bnd_lbl = QLabel("Boundaries / 4s & 6s (+ = more boundaries):")
        t20_bnd_lbl.setStyleSheet("font-size: 12px;")
        t20_layout.addWidget(t20_bnd_lbl, 4, 0)
        self.t20_boundary_slider = self.create_adjustment_slider('t20_boundary_adj')
        t20_layout.addWidget(self.t20_boundary_slider, 4, 1)
        self.t20_boundary_label = QLabel(f"{self.settings['t20_boundary_adj']}%")
        self.t20_boundary_label.setMinimumWidth(50)
        t20_layout.addWidget(self.t20_boundary_label, 4, 2)
        self.t20_boundary_slider.valueChanged.connect(lambda v: self.update_slider_realtime('t20_boundary_adj', v, self.t20_boundary_label))
        
        # T20 Wicket
        t20_wkt_lbl = QLabel("Wickets (+ = more wickets):")
        t20_wkt_lbl.setStyleSheet("font-size: 12px;")
        t20_layout.addWidget(t20_wkt_lbl, 5, 0)
        self.t20_wicket_slider = self.create_adjustment_slider('t20_wicket_adj')
        t20_layout.addWidget(self.t20_wicket_slider, 5, 1)
        self.t20_wicket_label = QLabel(f"{self.settings['t20_wicket_adj']}%")
        self.t20_wicket_label.setMinimumWidth(50)
        t20_layout.addWidget(self.t20_wicket_label, 5, 2)
        self.t20_wicket_slider.valueChanged.connect(lambda v: self.update_slider_realtime('t20_wicket_adj', v, self.t20_wicket_label))
        
        t20_group.setLayout(t20_layout)
        layout.addWidget(t20_group)
        
        # ODI Settings
        odi_group = QGroupBox("ODI Adjustments")
        odi_group.setStyleSheet(t20_group.styleSheet())
        odi_layout = QGridLayout()
        odi_layout.setSpacing(10)
        
        # ODI Dot Ball (0s)
        odi_dot_lbl = QLabel("Dot Balls / 0s (+ = more dots):")
        odi_dot_lbl.setStyleSheet("font-size: 12px;")
        odi_layout.addWidget(odi_dot_lbl, 0, 0)
        self.odi_dot_slider = self.create_adjustment_slider('odi_dot_adj')
        odi_layout.addWidget(self.odi_dot_slider, 0, 1)
        self.odi_dot_label = QLabel(f"{self.settings['odi_dot_adj']}%")
        self.odi_dot_label.setMinimumWidth(50)
        odi_layout.addWidget(self.odi_dot_label, 0, 2)
        self.odi_dot_slider.valueChanged.connect(lambda v: self.update_slider_realtime('odi_dot_adj', v, self.odi_dot_label))
        
        # ODI Singles (1s)
        odi_single_lbl = QLabel("Singles / 1s (+ = more singles):")
        odi_single_lbl.setStyleSheet("font-size: 12px;")
        odi_layout.addWidget(odi_single_lbl, 1, 0)
        self.odi_single_slider = self.create_adjustment_slider('odi_single_adj')
        odi_layout.addWidget(self.odi_single_slider, 1, 1)
        self.odi_single_label = QLabel(f"{self.settings['odi_single_adj']}%")
        self.odi_single_label.setMinimumWidth(50)
        odi_layout.addWidget(self.odi_single_label, 1, 2)
        self.odi_single_slider.valueChanged.connect(lambda v: self.update_slider_realtime('odi_single_adj', v, self.odi_single_label))
        
        # ODI Doubles (2s)
        odi_double_lbl = QLabel("Doubles / 2s (+ = more doubles):")
        odi_double_lbl.setStyleSheet("font-size: 12px;")
        odi_layout.addWidget(odi_double_lbl, 2, 0)
        self.odi_double_slider = self.create_adjustment_slider('odi_double_adj')
        odi_layout.addWidget(self.odi_double_slider, 2, 1)
        self.odi_double_label = QLabel(f"{self.settings['odi_double_adj']}%")
        self.odi_double_label.setMinimumWidth(50)
        odi_layout.addWidget(self.odi_double_label, 2, 2)
        self.odi_double_slider.valueChanged.connect(lambda v: self.update_slider_realtime('odi_double_adj', v, self.odi_double_label))
        
        # ODI Triples (3s)
        odi_triple_lbl = QLabel("Triples / 3s (+ = more triples):")
        odi_triple_lbl.setStyleSheet("font-size: 12px;")
        odi_layout.addWidget(odi_triple_lbl, 3, 0)
        self.odi_triple_slider = self.create_adjustment_slider('odi_triple_adj')
        odi_layout.addWidget(self.odi_triple_slider, 3, 1)
        self.odi_triple_label = QLabel(f"{self.settings['odi_triple_adj']}%")
        self.odi_triple_label.setMinimumWidth(50)
        odi_layout.addWidget(self.odi_triple_label, 3, 2)
        self.odi_triple_slider.valueChanged.connect(lambda v: self.update_slider_realtime('odi_triple_adj', v, self.odi_triple_label))
        
        # ODI Boundary
        odi_bnd_lbl = QLabel("Boundaries / 4s & 6s (+ = more boundaries):")
        odi_bnd_lbl.setStyleSheet("font-size: 12px;")
        odi_layout.addWidget(odi_bnd_lbl, 4, 0)
        self.odi_boundary_slider = self.create_adjustment_slider('odi_boundary_adj')
        odi_layout.addWidget(self.odi_boundary_slider, 4, 1)
        self.odi_boundary_label = QLabel(f"{self.settings['odi_boundary_adj']}%")
        self.odi_boundary_label.setMinimumWidth(50)
        odi_layout.addWidget(self.odi_boundary_label, 4, 2)
        self.odi_boundary_slider.valueChanged.connect(lambda v: self.update_slider_realtime('odi_boundary_adj', v, self.odi_boundary_label))
        
        # ODI Wicket
        odi_wkt_lbl = QLabel("Wickets (+ = more wickets):")
        odi_wkt_lbl.setStyleSheet("font-size: 12px;")
        odi_layout.addWidget(odi_wkt_lbl, 5, 0)
        self.odi_wicket_slider = self.create_adjustment_slider('odi_wicket_adj')
        odi_layout.addWidget(self.odi_wicket_slider, 5, 1)
        self.odi_wicket_label = QLabel(f"{self.settings['odi_wicket_adj']}%")
        self.odi_wicket_label.setMinimumWidth(50)
        odi_layout.addWidget(self.odi_wicket_label, 5, 2)
        self.odi_wicket_slider.valueChanged.connect(lambda v: self.update_slider_realtime('odi_wicket_adj', v, self.odi_wicket_label))
        
        odi_group.setLayout(odi_layout)
        layout.addWidget(odi_group)
        
        # Test Settings
        test_group = QGroupBox("Test Match Adjustments")
        test_group.setStyleSheet(t20_group.styleSheet())
        test_layout = QGridLayout()
        test_layout.setSpacing(10)
        
        # Test Dot Ball (0s)
        test_dot_lbl = QLabel("Dot Balls / 0s (+ = more dots):")
        test_dot_lbl.setStyleSheet("font-size: 12px;")
        test_layout.addWidget(test_dot_lbl, 0, 0)
        self.test_dot_slider = self.create_adjustment_slider('test_dot_adj')
        test_layout.addWidget(self.test_dot_slider, 0, 1)
        self.test_dot_label = QLabel(f"{self.settings['test_dot_adj']}%")
        self.test_dot_label.setMinimumWidth(50)
        test_layout.addWidget(self.test_dot_label, 0, 2)
        self.test_dot_slider.valueChanged.connect(lambda v: self.update_slider_realtime('test_dot_adj', v, self.test_dot_label))
        
        # Test Singles (1s)
        test_single_lbl = QLabel("Singles / 1s (+ = more singles):")
        test_single_lbl.setStyleSheet("font-size: 12px;")
        test_layout.addWidget(test_single_lbl, 1, 0)
        self.test_single_slider = self.create_adjustment_slider('test_single_adj')
        test_layout.addWidget(self.test_single_slider, 1, 1)
        self.test_single_label = QLabel(f"{self.settings['test_single_adj']}%")
        self.test_single_label.setMinimumWidth(50)
        test_layout.addWidget(self.test_single_label, 1, 2)
        self.test_single_slider.valueChanged.connect(lambda v: self.update_slider_realtime('test_single_adj', v, self.test_single_label))
        
        # Test Doubles (2s)
        test_double_lbl = QLabel("Doubles / 2s (+ = more doubles):")
        test_double_lbl.setStyleSheet("font-size: 12px;")
        test_layout.addWidget(test_double_lbl, 2, 0)
        self.test_double_slider = self.create_adjustment_slider('test_double_adj')
        test_layout.addWidget(self.test_double_slider, 2, 1)
        self.test_double_label = QLabel(f"{self.settings['test_double_adj']}%")
        self.test_double_label.setMinimumWidth(50)
        test_layout.addWidget(self.test_double_label, 2, 2)
        self.test_double_slider.valueChanged.connect(lambda v: self.update_slider_realtime('test_double_adj', v, self.test_double_label))
        
        # Test Triples (3s)
        test_triple_lbl = QLabel("Triples / 3s (+ = more triples):")
        test_triple_lbl.setStyleSheet("font-size: 12px;")
        test_layout.addWidget(test_triple_lbl, 3, 0)
        self.test_triple_slider = self.create_adjustment_slider('test_triple_adj')
        test_layout.addWidget(self.test_triple_slider, 3, 1)
        self.test_triple_label = QLabel(f"{self.settings['test_triple_adj']}%")
        self.test_triple_label.setMinimumWidth(50)
        test_layout.addWidget(self.test_triple_label, 3, 2)
        self.test_triple_slider.valueChanged.connect(lambda v: self.update_slider_realtime('test_triple_adj', v, self.test_triple_label))
        
        # Test Boundary
        test_bnd_lbl = QLabel("Boundaries / 4s & 6s (+ = more boundaries):")
        test_bnd_lbl.setStyleSheet("font-size: 12px;")
        test_layout.addWidget(test_bnd_lbl, 4, 0)
        self.test_boundary_slider = self.create_adjustment_slider('test_boundary_adj')
        test_layout.addWidget(self.test_boundary_slider, 4, 1)
        self.test_boundary_label = QLabel(f"{self.settings['test_boundary_adj']}%")
        self.test_boundary_label.setMinimumWidth(50)
        test_layout.addWidget(self.test_boundary_label, 4, 2)
        self.test_boundary_slider.valueChanged.connect(lambda v: self.update_slider_realtime('test_boundary_adj', v, self.test_boundary_label))
        
        # Test Wicket
        test_wkt_lbl = QLabel("Wickets (+ = more wickets):")
        test_wkt_lbl.setStyleSheet("font-size: 12px;")
        test_layout.addWidget(test_wkt_lbl, 5, 0)
        self.test_wicket_slider = self.create_adjustment_slider('test_wicket_adj')
        test_layout.addWidget(self.test_wicket_slider, 5, 1)
        self.test_wicket_label = QLabel(f"{self.settings['test_wicket_adj']}%")
        self.test_wicket_label.setMinimumWidth(50)
        test_layout.addWidget(self.test_wicket_label, 5, 2)
        self.test_wicket_slider.valueChanged.connect(lambda v: self.update_slider_realtime('test_wicket_adj', v, self.test_wicket_label))
        
        test_group.setLayout(test_layout)
        layout.addWidget(test_group)
        
        container.setLayout(layout)
        return container
    
    def update_slider_realtime(self, setting_key, value, label):
        """Update slider value in real-time and sync to game engine"""
        # Update label
        label.setText(f"{value}%")
        
        # Update local settings
        self.settings[setting_key] = value
        
        # Update game engine immediately (real-time)
        if self.game_engine:
            if not hasattr(self.game_engine, 'simulation_settings'):
                self.game_engine.simulation_settings = {}
            self.game_engine.simulation_settings[setting_key] = value
    
    def create_adjustment_slider(self, setting_key):
        """Create a slider for probability adjustment (-100 to +100)"""
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(-100, 100)
        slider.setValue(self.settings.get(setting_key, 0))
        slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        slider.setTickInterval(25)
        slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid {COLORS['border']};
                height: 8px;
                background: #f0f0f0;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {COLORS['primary']};
                border: none;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }}
            QSlider::sub-page:horizontal {{
                background: {COLORS['primary_light']};
                border-radius: 4px;
            }}
        """)
        return slider
    
    def create_action_buttons(self):
        """Create action buttons"""
        container = QFrame()
        container.setStyleSheet(f"""
            background-color: #111827;
            border-radius: 8px;
            border: 1px solid {COLORS['border']};
            padding: 20px;
        """)
        
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        # Info text
        info = QLabel("Changes will be applied immediately")
        info.setStyleSheet("""
            font-size: 12px;
            color: #666;
        """)
        layout.addWidget(info)
        
        layout.addStretch()
        
        # Reset to defaults button
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['warning']};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent_light']};
            }}
        """)
        reset_btn.clicked.connect(self.reset_to_defaults)
        layout.addWidget(reset_btn)
        
        # Save button
        save_btn = QPushButton("💾 Save Settings")
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_light']};
            }}
        """)
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        
        container.setLayout(layout)
        return container
    
    def save_settings(self):
        """Save current settings"""
        # Update settings dictionary
        self.settings['player_name'] = self.manager_name.text()
        
        # Get selected managed team (strip leading spaces and skip category headers)
        selected_team_name = self.managed_team_combo.currentText().strip()
        # Skip if it's a category header
        if selected_team_name.startswith("──"):
            QMessageBox.warning(self, "Invalid Selection", "Please select a team, not a category header.")
            return
        self.settings['favorite_team'] = selected_team_name
        
        self.settings['difficulty'] = self.difficulty_combo.currentText()
        
        # Simulation tuning - T20
        self.settings['t20_dot_adj'] = self.t20_dot_slider.value()
        self.settings['t20_single_adj'] = self.t20_single_slider.value()
        self.settings['t20_double_adj'] = self.t20_double_slider.value()
        self.settings['t20_triple_adj'] = self.t20_triple_slider.value()
        self.settings['t20_boundary_adj'] = self.t20_boundary_slider.value()
        self.settings['t20_wicket_adj'] = self.t20_wicket_slider.value()
        # Simulation tuning - ODI
        self.settings['odi_dot_adj'] = self.odi_dot_slider.value()
        self.settings['odi_single_adj'] = self.odi_single_slider.value()
        self.settings['odi_double_adj'] = self.odi_double_slider.value()
        self.settings['odi_triple_adj'] = self.odi_triple_slider.value()
        self.settings['odi_boundary_adj'] = self.odi_boundary_slider.value()
        self.settings['odi_wicket_adj'] = self.odi_wicket_slider.value()
        # Simulation tuning - Test
        self.settings['test_dot_adj'] = self.test_dot_slider.value()
        self.settings['test_single_adj'] = self.test_single_slider.value()
        self.settings['test_double_adj'] = self.test_double_slider.value()
        self.settings['test_triple_adj'] = self.test_triple_slider.value()
        self.settings['test_boundary_adj'] = self.test_boundary_slider.value()
        self.settings['test_wicket_adj'] = self.test_wicket_slider.value()
        
        # Update game engine
        team_changed = False
        if self.game_engine:
            # Update managed team
            new_team = self.game_engine.get_team_by_name(selected_team_name)
            if new_team and new_team != self.game_engine.user_team:
                old_team = self.game_engine.user_team.name if self.game_engine.user_team else "None"
                self.game_engine.user_team = new_team
                team_changed = True
                print(f"[Settings] Changed managed team from {old_team} to {new_team.name}")
            
            # Sync simulation settings
            self.game_engine.simulation_settings = {
                't20_dot_adj': self.settings['t20_dot_adj'],
                't20_single_adj': self.settings['t20_single_adj'],
                't20_double_adj': self.settings['t20_double_adj'],
                't20_triple_adj': self.settings['t20_triple_adj'],
                't20_boundary_adj': self.settings['t20_boundary_adj'],
                't20_wicket_adj': self.settings['t20_wicket_adj'],
                'odi_dot_adj': self.settings['odi_dot_adj'],
                'odi_single_adj': self.settings['odi_single_adj'],
                'odi_double_adj': self.settings['odi_double_adj'],
                'odi_triple_adj': self.settings['odi_triple_adj'],
                'odi_boundary_adj': self.settings['odi_boundary_adj'],
                'odi_wicket_adj': self.settings['odi_wicket_adj'],
                'test_dot_adj': self.settings['test_dot_adj'],
                'test_single_adj': self.settings['test_single_adj'],
                'test_double_adj': self.settings['test_double_adj'],
                'test_triple_adj': self.settings['test_triple_adj'],
                'test_boundary_adj': self.settings['test_boundary_adj'],
                'test_wicket_adj': self.settings['test_wicket_adj'],
            }
            # Sync difficulty to game engine (Medium -> Normal for engine)
            diff = self.difficulty_combo.currentText()
            self.game_engine.difficulty = 'Normal' if diff == 'Medium' else diff
            print(f"[Settings] Synced simulation settings to game engine")
        
        # Notify main window to update UI if team changed
        if team_changed and self.screen_manager:
            # Try to update main window's top bar
            main_window = self.screen_manager.parent() if self.screen_manager else None
            if main_window and hasattr(main_window, 'update_top_bar'):
                main_window.update_top_bar()
                print("[Settings] Updated main window top bar")
            
            # Refresh training screen if it exists
            if hasattr(self.screen_manager, 'screens') and 'Training' in self.screen_manager.screens:
                training_screen = self.screen_manager.screens['Training']
                if hasattr(training_screen, 'refresh_data'):
                    training_screen.refresh_data()
                    print("[Settings] Refreshed training screen")
        
        # Show confirmation
        msg = "Your settings have been saved successfully!"
        if team_changed:
            msg += f"\n\nManaged team changed to: {selected_team_name}"
        
        QMessageBox.information(
            self,
            "Settings Saved",
            msg,
            QMessageBox.StandardButton.Ok
        )
        
        print(f"[Settings] Saved: {self.settings}")
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.settings = self.load_default_settings()
            self.update_ui_from_settings()
            QMessageBox.information(
                self,
                "Settings Reset",
                "All settings have been reset to defaults.",
                QMessageBox.StandardButton.Ok
            )
            print("[Settings] Reset to defaults")
    
    def update_ui_from_settings(self):
        """Update UI controls from settings (only updates widgets that exist)."""
        if hasattr(self, 'manager_name'):
            self.manager_name.setText(self.settings['player_name'])
        if hasattr(self, 'managed_team_combo'):
            self.managed_team_combo.setCurrentText(self.settings['favorite_team'])
        if hasattr(self, 'difficulty_combo'):
            self.difficulty_combo.setCurrentText(self.settings.get('difficulty', 'Medium'))
        
        # Simulation tuning - T20
        self.t20_dot_slider.setValue(self.settings['t20_dot_adj'])
        self.t20_single_slider.setValue(self.settings['t20_single_adj'])
        self.t20_double_slider.setValue(self.settings['t20_double_adj'])
        self.t20_triple_slider.setValue(self.settings['t20_triple_adj'])
        self.t20_boundary_slider.setValue(self.settings['t20_boundary_adj'])
        self.t20_wicket_slider.setValue(self.settings['t20_wicket_adj'])
        self.t20_dot_label.setText(f"{self.settings['t20_dot_adj']}%")
        self.t20_single_label.setText(f"{self.settings['t20_single_adj']}%")
        self.t20_double_label.setText(f"{self.settings['t20_double_adj']}%")
        self.t20_triple_label.setText(f"{self.settings['t20_triple_adj']}%")
        self.t20_boundary_label.setText(f"{self.settings['t20_boundary_adj']}%")
        self.t20_wicket_label.setText(f"{self.settings['t20_wicket_adj']}%")
        # Simulation tuning - ODI
        self.odi_dot_slider.setValue(self.settings['odi_dot_adj'])
        self.odi_single_slider.setValue(self.settings['odi_single_adj'])
        self.odi_double_slider.setValue(self.settings['odi_double_adj'])
        self.odi_triple_slider.setValue(self.settings['odi_triple_adj'])
        self.odi_boundary_slider.setValue(self.settings['odi_boundary_adj'])
        self.odi_wicket_slider.setValue(self.settings['odi_wicket_adj'])
        self.odi_dot_label.setText(f"{self.settings['odi_dot_adj']}%")
        self.odi_single_label.setText(f"{self.settings['odi_single_adj']}%")
        self.odi_double_label.setText(f"{self.settings['odi_double_adj']}%")
        self.odi_triple_label.setText(f"{self.settings['odi_triple_adj']}%")
        self.odi_boundary_label.setText(f"{self.settings['odi_boundary_adj']}%")
        self.odi_wicket_label.setText(f"{self.settings['odi_wicket_adj']}%")
        # Simulation tuning - Test
        self.test_dot_slider.setValue(self.settings['test_dot_adj'])
        self.test_single_slider.setValue(self.settings['test_single_adj'])
        self.test_double_slider.setValue(self.settings['test_double_adj'])
        self.test_triple_slider.setValue(self.settings['test_triple_adj'])
        self.test_boundary_slider.setValue(self.settings['test_boundary_adj'])
        self.test_wicket_slider.setValue(self.settings['test_wicket_adj'])
        self.test_dot_label.setText(f"{self.settings['test_dot_adj']}%")
        self.test_single_label.setText(f"{self.settings['test_single_adj']}%")
        self.test_double_label.setText(f"{self.settings['test_double_adj']}%")
        self.test_triple_label.setText(f"{self.settings['test_triple_adj']}%")
        self.test_boundary_label.setText(f"{self.settings['test_boundary_adj']}%")
        self.test_wicket_label.setText(f"{self.settings['test_wicket_adj']}%")
    
    def refresh_data(self):
        """Refresh settings when tab is clicked (reload from game engine after load)"""
        self.load_settings_from_engine()
        self.update_ui_from_settings()
        print("[Settings] Settings refreshed from game engine")
