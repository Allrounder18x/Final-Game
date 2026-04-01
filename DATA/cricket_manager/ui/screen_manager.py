"""
Screen Manager - Single-screen navigation system
Manages full-screen transitions between different views
"""

from PyQt6.QtWidgets import QStackedWidget, QWidget
from PyQt6.QtCore import pyqtSignal


class ScreenManager(QStackedWidget):
    """
    Manages single-screen navigation
    Each screen takes up the full window, no tabs or splits
    """
    
    # Signals
    screen_changed = pyqtSignal(str)  # Emitted when screen changes
    
    def __init__(self):
        super().__init__()
        self.screens = {}  # Dictionary of screen_name: widget
        self.screen_history = []  # Navigation history
    
    def add_screen(self, name, widget):
        """
        Add a screen to the manager
        
        Args:
            name: Unique identifier for the screen
            widget: QWidget to display
        """
        self.screens[name] = widget
        self.addWidget(widget)
    
    def show_screen(self, name, add_to_history=True):
        """
        Show a specific screen (full screen)
        
        Args:
            name: Name of screen to show
            add_to_history: Whether to add to navigation history
        """
        if name not in self.screens:
            print(f"[ScreenManager] Screen '{name}' not found")
            return
        
        widget = self.screens[name]
        self.setCurrentWidget(widget)
        
        if add_to_history:
            self.screen_history.append(name)
        
        self.screen_changed.emit(name)
        print(f"[ScreenManager] Showing screen: {name}")
    
    def go_back(self):
        """Go back to previous screen"""
        if len(self.screen_history) > 1:
            self.screen_history.pop()  # Remove current
            previous = self.screen_history[-1]
            self.show_screen(previous, add_to_history=False)
    
    def get_current_screen_name(self):
        """Get name of current screen"""
        current_widget = self.currentWidget()
        for name, widget in self.screens.items():
            if widget == current_widget:
                return name
        return None
    
    def clear_history(self):
        """Clear navigation history"""
        self.screen_history.clear()


class BaseScreen(QWidget):
    """
    Base class for all screens
    Provides common functionality for navigation
    """
    
    # Signals
    navigate_to = pyqtSignal(str)  # Request navigation to another screen
    go_back = pyqtSignal()  # Request going back
    
    def __init__(self, screen_manager=None):
        super().__init__()
        self.screen_manager = screen_manager
    
    def navigate(self, screen_name):
        """Navigate to another screen"""
        if self.screen_manager:
            self.screen_manager.show_screen(screen_name)
        else:
            self.navigate_to.emit(screen_name)
    
    def back(self):
        """Go back to previous screen"""
        if self.screen_manager:
            self.screen_manager.go_back()
        else:
            self.go_back.emit()
