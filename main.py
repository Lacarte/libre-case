import sys
import pyperclip
from PyQt6.QtWidgets import QApplication, QMainWindow, QMenu
from PyQt6.QtGui import QIcon, QCursor
from PyQt6.QtCore import pyqtSignal, QObject
from pynput import mouse, keyboard
import win32clipboard
import win32con
import pygetwindow as gw
import pyautogui
import time
from PyQt6.QtCore import QEvent
import logging
from utils import setup_logging
from datetime import datetime, timedelta
from PyQt6.QtWidgets import QApplication, QMainWindow, QMenu
from PyQt6.QtGui import QIcon, QCursor, QMouseEvent 
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtCore import pyqtSignal, QObject, QTimer, QEvent

class ClickSignal(QObject):
    clicked = pyqtSignal(int, int)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
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

    def show_context_menu(self, x, y):
        self.menu = QMenu()
        # self.menu.installEventFilter(self)
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

        for action, icon_path in [("Uppercase", "icons/uppercase.png"), ("Lowercase", "icons/lowercase.png"), ("Reverse", "icons/reverse.png"), ("Close", "icons/close.png"), ("Exit", "icons/exit.png")]:
            act = self.menu.addAction(QIcon(icon_path), action)
            act.setToolTip(f"Convert text to {action.lower()}")

            # Connect each action to a specific method
            if action == "Uppercase":
                act.triggered.connect(lambda: self.menu_action_selected("uppercase"))
            elif action == "Lowercase":
                act.triggered.connect(lambda: self.menu_action_selected("lowercase"))
            elif action == "Reverse":
                act.triggered.connect(lambda: self.menu_action_selected("reverse"))
            elif action == "Close":
                act.triggered.connect(lambda: self.menu_action_selected("close"))
            elif action == "Exit":
                act.triggered.connect(lambda: self.menu_action_selected("exit"))

        self.menu.exec(QCursor.pos())


    def eventFilter(self, source, event):
        if source == self.menu:
            if event.type() == QEvent.Type.FocusOut:
                self.menu.close()
                return True
                
            if event.type() == QEvent.Type.MouseButtonPress:
                if not isinstance(event, QMouseEvent):
                    return False
                    
                if not self.menu.geometry().contains(event.pos()):
                    self.menu.close()
                    return True

        return super(MainWindow, self).eventFilter(source, event)

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
        time.sleep(0.5)

        # Get the new clipboard content
        new_clipboard = pyperclip.paste()
        logging.info(f"new_clipboard : {new_clipboard}")

        # If you want to restore the original content after some operations,
        # you can uncomment the following line
        pyperclip.copy(original_clipboard)

        return new_clipboard


    def menu_action_selected(self, action):
        if action == "exit":
            sys.exit(0)
        elif action == "close":
            return
        else:
            # Logic for other actions like Uppercase, Lowercase, and Reverse
            copied_text = self.copy_without_clearing_clipboard()
            logging.info(f"Copied text: {copied_text}")
            transformed_text = self.transform_text(action, copied_text)
            logging.info(f"Transformed text: {transformed_text}")
            time.sleep(0.25)
            pyautogui.write(transformed_text)


    def transform_text(self, transformation, copied_text):
        # Logic for transforming text
        if transformation == "uppercase":
            logging.info(f"Transforming to uppercase text: {copied_text}")
            return copied_text.upper()
        elif transformation == "lowercase":
            logging.info(f"Transforming to lowercase text: {copied_text}")
            return copied_text.lower()
        elif transformation == "reverse":
            logging.info(f"Transforming to reverse text: {copied_text}")
            return copied_text[::-1]

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