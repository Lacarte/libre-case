import sys
import pyperclip
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMainWindow, QMessageBox
from PyQt6.QtGui import QIcon, QAction, QCursor
from PyQt6.QtCore import pyqtSignal, QObject, QProcess, QTimer
from pynput import keyboard
import win32clipboard
import pygetwindow as gw
import pyautogui
import time
import logging
from utils import setup_logging, resource_path
from snippet_db import init_db, get_all_snippets, increment_use_count, add_snippet
from snippet_dialog import SnippetManagerDialog
import win32con
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QApplication, QMainWindow, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon
import os
import glob

logger = setup_logging()

# AI Helper Prompts Configuration
AI_PROMPTS = {
    "improve_writing": "Improve the writing of the following text while maintaining its meaning and tone:\n\n",
    "fix_spelling_grammar": "Fix all spelling and grammar errors in the following text:\n\n",
    "make_longer": "Make the following text longer while keeping the same meaning and style:\n\n",
    "make_shorter": "Make the following text shorter and more concise while preserving the key message:\n\n",
    "simplify": "Simplify the following text to make it easier to understand:\n\n",
    "explain": "Explain the following text in simple terms:\n\n",
    "summarize": "Summarize the following text:\n\n",
    # Translate prompts
    "translate_french": "Translate the following text to French:\n\n",
    "translate_english": "Translate the following text to English:\n\n",
    "translate_spanish": "Translate the following text to Spanish:\n\n",
    "translate_german": "Translate the following text to German:\n\n",
    "translate_portuguese": "Translate the following text to Portuguese:\n\n",
    "translate_italian": "Translate the following text to Italian:\n\n",
    "translate_chinese": "Translate the following text to Chinese:\n\n",
    "translate_japanese": "Translate the following text to Japanese:\n\n",
    "translate_korean": "Translate the following text to Korean:\n\n",
    "translate_arabic": "Translate the following text to Arabic:\n\n",
    "translate_russian": "Translate the following text to Russian:\n\n",
    "translate_kreyol": "Translate the following text to Haitian Creole (Kreyòl):\n\n",
    # Tone prompts
    "tone_professional": "Rewrite the following text in a professional tone:\n\n",
    "tone_casual": "Rewrite the following text in a casual, friendly tone:\n\n",
    "tone_formal": "Rewrite the following text in a formal tone:\n\n",
    "tone_confident": "Rewrite the following text in a confident, assertive tone:\n\n",
    "tone_friendly": "Rewrite the following text in a warm, friendly tone:\n\n",
    "tone_diplomatic": "Rewrite the following text in a diplomatic, tactful tone:\n\n",
}


class TextboxNotificationDialog(QDialog):

    def __init__(self):
        super().__init__()

        # Set up the layout
        layout = QVBoxLayout(self)

        # Add a text edit box
        self.textbox = QTextEdit(self)
        layout.addWidget(self.textbox)

        # Add a close button
        close_button = QPushButton("Close", self)
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        # Set dialog properties
        self.setWindowTitle("Last Actions")
        self.setFixedSize(480, 200)
  
    def set_text(self, text):
        self.textbox.setPlainText(text)

    def closeEvent(self, event):
        # Override the close event to hide the dialog instead of closing it
        self.hide()
        event.ignore()


class ClickSignal(QObject):
    clicked = pyqtSignal(int, int)
    snippet_triggered = pyqtSignal()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Force Qt to use a specific style that works better with custom stylesheets
        app = QApplication.instance()
        if app:
            app.setStyle('Fusion')  # This helps with custom stylesheet rendering
        
        init_db()
        self._snippets_cache = get_all_snippets()

        self.initUI()
        self.textboxDialog = None  # Dialog reference

        self.click_signal = ClickSignal()
        self.click_signal.clicked.connect(self.show_context_menu)
        self.click_signal.snippet_triggered.connect(self.show_snippet_quick_paste)

        self.key_sequence = []
        self.last_key_time = time.time()
        # logger.info("self.last_key_time: " + str(self.last_key_time))
        
    def on_click(self, x, y, button, pressed):
        # The mouse click handling remains the same as in your original script
        logging.info("Click")

    def on_press(self, key):
        current_time = time.time()
        # logger.info("current_time - self.last_key_time  " + str(current_time - self.last_key_time))
        if current_time - self.last_key_time > 0.7:
            self.tray_icon.setIcon(QIcon(resource_path("icons/icon.png")))
            self.key_sequence.clear()

        if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            self.key_sequence.append('ctrl')
            self.tray_icon.setIcon(QIcon(resource_path("icons/icon-red.png")))
            if len(self.key_sequence) >= 3: 
                self.key_sequence.clear()
                self.key_sequence = ['ctrl']
            if self.key_sequence == ['ctrl', 'ctrl'] : 
                self.tray_icon.setIcon(QIcon(resource_path("icons/icon-yellow.png")))
        elif key == keyboard.Key.shift:
            self.key_sequence.append('shift')
        elif hasattr(key, 'char') and key.char == 's' and self.key_sequence == ['ctrl', 'ctrl']:
            self.key_sequence.append('s')

        # logger.info("press append keys : " + str(self.key_sequence))
        self.last_key_time = current_time

    def on_release(self, key):
        if len(self.key_sequence) == 3 and self.key_sequence == ['ctrl', 'ctrl', 'shift']:
            x, y = pyautogui.position()
            self.click_signal.clicked.emit(x, y)
            self.tray_icon.setIcon(QIcon(resource_path("icons/icon-green.png")))
            logger.info("Open Menu on Release")
            self.key_sequence.clear()

        if len(self.key_sequence) == 3 and self.key_sequence == ['ctrl', 'ctrl', 's']:
            self.click_signal.snippet_triggered.emit()
            self.tray_icon.setIcon(QIcon(resource_path("icons/icon-green.png")))
            logger.info("Open Snippet Quick Paste on Release")
            self.key_sequence.clear()
 
        if key == keyboard.Key.esc:
            # TODO to fix implementation of esc to close the menu(problem if crash the app and leave the shape or shadow of the menu remains on the screen after hiding it) 
            # self.close_menu_if_open()  # Call the method to close the menu if it's open
            self.tray_icon.setIcon(QIcon(resource_path("icons/icon.png")))
            logging.info("Cancel")
            self.key_sequence.clear()
            return  # Exit the method to avoid processing further

    def close_menu_if_open(self):
        if hasattr(self, 'menu') and self.menu.isVisible():
            self.menu.hide()  # Continue using hide instead of close
            self.tray_icon.hide()  # Hide the system tray icon
            QTimer.singleShot(100, lambda: self.tray_icon.show())  # Then show it again after a short delay

    def initUI(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(resource_path("icons/icon.png")))
        self.tray_icon.setToolTip("Libre-Case") 
        self.tray_icon.activated.connect(self.show_welcome_notification)

        # Create a menu for the tray icon
        tray_menu = QMenu()

        # Add 'Open Transformations' action
        open_transformations_action = QAction("Open Transformations", self)
        open_transformations_action.triggered.connect(self.open_transformations)
        tray_menu.addAction(open_transformations_action)

        # Change 'Close' action to 'Restart'
        restart_action = QAction("Restart", self)
        restart_action.triggered.connect(self.restart_application)
        tray_menu.addAction(restart_action)

        # Add 'Exit' action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.exit_application)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        # logging.info(f"Tooltip : {self.tray_icon.toolTip()}")

        self.tray_icon.show()

    def open_transformations(self):
        # Function to open the context menu programmatically
        x, y = pyautogui.position()
        self.show_context_menu(x, y)

    def restart_application(self):
        # Restart the application
        QApplication.quit()
        QProcess.startDetached(sys.executable, sys.argv)

    def exit_application(self):
        # This method will be called when 'Exit' is clicked
        QApplication.quit()  # Quit the application

    def show_welcome_notification(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.textboxDialog is None or not self.textboxDialog.isVisible():
                self.textboxDialog = TextboxNotificationDialog()

                # Load the last log file and set its content
                log_content = self.get_last_log_content()
                self.textboxDialog.set_text(log_content)

                self.textboxDialog.show()
            else:
                # Bring the already opened dialog to the front
                self.textboxDialog.raise_()
                self.textboxDialog.activateWindow()

    def get_last_log_content(self):
        # Assuming your logs are in the "logs" directory
        log_directory = resource_path('logs')
        list_of_logs = glob.glob(log_directory + '/*.log')  # or the extension your logs have
        if not list_of_logs:
            return "No logs found."

        latest_log = max(list_of_logs, key=os.path.getmtime)
        with open(latest_log, 'r') as file:
            lines = file.readlines()
            # Reverse the order of lines and join them back into a single string
            return ''.join(reversed(lines))

    def get_submenu_stylesheet(self):
        """Return the stylesheet for submenus"""
        return """
        QMenu {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 8px 0px;
            font-size: 14px;
            font-family: 'Segoe UI', Arial, sans-serif;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.15);
        }
        QMenu::item {
            background-color: transparent;
            padding: 8px 16px;
            margin: 2px 8px;
            border-radius: 4px;
            color: #212529;
            min-width: 180px;
        }
        QMenu::item:selected {
            background-color: #0d6efd;
            color: white;
        }
        QMenu::item:pressed {
            background-color: #0b5ed7;
            color: white;
        }
        """

    def show_context_menu(self, x, y):
        # Check if a menu already exists. If it does, bring it to the front instead of creating a new one.
        if hasattr(self, 'menu') and self.menu is not None:
            self.menu.hide()  # Optionally hide the existing menu before showing it again, depending on desired behavior.
            self.menu.exec(QCursor.pos())
            return

        self.menu = QMenu()
        
        # Enhanced stylesheet with more specific selectors and Windows 11 compatibility
        self.menu.setStyleSheet("""
        QMenu {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 8px 0px;
            font-size: 14px;
            font-family: 'Segoe UI', Arial, sans-serif;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.15);
        }
        QMenu::item {
            background-color: transparent;
            padding: 8px 16px;
            margin: 2px 8px;
            border-radius: 4px;
            color: #212529;
            min-width: 180px;
        }
        QMenu::item:selected {
            background-color: #0d6efd;
            color: white;
        }
        QMenu::item:pressed {
            background-color: #0b5ed7;
            color: white;
        }
        QMenu::item:disabled {
            background-color: transparent;
            color: #6c757d;
        }
        QMenu::separator {
            height: 1px;
            background-color: #dee2e6;
            margin: 4px 8px;
        }
        QMenu::indicator {
            width: 16px;
            height: 16px;
            margin-left: 4px;
        }
        /* Submenu styling */
        QMenu QMenu {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            margin-left: 2px;
        }
        """)

        for action, icon_path in [
            ("Uppercase", "icons/uppercase.png"),
            ("Lowercase", "icons/lowercase.png"),
            ("Title Case", "icons/titlecase.png"),  
            ("Sentence Case", "icons/sentence-case.png"),
            ("Reverse", "icons/reverse.png"),
        ]:
            act = self.menu.addAction(QIcon(resource_path(icon_path)), action)
            act.setToolTip(f"Convert text to {action.lower()}")

            # Connect each action to a specific method
            if action == "Uppercase":
                act.triggered.connect(lambda: self.menu_action_selected("uppercase"))
            elif action == "Lowercase":
                act.triggered.connect(lambda: self.menu_action_selected("lowercase"))
            elif action == "Sentence Case":
                act.triggered.connect(lambda: self.menu_action_selected("sentence_case"))
            elif action == "Title Case":  # Add this block
                    act.triggered.connect(lambda: self.menu_action_selected("titlecase"))
            elif action == "Reverse":
                act.triggered.connect(lambda: self.menu_action_selected("reverse"))

        # ============================================
        # AI HELPER SUBMENU
        # ============================================
        self.menu.addSeparator()
        
        ai_helper_menu = self.menu.addMenu("✨ AI Helper")
        ai_helper_menu.setIcon(QIcon(resource_path("icons/ai-helper.png")))
        ai_helper_menu.setStyleSheet(self.get_submenu_stylesheet())

        # --- Suggested Section ---
        # Improve Writing
        act_improve = ai_helper_menu.addAction("✨ Improve writing")
        act_improve.triggered.connect(lambda: self.ai_action_selected("improve_writing"))

        # Fix spelling & grammar
        act_fix = ai_helper_menu.addAction("✓ Fix spelling & grammar")
        act_fix.triggered.connect(lambda: self.ai_action_selected("fix_spelling_grammar"))

        # Translate to submenu
        translate_menu = ai_helper_menu.addMenu("🌐 Translate to")
        translate_menu.setStyleSheet(self.get_submenu_stylesheet())
        
        languages = [
            ("English", "translate_english"),
            ("French", "translate_french"),
            ("Spanish", "translate_spanish"),
            ("German", "translate_german"),
            ("Portuguese", "translate_portuguese"),
            ("Italian", "translate_italian"),
            ("Chinese", "translate_chinese"),
            ("Japanese", "translate_japanese"),
            ("Korean", "translate_korean"),
            ("Arabic", "translate_arabic"),
            ("Russian", "translate_russian"),
            ("Kreyòl", "translate_kreyol"),
        ]
        
        for lang_name, lang_action in languages:
            act_lang = translate_menu.addAction(lang_name)
            # Use default argument to capture the current value
            act_lang.triggered.connect(lambda checked, action=lang_action: self.ai_action_selected(action))

        ai_helper_menu.addSeparator()

        # --- Edit Section ---
        # Make longer
        act_longer = ai_helper_menu.addAction("📝 Make longer")
        act_longer.triggered.connect(lambda: self.ai_action_selected("make_longer"))

        # Make shorter
        act_shorter = ai_helper_menu.addAction("📄 Make shorter")
        act_shorter.triggered.connect(lambda: self.ai_action_selected("make_shorter"))

        # Change tone submenu
        tone_menu = ai_helper_menu.addMenu("🎭 Change tone")
        tone_menu.setStyleSheet(self.get_submenu_stylesheet())
        
        tones = [
            ("Professional", "tone_professional"),
            ("Casual", "tone_casual"),
            ("Formal", "tone_formal"),
            ("Confident", "tone_confident"),
            ("Friendly", "tone_friendly"),
            ("Diplomatic", "tone_diplomatic"),
        ]
        
        for tone_name, tone_action in tones:
            act_tone = tone_menu.addAction(tone_name)
            act_tone.triggered.connect(lambda checked, action=tone_action: self.ai_action_selected(action))

        # Simplify language
        act_simplify = ai_helper_menu.addAction("📖 Simplify language")
        act_simplify.triggered.connect(lambda: self.ai_action_selected("simplify"))

        ai_helper_menu.addSeparator()

        # --- Other ---
        # Explain
        act_explain = ai_helper_menu.addAction("💡 Explain")
        act_explain.triggered.connect(lambda: self.ai_action_selected("explain"))

        # Summarize
        act_summarize = ai_helper_menu.addAction("📋 Summarize")
        act_summarize.triggered.connect(lambda: self.ai_action_selected("summarize"))

        # ============================================
        # SNIPPETS SUBMENU
        # ============================================
        self.menu.addSeparator()
        snippet_menu = self.menu.addMenu("Snippets")
        snippet_menu.setStyleSheet(self.get_submenu_stylesheet())

        if self._snippets_cache:
            for s in self._snippets_cache:
                truncated = s["title"][:35]
                preview = s["content"][:80].replace("\n", " ")
                act_snip = snippet_menu.addAction(truncated)
                act_snip.setToolTip(preview)
                sid = s["id"]
                content = s["content"]
                act_snip.triggered.connect(lambda checked, c=content, i=sid: self._paste_snippet(c, i))
        else:
            no_snip = snippet_menu.addAction("(No snippets yet)")
            no_snip.setEnabled(False)

        snippet_menu.addSeparator()
        add_to_snippet_act = snippet_menu.addAction("Add to Snippet")
        add_to_snippet_act.triggered.connect(self._add_selection_to_snippet)
        manage_act = snippet_menu.addAction("Manage Snippets...")
        manage_act.triggered.connect(self._open_snippet_manager)

        # ============================================
        # MORE TRANSFORMATIONS SUBMENU (existing)
        # ============================================
        more_transformations_menu = self.menu.addMenu("More Transformations")
        more_transformations_menu.setIcon(QIcon(resource_path("icons/more.png")))

        # Apply the same styling to the submenu
        more_transformations_menu.setStyleSheet(self.get_submenu_stylesheet())

        for action, icon_path in [
        ("Remove Extra Lines", "icons/remove-extra-lines.png"),
        ("Remove Extra Spaces", "icons/remove-extra-space.png"),
        ("Count Words", "icons/count-word.png"),
        ("Count Characters", "icons/count-characters.png"),
        ("Alternating", "icons/alternating.png"),
        ("InvertCase", "icons/invert-case.png"),
        ("Clear Format", "icons/clear-format.png"),
        ("Sup", "icons/sup.png"),
        ("Sub", "icons/sub.png")
        ]:
            act = more_transformations_menu.addAction(QIcon(resource_path(icon_path)), action)
            act.setToolTip(f"{action}")
            # Connect each action to a specific method

            if action == "Remove Extra Lines":
                act.triggered.connect(lambda: self.menu_action_selected("remove_extra_lines"))
            elif action == "Remove Extra Spaces":
                act.triggered.connect(lambda: self.menu_action_selected("remove_extra_spaces"))
            elif action == "Count Words":
                act.triggered.connect(lambda: self.menu_action_selected("count_words"))
            elif action == "Count Characters":
                act.triggered.connect(lambda: self.menu_action_selected("count_characters"))
            elif action == "Alternating":
                act.triggered.connect(lambda: self.menu_action_selected("alternating"))
            elif action == "InvertCase":
                act.triggered.connect(lambda: self.menu_action_selected("invert_case"))
            elif action == "Clear Format":
                act.triggered.connect(lambda: self.menu_action_selected("clear_format"))
            elif action == "Sup":
                act.triggered.connect(lambda: self.menu_action_selected("sup"))
            elif action == "Sub":
                act.triggered.connect(lambda: self.menu_action_selected("sub"))

         # Adding the 'Close Text Transformation' action at the end of the menu
        close_action = QAction("", self)
        close_action.setIcon(QIcon(resource_path("icons/hide.png")))
        close_action.triggered.connect(lambda: self.menu_action_selected("close"))
        self.menu.addAction(close_action)

        self.menu.exec(QCursor.pos())

    def _paste_snippet(self, content, snippet_id):
        increment_use_count(snippet_id)
        self._refresh_snippets_cache()
        pyperclip.copy(content)
        pyautogui.hotkey('ctrl', 'v')
        logging.info(f"Pasted snippet id={snippet_id}")

    def _add_selection_to_snippet(self):
        """Add the currently selected text as a new snippet with validation."""
        import re
        copied_text = self.copy_without_clearing_clipboard()
        if not copied_text:
            return

        # Strip leading/trailing whitespace
        content = copied_text.strip()

        # Remove non-visible / control characters (keep newlines, tabs, and normal printable chars)
        content = re.sub(r'[^\S \t\n]', '', content)  # remove non-standard whitespace
        content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', content)  # remove control chars

        # Collapse double (or more) spaces into single space
        content = re.sub(r' {2,}', ' ', content)

        # Final strip after cleanup
        content = content.strip()

        if not content:
            QMessageBox.warning(self, "Add to Snippet", "Selected text is empty or contains only invalid characters.")
            return

        # Auto-generate title from first 36 characters
        title = content[:36].replace("\n", " ").strip()

        error = add_snippet(title, content)
        if error:
            QMessageBox.warning(self, "Add to Snippet", error)
            return

        self._refresh_snippets_cache()
        QMessageBox.information(self, "Add to Snippet", f"Snippet \"{title}\" added successfully.")

    def _open_snippet_manager(self):
        dlg = SnippetManagerDialog(self)
        dlg.snippets_changed.connect(self._refresh_snippets_cache)
        result = dlg.exec()
        # If user clicked "Use", paste the snippet
        used_content = dlg.get_used_content()
        if used_content:
            pyperclip.copy(used_content)
            pyautogui.hotkey('ctrl', 'v')

    def _refresh_snippets_cache(self):
        self._snippets_cache = get_all_snippets()
        # Reset cached menu so it rebuilds with updated snippets next time
        self.menu = None

    def show_snippet_quick_paste(self):
        self._snippets_cache = get_all_snippets()
        menu = QMenu()
        menu.setStyleSheet(self.get_submenu_stylesheet())

        if self._snippets_cache:
            for s in self._snippets_cache:
                truncated = s["title"][:35]
                preview = s["content"][:80].replace("\n", " ")
                act = menu.addAction(f"{truncated}  —  {preview}")
                sid = s["id"]
                content = s["content"]
                act.triggered.connect(lambda checked, c=content, i=sid: self._paste_snippet(c, i))
        else:
            no_snip = menu.addAction("(No snippets)")
            no_snip.setEnabled(False)

        menu.addSeparator()
        manage_act = menu.addAction("Manage Snippets...")
        manage_act.triggered.connect(self._open_snippet_manager)

        menu.exec(QCursor.pos())

    def get_highlighted_text(self):
        win32clipboard.OpenClipboard()
        text = ""
        try: 
            text = win32clipboard.GetClipboardData(win32con.CF_TEXT)
        except:
            pass  
        win32clipboard.CloseClipboard()
        return text

    def get_active_window_title(self):
        active_window = gw.getActiveWindow()
        return active_window.title if active_window else None
    
    def copy_without_clearing_clipboard(self):
        # Save the Current clipboard content
        original_clipboard = pyperclip.paste()
        logging.info(f"original_clipboard : {original_clipboard}")

        # Simulate the Ctrl+C (copy) keyboard command
        logging.info("Simulate the Ctrl+C (copy) keyboard command")
        pyautogui.hotkey('ctrl', 'c')
        
        # Wait a bit for the Clipboard, to update
        time.sleep(0.25)

        # Get the new clipboard content
        new_clipboard = pyperclip.paste()
        logging.info(f"new_clipboard : {new_clipboard}")

        # Check if the copied text is empty
        if not new_clipboard.strip():
            # Display message box if no text is copied
            QMessageBox.information(self, "No Text Selected", "No text was selected or copied.")
            return ""

        # If you want to restore the original content after some operations,
        # you can uncomment the following line
        # pyperclip.copy(original_clipboard)

        return new_clipboard

    def ai_action_selected(self, action):
        """Handle AI Helper menu actions - copy prompt + selected text to clipboard"""
        copied_text = self.copy_without_clearing_clipboard()
        
        if not copied_text:
            return
        
        # Get the prompt for this action
        prompt = AI_PROMPTS.get(action, "")
        
        if prompt:
            # Combine prompt with selected text
            final_text = prompt + copied_text
            
            # Copy to clipboard
            pyperclip.copy(final_text)
            
            # Show notification
            logging.info(f"AI Helper: {action} - Text copied to clipboard with prompt")
            
            # Optional: Show a brief notification
            self.tray_icon.showMessage(
                "AI Helper",
                f"Prompt ready! Paste in your AI assistant.",
                QSystemTrayIcon.MessageIcon.Information,
                2000  # Duration in milliseconds
            )

    def menu_action_selected(self, action):
        if action == "close":
            return            
        else:
            copied_text = self.copy_without_clearing_clipboard()
            logging.info(f"Copied text: {copied_text}")
            transformed_text = self.transform_text(action, copied_text)
            logging.info(f"Transformed text: {transformed_text}")
            # Display the result in a message box for "count_words" and "count_characters"
            if action in ["count_words", "count_characters"]:
                title = ""
                message = ""
                if action == "count_words":
                    title = "Word Count"
                    message = f"The highlighted text contains {transformed_text} words."
                elif action == "count_characters":
                    title = "Character Count"
                    message = f"The highlighted text contains {transformed_text} characters."
                QMessageBox.information(self, title, message)
            else:
                # For other actions, continue with the existing logic
                # Copy the transformed text to the clipboard
                pyperclip.copy(transformed_text)

                # Simulate the Ctrl+V (paste) keyboard command
                pyautogui.hotkey('ctrl', 'v')

    def transform_text(self, transformation, copied_text):
        # Logic for transforming text
        if transformation == "uppercase":
            logging.info(f"Transforming to uppercase text: {copied_text}")
            return copied_text.upper()
        elif transformation == "lowercase":
            logging.info(f"Transforming to lowercase text: {copied_text}")
            return copied_text.lower()
        elif transformation == "titlecase":
            logging.info(f"Transforming to title case text: {copied_text}")
            return copied_text.title()
        elif transformation == "reverse":
            logging.info(f"Transforming to reverse text: {copied_text}")
            return copied_text[::-1]
            # New transformations
        elif transformation == "count_words":
            return str(len(copied_text.split()))
        elif transformation == "count_characters":
            return str(len(copied_text))
        elif transformation == "clear_format":
            # Implement logic to clear format
            # pass
            return "Not yet implemented"
        elif transformation == "remove_extra_lines":
            return '\n'.join(line for line in copied_text.splitlines() if line)
        elif transformation == "remove_extra_spaces":
            return ' '.join(copied_text.split())
        elif transformation == "sup":
            sup_map = str.maketrans("0123456789+-=()", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾")
            return copied_text.translate(sup_map)
        elif transformation == "sub":
                return ''.join(['₀₁₂₃₄₅₆₇₈₉'[int(c)] if c.isdigit() else c for c in copied_text])
        elif transformation == "alternating":
            return ''.join([c.lower() if i % 2 else c.upper() for i, c in enumerate(copied_text)])
        elif transformation == "sentence_case":
            return '. '.join([s.strip().capitalize() for s in copied_text.split('.')])
        elif transformation == "invert_case":
            return invert_case(copied_text)
   
def invert_case(text):
    return ''.join([char.lower() if char.isupper() else char.upper() for char in text])

if __name__ == "__main__":
    setup_logging()
    logging.info("Initializing the application")
    app = QApplication(sys.argv)
    window = MainWindow()

    keyboard_listener = keyboard.Listener(on_press=window.on_press, on_release=window.on_release)
    # mouse_listener = mouse.Listener(on_click=window.on_click)

    keyboard_listener.start()
    # mouse_listener.start()

    sys.exit(app.exec())