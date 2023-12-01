import sys
import pyperclip  # Used for clipboard operations
from PyQt6.QtWidgets import QApplication, QMainWindow, QMenu
from PyQt6.QtGui import QCursor
from PyQt6.QtCore import pyqtSignal, QObject
from pynput import mouse, keyboard
import win32gui
import win32api
import win32con
import win32gui
import win32clipboard
import win32con
import pygetwindow as gw
import pyperclip
import pyautogui
import time

class ClickSignal(QObject):
    clicked = pyqtSignal(int, int)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.click_signal = ClickSignal()
        self.click_signal.clicked.connect(self.show_context_menu)
        self.is_shift_pressed = False
        self.selected_text = ""

    def on_click(self, x, y, button, pressed):
        if self.is_shift_pressed and button == mouse.Button.right and pressed:
            self.click_signal.clicked.emit(x, y)

    def on_press(self, key):
        if key == keyboard.Key.shift_l:
            self.is_shift_pressed = True

    def on_release(self, key):
        if key == keyboard.Key.shift_l:
            self.is_shift_pressed = False

    def show_context_menu(self, x, y):
        menu = QMenu()
        for action in ["Uppercase", "Lowercase", "Reverse", "Close", "Exit"]:
            act = menu.addAction(action)
            act.triggered.connect(lambda _, a=action: self.menu_action_selected(a))
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
        # Save the current clipboard content
        original_clipboard = pyperclip.paste()

        # Simulate the Ctrl+C (copy) keyboard command
        pyautogui.hotkey('ctrl', 'c')
        
        # Wait a bit for the clipboard to update
        time.sleep(0.5)

        # Get the new clipboard content
        new_clipboard = pyperclip.paste()

        # If you want to restore the original content after some operations,
        # you can uncomment the following line
        # pyperclip.copy(original_clipboard)

        return new_clipboard


    def transform_text(self,transformation,copied_text):
        pyautogui.sleep(0.1)
        if transformation == "uppercase":
            transformed_text = copied_text.upper()
        elif transformation == "lowercase":
            transformed_text = copied_text.lower()
        elif transformation == "reverse":
            transformed_text = copied_text[::-1]
        return transformed_text

    def menu_action_selected(self, action):
        if action == "Exit":
            sys.exit(0)
        elif action == "Close":
            return
        else:
            copied_text = self.copy_without_clearing_clipboard()
            print("Copied text:", copied_text)
            transform_text = self.transform_text(action.lower(), copied_text)  # Corrected this line
            print(f"transform_text >> {transform_text}")
            pyautogui.write(transform_text)

            # active_window_title = self.get_active_window_title()
            # print(active_window_title)
            


app = QApplication(sys.argv)
window = MainWindow()

keyboard_listener = keyboard.Listener(
    on_press=window.on_press, 
    on_release=window.on_release
)
mouse_listener = mouse.Listener(
    on_click=window.on_click
)

keyboard_listener.start()
mouse_listener.start()

sys.exit(app.exec())
