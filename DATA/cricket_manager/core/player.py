"""
Player class with multi-format statistics support
Supports T20, ODI, and Test cricket formats
"""
import copy


def _fresh_career_stats():
    """Return a fresh career stats structure for senior career (after U21 promotion)."""
    return {
        'T20': {'matches': 0, 'runs': 0, 'balls_faced': 0, 'wickets': 0, 'balls_bowled': 0, 'runs_conceded': 0,
                'batting_average': 0.0, 'bowling_average': 0.0, 'strike_rate': 0.0, 'economy_rate': 0.0,
                'centuries': 0, 'fifties': 0, 'five_wickets': 0, 'highest_score': 0},
        'ODI': {'matches': 0, 'runs': 0, 'balls_faced': 0, 'wickets': 0, 'balls_bowled': 0, 'runs_conceded': 0,
                'batting_average': 0.0, 'bowling_average': 0.0, 'strike_rate': 0.0, 'economy_rate': 0.0,
                'centuries': 0, 'fifties': 0, 'five_wickets': 0, 'highest_score': 0},
        'Test': {'matches': 0, 'innings': 0, 'dismissals': 0, 'runs': 0, 'balls_faced': 0, 'wickets': 0,
                 'balls_bowled': 0, 'runs_conceded': 0, 'batting_average': 0.0, 'bowling_average': 0.0,
                 'strike_rate': 0.0, 'economy_rate': 0.0, 'centuries': 0, 'fifties': 0, 'five_wickets': 0,
                 'ten_wickets': 0, 'highest_score': 0}
    }


class Player:
    """Represents a cricket player with multi-format statistics"""
    
    def __init__(self, name, age, role, nationality):
        # Basic Info
        self.name = name
        self.age = age
        self.role = role  # Detailed roles like 'Opening Batter', 'Fast Bowler', 'Batting Allrounder (Fast Medium)', etc.
        self.nationality = nationality
        
        # Skills (0-100)
        self.batting = 0
        self.bowling = 0
        self.fielding = 0
        self.form = 50  # Current form (0-100)
        
        # Bowling Movement System (dynamic based on skill and role)
        self.bowling_movements = {}  # Dictionary of movement types with ratings and categories
        
        # Attributes
        self.fitness = 100
        self.confidence = 50
        self.potential = 0  # For youth players
        
        # Traits
        self.traits = []  # List of trait names
        
        # FORMAT-SPECIFIC CAREER STATISTICS (T20, ODI, Test)
        self.stats = {
            'T20': {
                'matches': 0,
                'runs': 0,
                'balls_faced': 0,
                'wickets': 0,
                'balls_bowled': 0,
                'runs_conceded': 0,
                'batting_average': 0.0,
                'bowling_average': 0.0,
                'strike_rate': 0.0,
                'economy_rate': 0.0,
                'centuries': 0,
                'fifties': 0,
                'five_wickets': 0,
                'highest_score': 0
            },
            'ODI': {
                'matches': 0,
                'runs': 0,
                'balls_faced': 0,
                'wickets': 0,
                'balls_bowled': 0,
                'runs_conceded': 0,
                'batting_average': 0.0,
                'bowling_average': 0.0,
                'strike_rate': 0.0,
                'economy_rate': 0.0,
                'centuries': 0,
                'fifties': 0,
                'five_wickets': 0,
                'highest_score': 0
            },
            'Test': {
                'matches': 0,
                'innings': 0,
                'dismissals': 0,  # Track dismissals for batting average
                'runs': 0,
                'balls_faced': 0,
                'wickets': 0,
                'balls_bowled': 0,
                'runs_conceded': 0,
                'batting_average': 0.0,
                'bowling_average': 0.0,
                'strike_rate': 0.0,
                'economy_rate': 0.0,
                'centuries': 0,
                'fifties': 0,
                'five_wickets': 0,
                'ten_wickets': 0,  # Test-specific
                'highest_score': 0
            }
        }
        
        # INTERNATIONAL-ONLY CAREER STATISTICS (subset of matches)
        # Rule: International matches also count towards domestic totals (self.stats),
        # but domestic matches do NOT count towards international totals.
        self.international_stats = _fresh_career_stats()
        # Senior caps for associate nations (Test tier ≠ 1); separate from full-member international_stats.
        self.associate_international_stats = _fresh_career_stats()
        # Youth international only (Pakistan U21 vs India U21, etc.) — not senior caps.
        self.u21_international_stats = _fresh_career_stats()
        self.u21_international_yearly_stats = {}
        
        # FORMAT-SPECIFIC SEASON STATISTICS
        self.season_stats = {
            'T20': {'runs': 0, 'wickets': 0, 'matches': 0, 'balls_faced': 0, 'balls_bowled': 0, 
                    'runs_conceded': 0, 'centuries': 0, 'fifties': 0, 'five_wickets': 0, 'highest_score': 0},
            'ODI': {'runs': 0, 'wickets': 0, 'matches': 0, 'balls_faced': 0, 'balls_bowled': 0,
                    'runs_conceded': 0, 'centuries': 0, 'fifties': 0, 'five_wickets': 0, 'highest_score': 0},
            'Test': {'runs': 0, 'wickets': 0, 'matches': 0, 'balls_faced': 0, 'balls_bowled': 0,
                     'runs_conceded': 0, 'centuries': 0, 'fifties': 0, 'five_wickets': 0, 'highest_score': 0}
        }
        
        # Pace speed attributes (for bowlers)
        self.avg_pace = 0.0  # Average bowling speed in kph
        self.top_pace = 0.0  # Top bowling speed in kph
        self.speed_potential = 0.0  # Potential for speed development
        
        # Speed tracking (for bowlers)
        self.speed_records = {
            'T20': [],  # List of speeds in each match
            'ODI': [],
            'Test': []
        }
        
        # Special flags
        self.is_youth_player = False
        self.is_injured = False
        self.injury_duration = 0  # Matches remaining until fit
        
        # Squad roles (captain, vice-captain, senior, young_gun) for morale/mentor
        self.squad_role = None  # 'captain' | 'vice_captain' | 'senior' | 'young_gun' | None
        # Last 5 innings form (runs when batted, wickets when bowled) for display and sim
        self.last_5_batting = []   # List of runs in last 5 batting innings (max 5)
        self.last_5_bowling = []   # List of wickets in last 5 bowling innings (max 5)
        # Morale 0-100 (affected by results, role, team performance)
        self.morale = 50
        
        # PHASE 14: Season-by-season history tracking (last 20 seasons)
        self.season_history = {
            'T20': [],  # List of season stat dictionaries
            'ODI': [],
            'Test': []
        }
        
        # Yearly stats keyed by year (like gamer 2024.py season_stats)
        # Structure: {year: {format: {runs, wickets, matches, ...}}}
        self.yearly_stats = {}
        # INTERNATIONAL-ONLY yearly stats keyed by year
        self.international_yearly_stats = {}
        self.associate_international_yearly_stats = {}
        
        # Domestic-only career stats (club / domestic league matches only)
        self.domestic_stats = _fresh_career_stats()
        self.domestic_yearly_stats = {}
        # Display: two club affiliations for international-list players (T20 vs ODI+FC)
        self.domestic_t20_club_name = ""
        self.domestic_odi_fc_club_name = ""
        # Optional third: overseas T20 franchise (top ~7–8 senior national players only)
        self.foreign_t20_club_name = ""
        
        # Career milestones
        self.milestones = []  # List of milestone dictionaries
        
        # U21 career snapshot (set when promoted to senior; senior stats then start fresh)
        self.u21_career_stats = None   # Copy of stats at promotion; never updated after
        self.u21_yearly_stats = None   # Copy of yearly_stats at promotion
        
        # Skill progression history
        self.skill_history = []  # List of {season, batting, bowling, fielding}
        # Season number when automatic end-of-year skill development last ran (U21 develop OR senior progression)
        self._annual_skill_development_season = None
        
        # Trait history
        self.trait_history = []  # List of {season, action, trait_name}
        # After returning from an associate nation to the national team: hide intl rank chips until next senior cap.
        self.clear_intl_rank_until_next_match = False
    
    def snapshot_u21_and_reset_senior_career(self):
        """Call when promoting from U21 to senior: save current stats as U21 career (frozen), reset stats for fresh senior career."""
        if getattr(self, 'u21_career_stats', None) is not None:
            return  # Already snapshotted
        # Frozen "U21 stats" = youth international numbers only (View U21 stats / promotion).
        u21_src = getattr(self, 'u21_international_stats', None)
        if u21_src and any(
            u21_src.get(fmt, {}).get('matches', 0) > 0 for fmt in ('T20', 'ODI', 'Test')
        ):
            self.u21_career_stats = copy.deepcopy(u21_src)
        else:
            self.u21_career_stats = copy.deepcopy(self.stats)
        self.u21_yearly_stats = copy.deepcopy(getattr(self, 'u21_international_yearly_stats', None) or {})
        self.stats = _fresh_career_stats()
        self.yearly_stats = {}
        self.international_stats = _fresh_career_stats()
        self.international_yearly_stats = {}
        self.associate_international_stats = _fresh_career_stats()
        self.associate_international_yearly_stats = {}
        self.u21_international_stats = _fresh_career_stats()
        self.u21_international_yearly_stats = {}
        self.domestic_stats = _fresh_career_stats()
        self.domestic_yearly_stats = {}
    
    def _apply_split_career_match(self, root, match_format, batting_stats, bowling_stats):
        """Accumulate one match into international_stats or domestic_stats bucket."""
        if not root or match_format not in root:
            return
        runs = batting_stats.get('runs', 0)
        balls = batting_stats.get('balls', 0)
        wickets = bowling_stats.get('wickets', 0)
        balls_bowled = bowling_stats.get('balls', 0)
        runs_conceded = bowling_stats.get('runs', 0)
        s = root[match_format]
        s['runs'] += runs
        s['balls_faced'] += balls
        if runs > s.get('highest_score', 0):
            s['highest_score'] = runs
        if runs >= 100:
            s['centuries'] += 1
        elif runs >= 50:
            s['fifties'] += 1
        s['wickets'] += wickets
        s['balls_bowled'] += balls_bowled
        s['runs_conceded'] += runs_conceded
        if wickets >= 5:
            s['five_wickets'] += 1
        if match_format == 'Test' and wickets >= 10:
            s['ten_wickets'] = s.get('ten_wickets', 0) + 1
        s['matches'] += 1
        if match_format == 'Test':
            s['innings'] = s.get('innings', 0) + 1
            extra_d = batting_stats.get('dismissals', 0) or 0
            if extra_d:
                s['dismissals'] = s.get('dismissals', 0) + int(extra_d)
        self._recalculate_averages_for_stats_dict(s, match_format)
    
    def update_stats_from_match(
        self,
        match_format,
        batting_stats,
        bowling_stats,
        season_number=None,
        count_as_international=True,
        count_as_u21_international=False,
        u21_only_pipeline=False,
        count_as_associate_international=False,
    ):
        """Update player statistics for specific format.
        
        Args:
            match_format: 'T20', 'ODI', 'Test'
            batting_stats: dict
            bowling_stats: dict
            season_number: optional season number (for milestones)
            count_as_international: when True, updates full-member senior international-only career stats.
            count_as_associate_international: when True, updates associate-nation senior international stats (mutually exclusive with count_as_international for split buckets).
            count_as_u21_international: when True, updates U21 youth international stats (not senior caps).
            u21_only_pipeline: when True with U21 intl, only u21_international_stats are updated (no combined totals).
        """
        if u21_only_pipeline and count_as_u21_international and getattr(self, 'u21_international_stats', None):
            self._apply_split_career_match(self.u21_international_stats, match_format, batting_stats, bowling_stats)
            if match_format in self.u21_international_stats:
                self._recalculate_averages_for_stats_dict(self.u21_international_stats[match_format], match_format)
            return
        
        format_stats = self.stats[match_format]
        
        # Update batting stats
        runs = batting_stats.get('runs', 0)
        balls = batting_stats.get('balls', 0)
        
        format_stats['runs'] += runs
        format_stats['balls_faced'] += balls
        
        # Update highest score
        if runs > format_stats['highest_score']:
            format_stats['highest_score'] = runs
            # PHASE 14: Record milestone
            if season_number and runs > 0:
                self.add_milestone(
                    season_number,
                    'highest_score',
                    f"New highest score: {runs} in {match_format}",
                    match_format
                )
        
        # Check for milestones
        if runs >= 100:
            format_stats['centuries'] += 1
            # PHASE 14: Record century milestone
            if season_number:
                self.add_milestone(
                    season_number,
                    'century',
                    f"Scored century ({runs}) in {match_format}",
                    match_format
                )
        elif runs >= 50:
            format_stats['fifties'] += 1
            # PHASE 14: Record fifty milestone (only first few)
            if season_number and format_stats['fifties'] <= 5:
                self.add_milestone(
                    season_number,
                    'fifty',
                    f"Scored fifty ({runs}) in {match_format}",
                    match_format
                )
        
        # Update bowling stats
        wickets = bowling_stats.get('wickets', 0)
        balls_bowled = bowling_stats.get('balls', 0)
        runs_conceded = bowling_stats.get('runs', 0)
        
        format_stats['wickets'] += wickets
        format_stats['balls_bowled'] += balls_bowled
        format_stats['runs_conceded'] += runs_conceded
        
        # Check for bowling milestones
        if wickets >= 5:
            format_stats['five_wickets'] += 1
            # PHASE 14: Record 5-wicket haul milestone
            if season_number:
                self.add_milestone(
                    season_number,
                    'five_wickets',
                    f"Took 5-wicket haul ({wickets} wickets) in {match_format}",
                    match_format
                )
        
        if match_format == 'Test' and wickets >= 10:
            format_stats['ten_wickets'] += 1
            # PHASE 14: Record 10-wicket haul milestone
            if season_number:
                self.add_milestone(
                    season_number,
                    'ten_wickets',
                    f"Took 10-wicket haul ({wickets} wickets) in Test match",
                    match_format
                )
        
        # Update speed records
        if 'speeds' in bowling_stats and bowling_stats['speeds']:
            self.speed_records[match_format].extend(bowling_stats['speeds'])
        
        # Update matches
        format_stats['matches'] += 1
        if match_format == 'Test':
            format_stats['innings'] += 1  # Simplified: 1 innings per match
            extra_d = batting_stats.get('dismissals', 0) or 0
            if extra_d:
                format_stats['dismissals'] = format_stats.get('dismissals', 0) + int(extra_d)
        
        # PHASE 14: Record debut milestone
        if season_number and format_stats['matches'] == 1:
            self.add_milestone(
                season_number,
                'debut',
                f"Made debut in {match_format}",
                match_format
            )
        
        # Recalculate averages
        self.recalculate_averages(match_format)
        
        if count_as_u21_international and getattr(self, 'u21_international_stats', None):
            self._apply_split_career_match(self.u21_international_stats, match_format, batting_stats, bowling_stats)
        elif count_as_associate_international and getattr(self, 'associate_international_stats', None):
            self._apply_split_career_match(self.associate_international_stats, match_format, batting_stats, bowling_stats)
        elif count_as_international and hasattr(self, 'international_stats'):
            self._apply_split_career_match(self.international_stats, match_format, batting_stats, bowling_stats)
        elif (
            not count_as_international
            and not count_as_u21_international
            and hasattr(self, 'domestic_stats')
        ):
            self._apply_split_career_match(self.domestic_stats, match_format, batting_stats, bowling_stats)
    
    def recalculate_averages(self, match_format):
        """Recalculate averages for specific format"""
        
        stats = self.stats[match_format]
        
        # Batting average: Test = runs per dismissal (2 innings per match); T20/ODI = runs per match
        if match_format == 'Test':
            dismissals = stats.get('dismissals', 0)
            if dismissals > 0:
                stats['batting_average'] = round(stats['runs'] / dismissals, 2)
            else:
                stats['batting_average'] = 0.0
        elif stats['matches'] > 0:
            stats['batting_average'] = round(stats['runs'] / stats['matches'], 2)
        
        # Bowling average (runs conceded per wicket)
        if stats['wickets'] > 0:
            stats['bowling_average'] = round(stats['runs_conceded'] / stats['wickets'], 2)
        else:
            stats['bowling_average'] = 0.0
        
        # Strike rate (runs per 100 balls)
        if stats['balls_faced'] > 0:
            stats['strike_rate'] = round((stats['runs'] / stats['balls_faced']) * 100, 2)
        else:
            stats['strike_rate'] = 0.0
        
        # Economy rate (runs per over)
        if stats['balls_bowled'] > 0:
            overs = stats['balls_bowled'] / 6
            stats['economy_rate'] = round(stats['runs_conceded'] / overs, 2)
        else:
            stats['economy_rate'] = 0.0

    def _recalculate_averages_for_stats_dict(self, stats, match_format):
        """Recalculate averages for a provided stats dict (used for international-only stats)."""
        if match_format == 'Test':
            dismissals = stats.get('dismissals', 0)
            stats['batting_average'] = round(stats['runs'] / dismissals, 2) if dismissals > 0 else 0.0
        elif stats.get('matches', 0) > 0:
            stats['batting_average'] = round(stats['runs'] / stats['matches'], 2)
        if stats.get('wickets', 0) > 0:
            stats['bowling_average'] = round(stats['runs_conceded'] / stats['wickets'], 2)
        else:
            stats['bowling_average'] = 0.0
        if stats.get('balls_faced', 0) > 0:
            stats['strike_rate'] = round((stats['runs'] / stats['balls_faced']) * 100, 2)
        else:
            stats['strike_rate'] = 0.0
        if stats.get('balls_bowled', 0) > 0:
            overs = stats['balls_bowled'] / 6
            stats['economy_rate'] = round(stats['runs_conceded'] / overs, 2)
        else:
            stats['economy_rate'] = 0.0
    
    def get_average_speed(self, match_format):
        """Get average bowling speed for format"""
        speeds = self.speed_records.get(match_format, [])
        if speeds:
            return round(sum(speeds) / len(speeds), 2)
        return 0.0
    
    def get_top_speed(self, match_format):
        """Get top bowling speed for format"""
        speeds = self.speed_records.get(match_format, [])
        if speeds:
            return max(speeds)
        return 0.0
    
    def age_player(self, team_tier=3):
        """Age player by one year with gamer 2024 style skill development"""
        import random
        
        self.age += 1
        
        # Skill development based on age (matching gamer 2024.py line 7396)
        if self.age < 24:  # Young players improve more
            batting_change = random.randint(-3, 4)
            bowling_change = random.randint(-3, 4)
            fielding_change = random.randint(-3, 5)
        elif self.age < 31:  # Prime years
            batting_change = random.randint(-2, 3)
            bowling_change = random.randint(-2, 3)
            fielding_change = random.randint(-1, 1)
        else:  # Decline phase
            batting_change = random.randint(-6, 1)
            bowling_change = random.randint(-6, 1)
            fielding_change = random.randint(-5, 0)
        
        # Apply changes with 1-100 limits (gamer 2024 style)
        self.batting = max(1, min(100, self.batting + batting_change))
        self.bowling = max(1, min(100, self.bowling + bowling_change))
        self.fielding = max(1, min(100, self.fielding + fielding_change))
        
        # Update pace speeds based on age progression
        from cricket_manager.systems.pace_speed_system import update_pace_speeds_for_season
        update_pace_speeds_for_season(self, season_increment=True)

        # Gradual veteran decline (was in GameEngine.age_all_players; keep once per yearly age_player)
        if self.age >= 34:
            decline_so_far = getattr(self, "_age_decline", 0)
            if decline_so_far < 5:
                self._age_decline = decline_so_far + 1
                self.batting = max(1, getattr(self, "batting", 50) - 1)
                self.bowling = max(1, getattr(self, "bowling", 50) - 1)
    
    def improve_skills(self, team_tier=3):
        """Improve player skills with TIER-BASED CAPS
        
        Gamer 2024 Style - Maximum skills depend on team tier:
        - Tier 1: Max 95 (world class)
        - Tier 2: Max 80 (strong associates)
        - Tier 3: Max 70 (associates)
        - Tier 4: Max 60 (emerging)
        - Tier 5: Max 70 (U21 of test nations)
        """
        import random
        
        # Tier-based maximum skill caps
        tier_max_skills = {
            1: 99,  # Test nations - NO CAP, can reach elite 99
            2: 99,  # Strong associates - NO CAP, can reach elite 99
            3: 70,  # Associates
            4: 60,  # Emerging nations
            5: 70   # U21 of test nations (can reach same level as associates)
        }
        max_skill = tier_max_skills.get(team_tier, 70)
        
        if random.random() < 0.5:  # 50% chance to improve (reduced from 60%)
            improvement = random.randint(1, 2)  # Reduced from 1-3
            self.batting = min(max_skill, self.batting + improvement)
            self.bowling = min(max_skill, self.bowling + improvement)
            self.fielding = min(max_skill, self.fielding + improvement)
    
    def decline_skills(self):
        """Decline player skills"""
        import random
        if random.random() < 0.3:
            self.batting = max(30, self.batting - random.randint(1, 2))
            self.bowling = max(30, self.bowling - random.randint(1, 2))
            self.fielding = max(30, self.fielding - random.randint(1, 2))
    
    # ============================================================================
    # PHASE 14: Season History Tracking Methods
    # ============================================================================
    
    def save_season_stats(self, season_number, match_format):
        """
        Save current season stats to history
        
        Args:
            season_number: Current season number
            match_format: 'T20', 'ODI', or 'Test'
        """
        season_stats = self.season_stats[match_format].copy()
        season_stats['season'] = season_number
        season_stats['age'] = self.age
        
        # Calculate averages for the season
        if season_stats['matches'] > 0:
            season_stats['batting_avg'] = season_stats['runs'] / season_stats['matches']
            if season_stats['wickets'] > 0:
                # Simplified bowling average
                season_stats['bowling_avg'] = (season_stats['runs'] * 0.5) / season_stats['wickets']
            else:
                season_stats['bowling_avg'] = 0.0
        else:
            season_stats['batting_avg'] = 0.0
            season_stats['bowling_avg'] = 0.0
        
        # Add to history
        self.season_history[match_format].append(season_stats)
        
        # Keep only last 20 seasons
        if len(self.season_history[match_format]) > 20:
            self.season_history[match_format] = self.season_history[match_format][-20:]
    
    def save_skill_snapshot(self, season_number):
        """
        Save current skill levels
        
        Args:
            season_number: Current season number
        """
        snapshot = {
            'season': season_number,
            'age': self.age,
            'batting': self.batting,
            'bowling': self.bowling,
            'fielding': self.fielding
        }
        self.skill_history.append(snapshot)
        
        # Keep only last 20 seasons
        if len(self.skill_history) > 20:
            self.skill_history = self.skill_history[-20:]
    
    def add_milestone(self, season_number, milestone_type, description, match_format=None):
        """
        Add a career milestone
        
        Args:
            season_number: Season when milestone achieved
            milestone_type: Type of milestone (century, five_wickets, debut, etc.)
            description: Description of the milestone
            match_format: Format where milestone was achieved (optional)
        """
        milestone = {
            'season': season_number,
            'age': self.age,
            'type': milestone_type,
            'description': description,
            'format': match_format
        }
        self.milestones.append(milestone)
    
    def add_trait_change(self, season_number, action, trait_name, trait_level=None):
        """
        Record trait change in history
        
        Args:
            season_number: Season when change occurred
            action: 'gained', 'lost', 'level_up', 'level_down'
            trait_name: Name of the trait
            trait_level: New level (optional)
        """
        change = {
            'season': season_number,
            'age': self.age,
            'action': action,
            'trait': trait_name,
            'level': trait_level
        }
        self.trait_history.append(change)
        
        # Keep only last 50 changes
        if len(self.trait_history) > 50:
            self.trait_history = self.trait_history[-50:]
    
    def get_season_history(self, match_format, max_seasons=20):
        """
        Get season-by-season statistics
        
        Args:
            match_format: 'T20', 'ODI', or 'Test'
            max_seasons: Maximum number of seasons to return
        
        Returns:
            List of season stat dictionaries
        """
        history = self.season_history.get(match_format, [])
        return history[-max_seasons:] if history else []
    
    def get_career_summary(self):
        """
        Get comprehensive career summary across all formats
        
        Returns:
            Dictionary with career highlights
        """
        summary = {
            'name': self.name,
            'age': self.age,
            'role': self.role,
            'nationality': self.nationality,
            'formats': {}
        }
        
        for format_type in ['T20', 'ODI', 'Test']:
            stats = self.stats[format_type]
            summary['formats'][format_type] = {
                'matches': stats['matches'],
                'runs': stats['runs'],
                'batting_avg': stats['batting_average'],
                'highest_score': stats['highest_score'],
                'centuries': stats['centuries'],
                'fifties': stats['fifties'],
                'wickets': stats['wickets'],
                'bowling_avg': stats['bowling_average'],
                'economy': stats['economy_rate'],
                'five_wickets': stats['five_wickets']
            }
        
        summary['total_matches'] = sum(self.stats[f]['matches'] for f in ['T20', 'ODI', 'Test'])
        summary['total_runs'] = sum(self.stats[f]['runs'] for f in ['T20', 'ODI', 'Test'])
        summary['total_wickets'] = sum(self.stats[f]['wickets'] for f in ['T20', 'ODI', 'Test'])
        summary['milestones'] = len(self.milestones)
        
        return summary
    
    def __repr__(self):
        return f"Player({self.name}, {self.age}, {self.role}, {self.nationality})"
