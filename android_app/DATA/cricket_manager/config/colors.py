"""
Color schemes for UI elements
Phase 12: Comprehensive color system
"""

# Main color palette
COLORS = {
    # Primary colors
    'primary': '#3498db',
    'primary_light': '#5dade2',
    'secondary': '#2ecc71',
    'accent': '#e74c3c',
    'warning': '#f39c12',
    'info': '#9b59b6',
    
    # Neutral colors
    'dark': '#2c3e50',
    'light': '#ecf0f1',
    'white': '#ffffff',
    'gray': '#95a5a6',
    'gray_dark': '#7f8c8d',
    'gray_light': '#bdc3c7',
    
    # Status colors
    'success': '#27ae60',
    'danger': '#e74c3c',
    'warning': '#f39c12',
    'info': '#3498db',
    
    # Tier colors
    'tier_1': '#f39c12',  # Gold
    'tier_2': '#c0c0c0',  # Silver
    'tier_3': '#cd7f32',  # Bronze
    'tier_4': '#3498db',  # Blue
    'tier_5': '#95a5a6',  # Gray
    
    # Trait level colors
    'trait_level_1': '#95a5a6',  # Gray
    'trait_level_2': '#3498db',  # Blue
    'trait_level_3': '#f39c12',  # Gold
    
    # Change type colors
    'skill_improvement': '#27ae60',  # Green
    'skill_decline': '#e74c3c',  # Red
    'trait_level_up': '#3498db',  # Blue
    'trait_level_down': '#e67e22',  # Orange
    'trait_gained': '#9b59b6',  # Purple
    'trait_lost': '#95a5a6',  # Gray
    
    # Format colors
    't20': '#e74c3c',  # Red
    'odi': '#3498db',  # Blue
    'test': '#2ecc71',  # Green
    
    # Background colors
    'bg_primary': '#ffffff',
    'bg_secondary': '#f8f9fa',
    'bg_dark': '#343a40',
    'bg_light': '#f1f3f5',
    
    # Text colors
    'text_primary': '#212529',
    'text_secondary': '#6c757d',
    'text_light': '#adb5bd',
    'text_white': '#ffffff',
    
    # Border colors
    'border_light': '#dee2e6',
    'border_dark': '#495057',
    
    # Button colors
    'btn_primary': '#007bff',
    'btn_success': '#28a745',
    'btn_danger': '#dc3545',
    'btn_warning': '#ffc107',
    'btn_info': '#17a2b8',
    
    # Highlight colors
    'highlight_yellow': '#fff3cd',
    'highlight_green': '#d4edda',
    'highlight_red': '#f8d7da',
    'highlight_blue': '#d1ecf1',
}


def get_tier_color(tier):
    """
    Get color for tier
    
    Args:
        tier: Tier number (1-5)
    
    Returns:
        Hex color string
    """
    return COLORS.get(f'tier_{tier}', COLORS['gray'])


def get_trait_level_color(level):
    """
    Get color for trait level
    
    Args:
        level: Trait level (1-3)
    
    Returns:
        Hex color string
    """
    return COLORS.get(f'trait_level_{level}', COLORS['gray'])


def get_format_color(format_type):
    """
    Get color for format
    
    Args:
        format_type: 'T20', 'ODI', or 'Test'
    
    Returns:
        Hex color string
    """
    return COLORS.get(format_type.lower(), COLORS['primary'])


def get_change_type_color(change_type):
    """
    Get color for change type
    
    Args:
        change_type: Type of change (skill_improvement, trait_gained, etc.)
    
    Returns:
        Hex color string
    """
    return COLORS.get(change_type, COLORS['gray'])


def get_status_color(status):
    """
    Get color for status
    
    Args:
        status: 'success', 'danger', 'warning', or 'info'
    
    Returns:
        Hex color string
    """
    return COLORS.get(status, COLORS['gray'])


def hex_to_rgb(hex_color):
    """
    Convert hex color to RGB tuple
    
    Args:
        hex_color: Hex color string (e.g., '#3498db')
    
    Returns:
        Tuple of (r, g, b) values (0-255)
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r, g, b):
    """
    Convert RGB tuple to hex color
    
    Args:
        r, g, b: RGB values (0-255)
    
    Returns:
        Hex color string
    """
    return f'#{r:02x}{g:02x}{b:02x}'


def lighten_color(hex_color, factor=0.2):
    """
    Lighten a color by a factor
    
    Args:
        hex_color: Hex color string
        factor: Lightening factor (0-1, where 1 is white)
    
    Returns:
        Lightened hex color string
    """
    r, g, b = hex_to_rgb(hex_color)
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return rgb_to_hex(r, g, b)


def darken_color(hex_color, factor=0.2):
    """
    Darken a color by a factor
    
    Args:
        hex_color: Hex color string
        factor: Darkening factor (0-1, where 1 is black)
    
    Returns:
        Darkened hex color string
    """
    r, g, b = hex_to_rgb(hex_color)
    r = int(r * (1 - factor))
    g = int(g * (1 - factor))
    b = int(b * (1 - factor))
    return rgb_to_hex(r, g, b)
