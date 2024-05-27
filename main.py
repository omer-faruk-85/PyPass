import sys
import sqlite3
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog
from PyQt5.QtGui import QClipboard

class PasswordManager(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.initDB()  # initDB'yi initUI'den önce çağırıyoruz
        self.initUI()

    def initUI(self):
        self.setWindowTitle(f'Password Manager - {self.username}')
        self.setGeometry(100, 100, 800, 400)

        layout = QVBoxLayout()

        form_layout = QHBoxLayout()
        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText('Name')
        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText('URL')
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText('Username')
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText('Password')
        self.note_input = QLineEdit(self)
        self.note_input.setPlaceholderText('Note')

        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.url_input)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.note_input)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        add_button = QPushButton('Add', self)
        add_button.clicked.connect(self.add_entry)
        update_button = QPushButton('Update', self)
        update_button.clicked.connect(self.update_entry)
        delete_button = QPushButton('Delete', self)
        delete_button.clicked.connect(self.delete_entry)
        import_button = QPushButton('Import CSV', self)
        import_button.clicked.connect(self.import_csv)
        export_button = QPushButton('Export CSV', self)
        export_button.clicked.connect(self.export_csv)

        button_layout.addWidget(add_button)
        button_layout.addWidget(update_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(import_button)
        button_layout.addWidget(export_button)

        layout.addLayout(button_layout)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText('Search by URL or Username')
        search_button = QPushButton('Search', self)
        search_button.clicked.connect(self.search_entries)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)

        layout.addLayout(search_layout)

        self.table = QTableWidget(self)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['ID', 'Name', 'URL', 'Username', 'Password', 'Note'])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.cellClicked.connect(self.load_entry)
        self.table.cellDoubleClicked.connect(self.copy_password)

        layout.addWidget(self.table)

        self.setLayout(layout)
        self.load_entries()

    def initDB(self):
        self.conn = sqlite3.connect('password_manager.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS passwords
                          (id INTEGER PRIMARY KEY, username TEXT, name TEXT, url TEXT, username_entry TEXT, password TEXT, note TEXT)''')
        self.conn.commit()

    def add_entry(self):
        name = self.name_input.text()
        url = self.url_input.text()
        username_entry = self.username_input.text()
        password = self.password_input.text()
        note = self.note_input.text()
        if name and url and username_entry and password:
            self.c.execute("INSERT INTO passwords (username, name, url, username_entry, password, note) VALUES (?, ?, ?, ?, ?, ?)", (self.username, name, url, username_entry, password, note))
            self.conn.commit()
            self.load_entries()
            self.clear_inputs()
        else:
            QMessageBox.warning(self, 'Input Error', 'All fields except Note are required!')

    def update_entry(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            entry_id_item = self.table.item(current_row, 0)
            if entry_id_item is None:
                QMessageBox.warning(self, 'Selection Error', 'No entry selected!')
                return

            entry_id = int(entry_id_item.text())
            name = self.name_input.text()
            url = self.url_input.text()
            username_entry = self.username_input.text()
            password = self.password_input.text()
            note = self.note_input.text()
            if name and url and username_entry and password:
                self.c.execute("UPDATE passwords SET name=?, url=?, username_entry=?, password=?, note=? WHERE id=? AND username=?", (name, url, username_entry, password, note, entry_id, self.username))
                self.conn.commit()
                self.load_entries()
                self.clear_inputs()
            else:
                QMessageBox.warning(self, 'Input Error', 'All fields except Note are required!')
        else:
            QMessageBox.warning(self, 'Selection Error', 'No entry selected!')

    def delete_entry(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            entry_id_item = self.table.item(current_row, 0)
            if entry_id_item is None:
                QMessageBox.warning(self, 'Selection Error', 'No entry selected!')
                return

            entry_id = int(entry_id_item.text())
            self.c.execute("DELETE FROM passwords WHERE id=? AND username=?", (entry_id, self.username))
            self.conn.commit()
            self.load_entries()
            self.clear_inputs()
        else:
            QMessageBox.warning(self, 'Selection Error', 'No entry selected!')

    def load_entries(self):
        self.table.setRowCount(0)
        self.c.execute("SELECT id, name, url, username_entry, password, note FROM passwords WHERE username=?", (self.username,))
        rows = self.c.fetchall()
        for row in rows:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            for column, data in enumerate(row):
                self.table.setItem(row_position, column, QTableWidgetItem(str(data)))

    def load_entry(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            id_item = self.table.item(current_row, 0)
            name_item = self.table.item(current_row, 1)
            url_item = self.table.item(current_row, 2)
            username_item = self.table.item(current_row, 3)
            password_item = self.table.item(current_row, 4)
            note_item = self.table.item(current_row, 5)

            if id_item and name_item and url_item and username_item and password_item and note_item:
                self.name_input.setText(name_item.text())
                self.url_input.setText(url_item.text())
                self.username_input.setText(username_item.text())
                self.password_input.setText(password_item.text())
                self.note_input.setText(note_item.text())
            else:
                QMessageBox.warning(self, 'Load Error', 'Failed to load entry!')

    def clear_inputs(self):
        self.name_input.clear()
        self.url_input.clear()
        self.username_input.clear()
        self.password_input.clear()
        self.note_input.clear()

    def import_csv(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_name:
            try:
                df = pd.read_csv(file_name)
                for index, row in df.iterrows():
                    self.c.execute("INSERT INTO passwords (username, name, url, username_entry, password, note) VALUES (?, ?, ?, ?, ?, ?)", (self.username, row['name'], row['url'], row['username'], row['password'], row['note']))
                self.conn.commit()
                self.load_entries()
                QMessageBox.information(self, 'Success', 'CSV file imported successfully!')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to import CSV file: {e}')

    def export_csv(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save CSV File", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_name:
            try:
                self.c.execute("SELECT name, url, username_entry, password, note FROM passwords WHERE username=?", (self.username,))
                rows = self.c.fetchall()
                df = pd.DataFrame(rows, columns=['name', 'url', 'username', 'password', 'note'])
                df.to_csv(file_name, index=False)
                QMessageBox.information(self, 'Success', 'CSV file exported successfully!')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to export CSV file: {e}')

    def search_entries(self):
        search_text = self.search_input.text()
        query = "SELECT * FROM passwords WHERE username=? AND (url LIKE ? OR username_entry LIKE ?)"
        self.c.execute(query, (self.username, '%' + search_text + '%', '%' + search_text + '%'))
        rows = self.c.fetchall()
        self.table.setRowCount(0)
        for row in rows:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            for column, data in enumerate(row):
                self.table.setItem(row_position, column, QTableWidgetItem(str(data)))

    def copy_password(self, row, column):
        if column == 4:  # Password column
            password = self.table.item(row, column).text()
            clipboard = QApplication.clipboard()
            clipboard.setText(password)
            QMessageBox.information(self, 'Copied', 'Password copied to clipboard!')

    def closeEvent(self, event):
        self.conn.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PasswordManager("default_user")
    ex.show()
    sys.exit(app.exec_())