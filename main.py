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
import win32con

class ClickSignal(QObject):
    clicked = pyqtSignal(int, int)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

        self.click_signal = ClickSignal()
        self.click_signal.clicked.connect(self.show_context_menu)

        self.key_sequence = []
        self.last_key_time = time.time()

    def on_click(self, x, y, button, pressed):
        # The mouse click handling remains the same as in your original script
        logging.info("Click")

    def on_press(self, key):
        current_time = time.time()
        if current_time - self.last_key_time > 2:
            self.key_sequence.clear()

        if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            self.key_sequence.append('ctrl')
        elif key == keyboard.Key.shift:
            self.key_sequence.append('shift')

        self.last_key_time = current_time

    def on_release(self, key):
        if len(self.key_sequence) == 3 and self.key_sequence == ['ctrl', 'ctrl', 'shift']:
            x, y = pyautogui.position()
            self.click_signal.clicked.emit(x, y)
            self.key_sequence.clear()

    def initUI(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(resource_path("icons/icon.png")))

        # Create a menu for the tray icon
        tray_menu = QMenu()

        # Change 'Close' action to 'Restart'
        restart_action = QAction("Restart", self)
        restart_action.triggered.connect(self.restart_application)
        tray_menu.addAction(restart_action)

        # Add 'Exit' action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.exit_application)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def restart_application(self):
        # Restart the application
        QApplication.quit()
        QProcess.startDetached(sys.executable, sys.argv)


    def exit_application(self):
        # This method will be called when 'Exit' is clicked
        QApplication.quit()  # Quit the application


    def show_context_menu(self, x, y):
        self.menu = QMenu()
        self.menu.setStyleSheet("""
        QMenu {
            background-color: #f0f0f0;
            border: 1px solid black;
        }
        QMenu::item {
            background-color: transparent;
        }
        QMenu::item:selected {
            background-color: #a8d8ea;
        }
        """)

        for action, icon_path in [
            ("Uppercase", "icons/uppercase.png"),
            ("Lowercase", "icons/lowercase.png"),
            ("Title Case", "icons/titlecase.png"),  
            ("Reverse", "icons/reverse.png"),
            ("Count Words", "icons/count-word.png"),
            ("Count Characters", "icons/count-characters.png"),
        ]:
            act = self.menu.addAction(QIcon(icon_path), action)
            act.setToolTip(f"Convert text to {action.lower()}")

            # Connect each action to a specific method
            if action == "Uppercase":
                act.triggered.connect(lambda: self.menu_action_selected("uppercase"))
            elif action == "Lowercase":
                act.triggered.connect(lambda: self.menu_action_selected("lowercase"))
            elif action == "Title Case":  # Add this block
                    act.triggered.connect(lambda: self.menu_action_selected("titlecase"))
            elif action == "Reverse":
                act.triggered.connect(lambda: self.menu_action_selected("reverse"))
            elif action == "Count Words":
                act.triggered.connect(lambda: self.menu_action_selected("count_words"))
            elif action == "Count Characters":
                act.triggered.connect(lambda: self.menu_action_selected("count_characters"))


        more_transformations_menu = self.menu.addMenu("More Transformations")
        more_transformations_menu.setIcon(QIcon("icons/more.png"))

        for action, icon_path in [
            ("Clear Format", "icons/clear-format.png"), 
            ("Remove Double Lines", "icons/remove-double-lines.png"),
            ("Remove Double Spaces", "icons/remove-double-space.png")
        ]:
            act = more_transformations_menu.addAction(QIcon(icon_path), action)
            act.setToolTip(f"{action}")
            # Connect each action to a specific method
            if action == "Clear Format":
                act.triggered.connect(lambda: self.menu_action_selected("clear_format"))
            elif action == "Remove Double Lines":
                act.triggered.connect(lambda: self.menu_action_selected("remove_double_lines"))
            elif action == "Remove Double Spaces":
                act.triggered.connect(lambda: self.menu_action_selected("remove_double_spaces"))


         # Adding the 'Close Text Transformation' action at the end of the menu
        close_action = QAction("Close Transformation", self)
        close_action.setIcon(QIcon("icons/close.png"))
        close_action.triggered.connect(lambda: self.menu_action_selected("close"))
        self.menu.addAction(close_action)


        self.menu.exec(QCursor.pos())


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
        
        # Wait a bit for the clipboard to update
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
                time.sleep(0.125)
                pyautogui.write(transformed_text)


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
            pass
        elif transformation == "remove_double_lines":
            return '\n'.join(line for line in copied_text.splitlines() if line)
        elif transformation == "remove_double_spaces":
            return ' '.join(copied_text.split())


if __name__ == "__main__":
    logging.info(f"Initialize")
    setup_logging()
    app = QApplication(sys.argv)
    window = MainWindow()

    keyboard_listener = keyboard.Listener(on_press=window.on_press, on_release=window.on_release)
    # mouse_listener = mouse.Listener(on_click=window.on_click)

    keyboard_listener.start()
    # mouse_listener.start()

    sys.exit(app.exec())