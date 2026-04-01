"""
Select XI Dialog - Manual team selection: pick 11 players, batting order, captain, vice-captain.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QComboBox, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt

from cricket_manager.ui.styles import COLORS, MAIN_STYLESHEET


class SelectXIDialog(QDialog):
    """Dialog to select playing XI, batting order, captain and vice-captain."""
    
    def __init__(self, team, parent=None):
        super().__init__(parent)
        self.setStyleSheet(MAIN_STYLESHEET)
        self.team = team
        self.setWindowTitle(f"Select XI – {team.name}")
        self.setMinimumSize(500, 550)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        available = [p for p in self.team.players if not getattr(p, 'is_injured', False)]
        self.available_list = QListWidget()
        self.available_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        for p in available:
            item = QListWidgetItem(p.name)
            item.setData(Qt.ItemDataRole.UserRole, p)
            self.available_list.addItem(item)
        
        self.selected_list = QListWidget()
        self.selected_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        existing = getattr(self.team, 'selected_xi_names', None) or []
        name_to_player = {p.name: p for p in self.team.players}
        for name in existing[:11]:
            if name in name_to_player and not getattr(name_to_player[name], 'is_injured', False):
                self.selected_list.addItem(name)
        while self.selected_list.count() < 11:
            added = False
            for p in available:
                if self.selected_list.findItems(p.name, Qt.MatchFlag.MatchExactly):
                    continue
                self.selected_list.addItem(p.name)
                added = True
                break
            if not added:
                break
        
        layout.addWidget(QLabel("Available (non-injured):"))
        layout.addWidget(self.available_list)
        add_btn = QPushButton("Add selected to XI")
        add_btn.clicked.connect(self._add_selected)
        layout.addWidget(add_btn)
        
        layout.addWidget(QLabel("Playing XI (drag to reorder):"))
        layout.addWidget(self.selected_list)
        remove_btn = QPushButton("Remove selected from XI")
        remove_btn.clicked.connect(self._remove_selected)
        layout.addWidget(remove_btn)
        
        cap_layout = QHBoxLayout()
        cap_layout.addWidget(QLabel("Captain:"))
        self.captain_combo = QComboBox()
        self.captain_combo.addItem("(Auto)")
        for i in range(self.selected_list.count()):
            self.captain_combo.addItem(self.selected_list.item(i).text())
        cap = getattr(self.team, 'captain_name', None)
        if cap:
            idx = self.captain_combo.findText(cap)
            if idx >= 0:
                self.captain_combo.setCurrentIndex(idx)
        cap_layout.addWidget(self.captain_combo)
        layout.addLayout(cap_layout)
        
        vc_layout = QHBoxLayout()
        vc_layout.addWidget(QLabel("Vice-captain:"))
        self.vice_captain_combo = QComboBox()
        self.vice_captain_combo.addItem("(Auto)")
        for i in range(self.selected_list.count()):
            self.vice_captain_combo.addItem(self.selected_list.item(i).text())
        vc = getattr(self.team, 'vice_captain_name', None)
        if vc:
            idx = self.vice_captain_combo.findText(vc)
            if idx >= 0:
                self.vice_captain_combo.setCurrentIndex(idx)
        vc_layout.addWidget(self.vice_captain_combo)
        layout.addLayout(vc_layout)
        
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("Save XI")
        ok_btn.clicked.connect(self._save)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def _add_selected(self):
        for item in self.available_list.selectedItems():
            name = item.text()
            if self.selected_list.findItems(name, Qt.MatchFlag.MatchExactly):
                continue
            if self.selected_list.count() >= 11:
                break
            self.selected_list.addItem(name)
    
    def _remove_selected(self):
        for item in self.selected_list.selectedItems():
            self.selected_list.takeItem(self.selected_list.row(item))
    
    def _update_captain_combos(self):
        names = [self.selected_list.item(i).text() for i in range(self.selected_list.count())]
        self.captain_combo.clear()
        self.captain_combo.addItem("(Auto)")
        self.captain_combo.addItems(names)
        self.vice_captain_combo.clear()
        self.vice_captain_combo.addItem("(Auto)")
        self.vice_captain_combo.addItems(names)
    
    def _save(self):
        names = [self.selected_list.item(i).text() for i in range(self.selected_list.count())]
        if len(names) < 11:
            QMessageBox.warning(self, "Select XI", "Please select exactly 11 players.")
            return
        self.team.selected_xi_names = names[:11]
        self.team.batting_order_names = names[:11]
        cap = self.captain_combo.currentText()
        vc = self.vice_captain_combo.currentText()
        self.team.captain_name = None if cap == "(Auto)" else cap
        self.team.vice_captain_name = None if vc == "(Auto)" else vc
        for p in self.team.players:
            p.squad_role = None
        if self.team.captain_name:
            for p in self.team.players:
                if p.name == self.team.captain_name:
                    p.squad_role = 'captain'
                    break
        if self.team.vice_captain_name:
            for p in self.team.players:
                if p.name == self.team.vice_captain_name:
                    p.squad_role = 'vice_captain'
                    break
        QMessageBox.information(self, "Select XI", "Playing XI, captain and vice-captain saved.")
        self.accept()
