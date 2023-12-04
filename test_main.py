import unittest
from main import MainWindow, ClickSignal
from PyQt6.QtWidgets import QApplication, QMenu
from PyQt6.QtGui import QCursor
from PyQt6.QtCore import pyqtSignal
import pyautogui

class TestMainWindow(unittest.TestCase):

    def test_show_context_menu(self):
        app = QApplication([])
        window = MainWindow()
        window.show()
        
        # Emit signal to open context menu 
        window.click_signal.clicked.emit(100, 200)
        
        # Check menu opened at correct position
        self.assertEqual(window.menu.geometry().topLeft(), QCursor.pos())
        
        # Check number of actions
        self.assertEqual(window.menu.actions().__len__(), 5)  
        
        window.menu.close()
        
    def test_transform_text(self):
        window = MainWindow()
        
        text = "Hello World"
        expected_uppercase = "HELLO WORLD"
        self.assertEqual(window.transform_text("uppercase", text), expected_uppercase)
        
        expected_lowercase = "hello world"
        self.assertEqual(window.transform_text("lowercase", text), expected_lowercase)
        
        expected_reverse = "dlroW olleH"
        self.assertEqual(window.transform_text("reverse", text), expected_reverse)
        
if __name__ == '__main__':
    unittest.main()