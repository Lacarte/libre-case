import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QMenu
from PyQt6.QtGui import QCursor
from PyQt6.QtCore import pyqtSignal, QObject
from pynput import mouse, keyboard

class ClickSignal(QObject):
    # Signal to indicate a right-click event
    clicked = pyqtSignal(int, int)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.click_signal = ClickSignal()
        self.click_signal.clicked.connect(self.show_context_menu)
        self.is_shift_pressed = False

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

    def menu_action_selected(self, action):
        if action == "Exit":
            sys.exit(0)
        elif action == "Close":
            return
        else:
            print(f"Selected Transformation: {action}")

app = QApplication(sys.argv)
window = MainWindow()

# Create and start pynput listeners
keyboard_listener = keyboard.Listener(
    on_press=window.on_press, 
    on_release=window.on_release
)
mouse_listener = mouse.Listener(
    on_click=window.on_click
)

keyboard_listener.start()
mouse_listener.start()

# Start the application
sys.exit(app.exec())
