from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget, QListWidgetItem,
    QTextEdit, QPushButton, QLabel, QMessageBox,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
import snippet_db


class AddEditSnippetDialog(QDialog):
    """Dialog for adding or editing a single snippet."""

    def __init__(self, parent=None, snippet=None):
        super().__init__(parent)
        self.snippet = snippet
        self.setWindowTitle("Edit Snippet" if snippet else "Add Snippet")
        self.setMinimumSize(420, 340)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Title
        layout.addWidget(QLabel("Title:"))
        self.title_edit = QLineEdit()
        self.title_edit.setMaxLength(100)
        self.title_edit.setPlaceholderText("Snippet title...")
        layout.addWidget(self.title_edit)

        # Content
        layout.addWidget(QLabel("Content:"))
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("Snippet content...")
        self.content_edit.textChanged.connect(self._on_content_changed)
        layout.addWidget(self.content_edit)

        # Character counter
        self.char_label = QLabel(f"0 / {snippet_db.get_max_content_length()} characters")
        layout.addWidget(self.char_label)

        # Buttons
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("Save")
        self.ok_btn.clicked.connect(self._on_save)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        # Pre-fill if editing
        if self.snippet:
            self.title_edit.setText(self.snippet["title"])
            self.content_edit.setPlainText(self.snippet["content"])

    def _on_content_changed(self):
        text = self.content_edit.toPlainText()
        length = len(text)
        max_length = snippet_db.get_max_content_length()
        if length > max_length:
            # Block excess characters
            self.content_edit.blockSignals(True)
            cursor = self.content_edit.textCursor()
            self.content_edit.setPlainText(text[:max_length])
            self.content_edit.setTextCursor(cursor)
            self.content_edit.blockSignals(False)
            length = max_length
        self.char_label.setText(f"{length} / {max_length} characters")

    def _on_save(self):
        title = self.title_edit.text().strip()
        content = self.content_edit.toPlainText().strip()

        if not title:
            if content:
                title = content[:36].replace("\n", " ").strip()
            else:
                QMessageBox.warning(self, "Validation", "Title is required.")
                return
        if not content:
            QMessageBox.warning(self, "Validation", "Content is required.")
            return

        if self.snippet:
            error = snippet_db.update_snippet(self.snippet["id"], title, content)
        else:
            error = snippet_db.add_snippet(title, content)

        if error:
            QMessageBox.warning(self, "Error", error)
            return

        self.accept()


class SnippetManagerDialog(QDialog):
    """Full snippet management dialog with search, preview, and CRUD."""

    snippets_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Snippet Manager")
        self.setMinimumSize(500, 450)
        self._build_ui()
        self._load_snippets()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Search bar
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search snippets...")
        self.search_edit.textChanged.connect(self._on_search)
        layout.addWidget(self.search_edit)

        # Snippet list
        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self._on_selection_changed)
        layout.addWidget(self.list_widget)

        # Preview pane
        layout.addWidget(QLabel("Preview:"))
        self.preview_edit = QTextEdit()
        self.preview_edit.setReadOnly(True)
        self.preview_edit.setMaximumHeight(120)
        preview_font = QFont("Consolas", 10)
        self.preview_edit.setFont(preview_font)
        layout.addWidget(self.preview_edit)

        # Action buttons
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add")
        self.add_btn.clicked.connect(self._on_add)
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.clicked.connect(self._on_edit)
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self._on_delete)
        self.use_btn = QPushButton("Use")
        self.use_btn.setToolTip("Copy snippet to clipboard and paste")
        self.use_btn.clicked.connect(self._on_use)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.use_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        # Status label
        self.status_label = QLabel()
        layout.addWidget(self.status_label)

        self._update_button_states()

    def _load_snippets(self, query=None):
        self.list_widget.clear()
        self.preview_edit.clear()

        if query:
            self._snippets = snippet_db.search_snippets(query)
        else:
            self._snippets = snippet_db.get_all_snippets()

        for s in self._snippets:
            preview = s["content"][:50].replace("\n", " ")
            item = QListWidgetItem(f"{s['title']}  —  {preview}")
            item.setData(Qt.ItemDataRole.UserRole, s["id"])
            self.list_widget.addItem(item)

        total = snippet_db.get_snippet_count()
        self.status_label.setText(f"{total} / {snippet_db.get_max_snippets()} snippets")
        self._update_button_states()

    def _on_search(self, text):
        query = text.strip()
        self._load_snippets(query if query else None)

    def _on_selection_changed(self, row):
        if 0 <= row < len(self._snippets):
            self.preview_edit.setPlainText(self._snippets[row]["content"])
        else:
            self.preview_edit.clear()
        self._update_button_states()

    def _update_button_states(self):
        has_selection = self.list_widget.currentRow() >= 0
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
        self.use_btn.setEnabled(has_selection)

    def _get_selected_snippet(self):
        row = self.list_widget.currentRow()
        if 0 <= row < len(self._snippets):
            return self._snippets[row]
        return None

    def _on_add(self):
        dlg = AddEditSnippetDialog(self)
        if dlg.exec():
            self._load_snippets()
            self.snippets_changed.emit()

    def _on_edit(self):
        snippet = self._get_selected_snippet()
        if not snippet:
            return
        dlg = AddEditSnippetDialog(self, snippet=snippet)
        if dlg.exec():
            self._load_snippets()
            self.snippets_changed.emit()

    def _on_delete(self):
        snippet = self._get_selected_snippet()
        if not snippet:
            return
        reply = QMessageBox.question(
            self,
            "Delete Snippet",
            f"Delete \"{snippet['title']}\"?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            snippet_db.delete_snippet(snippet["id"])
            self._load_snippets()
            self.snippets_changed.emit()

    def _on_use(self):
        snippet = self._get_selected_snippet()
        if not snippet:
            return
        snippet_db.increment_use_count(snippet["id"])
        self.snippets_changed.emit()
        # Store content so MainWindow can paste it after dialog closes
        self._used_snippet_content = snippet["content"]
        self.accept()

    def get_used_content(self):
        return getattr(self, "_used_snippet_content", None)
