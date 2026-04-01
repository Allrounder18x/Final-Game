"""
Cricket Manager 2024 - Main Entry Point

A comprehensive cricket management simulation game featuring:
- Multi-format support (T20, ODI, Test)
- 76 teams across 5 tiers per format
- Youth development system
- Training and progression
- World Cup tournaments
- Loot pack system
- Comprehensive statistics tracking
- Regional name generation
- Fast match simulation
- Interactive match player

Version: 1.0
Author: Cricket Manager Development Team
Date: January 2026
"""

import sys
import os


def check_dependencies():
    """Check if all required dependencies are available"""
    missing = []
    
    # Check PyQt6
    try:
        import PyQt6
    except ImportError:
        missing.append("PyQt6")
    
    # Check standard library modules
    required_modules = ['pickle', 'random', 'copy', 'datetime', 'json']
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    return missing


def check_project_structure():
    """Check if project structure is correct"""
    # Get current directory (should be DATA folder)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    required_dirs = [
        os.path.join(current_dir, 'cricket_manager/core'),
        os.path.join(current_dir, 'cricket_manager/systems'),
        os.path.join(current_dir, 'cricket_manager/ui'),
        os.path.join(current_dir, 'cricket_manager/data'),
        os.path.join(current_dir, 'cricket_manager/utils'),
        os.path.join(current_dir, 'cricket_manager/config')
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    return missing_dirs


def print_banner():
    """Print application banner"""
    print("\n" + "="*70)
    print(" "*20 + "CRICKET MANAGER 2024")
    print("="*70)
    print("\n  A Comprehensive Cricket Management Simulation Game")
    print("\n  Features:")
    print("    • 76 Teams across 5 tiers per format")
    print("    • Multi-format support (T20, ODI, Test)")
    print("    • 1,140+ players with regional names")
    print("    • Youth development & training systems")
    print("    • World Cup tournaments every 2 years")
    print("    • Fast match simulation engine")
    print("    • Interactive match player")
    print("    • Comprehensive statistics tracking")
    print("\n" + "="*70 + "\n")


def main():
    """Main application entry point"""
    
    # Print banner
    print_banner()
    
    # Check dependencies
    print("Checking dependencies...")
    missing_deps = check_dependencies()
    if missing_deps:
        print(f"\n✗ ERROR: Missing dependencies: {', '.join(missing_deps)}")
        print("\nPlease install required dependencies:")
        print("  pip install PyQt6")
        print("\nPress Enter to exit...")
        input()
        sys.exit(1)
    print("✓ All dependencies found")
    
    # Check project structure
    print("\nChecking project structure...")
    missing_dirs = check_project_structure()
    if missing_dirs:
        print(f"\n✗ ERROR: Missing directories: {', '.join(missing_dirs)}")
        print("\nPlease ensure all project files are in the correct locations.")
        print("\nPress Enter to exit...")
        input()
        sys.exit(1)
    print("✓ Project structure valid")
    
    # Import game modules
    print("\nLoading game modules...")
    try:
        from cricket_manager.core.game_engine import GameEngine
        from cricket_manager.ui.main_window import MainWindow
        print("✓ Game modules loaded")
    except ImportError as e:
        print(f"\n✗ ERROR: Failed to import game modules")
        print(f"  {str(e)}")
        print("\nPlease ensure all game files are present and correct.")
        print("\nPress Enter to exit...")
        input()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: Unexpected error loading modules")
        print(f"  {str(e)}")
        import traceback
        traceback.print_exc()
        print("\nPress Enter to exit...")
        input()
        sys.exit(1)
    
    # Initialize game engine
    print("\nInitializing game engine...")
    try:
        game_engine = GameEngine()
        print("✓ Game engine initialized")
        print(f"  • {len(game_engine.all_teams)} teams loaded")
        print(f"  • {sum(len(team.players) for team in game_engine.all_teams)} players generated")
        
        # Count total fixtures across all formats
        total_fixtures = sum(len(fixtures) for fixtures in game_engine.fixtures.values())
        print(f"  • {total_fixtures} fixtures scheduled")
    except Exception as e:
        print(f"\n✗ ERROR: Failed to initialize game engine")
        print(f"  {str(e)}")
        import traceback
        traceback.print_exc()
        print("\nPress Enter to exit...")
        input()
        sys.exit(1)
    
    # Create and launch UI
    print("\nLaunching user interface...")
    try:
        from PyQt6.QtWidgets import QApplication
        
        app = QApplication(sys.argv)
        app.setApplicationName("Cricket Manager 2024")
        app.setOrganizationName("Cricket Manager")
        
        # Pass the game_engine to MainWindow to avoid double initialization
        window = MainWindow(game_engine)
        window.showMaximized()
        
        print("✓ UI launched successfully")
        print("\n" + "="*70)
        print(" "*15 + "GAME READY - ENJOY PLAYING!")
        print("="*70 + "\n")
        
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"\n✗ ERROR: Failed to launch UI")
        print(f"  {str(e)}")
        import traceback
        traceback.print_exc()
        print("\nPress Enter to exit...")
        input()
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGame interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n✗ FATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\nPress Enter to exit...")
        input()
        sys.exit(1)
