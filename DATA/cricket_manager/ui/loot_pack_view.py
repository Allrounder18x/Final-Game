"""
Loot Pack Screen - Full-screen view for the loot pack system
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QGroupBox, QMessageBox,
    QDialog, QListWidget, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from cricket_manager.ui.styles import COLORS, MAIN_STYLESHEET
from cricket_manager.ui.screen_manager import BaseScreen


class LootPackScreen(BaseScreen):
    """Full-screen view for loot pack system"""
    
    # Signals
    pack_opened = pyqtSignal(list)
    item_used = pyqtSignal(dict, object)
    
    def __init__(self, screen_manager=None, game_engine=None):
        super().__init__(screen_manager)
        self.setStyleSheet(MAIN_STYLESHEET)
        self.game_engine = game_engine
        self.loot_pack_system = game_engine.loot_system if game_engine else None
        self.user_team = game_engine.user_team if game_engine else None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header with back button
        header_layout = QHBoxLayout()
        
        back_btn = QPushButton("← Back")
        back_btn.setMaximumWidth(120)
        back_btn.clicked.connect(self.back)
        header_layout.addWidget(back_btn)
        
        header_layout.addStretch()
        
        title = QLabel("🎁 Loot Pack System")
        title.setProperty("class", "title")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        spacer = QLabel("")
        spacer.setMaximumWidth(120)
        header_layout.addWidget(spacer)
        
        layout.addLayout(header_layout)
        
        # Main content
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # Left side
        left_layout = QVBoxLayout()
        left_layout.setSpacing(20)
        
        credits_group = self.create_credits_section()
        left_layout.addWidget(credits_group)
        
        purchase_group = self.create_purchase_section()
        left_layout.addWidget(purchase_group)
        left_layout.addStretch()
        
        content_layout.addLayout(left_layout, 1)
        
        # Right side
        inventory_group = self.create_inventory_section()
        content_layout.addWidget(inventory_group, 2)
        
        layout.addLayout(content_layout, 1)
        self.setLayout(layout)
        
        self.refresh_credits()
        self.refresh_inventory()
    
    def create_credits_section(self):
        """Create credits display"""
        group = QGroupBox("Credits")
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 30, 20, 20)
        
        self.credits_label = QLabel(f"{self.user_team.credits}")
        self.credits_label.setStyleSheet(f"font-size: 56px; font-weight: 700; color: {COLORS['gold']}; padding: 20px;")
        self.credits_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.credits_label)
        
        info_label = QLabel("Earn credits by winning matches")
        info_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px; font-weight: 600;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
        
        group.setLayout(layout)
        return group
    
    def create_purchase_section(self):
        """Create pack purchase section"""
        group = QGroupBox("Purchase Loot Pack")
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 30, 20, 20)
        
        info_frame = QFrame()
        info_frame.setProperty("class", "card")
        info_layout = QVBoxLayout()
        info_layout.setSpacing(10)
        
        cost_label = QLabel(f"💰 Cost: {self.loot_pack_system.pack_cost} Credits")
        cost_label.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {COLORS['primary']};")
        info_layout.addWidget(cost_label)
        
        contents_label = QLabel("📦 Contains: 3-5 random items")
        contents_label.setStyleSheet(f"font-size: 15px; color: {COLORS['text_secondary']}; font-weight: 600;")
        info_layout.addWidget(contents_label)
        
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"background-color: {COLORS['border']};")
        info_layout.addWidget(divider)
        
        types_label = QLabel("🎯 Possible Items:\n• Youth Players\n• Skill Boosts\n• Trait Modifiers\n• New Traits")
        types_label.setStyleSheet(f"font-size: 13px; color: {COLORS['text_primary']};")
        info_layout.addWidget(types_label)
        
        info_frame.setLayout(info_layout)
        layout.addWidget(info_frame)
        
        self.open_pack_btn = QPushButton("🎁 OPEN LOOT PACK")
        self.open_pack_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                font-size: 18px;
                font-weight: 700;
                padding: 18px;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent_light']};
            }}
            QPushButton:disabled {{
                background-color: {COLORS['border']};
                color: {COLORS['text_disabled']};
            }}
        """)
        self.open_pack_btn.clicked.connect(self.open_loot_pack)
        layout.addWidget(self.open_pack_btn)
        
        group.setLayout(layout)
        return group
    
    def create_inventory_section(self):
        """Create inventory display"""
        group = QGroupBox("Inventory")
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 30, 20, 20)
        
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(3)
        self.inventory_table.setHorizontalHeaderLabels(['Item', 'Type', 'Description'])
        self.inventory_table.horizontalHeader().setStretchLastSection(True)
        self.inventory_table.setColumnWidth(0, 220)
        self.inventory_table.setColumnWidth(1, 160)
        self.inventory_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.inventory_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.inventory_table.setAlternatingRowColors(True)
        self.inventory_table.verticalHeader().setVisible(False)
        layout.addWidget(self.inventory_table)
        
        self.use_item_btn = QPushButton("✨ Use Item on Player")
        self.use_item_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: white;
                font-size: 16px;
                font-weight: 700;
                padding: 14px;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: #66BB6A;
            }}
        """)
        self.use_item_btn.clicked.connect(self.use_item)
        layout.addWidget(self.use_item_btn)
        
        group.setLayout(layout)
        return group
    
    def open_loot_pack(self):
        """Open a loot pack"""
        items, message = self.loot_pack_system.open_loot_pack(self.user_team)
        
        if items is None:
            QMessageBox.warning(self, "Insufficient Credits", message)
            return
        
        self.show_pack_contents(items)
        self.pack_opened.emit(items)
        self.refresh_credits()
        self.refresh_inventory()
    
    def show_pack_contents(self, items):
        """Show pack contents dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Loot Pack Contents")
        dialog.setMinimumSize(550, 450)
        dialog.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("🎁 You received:")
        title.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {COLORS['primary']};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: transparent;")
        
        items_widget = QWidget()
        items_widget.setStyleSheet("background-color: transparent;")
        items_layout = QVBoxLayout()
        items_layout.setSpacing(12)
        
        for item in items:
            item_frame = QFrame()
            item_frame.setProperty("class", "card")
            item_frame.setStyleSheet(f"background-color: #111827; border: 2px solid {COLORS['primary_light']}; border-radius: 8px; padding: 16px;")
            
            item_layout = QVBoxLayout()
            
            name_label = QLabel(item['name'])
            name_label.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {COLORS['primary']};")
            item_layout.addWidget(name_label)
            
            desc_label = QLabel(item['description'])
            desc_label.setStyleSheet(f"font-size: 13px; color: {COLORS['text_secondary']};")
            desc_label.setWordWrap(True)
            item_layout.addWidget(desc_label)
            
            item_frame.setLayout(item_layout)
            items_layout.addWidget(item_frame)
        
        items_widget.setLayout(items_layout)
        scroll.setWidget(items_widget)
        layout.addWidget(scroll)
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(f"QPushButton {{ background-color: {COLORS['primary']}; color: white; font-size: 15px; font-weight: 700; padding: 12px; border-radius: 6px; }} QPushButton:hover {{ background-color: {COLORS['primary_light']}; }}")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def refresh_credits(self):
        """Refresh credits display"""
        self.credits_label.setText(f"{self.user_team.credits}")
        can_open = self.loot_pack_system.can_open_pack(self.user_team)
        self.open_pack_btn.setEnabled(can_open)
    
    def refresh_inventory(self):
        """Refresh inventory display"""
        self.inventory_table.setRowCount(0)
        
        for item in self.user_team.inventory:
            row = self.inventory_table.rowCount()
            self.inventory_table.insertRow(row)
            
            name_item = QTableWidgetItem(item['name'])
            name_item.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            self.inventory_table.setItem(row, 0, name_item)
            
            type_item = QTableWidgetItem(item['type'])
            self.inventory_table.setItem(row, 1, type_item)
            
            desc_item = QTableWidgetItem(item['description'])
            self.inventory_table.setItem(row, 2, desc_item)
            
            self.inventory_table.setRowHeight(row, 45)
    
    def use_item(self):
        """Use selected item"""
        selected_rows = self.inventory_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select an item")
            return
        
        item_index = selected_rows[0].row()
        item = self.user_team.inventory[item_index]
        
        if item['type'] == 'youth_player':
            success, message = self.loot_pack_system.add_youth_player_to_squad(self.user_team, item_index)
            if success:
                QMessageBox.information(self, "Success", message)
            else:
                QMessageBox.warning(self, "Error", message)
            self.refresh_inventory()
            return
        
        self.show_player_selection_dialog(item_index)
    
    def show_player_selection_dialog(self, item_index):
        """Show player selection dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Player")
        dialog.setMinimumSize(500, 550)
        dialog.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Select a player:")
        title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {COLORS['primary']};")
        layout.addWidget(title)
        
        player_list = QListWidget()
        player_list.setStyleSheet("QListWidget::item { padding: 12px; font-size: 13px; }")
        for player in self.user_team.players:
            player_list.addItem(f"{player.name} ({player.role}) - BAT:{player.batting} BOWL:{player.bowling}")
        layout.addWidget(player_list)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        apply_btn = QPushButton("✓ Apply")
        apply_btn.setStyleSheet(f"QPushButton {{ background-color: {COLORS['success']}; color: white; font-size: 15px; font-weight: 700; padding: 12px 24px; border-radius: 6px; }} QPushButton:hover {{ background-color: #66BB6A; }}")
        apply_btn.clicked.connect(lambda: self.apply_item_to_selected(item_index, player_list, dialog))
        button_layout.addWidget(apply_btn)
        
        cancel_btn = QPushButton("✗ Cancel")
        cancel_btn.setStyleSheet(f"QPushButton {{ background-color: {COLORS['text_secondary']}; color: white; font-size: 15px; font-weight: 700; padding: 12px 24px; border-radius: 6px; }} QPushButton:hover {{ background-color: {COLORS['text_primary']}; }}")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        dialog.exec()
    
    def apply_item_to_selected(self, item_index, player_list, dialog):
        """Apply item to selected player"""
        selected_items = player_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a player")
            return
        
        player_index = player_list.row(selected_items[0])
        player = self.user_team.players[player_index]
        
        success, message = self.loot_pack_system.use_item_from_inventory(self.user_team, item_index, player)
        
        if success:
            QMessageBox.information(self, "Success", message)
            self.refresh_inventory()
            self.item_used.emit(self.user_team.inventory[item_index] if item_index < len(self.user_team.inventory) else {}, player)
            dialog.accept()
        else:
            QMessageBox.warning(self, "Error", message)
