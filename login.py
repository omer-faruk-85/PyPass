import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QInputDialog

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initDB()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Login')
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText('Username')
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText('Password')
        self.password_input.setEchoMode(QLineEdit.Password)

        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)

        button_layout = QHBoxLayout()
        login_button = QPushButton('Login', self)
        login_button.clicked.connect(self.login)
        register_button = QPushButton('Register', self)
        register_button.clicked.connect(self.register)
        reset_button = QPushButton('Reset Password', self)
        reset_button.clicked.connect(self.reset_password)

        button_layout.addWidget(login_button)
        button_layout.addWidget(register_button)
        button_layout.addWidget(reset_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def initDB(self):
        self.conn = sqlite3.connect('user_manager.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS users
                          (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
        self.conn.commit()

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        self.c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = self.c.fetchone()
        if user:
            QMessageBox.information(self, 'Success', 'Login successful!')
            self.close()
            self.open_main_app(username)
        else:
            QMessageBox.warning(self, 'Error', 'Invalid username or password!')

    def register(self):
        username, ok = QInputDialog.getText(self, 'Register', 'Enter a new username:')
        if ok and username:
            password, ok = QInputDialog.getText(self, 'Register', 'Enter a new password:', QLineEdit.Password)
            if ok and password:
                try:
                    self.c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                    self.conn.commit()
                    QMessageBox.information(self, 'Success', 'Registration successful!')
                except sqlite3.IntegrityError:
                    QMessageBox.warning(self, 'Error', 'Username already exists!')

    def reset_password(self):
        username, ok = QInputDialog.getText(self, 'Reset Password', 'Enter your username:')
        if ok and username:
            new_password, ok = QInputDialog.getText(self, 'Reset Password', 'Enter new password:', QLineEdit.Password)
            if ok and new_password:
                self.c.execute("UPDATE users SET password=? WHERE username=?", (new_password, username))
                self.conn.commit()
                QMessageBox.information(self, 'Success', 'Password reset successful!')

    def open_main_app(self, username):
        from main import PasswordManager
        self.main_app = PasswordManager(username)
        self.main_app.show()

    def closeEvent(self, event):
        self.conn.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())

  