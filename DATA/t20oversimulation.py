import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import random
import os
import copy
from datetime import datetime
from player_traits import get_trait_effect, get_negative_trait_effect, POSITIVE_TRAITS, NEGATIVE_TRAITS
from cricket_manager.core.statistics_manager import StatisticsManager
from cricket_manager.systems.bowling_movements import get_movement_display_name, determine_bowler_type

# Game theme colors - Professional Cricket Manager Theme (Dark Green)
BG_COLOR = "#1B4332"  # Dark green
FG_COLOR = "#D8F3DC"  # Light green-gray
ACCENT_COLOR = "#52B788"  # Medium green
BUTTON_COLOR = "#2D6A4F"  # Darker green
SUCCESS_COLOR = "#74C69D"  # Light green

class T20Match:
    def _player_to_dict(self, p):
        """Convert Player object to dict while keeping bowling_movements if present"""
        if isinstance(p, dict):
            return p
        return {
            'name': getattr(p, 'name', 'Unknown'),
            'role': getattr(p, 'role', ''),
            'batting': getattr(p, 'batting', 0),
            'bowling': getattr(p, 'bowling', 0),
            'age': getattr(p, 'age', 0),
            'bowling_movements': getattr(p, 'bowling_movements', {})
        }

    def _get_team_name(self, team):
        return team.name if hasattr(team, 'name') else team.get('name', 'Unknown Team') if isinstance(team, dict) else 'Unknown Team'

    def _format_overs(self, overs, balls):
        return f"{overs}.{balls}" if balls < 6 else f"{overs + balls // 6}.{balls % 6}"

    def _record_innings(self, batting_team_name, bowling_team_name, runs, wickets, overs, balls):
        """Store innings snapshot for summary/export"""
        batting_stats = {}
        bowling_stats = {}
        for player, stats in self.match_stats.items():
            if player in [p['name'] for p in self.playing_xis.get(batting_team_name, [])]:
                batting_stats[player] = stats['batting']
            if player in [p['name'] for p in self.playing_xis.get(bowling_team_name, [])]:
                bowling_stats[player] = stats['bowling']
        self.innings_history.append({
            'batting_team': batting_team_name,
            'bowling_team': bowling_team_name,
            'score': runs,
            'wickets': wickets,
            'overs': float(f"{overs}.{balls % 6}"),
            'balls': balls,
            'batting_stats': batting_stats,
            'bowling_stats': bowling_stats
        })

    def export_scorecards_to_csv(self):
        """Export batting and bowling scorecards for both innings to CSV"""
        if not self.innings_history:
            messagebox.showwarning("No Data", "No innings data to export yet.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save Scorecards As"
        )
        if not file_path:
            return
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Match Scorecards"])
                writer.writerow(["Teams", f"{self.team1_name} vs {self.team2_name}"])
                writer.writerow(["Format", self.match_format])
                writer.writerow(["Date", datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
                writer.writerow([])

                for idx, inn in enumerate(self.innings_history, start=1):
                    writer.writerow([f"Innings {idx}", f"{inn['batting_team']} vs {inn['bowling_team']}"])
                    writer.writerow(["Score", f"{inn['score']}/{inn['wickets']} in {inn['overs']:.1f} overs"])
                    writer.writerow([])
                    writer.writerow(["Batting"])
                    writer.writerow(["Batter", "R", "B", "4s", "6s", "Dismissal"])
                    for name, stats in inn['batting_stats'].items():
                        writer.writerow([
                            name,
                            stats.get('runs', 0),
                            stats.get('balls', 0),
                            stats.get('fours', 0),
                            stats.get('sixes', 0),
                            stats.get('dismissal', 'not out') or 'not out'
                        ])
                    writer.writerow([])
                    writer.writerow(["Bowling"])
                    writer.writerow(["Bowler", "O", "M", "R", "W"])
                    for name, stats in inn['bowling_stats'].items():
                        overs = stats.get('balls', 0) // 6
                        balls = stats.get('balls', 0) % 6
                        writer.writerow([
                            name,
                            f"{overs}.{balls}",
                            stats.get('maidens', 0),
                            stats.get('runs', 0),
                            stats.get('wickets', 0)
                        ])
                    writer.writerow([])

            messagebox.showinfo("Export Successful", f"Scorecards exported to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))
    def quick_simulate_match(self):
        """
        Simulate the entire match (both innings) as quickly as possible in the background.
        No GUI updates or delays, only shows summary at the end.
        """
        # Simulate first innings
        self.current_innings = 1
        self.total_overs = 0
        self.total_balls = 0
        self.total_runs = 0
        self.total_wickets = 0
        self.match_ended = False
        self.striker = self.batting_xi[0]
        self.non_striker = self.batting_xi[1]
        self.current_bowler = self.opening_bowlers[0]
        while not self.match_ended:
            self.simulate_ball()
            if self.total_balls == 6 or self.total_wickets >= 10 or (self.max_overs and self.total_overs >= self.max_overs):
                self.total_balls = 0
                self.total_overs += 1
                self.change_bowler()
            if self.total_wickets >= 10 or (self.max_overs and self.total_overs >= self.max_overs):
                self.end_innings()
                break
        # Simulate second innings if match not ended
        if not self.match_ended and self.current_innings == 2:
            self.total_overs = 0
            self.total_balls = 0
            self.total_runs = 0
            self.total_wickets = 0
            self.striker = self.batting_xi[0]
            self.non_striker = self.batting_xi[1]
            self.current_bowler = self.opening_bowlers[0]
            while not self.match_ended:
                self.simulate_ball()
                if self.total_balls == 6 or self.total_wickets >= 10 or (self.max_overs and self.total_overs >= self.max_overs):
                    self.total_balls = 0
                    self.total_overs += 1
                    self.change_bowler()
                if self.total_wickets >= 10 or (self.max_overs and self.total_overs >= self.max_overs) or (self.target and self.total_runs >= self.target):
                    self.end_match()
                    break
        # At the end, show only the match summary
        self.show_match_summary()

    def on_pitch_slider_change(self, event=None):
        self.pitch_pace_rating = int(self.pace_pitch_slider.get())
        self.pitch_spin_rating = int(self.spin_pitch_slider.get())
        self.pitch_bounce_rating = int(self.bounce_pitch_slider.get())
        self.pitch_description.config(text=self.get_pitch_description())
    
        
    def __init__(self, master, team1, team2, match_format='ODI', headless=False, simulation_adjustments=None, pitch_conditions=None):
        """Initialize the T20 match, optionally in headless (no-GUI) mode"""
        self.master = master
        
        # Store teams directly
        self.team1 = team1
        self.team2 = team2
        self.team1_name = self._get_team_name(self.team1)
        self.team2_name = self._get_team_name(self.team2)
        self.match_format = match_format
        self._fixture_pitch_conditions = pitch_conditions  # From fixture (host country)
        self.max_overs = 50 if match_format == 'ODI' else 20 if match_format == 'T20' else 90
        self.headless = headless
        
        # User simulation adjustments from settings (-100 to +100)
        self.simulation_adjustments = simulation_adjustments or {
            'dot_adj': 0,
            'boundary_adj': 0,
            'wicket_adj': 0
        }
        self.first_innings_score = 0
        self.first_innings_wickets = 0
        self.first_innings_overs = 0
        self.first_innings_balls = 0
        self.second_innings_overs = 0
        self.second_innings_balls = 0
        
        # Configure ttk style with game theme colors (only when GUI is created)
        if not headless:
            # Configure styles after window is created
            def configure_styles():
                style = ttk.Style()
                style.theme_use('clam')
                
                # Configure styles using global colors
                style.configure('TLabel', 
                                font=('Arial', 10), 
                                foreground=FG_COLOR, 
                                background=BG_COLOR)
                style.configure('TButton', 
                                font=('Arial', 10, 'bold'), 
                                foreground='white', 
                                background=BUTTON_COLOR,
                                borderwidth=1,
                                relief='raised')
                style.map('TButton', 
                          background=[('active', '#1B5E3F'), ('pressed', '#0F3420')])
                style.configure('TLabelframe.Label', 
                                font=('Arial', 10, 'bold'), 
                                foreground=FG_COLOR, 
                                background=BG_COLOR)
                style.configure('TLabelframe', 
                                foreground=FG_COLOR, 
                                background=BG_COLOR,
                                borderwidth=2,
                                relief='solid')
                style.configure('TEntry', 
                                foreground=FG_COLOR, 
                                background=BUTTON_COLOR,
                                fieldbackground=BUTTON_COLOR)
                style.configure('TCombobox', 
                                foreground=FG_COLOR, 
                                background=BUTTON_COLOR,
                                fieldbackground=BUTTON_COLOR)
                style.configure('Treeview', 
                                font=('Arial', 9), 
                                foreground=FG_COLOR, 
                                background=BUTTON_COLOR,
                                fieldbackground=BUTTON_COLOR)
                style.configure('Treeview.Heading', 
                                font=('Arial', 10, 'bold'), 
                                foreground=FG_COLOR, 
                                background=BG_COLOR)
                
                # Also configure basic tk widgets
                if hasattr(self, 'match_window') and self.match_window:
                    self.match_window.option_add('*TLabel*background', BG_COLOR)
                    self.match_window.option_add('*TLabel*foreground', FG_COLOR)
                    self.match_window.option_add('*TButton*background', BUTTON_COLOR)
                    self.match_window.option_add('*TButton*foreground', 'white')
                    self.match_window.option_add('*Frame*background', BG_COLOR)
            
            # Store configuration function for later use
            self._configure_styles = configure_styles
        
        # Only build GUI if not headless
        if not self.headless:
            # (GUI initialization code goes here, leave as-is)
            pass
        
        # Bowling management
        self.bowlers_used = set()
        self.bowler_data = {}
        self.last_bowler = None
        self.current_bowler = None
        
        # Pitch conditions - use fixture-provided values if available, else random
        if self._fixture_pitch_conditions:
            self.pitch_pace_rating = self._fixture_pitch_conditions.get('pitch_pace', random.randint(3, 9))
            self.pitch_spin_rating = self._fixture_pitch_conditions.get('pitch_spin', random.randint(3, 9))
            self.pitch_bounce_rating = self._fixture_pitch_conditions.get('pitch_bounce', random.randint(3, 9))
        else:
            self.pitch_pace_rating = random.randint(3, 9)
            self.pitch_spin_rating = random.randint(3, 9)
            self.pitch_bounce_rating = random.randint(3, 9)
        self.pitch_overall_rating = (self.pitch_pace_rating + self.pitch_spin_rating + self.pitch_bounce_rating) // 3
        
        # Match format setup
        if match_format == 'ODI':
            self.max_overs = 50
            self.innings = 1
        elif match_format == 'Test':
            self.max_overs = None
            self.innings = 2
        else:
            self.max_overs = 20
            self.innings = 1
            
        print(f"Match format: {match_format}, Max overs: {self.max_overs}")
        
        self.batting_team = self.team1
        self.bowling_team = self.team2
        
        # Select playing XI and initialize bowling squad
        self.select_playing_xi()
        
        self.current_innings = 1
        self.total_runs = 0
        self.total_wickets = 0
        self.total_overs = 0
        self.total_balls = 0
        self.first_innings_wickets = 0
        self.first_innings_score = 0
        self.target = None
        self.result = None
        self.match_ended = False
        
        # Initialize match stats for ALL players in both teams (ensures all potential bowlers are tracked)
        self.match_stats = {}
        team1_players = self.team1.players if hasattr(self.team1, 'players') else self.team1['players']
        team2_players = self.team2.players if hasattr(self.team2, 'players') else self.team2['players']
        for player in team1_players + team2_players:
            player_name = player.name if hasattr(player, 'name') else player['name']
            self.match_stats[player_name] = {
                'batting': {'runs': 0, 'balls': 0, 'fours': 0, 'sixes': 0, 'dismissal': None},
                'bowling': {'balls': 0, 'runs': 0, 'wickets': 0, 'maidens': 0, 'speeds': []}
            }
            
        # Convert XI players to dictionaries if they are Player objects
        self.batting_xi = [self._player_to_dict(p) for p in self.batting_xi]
        self.bowling_xi = [self._player_to_dict(p) for p in self.bowling_xi]
        self.playing_xis = {
            self.team1_name: copy.deepcopy(self.batting_xi),
            self.team2_name: copy.deepcopy(self.bowling_xi)
        }
        self.innings_history = []
        
        self.striker = self.batting_xi[0]
        self.non_striker = self.batting_xi[1]
        
        # Create match window first
        self.create_match_window()
        
        # Now select opening bowlers after window is created
        self.select_opening_bowlers()
        self.current_bowler = self.opening_bowlers[0]
        
        # Initialize the score display and add match introduction commentary
        self.update_score_display()
        team1_name = self.team1.name if hasattr(self.team1, 'name') else self.team1['name']
        team2_name = self.team2.name if hasattr(self.team2, 'name') else self.team2['name']
        bowler_name = self.current_bowler.name if hasattr(self.current_bowler, 'name') else self.current_bowler['name']
        self.add_commentary(f"Match between {team1_name} and {team2_name} begins!")
        self.add_commentary(f"{team1_name} will bat first against {team2_name}")
        self.add_commentary(f"Opening bowler: {bowler_name}")
    
    def create_match_window(self):
        """Create and setup the match window"""
        if self.master is None:
            # No master window - create main window
            self.match_window = tk.Tk()
        else:
            # Has master window - create toplevel
            self.match_window = tk.Toplevel()
        
        self.match_window.title(f"{self.match_format} Match")
        
        # Make full screen
        screen_width = self.match_window.winfo_screenwidth()
        screen_height = self.match_window.winfo_screenheight()
        self.match_window.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # Make modal but don't use topmost to avoid blank window issue
        self.match_window.grab_set()
        self.match_window.focus_set()
        self.match_window.lift()
        
        self.match_window.configure(bg=BG_COLOR)
        
        # Apply styles after window is created
        if hasattr(self, '_configure_styles'):
            self._configure_styles()
        
        # Main frames
        left_frame = ttk.Frame(self.match_window)
        left_frame.grid(row=0, column=0, sticky='nsew')
        right_frame = ttk.Frame(self.match_window)
        right_frame.grid(row=0, column=1, sticky='nsew')
        
        self.match_window.grid_columnconfigure(0, weight=1)
        self.match_window.grid_columnconfigure(1, weight=1)
        self.match_window.grid_rowconfigure(0, weight=1)
        
        # Control panel
        control_panel = ttk.LabelFrame(left_frame, text="Match Controls")
        control_panel.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        
        ttk.Label(control_panel, text="Batting Aggression:").grid(row=0, column=0, padx=5)
        self.batting_slider = ttk.Scale(control_panel, from_=0, to=100, orient='horizontal', value=50)
        self.batting_slider.grid(row=0, column=1, padx=5)
        
        pitch_frame = ttk.LabelFrame(control_panel, text="Pitch Conditions")
        pitch_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        
        ttk.Label(pitch_frame, text="Pace Bowler Assistance:").grid(row=0, column=0, padx=5)
        self.pace_pitch_slider = ttk.Scale(pitch_frame, from_=1, to=10, orient='horizontal', value=self.pitch_pace_rating)
        self.pace_pitch_slider.grid(row=0, column=1, padx=5)
        self.pace_pitch_slider.config(command=lambda v: self.on_pitch_slider_change())
        # self.pace_pitch_slider.state(['disabled'])
        
        ttk.Label(pitch_frame, text="Spin Bowler Assistance:").grid(row=1, column=0, padx=5)
        self.spin_pitch_slider = ttk.Scale(pitch_frame, from_=1, to=10, orient='horizontal', value=self.pitch_spin_rating)
        self.spin_pitch_slider.grid(row=1, column=1, padx=5)
        self.spin_pitch_slider.config(command=lambda v: self.on_pitch_slider_change())
        # self.spin_pitch_slider.state(['disabled'])

        # New Bounce slider
        ttk.Label(pitch_frame, text="Pitch Bounce:").grid(row=0, column=2, padx=5)
        self.bounce_pitch_slider = ttk.Scale(pitch_frame, from_=1, to=10, orient='horizontal', value=self.pitch_bounce_rating)
        self.bounce_pitch_slider.grid(row=0, column=3, padx=5)
        self.bounce_pitch_slider.config(command=lambda v: self.on_pitch_slider_change())
        
        self.pitch_description = ttk.Label(pitch_frame, text=self.get_pitch_description(), font=('Arial', 10))
        self.pitch_description.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        
        start_button = ttk.Button(control_panel, text=f"Start {self.match_format} Match", command=self.setup_match)
        start_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        
        # Bowling controls
        bowling_frame = ttk.LabelFrame(control_panel, text="Bowling Controls")
        bowling_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        
        ttk.Label(bowling_frame, text="Bowling Aggression:").grid(row=0, column=0, padx=5)
        self.bowling_slider = ttk.Scale(bowling_frame, from_=0, to=100, orient='horizontal', value=50)
        self.bowling_slider.grid(row=0, column=1, padx=5)
        
        ttk.Label(bowling_frame, text="Bowling Line:").grid(row=1, column=0, padx=5)
        self.bowling_line_var = tk.StringVar(value='Good Length')
        ttk.Combobox(bowling_frame, textvariable=self.bowling_line_var, values=['Short', 'Good Length', 'Full']).grid(row=1, column=1, padx=5)
        
        ttk.Label(bowling_frame, text="Field Setting:").grid(row=2, column=0, padx=5)
        self.field_setting_var = tk.StringVar(value='Balanced')
        ttk.Combobox(bowling_frame, textvariable=self.field_setting_var, values=['Aggressive', 'Balanced', 'Defensive']).grid(row=2, column=1, padx=5)
        
        # Score display
        score_frame = ttk.LabelFrame(left_frame, text="Match Status")
        score_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        
        self.score_label = ttk.Label(score_frame, text="0/0 (0.0)", font=('Arial', 16, 'bold'))
        self.score_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        
        self.target_label = ttk.Label(score_frame, text="", font=('Arial', 12))
        self.target_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        
        # Batsmen frame
        batsmen_frame = ttk.LabelFrame(left_frame, text="Current Batsmen")
        batsmen_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        
        self.striker_label = ttk.Label(batsmen_frame, text="", font=('Arial', 12))
        self.striker_label.grid(row=0, column=0, padx=5, pady=5)
        
        self.non_striker_label = ttk.Label(batsmen_frame, text="", font=('Arial', 12))
        self.non_striker_label.grid(row=1, column=0, padx=5, pady=5)
        
        # Bowler frame
        bowler_frame = ttk.LabelFrame(left_frame, text="Current Bowler")
        bowler_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        
        self.bowler_label = ttk.Label(bowler_frame, text="", font=('Arial', 12))
        self.bowler_label.grid(row=0, column=0, padx=5, pady=5)
        
        # Control buttons
        control_frame = ttk.LabelFrame(left_frame, text="Controls")
        control_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        
        ttk.Button(control_frame, text="Bowl", command=self.bowl_delivery).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(control_frame, text="Bowl Over", command=self.bowl_over).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(control_frame, text="Change Bowler", command=self.change_bowler).grid(row=0, column=2, padx=5, pady=5)
        
        # Commentary box
        commentary_frame = ttk.LabelFrame(left_frame, text="Commentary")
        commentary_frame.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        
        self.commentary_text = tk.Text(commentary_frame, height=20, wrap=tk.WORD)
        self.commentary_text.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        
        commentary_scroll = ttk.Scrollbar(commentary_frame, orient='vertical', command=self.commentary_text.yview)
        commentary_scroll.grid(row=0, column=1, sticky='ns')
        self.commentary_text.configure(yscrollcommand=commentary_scroll.set)
        
        # Export button
        export_button = ttk.Button(commentary_frame, text="Export Commentary to CSV", command=self.export_commentary)
        export_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        export_scores_button = ttk.Button(commentary_frame, text="Export Scorecards to CSV", command=self.export_scorecards_to_csv)
        export_scores_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        
        # Batting scorecard
        batting_team_name = self.batting_team.name if hasattr(self.batting_team, 'name') else self.batting_team['name']
        batting_frame = ttk.LabelFrame(right_frame, text=f"{batting_team_name} Batting Scorecard")
        self.batting_frame = batting_frame
        batting_frame.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        
        self.batting_tree = ttk.Treeview(
            batting_frame,
            columns=('Name', 'Runs', 'Balls', '4s', '6s', 'SR', 'Status'),
            show='headings',
            height=11
        )
        self.batting_tree.heading('Name', text='Batsman')
        self.batting_tree.heading('Runs', text='R')
        self.batting_tree.heading('Balls', text='B')
        self.batting_tree.heading('4s', text='4s')
        self.batting_tree.heading('6s', text='6s')
        self.batting_tree.heading('SR', text='SR')
        self.batting_tree.heading('Status', text='Status')
        
        self.batting_tree.column('Name', width=150)
        self.batting_tree.column('Runs', width=50, anchor='center')
        self.batting_tree.column('Balls', width=50, anchor='center')
        self.batting_tree.column('4s', width=50, anchor='center')
        self.batting_tree.column('6s', width=50, anchor='center')
        self.batting_tree.column('SR', width=50, anchor='center')
        self.batting_tree.column('Status', width=100, anchor='center')
        self.batting_tree.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        
        batting_frame.grid_columnconfigure(0, weight=1)
        batting_frame.grid_rowconfigure(0, weight=1)
        
        # Bowling scorecard
        bowling_team_name = self.bowling_team.name if hasattr(self.bowling_team, 'name') else self.bowling_team['name']
        bowling_frame = ttk.LabelFrame(right_frame, text=f"{bowling_team_name} Bowling Scorecard")
        self.bowling_frame = bowling_frame
        bowling_frame.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        
        self.bowling_tree = ttk.Treeview(
            bowling_frame,
            columns=('Name', 'Overs', 'Maidens', 'Runs', 'Wickets', 'Econ', 'TopSpeed', 'AvgSpeed'),
            show='headings',
            height=8
        )
        self.bowling_tree.heading('Name', text='Bowler')
        self.bowling_tree.heading('Overs', text='O')
        self.bowling_tree.heading('Maidens', text='M')
        self.bowling_tree.heading('Runs', text='R')
        self.bowling_tree.heading('Wickets', text='W')
        self.bowling_tree.heading('Econ', text='Econ')
        self.bowling_tree.heading('TopSpeed', text='Top Speed')
        self.bowling_tree.heading('AvgSpeed', text='Avg Speed')
        
        self.bowling_tree.column('Name', width=120)
        self.bowling_tree.column('Overs', width=50, anchor='center')
        self.bowling_tree.column('Maidens', width=50, anchor='center')
        self.bowling_tree.column('Runs', width=50, anchor='center')
        self.bowling_tree.column('Wickets', width=50, anchor='center')
        self.bowling_tree.column('Econ', width=60, anchor='center')
        self.bowling_tree.column('TopSpeed', width=90, anchor='center')
        self.bowling_tree.column('AvgSpeed', width=90, anchor='center')
        self.bowling_tree.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        
        bowling_frame.grid_columnconfigure(0, weight=1)
        bowling_frame.grid_rowconfigure(0, weight=1)
        
        self.update_bowling_scorecard()
        
    def add_commentary(self, text):
        """Add commentary"""
        self.commentary_text.configure(state='normal')
        self.commentary_text.insert(tk.END, text + "\n")
        self.commentary_text.see(tk.END)
        self.commentary_text.configure(state='disabled')
    
    def export_commentary(self):
        """Export commentary to CSV file"""
        try:
            commentary_content = self.commentary_text.get(1.0, tk.END).strip()
            if not commentary_content:
                messagebox.showwarning("No Commentary", "There is no commentary to export.")
                return

            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")],
                title="Save Commentary As"
            )
            if not file_path:
                return

            team1_name = self.team1_name
            team2_name = self.team2_name

            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Match Commentary Export'])
                writer.writerow(['Teams', f'{team1_name} vs {team2_name}'])
                writer.writerow(['Format', self.match_format])
                writer.writerow([])

                lines = commentary_content.split('\n')
                writer.writerow(['Ball', 'Commentary', 'Details'])
                for line in lines:
                    if not line.strip():
                        continue
                    if line[0].isdigit() and '.' in line.split()[0]:
                        writer.writerow([line.split()[0], line.strip(), self.extract_ball_details(line.strip())])
                    else:
                        writer.writerow(['General', line.strip(), ''])

                # Append scorecards if available
                if getattr(self, 'innings_history', None):
                    writer.writerow([])
                    writer.writerow(['Scorecards'])
                    for idx, inn in enumerate(self.innings_history, start=1):
                        writer.writerow([f'Innings {idx}', f"{inn['batting_team']} vs {inn['bowling_team']}"])
                        writer.writerow(['Score', f"{inn['score']}/{inn['wickets']} in {inn['overs']:.1f} overs"])
                        writer.writerow([])
                        writer.writerow(['Batting'])
                        writer.writerow(['Batter', 'R', 'B', '4s', '6s', 'Dismissal'])
                        for name, stats in inn['batting_stats'].items():
                            writer.writerow([name, stats.get('runs',0), stats.get('balls',0), stats.get('fours',0), stats.get('sixes',0), stats.get('dismissal','not out') or 'not out'])
                        writer.writerow([])
                        writer.writerow(['Bowling'])
                        writer.writerow(['Bowler', 'O', 'M', 'R', 'W'])
                        for name, stats in inn['bowling_stats'].items():
                            overs = stats.get('balls',0)//6
                            balls = stats.get('balls',0)%6
                            writer.writerow([name, f"{overs}.{balls}", stats.get('maidens',0), stats.get('runs',0), stats.get('wickets',0)])
                        writer.writerow([])

            messagebox.showinfo("Export Successful", f"Commentary + scorecards exported to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export commentary:\n{str(e)}")

    def extract_ball_details(self, commentary_line):
        """Extract structured ball details from a commentary line"""
        details = []

        # Extract speed
        if 'kph' in commentary_line:
            import re
            speed_match = re.search(r'(\d+\.?\d*)\s*kph', commentary_line)
            if speed_match:
                details.append(f"Speed: {speed_match.group(1)} kph")

        text_lower = commentary_line.lower()

        # Length keywords
        length_keywords = ['full length', 'good length', 'short of good length', 'short pitch', 'yorker', 'full toss']
        for key in length_keywords:
            if key in text_lower:
                details.append(f"Length: {key}")
                break

        # Line keywords
        line_keywords = ['outside off stump', 'off stump', 'middle stump', 'leg stump', 'outside leg stump']
        for key in line_keywords:
            if key in text_lower:
                details.append(f"Line: {key}")
                break

        # Movement keywords (pace & spin)
        movement_keywords = ['swinging in', 'swinging away', 'seaming in', 'seaming away', 'leg cutter', 'off cutter', 'straight ball',
                             'drift in', 'drift out', 'spinning in', 'spinning away', 'straighter']
        for key in movement_keywords:
            if key in text_lower:
                details.append(f"Movement: {key}")
                break

        # Shot hints
        shot_keywords = ['defends', 'drives', 'pulls', 'cuts', 'sweeps', 'hooks', 'lofts', 'nudges', 'pushes', 'blocks', 'leaves']
        for key in shot_keywords:
            if key in text_lower:
                details.append(f"Shot: {key}")
                break

        return ' | '.join(details) if details else 'No details extracted'

    def select_playing_xi(self):
        """Select the playing XI for both teams and initialize bowling squad"""
        # --- Improved XI selection logic ---
        import random
        def select_xi(team):
            players = team.players if hasattr(team, 'players') else team['players']
            players = players[:]
            random.shuffle(players)
            
            # Categorize players by role - each player goes into exactly one category
            batters = []
            allrounders = []
            bowlers = []
            uncategorized = []
            
            for p in players:
                role = p.role.lower() if hasattr(p, 'role') else p['role'].lower()
                if 'allrounder' in role:
                    allrounders.append(p)
                elif 'batter' in role or 'batsman' in role or 'wicketkeeper' in role or 'keeper' in role:
                    batters.append(p)
                elif any(x in role for x in ['fast', 'medium', 'pacer', 'spinner', 'bowler']):
                    bowlers.append(p)
                else:
                    uncategorized.append(p)
            
            # Fallbacks if not enough in any category - use uncategorized first, then borrow
            if len(batters) < 5:
                needed = 5 - len(batters)
                batters += uncategorized[:needed]
                uncategorized = uncategorized[needed:]
            if len(allrounders) < 2:
                needed = 2 - len(allrounders)
                allrounders += uncategorized[:needed]
                uncategorized = uncategorized[needed:]
            if len(bowlers) < 4:
                needed = 4 - len(bowlers)
                bowlers += uncategorized[:needed]
                uncategorized = uncategorized[needed:]
            
            # Select players: 5 batters, 2 allrounders, 4 bowlers
            selected_batters = random.sample(batters, min(5, len(batters)))
            selected_allrounders = random.sample(allrounders, min(2, len(allrounders)))
            selected_bowlers = random.sample(bowlers, min(4, len(bowlers)))
            
            # Deduplicate by player name
            seen_names = set()
            xi = []
            for p in selected_batters + selected_allrounders + selected_bowlers:
                player_name = p.name if hasattr(p, 'name') else p['name']
                if player_name not in seen_names:
                    seen_names.add(player_name)
                    xi.append(p)
            
            # If less than 11, fill with best remaining players
            if len(xi) < 11:
                remaining = [p for p in players if (p.name if hasattr(p, 'name') else p['name']) not in seen_names]
                for p in sorted(remaining, key=lambda x: (x.batting if hasattr(x, 'batting') else x.get('batting', 0) + x.bowling if hasattr(x, 'bowling') else x.get('bowling', 0)), reverse=True):
                    player_name = p.name if hasattr(p, 'name') else p['name']
                    if player_name not in seen_names:
                        seen_names.add(player_name)
                        xi.append(p)
                    if len(xi) >= 11:
                        break
            xi = xi[:11]
            
            # Rebuild selected lists from the deduplicated xi
            selected_batters = [p for p in xi if p in selected_batters]
            selected_allrounders = [p for p in xi if p in selected_allrounders]
            selected_bowlers = [p for p in xi if p in selected_bowlers]
            
            # Batting order: batters at top, allrounders middle, bowlers at bottom
            batters_top5 = sorted(selected_batters, key=lambda x: x.batting if hasattr(x, 'batting') else x.get('batting', 0), reverse=True)
            allrounders_6_7 = selected_allrounders
            bowlers_8_11 = sorted(selected_bowlers, key=lambda x: x.batting if hasattr(x, 'batting') else x.get('batting', 0), reverse=True)
            
            # Construct the lineup
            lineup_names = set()
            lineup = []
            for p in batters_top5 + allrounders_6_7 + bowlers_8_11:
                player_name = p.name if hasattr(p, 'name') else p['name']
                if player_name not in lineup_names:
                    lineup_names.add(player_name)
                    lineup.append(p)
            
            # If not enough, fill with remaining players from xi
            if len(lineup) < 11:
                for p in xi:
                    player_name = p.name if hasattr(p, 'name') else p['name']
                    if player_name not in lineup_names:
                        lineup_names.add(player_name)
                        lineup.append(p)
                    if len(lineup) >= 11:
                        break
            
            return lineup[:11]
        
        self.batting_xi = select_xi(self.team1)
        self.bowling_xi = select_xi(self.team2)
        # Define top 7 skilled bowlers as the bowling squad
        sorted_bowlers = sorted(self.bowling_xi, key=lambda x: x.bowling if hasattr(x, 'bowling') else x.get('bowling', 0), reverse=True)
        self.bowling_squad = sorted_bowlers[:7]
        # Initialize bowler tracking data with spell_length and can_bowl_after
        self.bowler_data = {}
        for bowler in self.bowling_squad:
            name = bowler.name if hasattr(bowler, 'name') else bowler['name']
            self.bowler_data[name] = {
                'overs_bowled': 0,
                'current_spell': 0,
                'spell_length': None,
                'can_bowl_after': None,
                'spells': 0
            }
        self.bowlers_used = set()
        print("Selected Batting XI:", [player.name if hasattr(player, 'name') else player['name'] for player in self.batting_xi])
        print("Selected Bowling XI:", [player.name if hasattr(player, 'name') else player['name'] for player in self.bowling_xi])

    def change_bowler(self):
        """Select the next bowler with structured rotation and over limits"""
        if self.match_ended:
            return False

        # Update stats for the bowler who just bowled the previous over
        if self.current_bowler:
            name = getattr(self.current_bowler, 'name', self.current_bowler['name'] if isinstance(self.current_bowler, dict) else 'Unknown')
            if name not in self.bowler_data:
                self.bowler_data[name] = {
                    'overs_bowled': 0,
                    'current_spell': 0,
                    'spell_length': None,
                    'can_bowl_after': None,
                    'spells': 0
                }
            
            # Update bowler stats
            self.bowler_data[name]['overs_bowled'] += 1
            self.bowler_data[name]['current_spell'] += 1
            
            # Record the last bowler
            self.last_bowler = self.current_bowler
        
        # Determine max overs per bowler based on format
        if self.match_format == 'T20':
            max_overs_per_bowler = 4
        elif self.match_format == 'ODI':
            max_overs_per_bowler = 10
        else:  # Test
            max_overs_per_bowler = 999
        
        # Helper function to check if bowler can still bowl
        def can_bowl(bowler):
            if bowler is None:
                return False
            bowler_name = getattr(bowler, 'name', bowler['name'] if isinstance(bowler, dict) else 'Unknown')
            overs = self.bowler_data.get(bowler_name, {}).get('overs_bowled', 0)
            return overs < max_overs_per_bowler and bowler != self.last_bowler
        
        # Helper function to get eligible bowlers from a list
        def get_eligible(bowler_list):
            return [b for b in bowler_list if can_bowl(b)]
        
        current_over = self.total_overs + 1
        
        # T20 Format: Phase-based rotation with 4-over limit
        if self.match_format == 'T20':
            # Phase 1: Opening bowlers - overs 1-6 (powerplay)
            if current_over <= 6:
                eligible = get_eligible(self.opening_bowlers)
                if eligible:
                    # Alternate between openers
                    if current_over % 2 == 1:
                        selected_bowler = eligible[0]
                    else:
                        selected_bowler = eligible[-1] if len(eligible) > 1 else eligible[0]
                    self.current_bowler = selected_bowler
                    bowler_name = getattr(selected_bowler, 'name', selected_bowler['name'] if isinstance(selected_bowler, dict) else 'Unknown')
                    if current_over == 2:
                        self.add_commentary(f"Change of ends: {bowler_name} takes over")
                    else:
                        self.add_commentary(f"Opening bowler {bowler_name} continues")
                    return True
                else:
                    # No eligible opening bowlers, use current bowler
                    if self.current_bowler:
                        bowler_name = getattr(self.current_bowler, 'name', self.current_bowler['name'] if isinstance(self.current_bowler, dict) else 'Unknown')
                        self.add_commentary(f"Opening bowler {bowler_name} continues")
                    return True
            
            # Phase 2: First change bowlers - overs 7-12
            elif 6 < current_over <= 12:
                eligible = get_eligible(self.bowling_squad[2:4])
                if eligible:
                    selected_bowler = eligible[0]
                    self.current_bowler = selected_bowler
                    bowler_name = getattr(selected_bowler, 'name', selected_bowler['name'] if isinstance(selected_bowler, dict) else 'Unknown')
                    self.add_commentary(f"First change: {bowler_name} into the attack")
                    return True
            
            # Phase 3: Death bowlers / spinners - overs 13-16
            elif 12 < current_over <= 16:
                eligible = get_eligible(self.bowling_squad[4:6])
                if eligible:
                    selected_bowler = eligible[0]
                    self.current_bowler = selected_bowler
                    bowler_name = getattr(selected_bowler, 'name', selected_bowler['name'] if isinstance(selected_bowler, dict) else 'Unknown')
                    self.add_commentary(f"Second change: {bowler_name} comes on")
                    return True
            
            # Phase 4: Death overs - overs 17-20 (best bowlers return)
            elif 16 < current_over <= 20:
                # Try opening bowlers first (usually best death bowlers)
                eligible = get_eligible(self.opening_bowlers)
                if not eligible:
                    eligible = get_eligible(self.bowling_squad[2:4])
                if not eligible:
                    eligible = get_eligible(self.bowling_squad)
                if eligible:
                    selected_bowler = eligible[0]
                    self.current_bowler = selected_bowler
                    bowler_name = getattr(selected_bowler, 'name', selected_bowler['name'] if isinstance(selected_bowler, dict) else 'Unknown')
                    self.add_commentary(f"Death overs: {bowler_name} returns")
                    return True
        
        # ODI Format: Phase-based rotation with 10-over limit
        else:
            # Phase 1: Opening bowlers (1st & 2nd) - overs 1-10
            if current_over <= 10:
                eligible = get_eligible(self.opening_bowlers)
                if eligible:
                    if current_over % 2 == 1:
                        selected_bowler = eligible[0]
                    else:
                        selected_bowler = eligible[-1] if len(eligible) > 1 else eligible[0]
                    self.current_bowler = selected_bowler
                    if current_over == 2:
                        bowler_name = getattr(selected_bowler, 'name', selected_bowler['name'] if isinstance(selected_bowler, dict) else 'Unknown')
                        self.add_commentary(f"Change of ends: {bowler_name} takes over the bowling")
                    else:
                        bowler_name = getattr(selected_bowler, 'name', selected_bowler['name'] if isinstance(selected_bowler, dict) else 'Unknown')
                        self.add_commentary(f"Opening bowler {bowler_name} continues")
                    return True
            
            # Phase 2: 3rd & 4th bowlers - overs 10-20
            elif 10 < current_over <= 20:
                eligible = get_eligible(self.bowling_squad[2:4])
                if eligible:
                    selected_bowler = eligible[0]
                    self.current_bowler = selected_bowler
                    bowler_name = getattr(selected_bowler, 'name', selected_bowler['name'] if isinstance(selected_bowler, dict) else 'Unknown')
                    self.add_commentary(f"First change: {bowler_name} comes into the attack")
                    return True
            
            # Phase 3: 5th & 6th bowlers - overs 20-30
            elif 20 < current_over <= 30:
                eligible = get_eligible(self.bowling_squad[4:6])
                if eligible:
                    selected_bowler = eligible[0]
                    self.current_bowler = selected_bowler
                    bowler_name = getattr(selected_bowler, 'name', selected_bowler['name'] if isinstance(selected_bowler, dict) else 'Unknown')
                    self.add_commentary(f"Second change: {bowler_name} comes into the attack")
                    return True
            
            # Phase 4: 3rd & 4th bowlers return - overs 30-40
            elif 30 < current_over <= 40:
                eligible = get_eligible(self.bowling_squad[2:4])
                if eligible:
                    selected_bowler = eligible[0]
                    self.current_bowler = selected_bowler
                    bowler_name = getattr(selected_bowler, 'name', selected_bowler['name'] if isinstance(selected_bowler, dict) else 'Unknown')
                    self.add_commentary(f"Third change: {bowler_name} returns for their second spell")
                    return True
            
            # Phase 5: Opening bowlers return - overs 40-50
            elif 40 < current_over <= 50:
                eligible = get_eligible(self.opening_bowlers)
                if eligible:
                    selected_bowler = eligible[0]
                    self.current_bowler = selected_bowler
                    bowler_name = getattr(selected_bowler, 'name', selected_bowler['name'] if isinstance(selected_bowler, dict) else 'Unknown')
                    self.add_commentary(f"Final phase: {bowler_name} returns for their second spell")
                    return True
        
        # Fallback: Find any eligible bowler who hasn't maxed out and isn't the last bowler
        eligible_bowlers = get_eligible(self.bowling_squad)
        if eligible_bowlers:
            # Sort by overs bowled (prefer bowlers with fewer overs)
            eligible_bowlers.sort(key=lambda b: self.bowler_data.get(getattr(b, 'name', b['name'] if isinstance(b, dict) else 'Unknown'), {}).get('overs_bowled', 0))
            selected_bowler = eligible_bowlers[0]
            self.current_bowler = selected_bowler
            bowler_name = getattr(selected_bowler, 'name', selected_bowler['name'] if isinstance(selected_bowler, dict) else 'Unknown')
            self.add_commentary(f"Captain brings in {bowler_name} for this over")
            return True
        
        # Last resort: Allow any bowler who hasn't maxed out (even if they bowled last over)
        any_eligible = [b for b in self.bowling_squad 
                       if self.bowler_data.get(getattr(b, 'name', b['name'] if isinstance(b, dict) else 'Unknown'), {}).get('overs_bowled', 0) < max_overs_per_bowler]
        if any_eligible:
            any_eligible.sort(key=lambda b: self.bowler_data.get(getattr(b, 'name', b['name'] if isinstance(b, dict) else 'Unknown'), {}).get('overs_bowled', 0))
            selected_bowler = any_eligible[0]
            self.current_bowler = selected_bowler
            bowler_name = getattr(selected_bowler, 'name', selected_bowler['name'] if isinstance(selected_bowler, dict) else 'Unknown')
            self.add_commentary(f"No choice but to continue with {bowler_name}")
            return True
            
        self.add_commentary("No eligible bowlers available!")
        return False

    def end_innings(self):
        """End current innings and update bowling squad for second innings"""
        if self.current_innings == 1:
            self.first_innings_score = self.total_runs
            self.first_innings_wickets = self.total_wickets
            self.first_innings_overs = self.total_overs
            self.first_innings_balls = self.total_balls
            batting_team_name = self.team1_name
            bowling_team_name = self.team2_name
            self._record_innings(batting_team_name, bowling_team_name, self.total_runs, self.total_wickets, self.total_overs, self.total_balls)
            self.target = self.total_runs + 1
            
            self.current_innings = 2
            self.total_runs = 0
            self.total_wickets = 0
            self.total_overs = 0
            self.total_balls = 0
            
            # Swap teams
            self.batting_team, self.bowling_team = self.bowling_team, self.batting_team
            self.batting_xi, self.bowling_xi = self.bowling_xi, self.batting_xi
            
            # Update bowling squad based on new bowling_xi
            sorted_bowlers = sorted(self.bowling_xi, key=lambda x: x.get('bowling', 0), reverse=True)
            self.bowling_squad = sorted_bowlers[:7]
            
            # Reset bowler data for the new bowling squad
            self.bowlers_used = set()
            self.bowler_data = {}
            for bowler in self.bowling_squad:
                self.bowler_data[bowler['name']] = {
                    'overs_bowled': 0,
                    'current_spell': 0,
                    'spell_length': None,
                    'can_bowl_after': None,
                    'spells': 0
                }
            
            self.striker = self.batting_xi[0]
            self.non_striker = self.batting_xi[1]
            self.select_opening_bowlers()
            self.current_bowler = self.opening_bowlers[0]
            self.last_bowler = None
            
            team1_name = self.team1_name
            team2_name = self.team2_name
            self.add_commentary(f"\nEnd of {team1_name}'s innings: {self.first_innings_score}/{self.first_innings_wickets}")
            self.add_commentary(f"{team2_name} needs {self.target} runs to win")
            
            self.target_label.config(text=f"Target: {self.target}")
            
            # Update scorecard labels with swapped team names
            batting_team_name = self.batting_team.name if hasattr(self.batting_team, 'name') else self.batting_team['name']
            bowling_team_name = self.bowling_team.name if hasattr(self.bowling_team, 'name') else self.bowling_team['name']
            self.batting_frame.config(text=f"{batting_team_name} Batting Scorecard")
            self.bowling_frame.config(text=f"{bowling_team_name} Bowling Scorecard")
            self.update_score_display()
            self.update_bowler_display()
            self.match_window.after(2000, self.simulate_innings)
        else:
            self.add_commentary("End of innings")
            self.update_score_display()
            if self.current_innings == 2:
                if self.total_runs >= self.target:
                    margin = 10 - self.total_wickets
                    batting_team_name = self.batting_team.name if hasattr(self.batting_team, 'name') else self.batting_team['name']
                    result = f"{batting_team_name} won by {margin} wickets"
                    self.add_commentary(result)
                    self.end_match(result)
                else:
                    margin = self.target - self.total_runs - 1
                    bowling_team_name = self.bowling_team.name if hasattr(self.bowling_team, 'name') else self.bowling_team['name']
                    result = f"{bowling_team_name} won by {margin} runs"
                    self.add_commentary(result)
                    self.end_match(result)
            else:
                self.show_match_summary()

    def select_opening_bowlers(self):
        """Select opening bowlers"""
        if len(self.bowling_squad) < 2:
            # If we don't have enough bowlers, show an error and return
            bowling_team_name = self.bowling_team.name if hasattr(self.bowling_team, 'name') else self.bowling_team['name']
            error_msg = f"Error: {bowling_team_name} only has {len(self.bowling_squad)} bowler(s). Need at least 2 bowlers to play."
            self.add_commentary(error_msg)
            print(error_msg)
            return []
        
        # Sort bowlers by bowling skill and select the best 2
        sorted_bowlers = sorted(self.bowling_squad, key=lambda x: x.bowling if hasattr(x, 'bowling') else x.get('bowling', 0), reverse=True)
        self.opening_bowlers = sorted_bowlers[:2]
        
        # Set the first opening bowler
        self.current_bowler = self.opening_bowlers[0]
        self.last_bowler = self.current_bowler  # Set last_bowler to current to prevent consecutive overs
        
        # Initialize bowler data for both opening bowlers
        for bowler in self.opening_bowlers:
            name = bowler.name if hasattr(bowler, 'name') else bowler['name']
            if name not in self.bowler_data:
                self.bowler_data[name] = {
                    'overs_bowled': 0,
                    'current_spell': 0,
                    'spell_length': random.randint(4, 6),
                    'can_bowl_after': None,
                    'spells': 0
                }
            self.bowler_data[name]['current_spell'] = 0
            self.bowler_data[name]['can_bowl_after'] = None
        
        bowler_name = self.current_bowler.name if hasattr(self.current_bowler, 'name') else self.current_bowler['name']
        self.add_commentary(f"{bowler_name} will open the bowling")
        return self.opening_bowlers

    def end_match(self, result=None):
        """End the match and return result"""
        if result:
            self.result = result
        
        self.match_ended = True
        
        # Calculate match stats
        if self.current_innings == 1:
            self.first_innings_score = self.total_runs
            self.first_innings_wickets = self.total_wickets
            
            # Swap teams for second innings
            temp = self.batting_team
            self.batting_team = self.bowling_team
            self.bowling_team = temp
            
            # Swap XIs
            temp = self.batting_xi
            self.batting_xi = self.bowling_xi
            self.bowling_xi = temp
            
            # Reset match state for second innings
            self.total_runs = 0
            self.total_wickets = 0
            self.total_overs = 0
            self.total_balls = 0
            self.target = self.first_innings_score + 1
            
            # Reset bowlers used
            self.bowlers_used = set()
            
            # Setup second innings
            self.current_innings = 2
            self.select_opening_batsmen()
            self.select_opening_bowlers()
            
            # Add commentary
            bowling_team_name = self.bowling_team.name if hasattr(self.bowling_team, 'name') else self.bowling_team['name']
            batting_team_name = self.batting_team.name if hasattr(self.batting_team, 'name') else self.batting_team['name']
            self.add_commentary(f"End of innings. {bowling_team_name} scored {self.first_innings_score}/{self.first_innings_wickets}")
            self.add_commentary(f"{batting_team_name} needs {self.target} runs to win")
            
            # Continue match
            self.update_score_display()
        else:
            # End of match
            batting_team_name = self.batting_team.name if hasattr(self.batting_team, 'name') else self.batting_team['name']
            bowling_team_name = self.bowling_team.name if hasattr(self.bowling_team, 'name') else self.bowling_team['name']
            if self.target and self.total_runs >= self.target:
                self.result = f"{batting_team_name} wins by {10-self.total_wickets} wickets"
            elif self.target and self.total_runs < self.target - 1:
                self.result = f"{bowling_team_name} wins by {self.target - self.total_runs - 1} runs"
            elif self.target and self.total_runs == self.target - 1:
                self.result = "Match Tied"
            else:
                self.result = f"{batting_team_name} scored {self.total_runs}/{self.total_wickets}"
            # Record second innings for summary/export
            self.second_innings_overs = self.total_overs
            self.second_innings_balls = self.total_balls
            self._record_innings(batting_team_name, bowling_team_name, self.total_runs, self.total_wickets, self.total_overs, self.total_balls)
            
            # Prepare match result data
            team1_name = self.team1.name if hasattr(self.team1, 'name') else self.team1['name']
            team2_name = self.team2.name if hasattr(self.team2, 'name') else self.team2['name']
            self.match_data = {
                'team1': team1_name,
                'team2': team2_name,
                'team1_score': self.first_innings_score,
                'team1_wickets': self.first_innings_wickets,
                'team2_score': self.total_runs,
                'team2_wickets': self.total_wickets,
                'result': self.result
            }
            
            # Update player stats from match_stats
            # THIS WAS PREVIOUSLY IN THE WRONG PLACE - should be in update_player_stats
            # Moving this logic to the proper function
            
            # Update master game stats
            print("Pre-emptively updating team data in end_match...")
            # REMOVING DUPLICATE UPDATES - Stats will be updated in close_summary
            # self.update_player_stats()
            # self.update_master_game_data()
            
            # Show match summary
            self.show_match_summary()

    def show_match_summary(self):
        """Display enhanced final match summary in a scrollable dialog with export"""
        team1_name = self.team1_name
        team2_name = self.team2_name

        # Add summary lines to commentary
        innings_one = f"{team1_name}: {self.first_innings_score}/{self.first_innings_wickets} in {self.first_innings_overs}.{self.first_innings_balls % 6} overs"
        innings_two = f"{team2_name}: {self.total_runs}/{self.total_wickets} in {self.total_overs}.{self.total_balls % 6} overs"
        summary_lines = ["\nMatch Summary:", innings_one, innings_two, self.result or "Result pending"]
        for line in summary_lines:
            self.add_commentary(line)

        if self.headless:
            return

        summary_window = tk.Toplevel(self.match_window)
        summary_window.title("Match Summary")
        summary_window.geometry("900x650")
        summary_window.transient(self.match_window)
        summary_window.grab_set()

        # Header
        header_frame = ttk.Frame(summary_window)
        header_frame.pack(fill='x', padx=10, pady=10)
        ttk.Label(header_frame, text="MATCH RESULT", font=('Arial', 18, 'bold')).pack()
        ttk.Label(header_frame, text=self.result or "Result pending", font=('Arial', 14, 'bold'), foreground='blue').pack()

        # Tabs for Team1/Team2 batting & bowling
        tabs = ttk.Notebook(summary_window)
        tabs.pack(expand=True, fill='both', padx=10, pady=5)

        team1_name = self.team1.name if hasattr(self.team1, 'name') else self.team1.get('name', 'Team 1') if isinstance(self.team1, dict) else 'Team 1'
        team2_name = self.team2.name if hasattr(self.team2, 'name') else self.team2.get('name', 'Team 2') if isinstance(self.team2, dict) else 'Team 2'

        def build_batting_tab(team_name):
            frame = ttk.Frame(tabs)
            tree = ttk.Treeview(frame, columns=('Batter','R','B','4s','6s','SR','Status'), show='headings')
            for col, w in [('Batter',180),('R',50),('B',50),('4s',50),('6s',50),('SR',70),('Status',180)]:
                tree.heading(col, text=col)
                tree.column(col, width=w, anchor='center' if col != 'Batter' else 'w')
            innings = [inn for inn in self.innings_history if inn['batting_team']==team_name]
            source = innings[0]['batting_stats'] if innings else {p['name']: self.match_stats.get(p['name'],{}).get('batting',{}) for p in self.playing_xis.get(team_name, [])}
            for name, stats in source.items():
                runs = stats.get('runs',0); balls = stats.get('balls',0)
                sr = f"{(runs/balls*100):.1f}" if balls else '0.0'
                tree.insert('', 'end', values=(name,runs,balls,stats.get('fours',0),stats.get('sixes',0),sr, stats.get('dismissal','not out') or 'not out'))
            tree.pack(expand=True, fill='both', padx=5, pady=5)
            return frame

        def build_bowling_tab(team_name):
            frame = ttk.Frame(tabs)
            tree = ttk.Treeview(frame, columns=('Bowler','O','M','R','W','Econ'), show='headings')
            for col,w in [('Bowler',180),('O',60),('M',50),('R',60),('W',60),('Econ',70)]:
                tree.heading(col, text=col)
                tree.column(col, width=w, anchor='center' if col != 'Bowler' else 'w')
            innings = [inn for inn in self.innings_history if inn['bowling_team']==team_name]
            source = innings[0]['bowling_stats'] if innings else {p['name']: self.match_stats.get(p['name'],{}).get('bowling',{}) for p in self.playing_xis.get(team_name, [])}
            for name, stats in source.items():
                balls = stats.get('balls',0); overs = balls//6; rem = balls%6
                econ = (stats.get('runs',0)/(balls/6)) if balls else 0
                tree.insert('', 'end', values=(name, f"{overs}.{rem}", stats.get('maidens',0), stats.get('runs',0), stats.get('wickets',0), f"{econ:.2f}"))
            tree.pack(expand=True, fill='both', padx=5, pady=5)
            return frame

        tabs.add(build_batting_tab(team1_name), text=f"{team1_name} Batting")
        tabs.add(build_bowling_tab(team1_name), text=f"{team1_name} Bowling")
        tabs.add(build_batting_tab(team2_name), text=f"{team2_name} Batting")
        tabs.add(build_bowling_tab(team2_name), text=f"{team2_name} Bowling")

        btn_frame = ttk.Frame(summary_window)
        btn_frame.pack(fill='x', pady=10, padx=10)
        # Export full scorecards + ball-by-ball commentary
        ttk.Button(btn_frame, text="Export to CSV", command=self.export_commentary).pack(side='left', padx=5)

        def close_all():
            summary_window.destroy()
            try:
                if hasattr(self, 'match_window') and self.match_window:
                    self.match_window.destroy()
            except Exception:
                pass
        ttk.Button(btn_frame, text="OK - Close", command=close_all).pack(side='right', padx=5)

    def update_master_game_data(self):
        """Update the main game's player data directly"""
        print("Updating master game data...")
        
        # Check if we've already updated master game data (prevent duplicate updates)
        if hasattr(self, 'master_updated') and self.master_updated:
            print("Master game data has already been updated for this match. Skipping update.")
            return
            
        if not hasattr(self.master, 'teams'):
            print("Master game has no teams attribute, skipping direct update.")
            return
            
        try:
            # Find and update the team objects in the master's teams list
            teams_updated = 0
            players_updated = 0
            
            # First check what type of data structure we're working with
            print(f"Master.teams type: {type(self.master.teams)}")
            
            # Since self.master.teams is a list, not a dictionary
            if isinstance(self.master.teams, list):
                for team_obj in self.master.teams:
                    if not isinstance(team_obj, dict):
                        print(f"Warning: team object is not a dict: {type(team_obj)}")
                        continue
                        
                    if 'name' not in team_obj:
                        print(f"Warning: team object has no 'name' field: {list(team_obj.keys()) if hasattr(team_obj, 'keys') else 'unknown structure'}")
                        continue
                        
                    # Check if this team matches either of our match teams
                    if team_obj['name'] == self.team1['name']:
                        # Update Team 1 players
                        print(f"Updating {team_obj['name']} players in master game")
                        if 'players' not in team_obj:
                            print(f"Warning: team {team_obj['name']} has no 'players' field")
                            continue
                            
                        for player in self.team1['players']:
                            for master_player in team_obj['players']:
                                if master_player['name'] == player['name']:
                                    # Store original values for debugging
                                    old_runs = master_player.get('runs', 0)
                                    old_wickets = master_player.get('wickets', 0)
                                    
                                    # Update with the updated player stats
                                    for key, value in player.items():
                                        if key != 'name':  # Don't overwrite name
                                            master_player[key] = value
                                    
                                    print(f"Master update: {player['name']} - Runs: {old_runs} -> {master_player.get('runs', 0)}, Wickets: {old_wickets} -> {master_player.get('wickets', 0)}")
                                    players_updated += 1
                        teams_updated += 1
                    
                    elif team_obj['name'] == self.team2['name']:
                        # Update Team 2 players
                        print(f"Updating {team_obj['name']} players in master game")
                        if 'players' not in team_obj:
                            print(f"Warning: team {team_obj['name']} has no 'players' field")
                            continue
                            
                        for player in self.team2['players']:
                            for master_player in team_obj['players']:
                                if master_player['name'] == player['name']:
                                    # Store original values for debugging
                                    old_runs = master_player.get('runs', 0)
                                    old_wickets = master_player.get('wickets', 0)
                                    
                                    # Update with the updated player stats
                                    for key, value in player.items():
                                        if key != 'name':  # Don't overwrite name
                                            master_player[key] = value
                                    
                                    print(f"Master update: {player['name']} - Runs: {old_runs} -> {master_player.get('runs', 0)}, Wickets: {old_wickets} -> {master_player.get('wickets', 0)}")
                                    players_updated += 1
                        teams_updated += 1
                    
            # Fallback approach if the teams structure is something else entirely
            elif False:  # Placeholder for other potential team structures
                print("Using alternative approach to update stats")
                # Your fallback code here
            
            print(f"Master game update complete: {teams_updated} teams and {players_updated} players updated.")
            
            # Mark that master game data has been updated for this match
            self.master_updated = True
            
            # Explicitly request UI updates if they exist
            if hasattr(self.master, 'update_all_tabs'):
                self.master.update_all_tabs()
                
        except Exception as e:
            print(f"Error updating master game data: {e}")
            import traceback
            traceback.print_exc()

    def update_score_display(self):
        """Update the score display and batsmen/bowler labels"""
        # If UI widgets aren't built (headless/temp simulations), skip safely
        needed_attrs = ['score_label', 'target_label', 'striker_label', 'non_striker_label', 'batting_tree']
        if any(not hasattr(self, attr) for attr in needed_attrs):
            return

        # Target / innings info
        if self.current_innings == 2 and self.target:
            required = self.target - self.total_runs
            balls_left = (self.max_overs * 6) - (self.total_overs * 6 + self.total_balls)
            if balls_left > 0:
                rr_required = (required * 6) / balls_left
                self.target_label.config(text=f"Target: {self.target} ({required} needed from {balls_left} balls, RRR: {rr_required:.2f})")
            else:
                self.target_label.config(text=f"Target: {self.target}")
        else:
            self.target_label.config(text="First Innings")

        # Scoreline (include batting team name)
        batting_team_name = None
        if hasattr(self, 'batting_team') and self.batting_team:
            batting_team_name = self.batting_team.name if hasattr(self.batting_team, 'name') else self.batting_team.get('name') if isinstance(self.batting_team, dict) else None
        prefix = f"{batting_team_name}: " if batting_team_name else ""
        self.score_label.config(text=f"{prefix}{self.total_runs}/{self.total_wickets} ({self.total_overs}.{self.total_balls % 6})")

        # Striker / non-striker labels
        striker_name = self.striker.name if hasattr(self.striker, 'name') else self.striker['name']
        non_striker_name = self.non_striker.name if hasattr(self.non_striker, 'name') else self.non_striker['name']
        striker_stats = self.match_stats.get(striker_name, {}).get('batting', {'runs': 0, 'balls': 0})
        non_striker_stats = self.match_stats.get(non_striker_name, {}).get('batting', {'runs': 0, 'balls': 0})
        self.striker_label.config(text=f"Striker: {striker_name} {striker_stats['runs']} ({striker_stats['balls']})")
        self.non_striker_label.config(text=f"Non-striker: {non_striker_name} {non_striker_stats['runs']} ({non_striker_stats['balls']})")

        # Bowler label
        self.update_bowler_display()

        # Refresh batting card
        self.batting_tree.delete(*self.batting_tree.get_children())
        for player in self.batting_xi:
            player_name = player.name if hasattr(player, 'name') else player['name']
            stats = self.match_stats[player_name]['batting']
            name = player_name
            if player == self.striker:
                name = f"**{name}***"
            elif player == self.non_striker:
                name = f"**{name}**"
            self.batting_tree.insert('', 'end', values=(
                name,
                stats['runs'],
                stats['balls'],
                stats['fours'],
                stats['sixes'],
                round(stats['runs'] * 100 / stats['balls'], 2) if stats['balls'] > 0 else 0,
                stats['dismissal'] if stats['dismissal'] else 'not out'
            ))

        # Update bowling scorecard to reflect latest over progress
        self.update_bowling_scorecard()

    def setup_match(self):
        """Set up the match based on format without auto-simulation"""
        if self.match_format == 'ODI':
            self.setup_odi_match()
        elif self.match_format == 'Test':
            self.setup_test_match()
        else:
            self.setup_t20_match()
        
        self.add_commentary(f"Match is ready to begin. Use 'Bowl Delivery' or 'Bowl Over' to play.")

    def setup_odi_match(self):
        """Set up an ODI match without auto-simulation"""
        self.total_overs = 0  # Reset to simulate full innings
        self.add_match_start_commentary()
        self.update_score_display()

    def setup_test_match(self):
        """Set up a Test match without auto-simulation"""
        self.total_overs = 0
        self.add_match_start_commentary()
        self.update_score_display()

    def setup_t20_match(self):
        """Set up a T20 match without auto-simulation"""
        self.total_overs = 0
        self.add_match_start_commentary()
        self.update_score_display()

    def simulate_match(self):
        """Simulate the match based on format"""
        if self.match_format == 'ODI':
            self.simulate_odi_match()
        elif self.match_format == 'Test':
            self.simulate_test_match()
        else:
            self.simulate_t20_match()

    def simulate_odi_match(self):
        """Simulate an ODI match"""
        self.total_overs = 0  # Reset to simulate full innings
        self.simulate_innings()

    def simulate_test_match(self):
        """Simulate a Test match"""
        self.total_overs = None
        self.simulate_innings(test=True)

    def simulate_t20_match(self):
        """Simulate a T20 match"""
        self.total_overs = 0
        self.simulate_innings()

    def simulate_innings(self, test=False):
        """Simulate innings"""
        if test:
            self.max_overs = None
        elif self.match_format == 'ODI':
            self.max_overs = 50
        else:
            self.max_overs = 20
        
        if self.current_innings == 1:
            self.add_match_start_commentary()
        else:
            self.add_commentary(f"Second innings begins. {self.batting_team['name']} needs {self.target} runs to win")
        
        self.simulation_speed = 1000
        self.match_window.after(500, self.bowl_ball)

    def bowl_ball(self):
        """Bowl a single ball in simulation - DEPRECATED - Use bowl_delivery instead"""
        # This function is kept for backward compatibility but should not be used
        # directly as it has auto-simulation behavior
        if self.match_ended:
            return
        self.simulate_ball()
        if not self.match_ended:
            # This line is the auto-simulation behavior we want to remove
            # self.match_window.after(self.simulation_speed, self.bowl_ball)
            pass

    def bowl_delivery(self):
        """Bowl a single delivery manually"""
        if self.match_ended:
            return
        self.simulate_ball()
        self.update_score_display()

    def bowl_over(self):
        """Bowl a complete over"""
        if self.match_ended:
            return
        
        # Calculate how many more balls to bowl in this over
        remaining_balls = 6 - self.total_balls
        
        # Bowl each remaining ball in the over
        for _ in range(remaining_balls):
            if self.match_ended:
                break
            self.bowl_delivery()

    def update_bowling_scorecard(self):
        """Update bowling scorecard"""
        for item in self.bowling_tree.get_children():
            self.bowling_tree.delete(item)
        for player in self.bowling_xi:
            player_name = player.name if hasattr(player, 'name') else player['name']
            stats = self.match_stats[player_name]['bowling']
            if stats['balls'] > 0:
                overs = stats['balls'] // 6
                balls = stats['balls'] % 6
                over_display = f"{overs}.{balls}"
                economy = (stats['runs'] * 6) / stats['balls'] if stats['balls'] > 0 else 0
                
                # Calculate top speed and average speed
                top_speed = 0
                avg_speed = 0
                if 'speeds' in stats and len(stats['speeds']) > 0:
                    top_speed = max(stats['speeds'])  # Get the fastest delivery
                    mean_speed = sum(stats['speeds']) / len(stats['speeds'])
                    # Clamp average within 7 kph of top speed and never above top
                    avg_speed = max(top_speed - 7, min(mean_speed, top_speed))
                
                self.bowling_tree.insert('', 'end', values=(
                    player_name,
                    over_display,
                    stats['maidens'],
                    stats['runs'],
                    stats['wickets'],
                    f"{economy:.1f}",
                    f"{top_speed:.0f} kph",
                    f"{avg_speed:.0f} kph"
                ))

    def get_pitch_description(self):
        """Generate pitch description"""
        pace_rating = self.pitch_pace_rating
        spin_rating = self.pitch_spin_rating
        avg_rating = (pace_rating + spin_rating) / 2
        
        if avg_rating <= 3:
            overall = "Batting paradise"
        elif avg_rating <= 5:
            overall = "Good batting pitch"
        elif avg_rating <= 7:
            overall = "Balanced pitch"
        else:
            overall = "Bowler-friendly pitch"
        
        pace = "minimal seam movement" if pace_rating <= 3 else "some seam assistance" if pace_rating <= 6 else "significant pace assistance"
        spin = "minimal turn" if spin_rating <= 3 else "moderate turn" if spin_rating <= 6 else "sharp turn"
        
        return f"{overall} with {pace} and {spin}."

    def simulate_ball(self):
        """Simulate a single delivery"""
        if self.match_ended:
            return
        
        batting_agg = self.batting_slider.get() / 100.0
        bowling_agg = self.bowling_slider.get() / 100.0
        bowling_line = self.bowling_line_var.get()
        field_setting = self.field_setting_var.get()
        
        # Calculate bowling speed
        from cricket_manager.systems.pace_speed_system import calculate_bowler_speed
        speed = calculate_bowler_speed(self.current_bowler)
        # Keep last delivery speed for commentary wording overrides
        self.last_ball_speed = speed
        
        # Use Player objects consistently; apply form (2x vs legacy 0.08) — keep in sync with FastMatchSimulator
        striker_batting = getattr(self.striker, 'batting', 50)
        bowler_bowling = getattr(self.current_bowler, 'bowling', 50)
        striker_form = getattr(self.striker, 'form', 50)
        bowler_form = getattr(self.current_bowler, 'form', 50)
        form_bat = 0.96 + (striker_form / 50.0) * 0.16
        form_bowl = 0.96 + (bowler_form / 50.0) * 0.16
        striker_batting = min(99, max(1, striker_batting * form_bat))
        bowler_bowling = min(99, max(1, bowler_bowling * form_bowl))
        
        probs = self.calculate_outcome_probabilities(
            striker_batting,
            bowler_bowling,
            batting_agg,
            bowling_agg,
            bowling_line,
            field_setting
        )
        
        outcome = random.choices(list(probs.keys()), weights=[probs[o] for o in probs], k=1)[0]
        
        # Use player role to determine bowler type
        bowler_role = getattr(self.current_bowler, 'role', '').lower()
        bowler_kind = determine_bowler_type(bowler_role)
        is_pace_bowler = bowler_kind == 'pace'
        is_spin_bowler = not is_pace_bowler
        
        pitch_effect_text = ""
        if is_pace_bowler and self.pitch_pace_rating >= 8 and (outcome == 'wicket' or outcome == 'dot'):
            pitch_effect_text = " The pitch is offering great assistance to the seamers!"
        elif is_spin_bowler and self.pitch_spin_rating >= 8 and (outcome == 'wicket' or outcome == 'dot'):
            pitch_effect_text = " The pitch is providing sharp turn for the spinners!"
        elif (is_pace_bowler and self.pitch_pace_rating <= 3 or is_spin_bowler and self.pitch_spin_rating <= 3) and (outcome == 'four' or outcome == 'six'):
            pitch_effect_text = " The batsman is enjoying these batting-friendly conditions!"
        
        # Safely get bowler name from either Player object or dict
        if hasattr(self.current_bowler, 'name'):
            bowler_name = self.current_bowler.name
        elif isinstance(self.current_bowler, dict) and 'name' in self.current_bowler:
            bowler_name = self.current_bowler['name']
        else:
            bowler_name = 'Unknown'
            print(f"Warning: Could not determine bowler name from {type(self.current_bowler)}")
        
        # Ensure bowler exists in match_stats before accessing
        if bowler_name not in self.match_stats:
            print(f"Warning: Bowler '{bowler_name}' not found in match_stats. Available bowlers: {list(self.match_stats.keys())}")
            return
        
        print(f"Before ball: total_overs={self.total_overs}, total_balls={self.total_balls}, bowler_balls={self.match_stats[bowler_name]['bowling']['balls']}")
        
        # Build current ball label before increments for commentary/export
        over_ball_label = f"{self.total_overs}.{self.total_balls}"

        if outcome == 'wicket':
            self.process_wicket(speed, pitch_effect_text, over_ball_label)
        else:
            runs = {'single': 1, 'double': 2, 'triple': 3, 'four': 4, 'six': 6, 'dot': 0}[outcome]
            self.process_runs(runs, speed, pitch_effect_text, over_ball_label)
        
        self.total_balls += 1
        self.match_stats[bowler_name]['bowling']['balls'] += 1
        
        # Track bowling speeds
        if 'speeds' not in self.match_stats[bowler_name]['bowling']:
            self.match_stats[bowler_name]['bowling']['speeds'] = []
        self.match_stats[bowler_name]['bowling']['speeds'].append(speed)
        
        if self.total_balls == 6:
            self.total_balls = 0
            self.total_overs += 1
            # Ensure the bowler_data is properly initialized before changing bowlers
            if self.current_bowler and bowler_name not in self.bowler_data:
                self.initialize_bowler_data(bowler_name)
            self.change_bowler()
            print(f"Change bowler called at over {self.total_overs}, innings {self.current_innings}")
        
        self.update_score_display()
        
        print(f"After ball: total_overs={self.total_overs}, total_balls={self.total_balls}, bowler_balls={self.match_stats[bowler_name]['bowling']['balls']}")
        
        if self.max_overs and self.total_overs >= self.max_overs:
            self.end_innings()
        if self.current_innings == 2 and self.target and self.total_runs >= self.target:
            self.end_match(f"{self.batting_team['name']} wins by {10 - self.total_wickets} wickets!")
        if self.total_wickets >= 10:  # Changed from >= to == for clarity
            self.end_innings()


    def process_wicket(self, speed, pitch_effect_text="", over_ball_label=None):
        """Process a wicket"""
        self.total_wickets += 1
        
        # Check if the bowler is a spin bowler - affects dismissal probabilities
        bowler_role = getattr(self.current_bowler, 'role', '').lower()
        is_spin_bowler = any(spin_type in bowler_role for spin_type in ['spin', 'spinner'])
        
        # Generate a random number for dismissal selection
        dismissal_roll = random.random() * 100  # 0-100
        
        # Select fielder for caught dismissals
        fielder = None
        if len(self.bowling_xi) > 0:
            # Exclude current bowler from potential fielders
            current_bowler_name = getattr(self.current_bowler, 'name', self.current_bowler['name'] if isinstance(self.current_bowler, dict) else 'Unknown')
            possible_fielders = [p for p in self.bowling_xi if getattr(p, 'name', p['name'] if isinstance(p, dict) else 'Unknown') != current_bowler_name]
            if possible_fielders:
                fielder = random.choice(possible_fielders)
            else:
                fielder = random.choice(self.bowling_xi)
        
        # Dismissal type allocation according to specified probabilities
        # Stumped only possible for spin bowlers, so adjust probabilities accordingly
        if is_spin_bowler:
            # With spin bowler
            if dismissal_roll < 30:  # 30%
                dismissal_type = "Caught"
                fielder_name = getattr(fielder, 'name', fielder['name'] if isinstance(fielder, dict) else 'Unknown')
                bowler_name = getattr(self.current_bowler, 'name', self.current_bowler['name'] if isinstance(self.current_bowler, dict) else 'Unknown')
                dismissal_display = f"c {fielder_name} b {bowler_name}"
            elif dismissal_roll < 45:  # 15%
                dismissal_type = "Bowled"
                bowler_name = getattr(self.current_bowler, 'name', self.current_bowler['name'] if isinstance(self.current_bowler, dict) else 'Unknown')
                dismissal_display = f"b {bowler_name}"
            elif dismissal_roll < 68:  # 23%
                dismissal_type = "LBW"
                bowler_name = getattr(self.current_bowler, 'name', self.current_bowler['name'] if isinstance(self.current_bowler, dict) else 'Unknown')
                dismissal_display = f"lbw b {bowler_name}"
            elif dismissal_roll < 77:  # 9% (Stumped only for spin)
                dismissal_type = "Stumped"
                fielder_name = getattr(fielder, 'name', fielder['name'] if isinstance(fielder, dict) else 'Unknown')
                bowler_name = getattr(self.current_bowler, 'name', self.current_bowler['name'] if isinstance(self.current_bowler, dict) else 'Unknown')
                dismissal_display = f"st {fielder_name} b {bowler_name}"
            elif dismissal_roll < 78:  # 1%
                dismissal_type = "Hit Wicket"
                bowler_name = getattr(self.current_bowler, 'name', self.current_bowler['name'] if isinstance(self.current_bowler, dict) else 'Unknown')
                dismissal_display = f"hit wicket b {bowler_name}"
            elif dismissal_roll < 96:  # 18%
                dismissal_type = "Edge Caught"
                fielder_name = getattr(fielder, 'name', fielder['name'] if isinstance(fielder, dict) else 'Unknown')
                bowler_name = getattr(self.current_bowler, 'name', self.current_bowler['name'] if isinstance(self.current_bowler, dict) else 'Unknown')
                dismissal_display = f"c {fielder_name} b {bowler_name} (edge)"
            else:  # 4% (adjusted for 9% Stumped)
                dismissal_type = "Run Out"
                dismissal_display = "run out"
                # Don't increment bowler wickets for run out - handled below
        else:
            # With pace bowler (no Stumped)
            if dismissal_roll < 30:  # 30%
                dismissal_type = "Caught"
                fielder_name = getattr(fielder, 'name', fielder['name'] if isinstance(fielder, dict) else 'Unknown')
                bowler_name = getattr(self.current_bowler, 'name', self.current_bowler['name'] if isinstance(self.current_bowler, dict) else 'Unknown')
                dismissal_display = f"c {fielder_name} b {bowler_name}"
            elif dismissal_roll < 45:  # 15%
                dismissal_type = "Bowled"
                bowler_name = getattr(self.current_bowler, 'name', self.current_bowler['name'] if isinstance(self.current_bowler, dict) else 'Unknown')
                dismissal_display = f"b {bowler_name}"
            elif dismissal_roll < 68:  # 23%
                dismissal_type = "LBW"
                bowler_name = getattr(self.current_bowler, 'name', self.current_bowler['name'] if isinstance(self.current_bowler, dict) else 'Unknown')
                dismissal_display = f"lbw b {bowler_name}"
            elif dismissal_roll < 69:  # 1%
                dismissal_type = "Hit Wicket"
                bowler_name = getattr(self.current_bowler, 'name', self.current_bowler['name'] if isinstance(self.current_bowler, dict) else 'Unknown')
                dismissal_display = f"hit wicket b {bowler_name}"
            elif dismissal_roll < 87:  # 18%
                dismissal_type = "Edge Caught"
                fielder_name = getattr(fielder, 'name', fielder['name'] if isinstance(fielder, dict) else 'Unknown')
                bowler_name = getattr(self.current_bowler, 'name', self.current_bowler['name'] if isinstance(self.current_bowler, dict) else 'Unknown')
                dismissal_display = f"c {fielder_name} b {bowler_name} (edge)"
            else:  # 13% (adjusted to make up for no Stumped)
                dismissal_type = "Run Out"
                dismissal_display = "run out"
                # Don't increment bowler wickets for run out - handled below
        
        # Update player stats with the enhanced dismissal display
        # Handle both Player objects and dictionary-style players for striker and bowler names
        if hasattr(self.striker, 'name'):
            striker_name = self.striker.name
        elif isinstance(self.striker, dict) and 'name' in self.striker:
            striker_name = self.striker['name']
        else:
            striker_name = str(self.striker)
        
        bowler_name = getattr(self.current_bowler, 'name', self.current_bowler['name'] if isinstance(self.current_bowler, dict) else 'Unknown')
        self.match_stats[striker_name]['batting']['dismissal'] = dismissal_display
        self.match_stats[striker_name]['batting']['balls'] += 1
        
        # For non-run out dismissals, count the wicket for the bowler
        if dismissal_type != "Run Out":
            # Get bowler name safely from either Player object or dict
            if hasattr(self.current_bowler, 'name'):
                bowler_name = self.current_bowler.name
            elif isinstance(self.current_bowler, dict) and 'name' in self.current_bowler:
                bowler_name = self.current_bowler['name']
            else:
                bowler_name = 'Unknown'
            
            # Ensure bowler exists in match_stats before incrementing wickets
            if bowler_name in self.match_stats:
                self.match_stats[bowler_name]['bowling']['wickets'] += 1
            else:
                print(f"Warning: Bowler '{bowler_name}' not found in match_stats when recording wicket")
        
        trait_commentary = ""
        is_pace_friendly = self.pitch_pace_rating >= 7
        is_spin_friendly = self.pitch_spin_rating >= 7
        is_batting_friendly = self.pitch_pace_rating <= 3 and self.pitch_spin_rating <= 3
        is_bowling_friendly = self.pitch_pace_rating >= 7 and self.pitch_spin_rating >= 7
        # Use Player objects consistently
        bowler_role = getattr(self.current_bowler, 'role', '').lower()
        is_pace_bowler = any(pace_type in bowler_role for pace_type in ['fast', 'medium', 'seam'])
        
        for trait in getattr(self.current_bowler, 'traits', []):
            trait_name = trait['name']
            if (trait_name == 'GREEN_TRACK_BULLY' and is_pace_friendly and is_pace_bowler) or                (trait_name == 'DUSTY_MAN' and is_spin_friendly and is_spin_bowler) or                (trait_name == 'PITCH_OUT_OF_EQUATION' and is_batting_friendly):
                trait_commentary = f" {getattr(self.current_bowler, 'name', 'Unknown')}'s {POSITIVE_TRAITS[trait_name]['name']} trait is proving effective on this pitch!"
                break
        
        for trait in getattr(self.striker, 'traits', []):
            trait_name = trait['name']
            if (trait_name == 'FLAT_TRACK_BULLY' and is_bowling_friendly) or                (trait_name == 'NO_TECHNIQUE_BASHER' and is_bowling_friendly):
                trait_dict = NEGATIVE_TRAITS.get(trait_name, POSITIVE_TRAITS.get(trait_name, {'name': trait_name}))
                trait_commentary = f" {striker_name} is struggling with the {trait_dict['name']} trait on this difficult pitch."
                break
        
        # Generate detailed ball-by-ball commentary for wickets
        detailed_commentary = self.get_detailed_ball_commentary(0, speed)
        
        # Handle both Player objects and dictionary-style players for commentary
        striker_display = getattr(self.striker, 'name', self.striker['name'] if isinstance(self.striker, dict) else str(self.striker))
        bowler_display = getattr(self.current_bowler, 'name', self.current_bowler['name'] if isinstance(self.current_bowler, dict) else 'Unknown')
        prefix = f"{over_ball_label}: " if over_ball_label else ""
        self.add_commentary(f"{prefix}OUT! {dismissal_type}! {striker_display} is dismissed by {bowler_display} ({detailed_commentary}).{pitch_effect_text}{trait_commentary}")
        
        if self.total_wickets == 10:  # Changed from >= to == for clarity
            self.add_commentary("All out!")
            self.end_innings()
            return
        
        # For wickets 1-9, get the next batsman (players at indices 2-10 in batting_xi)
        next_batsman_index = 1 + self.total_wickets  # Changed from 2 + to 1 + to fix the indexing
        if next_batsman_index < len(self.batting_xi):
            self.striker = self.batting_xi[next_batsman_index]
            self.add_commentary(f"New batsman: {self.striker['name']}")
        else:
            self.add_commentary("All out!")
            self.end_innings()
    def process_runs(self, runs, speed, pitch_effect_text="", over_ball_label=None):
        """Process runs scored"""
        self.total_runs += runs
        # Handle both Player objects and dictionary-style players for striker and bowler names
        if hasattr(self.striker, 'name'):
            striker_name = self.striker.name
        elif isinstance(self.striker, dict) and 'name' in self.striker:
            striker_name = self.striker['name']
        else:
            striker_name = str(self.striker)
        
        # Get bowler name safely from either Player object or dict
        if hasattr(self.current_bowler, 'name'):
            bowler_name = self.current_bowler.name
        elif isinstance(self.current_bowler, dict) and 'name' in self.current_bowler:
            bowler_name = self.current_bowler['name']
        else:
            bowler_name = 'Unknown'
            print(f"Warning: Could not determine bowler name from {type(self.current_bowler)}")
        
        self.match_stats[striker_name]['batting']['runs'] += runs
        self.match_stats[striker_name]['batting']['balls'] += 1
        
        shot_description = self.get_shot_description(runs)
        
        trait_commentary = ""
        is_pace_friendly = self.pitch_pace_rating >= 7
        is_spin_friendly = self.pitch_spin_rating >= 7
        is_batting_friendly = self.pitch_pace_rating <= 3 and self.pitch_spin_rating <= 3
        is_bowling_friendly = self.pitch_pace_rating >= 7 and self.pitch_spin_rating >= 7
        # Use Player objects consistently
        bowler_role = getattr(self.current_bowler, 'role', '').lower()
        is_pace_bowler = any(pace_type in bowler_role for pace_type in ['fast', 'medium', 'seam'])
        is_spin_bowler = any(spin_type in bowler_role for spin_type in ['spin', 'spinner'])
        
        if runs >= 4:
            for trait in getattr(self.striker, 'traits', []):
                trait_name = trait['name']
                if ((trait_name == 'GREAT_TECHNIQUE' and is_pace_friendly and is_pace_bowler) or 
                    (trait_name == 'PRESENCE_OF_MIND' and is_spin_friendly and is_spin_bowler) or 
                    (trait_name == 'NO_TECHNIQUE_BASHER' and is_batting_friendly) or
                    (trait_name == 'HAIRY_MONSTER' and is_bowling_friendly)):
                    trait_commentary = f" {striker_name}'s {POSITIVE_TRAITS[trait_name]['name']} trait is showing on this pitch!"
                    break
        
        if runs >= 4:
            for trait in getattr(self.current_bowler, 'traits', []):
                trait_name = trait['name']
                if trait_name == 'PITCH_DEPENDENT' and ((is_pace_bowler and not is_pace_friendly) or (is_spin_bowler and not is_spin_friendly)):
                    trait_commentary = f" {bowler_name} is struggling with the {NEGATIVE_TRAITS[trait_name]['name']} trait on this pitch."
                    break
        
        # Generate detailed ball-by-ball commentary
        detailed_commentary = self.get_detailed_ball_commentary(runs, speed)
        
        prefix = f"{over_ball_label}: " if over_ball_label else ""
        if runs == 4:
            self.match_stats[striker_name]['batting']['fours'] += 1
            self.add_commentary(f"{prefix}FOUR! {striker_name} {shot_description} off {bowler_name} ({detailed_commentary}){pitch_effect_text}{trait_commentary}")
        elif runs == 6:
            self.match_stats[striker_name]['batting']['sixes'] += 1
            self.add_commentary(f"{prefix}SIX! {striker_name} {shot_description} off {bowler_name} ({detailed_commentary}){pitch_effect_text}{trait_commentary}")
        elif runs == 0:
            self.add_commentary(f"{prefix}Dot ball from {bowler_name}. {striker_name} {shot_description} ({detailed_commentary}){pitch_effect_text}")
        else:
            self.add_commentary(f"{prefix}{runs} runs taken by {striker_name} - {shot_description} ({detailed_commentary}){pitch_effect_text}")
        
        self.match_stats[bowler_name]['bowling']['runs'] += runs
        
        if runs % 2 == 1:
            self.striker, self.non_striker = self.non_striker, self.striker

    def update_bowler_display(self):
        """Update bowler display"""
        if self.current_bowler:
            bowler_name = self.current_bowler.name if hasattr(self.current_bowler, 'name') else self.current_bowler['name']
            stats = self.match_stats[bowler_name]['bowling']
            overs = stats['balls'] // 6
            balls = stats['balls'] % 6
            self.bowler_label.config(text=f"{bowler_name}: {overs}.{balls}-{stats['maidens']}-{stats['runs']}-{stats['wickets']}")

    def get_detailed_ball_commentary(self, runs, speed):
        """Generate detailed ball-by-ball commentary with pitch, length, line, movement, and shot info"""
        # Bowler info
        bowler_role = getattr(self.current_bowler, 'role', '').lower()
        bowling_line = self.bowling_line_var.get()
        is_pace_bowler = any(pace_type in bowler_role for pace_type in ['fast', 'medium', 'seam'])
        
        # Length levels 0-10 as specified
        length_levels = [
            'level 0: full toss',
            'level 1: yorker',
            'level 2: fuller length',
            'level 3: full length',
            'level 4: fullish good length',
            'level 5: good length',
            'level 6: short of good length',
            'level 7: between hard and good length',
            'level 8: hard length',
            'level 9: short pitch length',
            'level 10: half tracker'
        ]

        # Cap slow bowlers (<110 kph) to not bowl above level 7
        effective_levels = length_levels
        effective_speed = speed if speed is not None else getattr(self, 'last_ball_speed', None)
        if effective_speed is not None and effective_speed < 110:
            effective_levels = length_levels[:8]  # levels 0-7
        length_choice = random.choice(effective_levels)

        # Line (stump/channel) levels (0-9 as requested)
        line_levels = [
            'line level 0: wide ball (way outside off)',
            'line level 1: close to wide outside off stump',
            'line level 2: way outside off stump',
            'line level 3: away from off stump',
            'line level 4: outside off stump',
            'line level 5: a bit outside off stump',
            'line level 6: just outside off stump',
            'line level 7: on off stump',
            'line level 8: on middle stump',
            'line level 9: on leg stump'
        ]
        line_choice = random.choice(line_levels)

        # Movement from player movements (50% major, 50% minor where available)
        movement_desc = ""
        movements_attr = None
        bowler_movements = getattr(self.current_bowler, 'bowling_movements', None)
        bowler_type = None
        if isinstance(bowler_movements, dict):
            movements_attr = bowler_movements.get('movements')
            bowler_type = bowler_movements.get('bowler_type')
        if not bowler_type:
            role_kind = determine_bowler_type(bowler_role)
            bowler_type = 'pace' if role_kind == 'pace' else 'spin'
        # Speed-based override: slow (<105 kph) treated as spin for movement wording
        last_speed = getattr(self, 'last_ball_speed', None)
        if last_speed is not None and last_speed < 105:
            bowler_type = 'spin'
        elif determine_bowler_type(bowler_role) == 'pace':
            bowler_type = 'pace'
        if isinstance(movements_attr, dict) and movements_attr:
            major = [m for m, data in movements_attr.items() if data.get('category') == 'major']
            minor = [m for m, data in movements_attr.items() if data.get('category') != 'major']

            pick_pool = None
            if major and minor:
                pick_pool = major if random.random() < 0.5 else minor
            elif major:
                pick_pool = major
            elif minor:
                pick_pool = minor

            if pick_pool:
                sel = random.choice(pick_pool)
                # Map movement types to requested phrasing
                spin_map = {
                    'off_spin': 'spinning in',
                    'leg_spin': 'spinning away',
                    'indrift': 'drift in',
                    'outdrift': 'drift out',
                    'straighter': 'straighter one'
                }
                pace_map = {
                    'inswing': 'swinging in',
                    'outswing': 'swinging away',
                    'seam': random.choice(['seaming in', 'seaming away']),
                    'off_cutter': 'off cutter',
                    'leg_cutter': 'leg cutter',
                    'straight': 'straight ball'
                }
                if bowler_type == 'spin':
                    movement_desc = f"with {spin_map.get(sel, get_movement_display_name(sel))}"
                else:
                    movement_desc = f"with {pace_map.get(sel, get_movement_display_name(sel))}"

        # Fallback movement if no player movements present
        if not movement_desc:
            if bowler_type == 'pace':
                fallback_moves = ['with swinging in', 'with swinging away', 'seaming in', 'seaming away', 'with leg cutter', 'with off cutter', 'with straight ball']
            else:
                fallback_moves = ['drift in', 'drift out', 'spinning in', 'spinning away', 'bowling the straighter one']
            movement_desc = random.choice(fallback_moves)

        # Shot description
        if runs == 0:
            batting_skill = getattr(self.striker, 'batting', 50)
            leave_bias = min(max((80 - batting_skill) / 100.0, 0), 0.6)  # better batters less play & miss
            options = [
                ('leaves outside off', 0.25 + leave_bias / 2),
                ('solid forward defense', 0.35),
                ('blocks late', 0.15),
                ('plays and misses', 0.25 - leave_bias / 2)
            ]
            shot_desc = random.choices([o[0] for o in options], weights=[o[1] for o in options], k=1)[0]
        elif runs == 1:
            shots = ['pushes for a single', 'nudges into the leg side', 'works to mid-wicket', 'taps to point']
            shot_desc = random.choice(shots)
        elif runs == 2:
            shots = ['places for two', 'runs hard for two', 'finds the gap', 'times it well']
            shot_desc = random.choice(shots)
        elif runs == 3:
            shots = ['excellent running for three', 'places in the gap', 'good timing, long chase for the fielder']
            shot_desc = random.choice(shots)
        elif runs == 4:
            shots = ['crashes it to the boundary', 'times it perfectly to the rope', 'finds the gap for four', 'beautiful placement beats the infield']
            shot_desc = random.choice(shots)
        else:
            shots = ['hits it out of the park', 'clears the boundary with ease', 'launches it for six', 'smashes it for a maximum']
            shot_desc = random.choice(shots)

        # Build detailed commentary
        detailed_commentary = f"{length_choice}, {line_choice}, {movement_desc} at {speed:.0f} kph. {shot_desc}"

        return detailed_commentary

    def get_shot_description(self, runs):
        """Legacy/simple shot description used by process_runs"""
        if runs == 0:
            return random.choice([
                "defends solidly",
                "plays and misses",
                "blocks carefully",
                "leaves the ball",
                "is beaten by the delivery"
            ])
        elif runs == 1:
            return random.choice([
                "pushes for single",
                "nudges into leg side",
                "works to mid-wicket",
                "taps to point"
            ])
        elif runs == 2:
            return random.choice([
                "places for two",
                "runs hard for two",
                "finds the gap",
                "times it well"
            ])
        elif runs == 3:
            return random.choice([
                "excellent running for three",
                "places in the gap",
                "good timing",
                "quick singles"
            ])
        elif runs == 4:
            return random.choice([
                "crashes it to boundary",
                "times it perfectly",
                "finds the rope",
                "beautiful placement"
            ])
        else:
            return random.choice([
                "hits it out of the park",
                "clears the boundary with ease",
                "launches it for six",
                "smashes it for a maximum",
                "sends it into the crowd"
            ])

    def calculate_outcome_probabilities(self, batting_skill, bowling_skill, batting_agg, bowling_agg, bowling_line, field_setting):
        """Calculate outcome probabilities"""
        # Use format-specific base probabilities
        if hasattr(self, 'match_format') and self.match_format == 'T20':
            # T20 base probabilities - increased boundaries and wickets by 10%
            base_probs = {'dot': 0.32, 'single': 0.28, 'double': 0.132, 'triple': 0.0165,
                   'four': 0.132, 'six': 0.088, 'wicket': 0.04554}  # +10% on four, six, wicket
        else:
            # ODI base probabilities - decreased wickets by 3%
            base_probs = {'dot': 0.43, 'single': 0.303, 'double': 0.12, 'triple': 0.02, 'four': 0.06, 'six': 0.04, 'wicket': 0.024}
        
        # Use Player objects consistently
        bowler_role = getattr(self.current_bowler, 'role', '').lower()
        bowler_kind = determine_bowler_type(bowler_role)
        is_pace_bowler = bowler_kind == 'pace'
        is_spin_bowler = not is_pace_bowler
        
        if is_pace_bowler:
            if self.pitch_pace_rating >= 7:
                base_probs['dot'] *= 1.2
                base_probs['wicket'] *= 1.2
                base_probs['four'] *= 0.8
                base_probs['six'] *= 0.7
            elif self.pitch_pace_rating <= 3:
                base_probs['dot'] *= 0.9
                base_probs['wicket'] *= 0.9
                base_probs['four'] *= 1.1
                base_probs['six'] *= 1.1
            # Bounce effect for pace bowlers (stronger)
            if self.pitch_bounce_rating >= 7:
                base_probs['dot'] *= 1.15
                base_probs['wicket'] *= 1.25
                base_probs['four'] *= 0.8
                base_probs['six'] *= 0.75
            elif self.pitch_bounce_rating <= 3:
                base_probs['dot'] *= 0.95
                base_probs['wicket'] *= 0.9
                base_probs['four'] *= 1.1
                base_probs['six'] *= 1.1
        else:
            if self.pitch_spin_rating >= 7:
                base_probs['dot'] *= 1.2
                base_probs['wicket'] *= 1.2
                base_probs['four'] *= 0.8
                base_probs['six'] *= 0.7
            elif self.pitch_spin_rating <= 3:
                base_probs['dot'] *= 0.9
                base_probs['wicket'] *= 0.75
                base_probs['four'] *= 1.1
                base_probs['six'] *= 1.1
            # Bounce effect for spin bowlers (milder)
            if self.pitch_bounce_rating >= 7:
                base_probs['dot'] *= 1.05
                base_probs['wicket'] *= 1.05
                base_probs['four'] *= 0.9
                base_probs['six'] *= 0.85
            elif self.pitch_bounce_rating <= 3:
                base_probs['dot'] *= 0.98
                base_probs['wicket'] *= 0.95
                base_probs['four'] *= 1.05
                base_probs['six'] *= 1.05
       
        for trait in getattr(self.striker, 'traits', []):
            trait_name = trait['name']
            trait_strength = trait.get('strength', 3)
            trait_effect = get_trait_effect(trait_name, trait_strength)
            current_over = self.total_overs
            is_powerplay = current_over <= 10
            is_middle_overs = 10 < current_over < 40
            is_death_overs = current_over >= 40
            
            if trait_name == 'POWER_OPENER' and is_powerplay:
                base_probs['four'] *= trait_effect
                base_probs['six'] *= trait_effect
                base_probs['dot'] /= trait_effect
            elif trait_name == 'CONSOLIDATOR' and is_middle_overs:
                base_probs['single'] *= trait_effect
                base_probs['double'] *= trait_effect
                base_probs['wicket'] /= trait_effect
            elif trait_name == 'SPIN_BASHER' and is_spin_bowler:
                base_probs['four'] *= trait_effect
                base_probs['six'] *= trait_effect
            elif trait_name == 'DEMOLISHER_OF_PACE' and is_pace_bowler and not is_powerplay:
                base_probs['four'] *= trait_effect
                base_probs['six'] *= trait_effect
            elif trait_name == 'FINISHER' and is_death_overs:
                base_probs['four'] *= trait_effect
                base_probs['six'] *= trait_effect
                base_probs['wicket'] /= trait_effect
            # --- T20-specific youth negative batting traits ---
            elif trait_name == 'T20_POWERPLAY_WASTER' and is_powerplay:
                neg = get_negative_trait_effect(trait_name, trait_strength)
                base_probs['dot'] *= (2.0 - neg)
                base_probs['single'] *= (2.0 - neg) * 0.5 + 0.5
                base_probs['four'] *= neg
                base_probs['six'] *= neg
            elif trait_name == 'T20_CANT_HIT_SIXES':
                neg = get_negative_trait_effect(trait_name, trait_strength)
                base_probs['six'] *= neg
                base_probs['four'] *= neg * 0.5 + 0.5
            elif trait_name == 'T20_DEATH_OVERS_CHOKER' and is_death_overs:
                neg = get_negative_trait_effect(trait_name, trait_strength)
                base_probs['four'] *= neg
                base_probs['six'] *= neg
                base_probs['dot'] *= (2.0 - neg)
                base_probs['wicket'] *= (2.0 - neg)
            elif trait_name == 'T20_DOT_BALL_MAGNET':
                neg = get_negative_trait_effect(trait_name, trait_strength)
                base_probs['dot'] *= (2.0 - neg)
                base_probs['single'] *= neg
                base_probs['four'] *= neg * 0.5 + 0.5
            elif trait_name == 'T20_RASH_SHOT_MERCHANT':
                neg = get_negative_trait_effect(trait_name, trait_strength)
                base_probs['wicket'] *= (2.0 - neg)
                base_probs['four'] *= 1.05
                base_probs['six'] *= 1.05
            # --- ODI-specific youth negative batting traits ---
            elif trait_name == 'ODI_MIDDLE_OVERS_STALLER' and not is_powerplay and not is_death_overs:
                neg = get_negative_trait_effect(trait_name, trait_strength)
                base_probs['dot'] *= (2.0 - neg)
                base_probs['single'] *= neg
                base_probs['four'] *= neg
            elif trait_name == 'ODI_SLOG_MISFIRE' and is_death_overs:
                neg = get_negative_trait_effect(trait_name, trait_strength)
                base_probs['wicket'] *= (2.0 - neg)
                base_probs['four'] *= neg
                base_probs['six'] *= neg
            elif trait_name == 'ODI_POOR_STRIKE_ROTATION':
                neg = get_negative_trait_effect(trait_name, trait_strength)
                base_probs['single'] *= neg
                base_probs['dot'] *= (2.0 - neg)
            elif trait_name == 'ODI_COLLAPSER' and self.current_wickets >= 3:
                neg = get_negative_trait_effect(trait_name, trait_strength)
                base_probs['wicket'] *= (2.0 - neg)
                base_probs['dot'] *= (2.0 - neg) * 0.5 + 0.5
            elif trait_name == 'ODI_CHASE_BOTTLER' and self.batting_second:
                neg = get_negative_trait_effect(trait_name, trait_strength)
                base_probs['wicket'] *= (2.0 - neg)
                base_probs['dot'] *= (2.0 - neg) * 0.5 + 0.5
                base_probs['four'] *= neg
        
        # Apply bowler's youth negative traits (T20 + ODI specific)
        for trait in getattr(self.current_bowler, 'traits', []):
            trait_name = trait['name']
            trait_strength = trait.get('strength', 3)
            current_over = self.total_overs
            if hasattr(self, 'match_format') and self.match_format == 'T20':
                bowl_death = current_over >= 16
            else:
                bowl_death = current_over >= 40
            
            # T20 bowling traits
            if trait_name == 'T20_DEATH_BOWLING_LIABILITY' and bowl_death:
                neg = get_negative_trait_effect(trait_name, trait_strength)
                base_probs['four'] *= (2.0 - neg)
                base_probs['six'] *= (2.0 - neg)
                base_probs['wicket'] *= neg
            elif trait_name == 'T20_POWERPLAY_LEAKER' and is_powerplay:
                neg = get_negative_trait_effect(trait_name, trait_strength)
                base_probs['four'] *= (2.0 - neg)
                base_probs['six'] *= (2.0 - neg) * 0.5 + 0.5
                base_probs['wicket'] *= neg
            elif trait_name == 'T20_NO_SLOWER_BALL':
                neg = get_negative_trait_effect(trait_name, trait_strength)
                base_probs['four'] *= (2.0 - neg)
                base_probs['six'] *= (2.0 - neg) * 0.5 + 0.5
                base_probs['wicket'] *= neg
            elif trait_name == 'T20_WIDE_MACHINE':
                neg = get_negative_trait_effect(trait_name, trait_strength)
                base_probs['dot'] *= neg
                base_probs['four'] *= (2.0 - neg) * 0.5 + 0.5
            elif trait_name == 'T20_PRESSURE_CRUMBLER':
                bowler_name = getattr(self.current_bowler, 'name', self.current_bowler['name'] if isinstance(self.current_bowler, dict) else 'Unknown')
                bowler_stats = self.match_stats.get(bowler_name, {}).get('bowling', {})
                bowler_runs = bowler_stats.get('runs', 0)
                bowler_balls = bowler_stats.get('balls', 0)
                if bowler_balls > 0 and bowler_runs / max(1, bowler_balls) > 1.5:
                    neg = get_negative_trait_effect(trait_name, trait_strength)
                    base_probs['four'] *= (2.0 - neg)
                    base_probs['six'] *= (2.0 - neg)
                    base_probs['wicket'] *= neg
            # ODI bowling traits
            elif trait_name == 'ODI_MIDDLE_OVERS_EXPENSIVE' and not is_powerplay and not bowl_death:
                neg = get_negative_trait_effect(trait_name, trait_strength)
                base_probs['four'] *= (2.0 - neg)
                base_probs['single'] *= (2.0 - neg) * 0.5 + 0.5
                base_probs['wicket'] *= neg
            elif trait_name == 'ODI_NO_WICKET_TAKER':
                neg = get_negative_trait_effect(trait_name, trait_strength)
                base_probs['wicket'] *= neg
                base_probs['dot'] *= (2.0 - neg) * 0.3 + 0.7
            elif trait_name == 'ODI_DEATH_OVERS_LEAKER' and bowl_death:
                neg = get_negative_trait_effect(trait_name, trait_strength)
                base_probs['four'] *= (2.0 - neg)
                base_probs['six'] *= (2.0 - neg)
                base_probs['wicket'] *= neg
            elif trait_name == 'ODI_FIRST_SPELL_ONLY':
                bowler_name = getattr(self.current_bowler, 'name', self.current_bowler['name'] if isinstance(self.current_bowler, dict) else 'Unknown')
                bowler_stats = self.match_stats.get(bowler_name, {}).get('bowling', {})
                bowler_balls = bowler_stats.get('balls', 0)
                if bowler_balls > 30:
                    neg = get_negative_trait_effect(trait_name, trait_strength)
                    base_probs['four'] *= (2.0 - neg)
                    base_probs['wicket'] *= neg
            elif trait_name == 'ODI_PARTNERSHIP_FEEDER':
                # Handle both Player objects and dictionary-style players for striker name
                striker_name = getattr(self.striker, 'name', self.striker['name'] if isinstance(self.striker, dict) else str(self.striker))
                batter_stats = self.match_stats.get(striker_name, {}).get('batting', {})
                if batter_stats.get('runs', 0) >= 30:
                    neg = get_negative_trait_effect(trait_name, trait_strength)
                    base_probs['four'] *= (2.0 - neg)
                    base_probs['six'] *= (2.0 - neg) * 0.5 + 0.5
                    base_probs['wicket'] *= neg
            
        skill_diff = (batting_skill - bowling_skill) / 100.0
        for outcome in base_probs:
            if outcome in ['four', 'six']:
                base_probs[outcome] *= (1 + skill_diff)
            elif outcome == 'wicket':
                base_probs[outcome] *= (1 - skill_diff)
        # Keep detailed simulator in sync with FastMatchSimulator:
        # increase T20/ODI wicket probability by 13% for batters with skill >= 40
        if hasattr(self, 'match_format') and self.match_format in ('T20', 'ODI') and batting_skill >= 40:
            base_probs['wicket'] *= 1.13
        
        # NOTE: To keep the detailed T20/ODI simulator in sync with FastMatchSimulator,
        # we disable the extra aggression/field/batting-tier tweaks below while preserving
        # the code for reference. The effective probability logic now mirrors the fast sim.
        if False:
            # Bonus for poor batsmen (< 45 batting) - increased 4s and 6s by 3%
            if batting_skill < 45:
                boundary_bonus = (45 - batting_skill) / 100  # 0.01 to 0.45 bonus
                base_probs['four'] *= (1.0 + boundary_bonus * 0.067)  # 3% increase max
                base_probs['six'] *= (1.0 + boundary_bonus * 0.067)   # 3% increase max
            
            if batting_agg > 0.5:
                base_probs['dot'] *= 0.8
                base_probs['single'] *= 0.9
                base_probs['four'] *= 1.2
                base_probs['six'] *= 1.3
                base_probs['wicket'] *= 1.2
            elif batting_agg < 0.5:
                base_probs['dot'] *= 1.2
                base_probs['single'] *= 1.1
                base_probs['four'] *= 0.8
                base_probs['six'] *= 0.7
                base_probs['wicket'] *= 0.8
            
            if bowling_line == 'Short':
                base_probs['six'] *= 1.2
                base_probs['wicket'] *= 1.1
            elif bowling_line == 'Full':
                base_probs['four'] *= 1.2
                base_probs['wicket'] *= 1.1
            
            if field_setting == 'Aggressive':
                base_probs['single'] *= 0.8
                base_probs['wicket'] *= 1.2
            elif field_setting == 'Defensive':
                base_probs['four'] *= 0.8
                base_probs['six'] *= 0.8
                base_probs['wicket'] *= 0.8
            
            # Batter skill tier adjustments (+3% wicket for good/elite/super elite)
            if batting_skill >= 80:
                # Elite batsmen (80+)
                base_probs['wicket'] *= 1.03
                base_probs['single'] *= 1.06
                base_probs['double'] *= 1.06
                base_probs['four'] *= 1.06
                base_probs['six'] *= 1.06
                base_probs['dot'] *= 0.94
                # Super elite batsmen (89+)
                if batting_skill >= 89:
                    base_probs['single'] *= 1.04
                    base_probs['double'] *= 1.04
                    base_probs['four'] *= 1.04
                    base_probs['six'] *= 1.04
                    base_probs['wicket'] *= 0.96
                    base_probs['dot'] *= 0.96
            elif batting_skill >= 60:
                # Good batters (60-79)
                base_probs['wicket'] *= 1.03
                base_probs['single'] *= 1.04
                base_probs['double'] *= 1.04
                base_probs['dot'] *= 0.96
            
            # T20 only: elite batters harder to dismiss, average batters easier to dismiss
            if hasattr(self, 'match_format') and self.match_format == 'T20':
                if batting_skill >= 75:
                    base_probs['wicket'] *= 0.72   # elite: reduce wicket chance
                elif batting_skill <= 50:
                    base_probs['wicket'] *= 1.28   # average: increase wicket chance
            
            # Revert T20 wicket changes while keeping code, and reduce 4s/6s for elite batters
            if hasattr(self, 'match_format') and self.match_format == 'T20':
                if batting_skill >= 75:
                    # Cancel previous wicket tweak for elite batters
                    base_probs['wicket'] /= 0.72
                    # New: slightly reduce 4s and 6s probability (3%) for elite batters
                    base_probs['four'] *= 0.97 * 0.97   # 3% + further 3% reduction for elite
                    base_probs['six'] *= 0.97 * 0.97
                elif batting_skill <= 50:
                    # Cancel previous wicket tweak for average batters
                    base_probs['wicket'] /= 1.28
        
        # Apply user simulation adjustments from settings (-100 to +100)
        if hasattr(self, 'simulation_adjustments') and self.simulation_adjustments:
            dot_adj = self.simulation_adjustments.get('dot_adj', 0) / 100.0
            boundary_adj = self.simulation_adjustments.get('boundary_adj', 0) / 100.0
            wicket_adj = self.simulation_adjustments.get('wicket_adj', 0) / 100.0
            
            base_probs['dot'] *= (1.0 + dot_adj)
            base_probs['four'] *= (1.0 + boundary_adj)
            base_probs['six'] *= (1.0 + boundary_adj)
            base_probs['wicket'] *= (1.0 + wicket_adj)
            
            # Ensure no negative probabilities
            for key in base_probs:
                base_probs[key] = max(0.001, base_probs[key])
        
        total = sum(base_probs.values())
        for outcome in base_probs:
            base_probs[outcome] /= total
        
        return base_probs

    def show_bowling_highlights(self, match_result):
        """Show 3D bowling highlights with ball tracking"""
        # Create HTML content with Three.js
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Bowling Highlights</title>
            <style>
                body { 
                    margin: 0; 
                    overflow: hidden; 
                    font-family: Arial, sans-serif;
                    background-color: #f0f0f0;
                }
                
                canvas { 
                    display: block; 
                }
                
                .controls {
                    position: absolute;
                    top: 20px;
                    left: 20px;
                    background: rgba(0,0,0,0.7);
                    color: white;
                    padding: 15px;
                    border-radius: 10px;
                    z-index: 100;
                    width: 250px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                }
                
                .controls h3 {
                    margin-top: 0;
                    margin-bottom: 10px;
                    color: #4CAF50;
                    border-bottom: 1px solid #555;
                    padding-bottom: 5px;
                }
                
                .bowler-select {
                    margin-bottom: 15px;
                    padding: 8px;
                    width: 100%;
                    border-radius: 5px;
                    background-color: #333;
                    color: white;
                    border: 1px solid #555;
                }
                
                button {
                    background: #4CAF50;
                    border: none;
                    color: white;
                    padding: 8px 12px;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 14px;
                    margin: 2px 5px 5px 0;
                    cursor: pointer;
                    border-radius: 5px;
                    transition: background-color 0.3s;
                }
                
                button:hover {
                    background-color: #2E8B57;
                }
                
                .controls > div {
                    margin-bottom: 15px;
                }
                
                .match-stats {
                    position: absolute;
                    top: 20px;
                    right: 20px;
                    background: rgba(0,0,0,0.7);
                    color: white;
                    padding: 15px;
                    border-radius: 10px;
                    z-index: 100;
                    width: 250px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                }
                
                .match-stats h3 {
                    margin-top: 0;
                    margin-bottom: 10px;
                    color: #2196F3;
                    border-bottom: 1px solid #555;
                    padding-bottom: 5px;
                }
                
                .score-display {
                    font-size: 18px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }
                
                .wickets-display {
                    font-size: 16px;
                    margin-bottom: 15px;
                }
                
                .delivery-info {
                    padding: 15px;
                    background: rgba(33, 150, 243, 0.1);
                    border-radius: 8px;
                    margin-top: 15px;
                    border-left: 3px solid #2196F3;
                    position: relative;
                    min-width: unset;
                    top: unset;
                    left: unset;
                }
                
                .delivery-info div {
                    margin-bottom: 8px;
                }
                
                .speed-meter {
                    margin-top: 10px;
                    font-size: 14px;
                }
                
                .help-text {
                    position: absolute;
                    bottom: 20px;
                    left: 20px;
                    background: rgba(0,0,0,0.7);
                    color: white;
                    padding: 10px 15px;
                    border-radius: 5px;
                    font-size: 12px;
                    max-width: 300px;
                }
                
                .runs-display {
                    display: inline-block;
                    width: 20px;
                    height: 20px;
                    line-height: 20px;
                    text-align: center;
                    margin-left: 10px;
                    padding: 2px 8px;
                    border-radius: 50%;
                    background-color: #4CAF50;  /* Default green */
                    color: white;
                    font-weight: bold;
                }
                .runs-display.runs-0 {  /* Dot ball */
                    background-color: #757575;  /* Gray */
                }
                .runs-display.runs-1 {  /* Single */
                    background-color: #4CAF50;  /* Green */
                }
                .runs-4 {
                    background-color: #2196F3;  /* Blue */
                }
                .runs-6 {
                    background-color: #9C27B0;  /* Purple */
                }
                .runs-wicket {
                    background-color: #F44336;
                }
            </style>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        </head>
        <body>
            <div class="controls">
                <h3>Simulation Controls</h3>
                <select id="bowlerSelect" class="bowler-select">
                    <!-- Will be populated dynamically -->
                </select>
                <div>
                    <button id="playButton">Play</button>
                    <button id="pauseButton">Pause</button>
                    <button id="resetButton">Reset</button>
                </div>
                <div>
                    <button id="viewAllButton">View All</button>
                    <button id="singleModeButton">Single Ball</button>
                </div>
                <div class="speed-meter">
                    Ball speed: <span id="currentSpeed">0</span> kph
                </div>
            </div>
            
            <div class="match-stats">
                <h3>Match Information</h3>
                <div class="score-display">Score: <span id="scoreDisplay">0/0</span></div>
                <div class="wickets-display">Overs: <span id="oversDisplay">0.0</span></div>
                
                <div class="delivery-info" id="deliveryInfo">
                    <div>Bowler: <span id="bowlerName">-</span></div>
                    <div>Type: <span id="deliveryType">-</span></div>
                    <div>Speed: <span id="deliverySpeed">-</span> kph</div>
                    <div>Movement: <span id="deliveryMovement">-</span></div>
                    <div>Result: <span id="deliveryResult">-</span> <span id="runsDisplay" class="runs-display">0</span></div>
                </div>
            </div>
            
            <div class="help-text">
                <div>Controls: Left click + drag to rotate | Right click + drag to pan | Scroll to zoom</div>
                <div>View All: Shows all deliveries by selected bowler</div>
                <div>Single Ball: Shows animated ball for each delivery</div>
            </div>
            
            <script>
                // Initialize Three.js scene
                const scene = new THREE.Scene();
                scene.background = new THREE.Color(0x87CEEB); // Sky blue background
                
                const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
                const renderer = new THREE.WebGLRenderer({ antialias: true });
                renderer.setSize(window.innerWidth, window.innerHeight);
                renderer.shadowMap.enabled = true;
                document.body.appendChild(renderer.domElement);
                
                // Add OrbitControls for better camera interaction
                const controls = new THREE.OrbitControls(camera, renderer.domElement);
                controls.enableDamping = true;
                controls.dampingFactor = 0.05;
                controls.screenSpacePanning = false;
                controls.minDistance = 5;
                controls.maxDistance = 50;
                
                // Create a cricket field
                function createCricketField() {
                    // Ground/Field
                    const fieldGeometry = new THREE.CircleGeometry(40, 64);
                    
                    // Create a grass-like texture for the field
                    const fieldCanvas = document.createElement('canvas');
                    const ctx = fieldCanvas.getContext('2d');
                    fieldCanvas.width = 512;
                    fieldCanvas.height = 512;
                    
                    // Base green color
                    ctx.fillStyle = '#2E8B57';
                    ctx.fillRect(0, 0, fieldCanvas.width, fieldCanvas.height);
                    
                    // Add texture variation to simulate grass
                    for (let i = 0; i < 5000; i++) {
                        const x = Math.random() * fieldCanvas.width;
                        const y = Math.random() * fieldCanvas.height;
                        const size = Math.random() * 3 + 1;
                        ctx.fillStyle = Math.random() > 0.5 ? '#1D7A46' : '#3C9A66';
                        ctx.fillRect(x, y, size, size);
                    }
                    
                    // Create pattern lines for the field (like mown grass)
                    for (let i = 0; i < fieldCanvas.width; i += 16) {
                        ctx.strokeStyle = 'rgba(29, 122, 70, 0.2)';
                        ctx.lineWidth = 8;
                        ctx.beginPath();
                        ctx.moveTo(i, 0);
                        ctx.lineTo(i, fieldCanvas.height);
                        ctx.stroke();
                    }
                    
                    const fieldTexture = new THREE.CanvasTexture(fieldCanvas);
                    fieldTexture.wrapS = THREE.RepeatWrapping;
                    fieldTexture.wrapT = THREE.RepeatWrapping;
                    fieldTexture.repeat.set(4, 4);
                    
                    const fieldMaterial = new THREE.MeshPhongMaterial({ 
                        map: fieldTexture,
                        side: THREE.DoubleSide
                    });
                    
                    const field = new THREE.Mesh(fieldGeometry, fieldMaterial);
                    field.rotation.x = -Math.PI / 2;
                    field.receiveShadow = true;
                    scene.add(field);
                    
                    // Create a realistic pitch texture
                    const pitchCanvas = document.createElement('canvas');
                    const pitchCtx = pitchCanvas.getContext('2d');
                    pitchCanvas.width = 512;
                    pitchCanvas.height = 512;
                    
                    // Base color - clay/dirt like cricket pitch
                    pitchCtx.fillStyle = '#D2B48C';
                    pitchCtx.fillRect(0, 0, pitchCanvas.width, pitchCanvas.height);
                    
                    // Add cracks and texture variation
                    for (let i = 0; i < 1000; i++) {
                        const x = Math.random() * pitchCanvas.width;
                        const y = Math.random() * pitchCanvas.height;
                        const size = Math.random() * 2 + 1;
                        pitchCtx.fillStyle = Math.random() > 0.5 ? '#C19A6B' : '#E5C29F';
                        pitchCtx.fillRect(x, y, size, size);
                    }
                    
                    // Add a worn/rough patch on one side of the pitch (for spin)
                    pitchCtx.fillStyle = 'rgba(193, 154, 107, 0.7)';
                    pitchCtx.beginPath();
                    pitchCtx.arc(pitchCanvas.width * 0.75, pitchCanvas.height * 0.6, 
                             pitchCanvas.width * 0.15, 0, Math.PI * 2);
                    pitchCtx.fill();
                    
                    // Add some dry cracks
                    for (let i = 0; i < 30; i++) {
                        const startX = Math.random() * pitchCanvas.width;
                        const startY = Math.random() * pitchCanvas.height;
                        const length = Math.random() * 20 + 5;
                        const angle = Math.random() * Math.PI;
                        
                        pitchCtx.strokeStyle = 'rgba(160, 120, 80, 0.5)';
                        pitchCtx.lineWidth = Math.random() * 1.5 + 0.5;
                        pitchCtx.beginPath();
                        pitchCtx.moveTo(startX, startY);
                        pitchCtx.lineTo(startX + Math.cos(angle) * length, 
                                     startY + Math.sin(angle) * length);
                        pitchCtx.stroke();
                    }
                    
                    const pitchTexture = new THREE.CanvasTexture(pitchCanvas);
                    pitchTexture.wrapS = THREE.RepeatWrapping;
                    pitchTexture.wrapT = THREE.RepeatWrapping;
                    pitchTexture.repeat.set(1, 2);
                    
                    const pitchGeometry = new THREE.PlaneGeometry(3, 20);
                    const pitchMaterial = new THREE.MeshPhongMaterial({ 
                        map: pitchTexture,
                        bumpMap: pitchTexture,
                        bumpScale: 0.05,
                        side: THREE.DoubleSide,
                        shininess: 5
                    });
                    const pitch = new THREE.Mesh(pitchGeometry, pitchMaterial);
                    pitch.rotation.x = -Math.PI / 2;
                    pitch.position.y = 0.01; // Slightly above the field to avoid z-fighting
                    pitch.receiveShadow = true;
                    scene.add(pitch);
                    
                    // Pitch markings
                    const createPitchMarking = (posZ) => {
                        const markingGeometry = new THREE.PlaneGeometry(2.5, 0.1);
                        const markingMaterial = new THREE.MeshBasicMaterial({ 
                            color: 0xFFFFFF, 
                            side: THREE.DoubleSide 
                        });
                        const marking = new THREE.Mesh(markingGeometry, markingMaterial);
                        marking.rotation.x = -Math.PI / 2;
                        marking.position.set(0, 0.02, posZ);
                        scene.add(marking);
                    };
                    
                    // Create crease markings
                    createPitchMarking(10);  // Batsman's crease
                    createPitchMarking(-10); // Bowler's crease
                    
                    // Add stumps
                    function createStumps(posZ) {
                        const stumpsGroup = new THREE.Group();
                        
                        // Three stumps
                        for (let i = -0.3; i <= 0.3; i += 0.3) {
                            const stumpGeometry = new THREE.CylinderGeometry(0.03, 0.03, 0.7, 8);
                            const stumpMaterial = new THREE.MeshPhongMaterial({ color: 0xF5F5DC });
                            const stump = new THREE.Mesh(stumpGeometry, stumpMaterial);
                            stump.position.set(i, 0.35, posZ);
                            stump.castShadow = true;
                            stumpsGroup.add(stump);
                        }
                        
                        // Bails
                        for (let i = -0.15; i <= 0.15; i += 0.3) {
                            const bailGeometry = new THREE.CylinderGeometry(0.01, 0.01, 0.3, 8);
                            bailGeometry.rotateZ(Math.PI / 2);
                            const bailMaterial = new THREE.MeshPhongMaterial({ color: 0xF5F5DC });
                            const bail = new THREE.Mesh(bailGeometry, bailMaterial);
                            bail.position.set(i, 0.71, posZ);
                            bail.castShadow = true;
                            stumpsGroup.add(bail);
                        }
                        
                        scene.add(stumpsGroup);
                    }
                    
                    createStumps(10);  // Batsman's end
                    createStumps(-10); // Bowler's end
                }
                
                // Initialize the field
                createCricketField();
                
                // Add lighting
                const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
                scene.add(ambientLight);
                
                const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
                directionalLight.position.set(20, 30, 0);
                directionalLight.castShadow = true;
                directionalLight.shadow.camera.left = -30;
                directionalLight.shadow.camera.right = 30;
                directionalLight.shadow.camera.top = 30;
                directionalLight.shadow.camera.bottom = -30;
                directionalLight.shadow.mapSize.width = 2048;
                directionalLight.shadow.mapSize.height = 2048;
                scene.add(directionalLight);
                
                // Add stadium-like lighting from four corners
                const createStadiumLight = (x, z) => {
                    const spotLight = new THREE.SpotLight(0xffffff, 0.4);
                    spotLight.position.set(x, 25, z);
                    spotLight.angle = Math.PI / 8;
                    spotLight.penumbra = 0.2;
                    spotLight.decay = 1.5;
                    spotLight.distance = 100;
                    spotLight.castShadow = true;
                    spotLight.shadow.bias = -0.0001;
                    spotLight.shadow.mapSize.width = 1024;
                    spotLight.shadow.mapSize.height = 1024;
                    scene.add(spotLight);
                    
                    // Target the pitch center
                    spotLight.target.position.set(0, 0, 0);
                    scene.add(spotLight.target);
                    
                    return spotLight;
                };
                
                // Create four stadium lights at the corners
                createStadiumLight(30, 30);
                createStadiumLight(-30, 30);
                createStadiumLight(30, -30);
                createStadiumLight(-30, -30);
                
                // Add subtle hemisphere light for better color balance
                const hemisphereLight = new THREE.HemisphereLight(0x0088ff, 0x00ff88, 0.3);
                scene.add(hemisphereLight);
                
                // Position camera
                camera.position.set(0, 20, 30);
                camera.lookAt(0, 0, 0);
                
                // Enable shadows on renderer
                renderer.shadowMap.enabled = true;
                renderer.shadowMap.type = THREE.PCFSoftShadowMap;
                
                // Add a simple skybox/environment
                const createSkybox = () => {
                    const skyGeometry = new THREE.SphereGeometry(80, 32, 32);
                    // Invert the geometry so that the texture is on the inside
                    skyGeometry.scale(-1, 1, 1);
                    
                    // Create sky gradient on canvas
                    const skyCanvas = document.createElement('canvas');
                    skyCanvas.width = 1024;
                    skyCanvas.height = 1024;
                    const skyCtx = skyCanvas.getContext('2d');
                    
                    // Create gradient
                    const gradient = skyCtx.createLinearGradient(0, 0, 0, skyCanvas.height);
                    gradient.addColorStop(0, '#1e90ff');  // Deep blue at top
                    gradient.addColorStop(0.5, '#87ceeb'); // Sky blue in middle
                    gradient.addColorStop(1, '#e0f7ff');  // Light at horizon
                    
                    skyCtx.fillStyle = gradient;
                    skyCtx.fillRect(0, 0, skyCanvas.width, skyCanvas.height);
                    
                    // Add some subtle clouds
                    for (let i = 0; i < 20; i++) {
                        const x = Math.random() * skyCanvas.width;
                        const y = skyCanvas.height * 0.5 + Math.random() * skyCanvas.height * 0.3;
                        const radius = Math.random() * 50 + 30;
                        
                        skyCtx.fillStyle = 'rgba(255, 255, 255, 0.5)';
                        skyCtx.beginPath();
                        skyCtx.arc(x, y, radius, 0, Math.PI * 2);
                        skyCtx.fill();
                    }
                    
                    const skyTexture = new THREE.CanvasTexture(skyCanvas);
                    const skyMaterial = new THREE.MeshBasicMaterial({ map: skyTexture });
                    const sky = new THREE.Mesh(skyGeometry, skyMaterial);
                    scene.add(sky);
                };
                
                createSkybox();
                
                // Animation and data variables
                let ballTrackingData = {};
                let bowlerDeliveries = [];
                let activeBall = null;
                let isPlaying = false;
                let singleBallMode = false;
                let currentDeliveryIndex = 0;
                let animationFrameId = null;
                let clock = new THREE.Clock();
                let trajectories = [];
                
                // Ball creation function
                function createBall(color = 0xCC0000) {
                    const ballGeometry = new THREE.SphereGeometry(0.07, 32, 32);
                    const ballMaterial = new THREE.MeshPhongMaterial({ 
                        color: color,
                        shininess: 100 
                    });
                    const ball = new THREE.Mesh(ballGeometry, ballMaterial);
                    ball.castShadow = true;
                    return ball;
                }
                
                // Create detailed ball trajectory
                function generateBallTrajectory(delivery) {
                    // This function creates trajectories for different bowling styles:
                    // - Off Spin: Moves from off stump to leg stump after pitching
                    // - Leg Spin: Moves from leg stump to off stump after pitching
                    // - Inswing: Starts outside off stump and swings in toward leg stump
                    // - Outswing: Starts at off stump and swings away to off side
                    // - Seam Up: Can move either way after pitching
                    
                    // Calculate points for ball path
                    const points = [];
                    const numPoints = 400; // Significantly increased for ultra-smooth curves
                    const releaseHeight = delivery.start.y;
                    const releaseZ = delivery.start.z;
                    const pitchZ = delivery.pitchPosition.z;
                    const endZ = delivery.end.z;
                    
                    // Movement factors for swing, seam, spin
                    const lateralMovement = delivery.movement.lateral;
                    const swingFactor = delivery.movement.swing;
                    const spinFactor = delivery.movement.spin;
                    
                    // Calculate time parameters
                    const totalTime = delivery.flightTime;
                    const timeToPitch = (pitchZ - releaseZ) / (endZ - releaseZ) * totalTime;
                    
                    // Pre-calculate full trajectory to allow smoothing
                    const rawPoints = [];
                    
                    for (let i = 0; i <= numPoints; i++) {
                        const t = i / numPoints;
                        const time = t * totalTime;
                        
                        let x = delivery.start.x;
                        let y = 0;
                        let z = 0;
                        
                        // Z-position (along pitch)
                        z = releaseZ + (endZ - releaseZ) * t;
                        
                        // Calculate if we're before or after pitching
                        const isPitched = z >= pitchZ;
                        const distanceFromPitch = Math.abs(z - pitchZ);
                        
                        // Add lateral movement (sideways movement)
                        if (!isPitched) {
                            // Pre-pitch swing movement (outswinger or inswinger)
                            const swingProgress = (z - releaseZ) / (pitchZ - releaseZ);
                            
                            // Get the bowling style
                            const bowlingStyle = delivery.bowlingStyle || '';
                            let initialOffset = 0;
                            
                            // Add special start position for swing deliveries
                            if (bowlingStyle === "Inswing") {
                                initialOffset = -0.5; // Start outside off
                            } else if (bowlingStyle === "Outswing") {
                                initialOffset = -0.1; // Start near off stump
                            }
                            
                            // Use smooth cubic curve for more natural swing
                            const smoothSwingProgress = Math.pow(swingProgress, 2) * (3 - 2 * swingProgress);
                            x = delivery.start.x + initialOffset + 
                                lateralMovement * swingFactor * smoothSwingProgress;
                        } else {
                            // Post-pitch seam/spin movement
                            const postPitchProgress = (z - pitchZ) / (endZ - pitchZ);
                            
                            if (spinFactor > 0.3) {
                                // For spin deliveries, use a smoothed cubic curve for turn
                                const turnRate = Math.pow(postPitchProgress, 0.7) * (1 - Math.pow(1 - postPitchProgress, 3));
                                x += -lateralMovement * (1 + spinFactor * turnRate * 2.0);
                            } else {
                                // For seam deliveries, use a smoothed sigmoid-like function
                                const initialSeamMovement = Math.min(1, postPitchProgress * 3);
                                const seam = initialSeamMovement * (1 - postPitchProgress * 0.5);
                                x += lateralMovement * (1 + seam * spinFactor * 1.8);
                            }
                        }
                        
                        // Y-position (height) with continuous curve
                        if (!isPitched) {
                            // Height before pitching - smooth projectile motion
                            const normalizedTime = time / timeToPitch;
                            y = releaseHeight * (1 - normalizedTime * 0.8);
                            y -= 4.9 * Math.pow(time, 2) * 0.7;
                        } else {
                            // After pitching - continuous rising curve
                            const bounceProgress = (z - pitchZ) / (endZ - pitchZ);
                            
                            // Calculate base trajectory parameters
                            let peakHeight = delivery.end.y * 1.1;
                            let peakPosition = 0.7;
                            let riseRate = 1.3;
                            
                            // Adjust parameters based on delivery type
                            if (delivery.type === "Yorker") {
                                peakHeight = delivery.bounceHeight * 1.5;
                                peakPosition = 0.3;
                                riseRate = 2.0;
                            } else if (delivery.type === "Full") {
                                peakHeight = delivery.end.y * 1.2;
                                peakPosition = 0.5;
                                riseRate = 1.5;
                            } else if (delivery.type === "Good Length") {
                                peakHeight = delivery.end.y * 1.1;
                                peakPosition = 0.7;
                                riseRate = 1.3;
                            } else if (delivery.type === "Back of Length" || delivery.type === "Short") {
                                peakHeight = delivery.end.y * 1.05;
                                peakPosition = 0.85;
                                riseRate = 1.2;
                            } else if (delivery.type === "Bouncer") {
                                peakHeight = delivery.end.y;
                                peakPosition = 1.0;
                                riseRate = 1.0;
                            }
                            
                            // Speed affects trajectory
                            const speedFactor = Math.min(1.8, Math.max(0.9, delivery.speed / 130));
                            peakHeight *= speedFactor;
                            
                            // Create continuous rising curve
                            if (bounceProgress <= peakPosition) {
                                const normalizedProgress = bounceProgress / peakPosition;
                                const easeOut = 1 - Math.pow(1 - normalizedProgress, riseRate);
                                y = peakHeight * easeOut;
                            } else {
                                if (delivery.type === "Yorker" || delivery.type === "Full") {
                                    const falloffProgress = (bounceProgress - peakPosition) / (1 - peakPosition);
                                    const descent = Math.pow(falloffProgress, 3) * 0.15;
                                    y = peakHeight * (1 - descent);
                                } else {
                                    const riseProgress = (bounceProgress - peakPosition) / (1 - peakPosition);
                                    const additionalRise = Math.pow(riseProgress, 2) * 0.05;
                                    y = peakHeight * (1 + additionalRise);
                                }
                            }
                            
                            // Ensure smooth transition to end height
                            if (bounceProgress > 0.95) {
                                const blendFactor = (bounceProgress - 0.95) / 0.05;
                                y = y * (1 - blendFactor) + delivery.end.y * blendFactor;
                            }
                            
                            // Add minimum height based on speed
                            const minHeight = 0.1 * speedFactor;
                            y = Math.max(y, minHeight);
                        }
                        
                        rawPoints.push({x, y: Math.max(y, 0.05), z});
                    }
                    
                    // Apply continuous smoothing throughout the trajectory
                    const smoothingWindow = 15; // Reduced for more natural movement
                    const pitchIndex = rawPoints.findIndex(p => p.z >= pitchZ);
                    
                    // Create final smoothed points with continuous blending
                    for (let i = 0; i < rawPoints.length; i++) {
                        let sampleRange = 5;
                        let weightFunction = (distance) => 1 / (distance + 1);
                        
                        // Apply weighted average smoothing
                        let smoothedPoint = {x: 0, y: 0, z: 0};
                        let totalWeight = 0;
                        
                        for (let j = Math.max(0, i - sampleRange); j <= Math.min(rawPoints.length - 1, i + sampleRange); j++) {
                            const distance = Math.abs(i - j);
                            const weight = weightFunction(distance);
                            
                            smoothedPoint.x += rawPoints[j].x * weight;
                            smoothedPoint.y += rawPoints[j].y * weight;
                            smoothedPoint.z += rawPoints[j].z * weight;
                            totalWeight += weight;
                        }
                        
                        // Normalize by weights
                        smoothedPoint.x /= totalWeight;
                        smoothedPoint.y /= totalWeight;
                        smoothedPoint.z /= totalWeight;
                        
                        points.push(new THREE.Vector3(smoothedPoint.x, smoothedPoint.y, smoothedPoint.z));
                    }
                    
                    return points;
                }
                
                // Create ball trajectory visualization
                function createTrajectoryPath(points, color) {
                    const curve = new THREE.CatmullRomCurve3(points);
                    const geometry = new THREE.TubeGeometry(curve, 100, 0.02, 8, false);
                    const material = new THREE.MeshBasicMaterial({ 
                        color: color,
                        transparent: true,
                        opacity: 0.6
                    });
                    
                    const trajectory = new THREE.Mesh(geometry, material);
                    return trajectory;
                }
                
                // Show delivery info
                function updateDeliveryInfo(delivery) {
                    document.getElementById('bowlerName').textContent = delivery.bowlerName;
                    document.getElementById('deliveryType').textContent = delivery.type;
                    document.getElementById('deliverySpeed').textContent = delivery.speed.toFixed(1);
                    
                    let movementText = '';
                    if (delivery.movement.swing > 0.5) {
                        movementText += delivery.movement.lateral > 0 ? 'Outswinger' : 'Inswinger';
                    } else if (delivery.movement.spin > 0.5) {
                        movementText += delivery.movement.lateral > 0 ? 'Off-spin' : 'Leg-spin';
                    } else if (Math.abs(delivery.movement.lateral) > 0.2) {
                        movementText += 'Seam movement';
                    } else {
                        movementText += 'Straight';
                    }
                    
                    document.getElementById('deliveryMovement').textContent = movementText;
                    document.getElementById('currentSpeed').textContent = delivery.speed.toFixed(1);
                    
                    // Update result display
                    const runsDisplay = document.getElementById('runsDisplay');
                    if (delivery.isWicket) {
                        document.getElementById('deliveryResult').textContent = 'WICKET!';
                        runsDisplay.textContent = 'W';
                        runsDisplay.className = 'runs-display runs-wicket';
                    } else {
                        const runs = delivery.runs;
                        document.getElementById('deliveryResult').textContent = runs === 0 ? 'Dot Ball' : 
                            runs === 1 ? 'Single' : 
                            runs === 2 ? 'Double' : 
                            runs === 3 ? 'Triple' : 
                            runs === 4 ? 'FOUR!' : 
                            'SIX!';
                        
                        runsDisplay.textContent = runs;
                        runsDisplay.className = 'runs-display' + 
                            (runs === 0 ? ' runs-0' : 
                             runs === 1 ? ' runs-1' : 
                             runs === 4 ? ' runs-4' : 
                             runs === 6 ? ' runs-6' : '');
                    }
                    
                    // Also update the match stats (if they exist)
                    const scoreDisplay = document.getElementById('scoreDisplay');
                    const oversDisplay = document.getElementById('oversDisplay');
                    
                    if (scoreDisplay && oversDisplay) {
                        // Update score
                        const currentScoreParts = scoreDisplay.textContent.split('/');
                        let score = parseInt(currentScoreParts[0]) || 0;
                        let wickets = parseInt(currentScoreParts[1]) || 0;
                        
                        // Update based on delivery
                        if (delivery.isWicket) {
                            wickets += 1;
                        } else {
                            score += delivery.runs;
                        }
                        
                        // Update overs
                        let overs = parseFloat(oversDisplay.textContent) || 0;
                        let oversWhole = Math.floor(overs);
                        let balls = Math.round((overs - oversWhole) * 10) + 1; // Add current ball
                        
                        if (balls >= 6) {
                            oversWhole += 1;
                            balls = 0;
                        }
                        
                        // Update displays
                        scoreDisplay.textContent = `${score}/${wickets}`;
                        oversDisplay.textContent = `${oversWhole}.${balls}`;
                    }
                }
                
                // Show all trajectories for a bowler
                function showAllTrajectories(bowlerName) {
                    // Clear existing trajectories
                    trajectories.forEach(t => scene.remove(t));
                    trajectories = [];
                    
                    const deliveries = ballTrackingData[bowlerName] || [];
                    bowlerDeliveries = deliveries;
                    
                    // Create and add all trajectories with different colors based on delivery type
                    deliveries.forEach(delivery => {
                        const points = generateBallTrajectory(delivery);
                        // Color based on speed
                        let color;
                        if (delivery.speed > 140) color = 0xFF0000; // Fast - red
                        else if (delivery.speed > 130) color = 0xFFFF00; // Medium - yellow
                        else if (delivery.speed > 120) color = 0x00FF00; // Medium-slow - green
                        else color = 0x0000FF; // Slow - blue
                        
                        const trajectory = createTrajectoryPath(points, color);
                        trajectories.push(trajectory);
                        scene.add(trajectory);
                    });
                    
                    // If there are deliveries, show info for the first one
                    if (deliveries.length > 0) {
                        updateDeliveryInfo(deliveries[0]);
                    }
                }
                
                // Animate single ball
                function animateSingleBall() {
                    if (!singleBallMode || bowlerDeliveries.length === 0) return;
                    
                    // Remove old ball if exists
                    if (activeBall) scene.remove(activeBall);
                    
                    // Create new ball
                    const delivery = bowlerDeliveries[currentDeliveryIndex];
                    const points = generateBallTrajectory(delivery);
                    
                    // Color based on speed
                    let color;
                    if (delivery.speed > 140) color = 0xFF0000; // Fast - red
                    else if (delivery.speed > 130) color = 0xFFFF00; // Medium - yellow
                    else if (delivery.speed > 120) color = 0x00FF00; // Medium-slow - green
                    else color = 0x0000FF; // Slow - blue
                    
                    activeBall = createBall(color);
                    scene.add(activeBall);
                    
                    // Update delivery info
                    updateDeliveryInfo(delivery);
                    
                    // Start animation
                    let progress = 0;
                    const curve = new THREE.CatmullRomCurve3(points);
                    
                    function animate() {
                        if (!isPlaying) {
                            animationFrameId = requestAnimationFrame(animate);
                            return;
                        }
                        
                        progress += 0.004 * (delivery.speed/100); // Speed affects animation speed - increased for faster playback
                        
                        if (progress >= 1) {
                            // Move to next delivery
                            progress = 0;
                            currentDeliveryIndex = (currentDeliveryIndex + 1) % bowlerDeliveries.length;
                            animateSingleBall();
                            return;
                        }
                        
                        // Update ball position
                        const point = curve.getPoint(progress);
                        activeBall.position.copy(point);
                        
                        animationFrameId = requestAnimationFrame(animate);
                    }
                    
                    // Cancel any existing animation
                    if (animationFrameId) cancelAnimationFrame(animationFrameId);
                    
                    // Start new animation
                    animationFrameId = requestAnimationFrame(animate);
                }
                
                // Switch to single ball mode
                function switchToSingleBallMode() {
                    singleBallMode = true;
                    
                    // Clear all trajectories
                    trajectories.forEach(t => scene.remove(t));
                    trajectories = [];
                    
                    // Set up ball animation
                    currentDeliveryIndex = 0;
                    animateSingleBall();
                }
                
                // Switch to all trajectories mode
                function switchToAllTrajectoriesMode() {
                    singleBallMode = false;
                    
                    // Remove active ball
                    if (activeBall) {
                        scene.remove(activeBall);
                        activeBall = null;
                    }
                    
                    // Show all trajectories for current bowler
                    const bowlerSelect = document.getElementById('bowlerSelect');
                    showAllTrajectories(bowlerSelect.value);
                }
                
                // Event listeners
                document.getElementById('bowlerSelect').addEventListener('change', function(e) {
                    const bowlerName = e.target.value;
                    if (singleBallMode) {
                        currentDeliveryIndex = 0;
                        bowlerDeliveries = ballTrackingData[bowlerName] || [];
                        animateSingleBall();
                    } else {
                        showAllTrajectories(bowlerName);
                    }
                });
                
                document.getElementById('playButton').addEventListener('click', function() {
                    isPlaying = true;
                });
                
                document.getElementById('pauseButton').addEventListener('click', function() {
                    isPlaying = false;
                });
                
                document.getElementById('resetButton').addEventListener('click', function() {
                    currentDeliveryIndex = 0;
                    if (singleBallMode) {
                        animateSingleBall();
                    }
                });
                
                document.getElementById('viewAllButton').addEventListener('click', switchToAllTrajectoriesMode);
                document.getElementById('singleModeButton').addEventListener('click', switchToSingleBallMode);
                
                // Initialize bowling data
                window.initializeBowlingData = function(data) {
                    console.log("Initializing bowling data");
                    ballTrackingData = JSON.parse(data);
                    const bowlerSelect = document.getElementById('bowlerSelect');
                    bowlerSelect.innerHTML = ''; // Clear existing options
                    
                    // Populate bowler select
                    Object.keys(ballTrackingData).forEach(bowler => {
                        const option = document.createElement('option');
                        option.value = bowler;
                        option.text = bowler;
                        bowlerSelect.appendChild(option);
                    });
                    
                    // If there are any bowlers, show the first one's data
                    if (Object.keys(ballTrackingData).length > 0) {
                        const firstBowler = Object.keys(ballTrackingData)[0];
                        bowlerDeliveries = ballTrackingData[firstBowler];
                        showAllTrajectories(firstBowler);
                    }
                };
                
                // Main animation loop
                function animate() {
                    requestAnimationFrame(animate);
                    controls.update();
                    renderer.render(scene, camera);
                }
                animate();
                
                // Handle window resize
                window.addEventListener('resize', onWindowResize, false);
                function onWindowResize() {
                    camera.aspect = window.innerWidth / window.innerHeight;
                    camera.updateProjectionMatrix();
                    renderer.setSize(window.innerWidth, window.innerHeight);
                }
                
                // Event listeners
                document.addEventListener('DOMContentLoaded', function() {
                    // Initialize match stats with mock data
                    document.getElementById('scoreDisplay').textContent = '25/1';
                    document.getElementById('oversDisplay').textContent = '3.2';
                    
                    // Populate bowler select
                    const bowlerSelect = document.getElementById('bowlerSelect');
                    ballTrackingData.deliveries.forEach(delivery => {
                        if (!bowlerDeliveries.some(d => d.bowlerName === delivery.bowlerName)) {
                            const option = document.createElement('option');
                            option.value = delivery.bowlerName;
                            option.textContent = delivery.bowlerName;
                            bowlerSelect.appendChild(option);
                        }
                    });
                
                    // Add remaining event listeners
                    // ... existing code ...
                });
            </script>
        </body>
        </html>
        """

        # Create a temporary HTML file
        import tempfile
        import os
        import json
        import webview
        import math
        
        # Prepare bowling data
        bowling_data = {}
        all_bowlers = []
        
        # Collect data from both innings
        for team in [self.team1, self.team2]:
            for player in team['players']:
                stats = match_result['match_stats'].get(player['name'], {}).get('bowling', {})
                if stats.get('balls', 0) > 0:
                    all_bowlers.append({
                        'name': player['name'],
                        'speeds': stats.get('speeds', []),
                        'role': player.get('role', ''),
                        'deliveries': []  # Will be populated with trajectory data
                    })

        # Generate realistic trajectory data for each delivery
        delivery_types = ["Good Length", "Yorker", "Bouncer", "Short", "Full Toss", "Back of Length"]
        
        for bowler in all_bowlers:
            deliveries = []
            is_spinner = 'spin' in bowler['role'].lower() if 'role' in bowler else False
            is_pace = any(term in bowler['role'].lower() for term in ['fast', 'medium', 'seam']) if 'role' in bowler else True
            
            # Generate varied deliveries for each ball bowled
            for i, speed in enumerate(bowler['speeds']):
                # Determine delivery type based on bowler type
                if is_spinner:
                    # Spinners tend to bowl more full and good length deliveries
                    delivery_type = random.choices(
                        ["Good Length", "Full Toss", "Full"], 
                        weights=[0.7, 0.15, 0.15], 
                        k=1
                    )[0]
                    
                    # Determine spin type - finger spinner (off) or wrist spinner (leg)
                    is_off_spinner = 'finger' in bowler['role'].lower() if 'role' in bowler else random.choice([True, False])
                    
                    # Set bowling style for spinners
                    if is_off_spinner:
                        bowling_style = "Off Spin"  # Turns from off to leg
                        # Off spinners generally move from off stump toward leg stump after pitching
                        # Positive lateral movement for right-arm off spin to right-hand batsman
                        lateral_movement = random.uniform(0.2, 0.5)
                    else:
                        bowling_style = "Leg Spin"  # Turns from leg to off
                        # Leg spinners generally move from leg stump toward off stump after pitching
                        # Negative lateral movement for right-arm leg spin to right-hand batsman
                        lateral_movement = random.uniform(-0.5, -0.2)
                    
                    # Spinners have high spin factor but low swing
                    spin_factor = random.uniform(0.7, 1.2)
                    swing_factor = random.uniform(0, 0.2)
                    
                    # Spinners have more bounce variation
                    bounce_height = random.uniform(0.2, 0.5)
                    
                else:
                    # Pace bowlers have a wider variety of deliveries
                    delivery_type = random.choices(
                        delivery_types, 
                        weights=[0.4, 0.15, 0.1, 0.15, 0.05, 0.15], 
                        k=1
                    )[0]
                    
                    # Determine bowling style for pace bowlers
                    pace_style_options = ["Inswing", "Outswing", "Off Cutter", "Leg Cutter", "Seam Up"]
                    bowling_style = random.choices(
                        pace_style_options,
                        weights=[0.25, 0.25, 0.15, 0.15, 0.2],
                        k=1
                    )[0]
                    
                    # Set lateral movement direction based on bowling style
                    if bowling_style == "Inswing":
                        # Inswing starts outside off and swings in toward leg stump
                        lateral_movement = random.uniform(0.2, 0.5)  # Positive for inswing
                        swing_factor = random.uniform(0.5, 0.9)
                        spin_factor = random.uniform(0, 0.1)
                    elif bowling_style == "Outswing":
                        # Outswing starts at off stump and swings away to off
                        lateral_movement = random.uniform(-0.5, -0.2)  # Negative for outswing
                        swing_factor = random.uniform(0.5, 0.9)
                        spin_factor = random.uniform(0, 0.1)
                    elif bowling_style == "Off Cutter":
                        # Off cutters behave like off spin after pitching
                        lateral_movement = random.uniform(0.2, 0.4)  # Off to leg
                        swing_factor = random.uniform(0.2, 0.4)
                        spin_factor = random.uniform(0.4, 0.6)  # Moderate spin
                    elif bowling_style == "Leg Cutter":
                        # Leg cutters behave like leg spin after pitching
                        lateral_movement = random.uniform(-0.4, -0.2)  # Leg to off
                        swing_factor = random.uniform(0.2, 0.4)
                        spin_factor = random.uniform(0.4, 0.6)  # Moderate spin
                    else:  # Seam Up
                        # Seam up can move either way after pitching
                        lateral_movement = random.uniform(-0.3, 0.3)  # Either direction
                        swing_factor = random.uniform(0.2, 0.5)
                        spin_factor = random.uniform(0.1, 0.3)
                    
                    # Bounce height depends on delivery type
                    if delivery_type == "Bouncer":
                        bounce_height = random.uniform(0.8, 1.2)
                    elif delivery_type == "Short":
                        bounce_height = random.uniform(0.6, 0.9)
                    elif delivery_type == "Good Length":
                        bounce_height = random.uniform(0.4, 0.6)
                    elif delivery_type == "Full":
                        bounce_height = random.uniform(0.2, 0.4)
                    elif delivery_type == "Yorker":
                        bounce_height = random.uniform(0.1, 0.2)
                    else:  # Full Toss
                        bounce_height = random.uniform(0, 0.1)
                
                # Calculate release height based on bowler speed and type
                release_height = 2.0  # Default
                if is_pace:
                    # Faster bowlers release from higher
                    release_height = 2.0 + (speed - 120) / 100
                else:
                    # Spinners generally release from slightly lower height
                    release_height = 1.8 + (speed - 80) / 100
                
                # Determine pitch position based on delivery type
                pitch_z = 0  # Default (middle of pitch)
                if delivery_type == "Good Length":
                    pitch_z = random.uniform(-2, 2)
                elif delivery_type == "Short" or delivery_type == "Bouncer":
                    pitch_z = random.uniform(-6, -2)
                elif delivery_type == "Full" or delivery_type == "Yorker":
                    pitch_z = random.uniform(2, 6)
                elif delivery_type == "Full Toss":
                    pitch_z = random.uniform(6, 9)  # Almost at the batsman
                else:  # Back of length
                    pitch_z = random.uniform(-4, 0)
                
                # Calculate end point height based on delivery type
                end_height = 0.9  # Default end height (above stump height)
                
                if delivery_type == "Yorker":
                    # Yorkers target the base of the stumps
                    end_height = random.uniform(0.1, 0.3)
                elif delivery_type == "Full":
                    # Full deliveries are low but may rise above stump height
                    end_height = random.uniform(0.3, 0.7)
                elif delivery_type == "Good Length":
                    # Good length deliveries typically bounce to chest height
                    end_height = random.uniform(1.0, 1.4)
                elif delivery_type == "Back of Length":
                    # Back of length bounces to chest/shoulder height
                    end_height = random.uniform(1.2, 1.6)
                elif delivery_type == "Short":
                    # Short deliveries bounce to head height
                    end_height = random.uniform(1.6, 1.9)
                elif delivery_type == "Bouncer":
                    # Bouncers can go above head height
                    end_height = random.uniform(1.8, 2.2)
                elif delivery_type == "Full Toss":
                    # Full tosses are above waist height without bouncing
                    end_height = random.uniform(0.9, 1.3)
                
                # Create delivery data
                delivery = {
                    'bowlerName': bowler['name'],
                    'type': delivery_type,
                    'bowlingStyle': bowling_style,  # Add bowling style for correct movement
                    'speed': speed,
                    'start': {
                        'x': random.uniform(-0.2, 0.2),  # Slight variation in release point
                        'y': release_height,
                        'z': -10  # Bowler's end
                    },
                    'pitchPosition': {
                        'x': (random.uniform(-0.3, 0.8) if random.random() < 0.8 else random.uniform(-0.2, 0.2)),  # 80% outside off stump, 20% on stumps
                        'y': 0,  # Ground level
                        'z': pitch_z
                    },
                    'end': {
                        'x': random.uniform(-0.3, 0.3),  # Where it reaches batsman
                        'y': end_height,  # Height determined by delivery type
                        'z': 10  # Batsman's end
                    },
                    'bounceHeight': bounce_height,
                    'flightTime': 20 / speed,  # Approximate flight time based on speed
                    'movement': {
                        'lateral': lateral_movement,
                        'swing': swing_factor,
                        'spin': spin_factor
                    },
                    'color': 0xff0000 if speed > 140 else 0x00ff00 if speed > 130 else 0x0000ff
                }
                
                deliveries.append(delivery)
            
            bowling_data[bowler['name']] = deliveries

        # Convert bowling data to JSON for JavaScript
        bowling_data_json = json.dumps(bowling_data)

        # Create a temporary HTML file
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html', encoding='utf-8') as f:
            f.write(html_content)
            html_path = f.name

        # Create the webview window with JavaScript API
        window = webview.create_window('Bowling Highlights', html=html_content, js_api=True, width=1200, height=800)
        
        # Define a function to initialize the data after the window loads
        def on_loaded():
            window.evaluate_js(f'initializeBowlingData(`{bowling_data_json}`)')
        
        # Start the webview with the on_loaded callback
        webview.start(func=on_loaded)

    def add_match_start_commentary(self):
        """Add initial match commentary"""
        self.add_commentary(f"\nMatch between {self.team1['name']} and {self.team2['name']} begins!")
        self.add_commentary(f"{self.team1['name']} will bat first against {self.team2['name']}")
        self.add_commentary(f"Pitch Report: {self.get_pitch_description()}")
        self.add_commentary(f"\nOpening batsmen for {self.team1['name']}: {self.striker['name']} and {self.non_striker['name']}")
        self.add_commentary(f"\nOpening bowler for {self.team2['name']}: {self.current_bowler['name']}")

    def initialize_bowler_data(self, bowler_name):
        """Initialize or update bowler data for a given bowler"""
        if bowler_name not in self.bowler_data:
            self.bowler_data[bowler_name] = {
                'overs_bowled': 0,
                'current_spell': 0,
                'spell_length': random.randint(4, 6),  # Initialize spell_length directly
                'can_bowl_after': None,
                'spells': 0
            }
            print(f"Initialized bowler data for {bowler_name} with spell_length {self.bowler_data[bowler_name]['spell_length']}")
        elif 'spell_length' not in self.bowler_data[bowler_name] or self.bowler_data[bowler_name]['spell_length'] is None:
            self.bowler_data[bowler_name]['spell_length'] = random.randint(4, 6)
            print(f"Set spell_length for {bowler_name} in initialize_bowler_data to {self.bowler_data[bowler_name]['spell_length']}")