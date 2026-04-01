from .core_screens import (
    DashboardScreen,
    FixturesScreen,
    MatchSimulationScreen,
    PlayerListScreen,
    PlayerProfileLiteScreen,
    StandingsScreen,
    TeamSelectionScreen,
)
from .parity_screens import PARITY_SCREEN_CLASSES


def register_screens(manager, service):
    mvp_screens = [
        TeamSelectionScreen(name="team_selection", service=service),
        DashboardScreen(name="dashboard", service=service),
        FixturesScreen(name="fixtures", service=service),
        MatchSimulationScreen(name="match_simulation", service=service),
        StandingsScreen(name="standings", service=service),
        PlayerListScreen(name="players", service=service),
        PlayerProfileLiteScreen(name="player_profile_lite", service=service),
    ]
    for screen in mvp_screens:
        manager.add_widget(screen)
    for cls in PARITY_SCREEN_CLASSES:
        manager.add_widget(cls(name=cls.screen_name, service=service))
