import os
import sys
import json

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QRadioButton, \
    QHBoxLayout, QCheckBox, QPushButton, QComboBox, QListWidget, QListWidgetItem, QMessageBox, QDialog
from PyQt6.QtCore import pyqtSignal, Qt

TASKS_FILE = os.path.join(os.path.dirname(__file__), 'tasks.json')


class MainWindow(QMainWindow):
    task_created = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.tasks = []
        self.next_task_id = 1

        self.counter_label = QLabel("Created tasks: 0")

        self.setWindowTitle("To-Do List")
        self.resize(600, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.vbox = QVBoxLayout()
        central_widget.setLayout(self.vbox)

        self.label_task = QLabel("Task")
        self.line_edit_task = QLineEdit()

        self.char_cnt_label = QLabel("Название: 0 символов")

        self.label_description = QLabel("Description")
        self.line_edit_description = QTextEdit()

        self.radio_layout = QHBoxLayout()

        self.low = QRadioButton("Low")
        self.medium = QRadioButton("Medium")
        self.high = QRadioButton("High")
        self.medium.setChecked(True)

        self.radio_layout.addWidget(self.low)
        self.radio_layout.addWidget(self.medium)
        self.radio_layout.addWidget(self.high)

        self.ch_layout = QHBoxLayout()
        self.check_box_1 = QCheckBox("Important")
        self.check_box_2 = QCheckBox("Send notification")
        self.ch_layout.addWidget(self.check_box_1)
        self.ch_layout.addWidget(self.check_box_2)

        self.button_layout = QHBoxLayout()
        self.button_create = QPushButton("Create task")
        self.button_remove = QPushButton("Delete last task")
        self.button_clear = QPushButton("Clear form")
        self.button_clear_list = QPushButton("Clear list")
        self.button_about = QPushButton("About")
        self.button_del_select = QPushButton("Delete task")
        self.button_del_select.setEnabled(False)
        self.button_layout.addWidget(self.button_create)
        self.button_layout.addWidget(self.button_remove)
        self.button_layout.addWidget(self.button_clear)
        self.button_layout.addWidget(self.button_clear_list)
        self.button_layout.addWidget(self.button_about)
        self.button_layout.addWidget(self.button_del_select)

        self.filter_task = QComboBox()
        self.filter_task.addItems(["All", "Low", "Medium", "High"])

        self.status_task = QLabel("status: ready")

        self.task_list = QListWidget()

        self.vbox.addWidget(self.label_task)
        self.vbox.addWidget(self.line_edit_task)
        self.vbox.addWidget(self.char_cnt_label)
        self.vbox.addWidget(self.label_description)
        self.vbox.addWidget(self.line_edit_description)
        self.vbox.addLayout(self.radio_layout)
        self.vbox.addLayout(self.ch_layout)
        self.vbox.addLayout(self.button_layout)
        self.vbox.addWidget(self.status_task)
        self.vbox.addWidget(self.filter_task)
        self.vbox.addWidget(self.task_list)
        self.vbox.addWidget(self.counter_label)

        self.filter_task.currentTextChanged.connect(self.update_tasks)
        self.task_list.itemDoubleClicked.connect(self.edit_task)
        self.button_create.clicked.connect(self.create_task)
        self.button_remove.clicked.connect(self.delete_task)
        self.button_clear.clicked.connect(self.clear_form)
        self.line_edit_task.textChanged.connect(self.title_changed)
        self.button_clear_list.clicked.connect(self.clear_list)
        self.task_created.connect(self.on_task_created)
        self.button_about.clicked.connect(self.show_about)
        self.button_del_select.clicked.connect(self.delete_task_sel)
        self.task_list.itemSelectionChanged.connect(self.on_selection_changed)

        self.load_tasks()
        self.update_tasks()
        self.counter_label.setText(f"Created tasks: {len(self.tasks)}")

        self.setStyleSheet("""
        QMainWindow{background-color: #FFB6C1}
        QPushButton{background-color: #FFFAFA; color: #C71585}
        QPushButton:hover {background-color: #D8BFD8}
        QPushButton:disabled {background-color: #f0eaee; color: #cec0c5}
        QlineEdit{background-color: #FFF0F5}
        QTextEdit{background-color: #FFF0F5}
        """)

    def on_selection_changed(self):
        has_selection = self.task_list.currentItem() is not None
        self.button_del_select.setEnabled(has_selection)

    def create_task(self):
        line = self.line_edit_task.text().strip()

        if not line:
            QMessageBox.warning(self, "Ошибка валидации", "Название задачи не должно быть пустым")
            return

        text = self.line_edit_description.toPlainText()

        if self.low.isChecked():
            priority = "Low"
        elif self.medium.isChecked():
            priority = "Medium"
        elif self.high.isChecked():
            priority = "High"

        if self.check_box_1.isChecked():
            important_cb = "Yes"
        else:
            important_cb = "No"

        if self.check_box_2.isChecked():
            send_cb = "Yes"
        else:
            send_cb = "No"

        task_data = {
            "id": self.next_task_id,
            "task": line,
            "description": text,
            "priority": priority,
            "important": important_cb,
            "send": send_cb,
        }
        self.next_task_id += 1

        self.tasks.append(task_data)
        self.task_created.emit(task_data)

    def on_task_created(self, task_data):
        self.update_tasks()
        self.counter_label.setText(f"Created tasks: {len(self.tasks)}")
        self.status_task.setText(f"Задача создана")
        self.clear_form()
        self.save_tasks()

    def delete_task(self):
        if not self.tasks:
            self.status_task.setText("Задач: 0")
            return

        self.tasks.pop()

        self.update_tasks()
        self.save_tasks()
        self.counter_label.setText(f"Created tasks: {len(self.tasks)}")
        self.status_task.setText("Status: Task deleted")

    def delete_task_sel(self):
        current_task = self.task_list.currentItem()

        task_id = current_task.data(Qt.ItemDataRole.UserRole)

        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите удалить выбранную задачу?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.tasks = [task for task in self.tasks if task["id"] != task_id]
            self.update_tasks()
            self.counter_label.setText(f"Created tasks: {len(self.tasks)}")
            self.status_task.setText("Status: Task deleted")
            self.save_tasks()

    def update_tasks(self):
        self.task_list.clear()

        if not self.tasks:
            self.task_list.addItem("Задач пока нет...")
            self.status_task.setText("Задач: 0")
            return

        curr_task = self.filter_task.currentText()

        if curr_task == "All":
            filter_tasks = self.tasks
        else:
            filter_tasks = [task for task in self.tasks if task['priority'] == curr_task]

        if not filter_tasks:
            self.status_task.setText("No task")
            return

        for i, task in enumerate(filter_tasks, start=1):
            decs = task["description"] if "description" in task else ""
            item = QListWidgetItem(
                f'№{i}. {task["task"]} - {task["priority"]}\nОписание: {decs} \nВажная: {task["important"]}\nУведомление: {task["send"]}')
            item.setData(Qt.ItemDataRole.UserRole, task['id'])
            self.task_list.addItem(item)

    def save_tasks(self):
        try:
            with open(TASKS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Оштбка сохранения:{e}")

    def load_tasks(self):
        if os.path.exists(TASKS_FILE):
            try:
                with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)

                    if self.tasks:
                        self.next_task_id = max(task["id"] for task in self.tasks) + 1
                    else:
                        self.next_task_id = 1
            except Exception as e:
                print("Ошибка загрузки {e}")
                self.tasks = []
                self.next_task_id = 1
        else:
            self.tasks = []
            self.next_task_id = 1

    def clear_form(self):
        self.line_edit_task.clear()
        self.line_edit_description.clear()

        self.medium.setChecked(True)
        self.check_box_1.setChecked(False)
        self.check_box_2.setChecked(False)

        self.status_task.setText("Status: Task cleared")

    def clear_list(self):
        if not self.tasks:
            QMessageBox.warning(self, "Внимание", "Список задач и так пуст")
            return

        reply = QMessageBox.question(self, "Подтверждение", "Хотите удалить все задачи?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.tasks.clear()
            self.task_list.clear()

            self.update_tasks()
            self.counter_label.setText(f"Created tasks: {len(self.tasks)}")
            self.status_task.setText("Status: Task cleared")
            self.save_tasks()

        else:
            self.status_task.setText("Отмена отчистки")

    def title_changed(self, text):
        self.char_cnt_label.setText(f"Название: {len(text)} символов")

    def show_about(self):
        dialog = Dialog()
        dialog.exec()

    def edit_task(self, item):
        task_id = item.data(Qt.ItemDataRole.UserRole)

        task_to_edit = None
        for task in self.tasks:
            if task["id"] == task_id:
                task_to_edit = task
                break
        dialog = EditionTask(task_to_edit)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            update_task = dialog.get_task()
            if update_task is None:
                QMessageBox.warning(self, "Ошибка", "Пустое название!")
                return

            for i, task in enumerate(self.tasks):
                if task["id"] == task_id:
                    self.tasks[i] = update_task
                    break

            self.save_tasks()
            self.update_tasks()
            self.status_task.setText("Status: Task edited")


class Dialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("О программе")
        self.resize(400, 300)
        layout = QVBoxLayout()
        self.setLayout(layout)
        name = QLabel("Название - 'To-Do List'")
        ver = QLabel("Версия - 2")
        avtor = QLabel("Автор - Адылева Анастасия")
        description = QLabel("Менджер задач")
        cl_btn = QPushButton("Закрыть")

        layout.addWidget(name)
        layout.addWidget(ver)
        layout.addWidget(avtor)
        layout.addWidget(description)
        layout.addWidget(cl_btn)

        cl_btn.clicked.connect(self.accept)

        self.setStyleSheet("""
        QDialog{background-color: #FFB6C1}
        QPushButton{background-color: #FFFAFA; color: #C71585}
        """)


class EditionTask(QDialog):
    def __init__(self, task_data):
        super().__init__()
        self.setWindowTitle("Редактор задач")
        self.resize(500, 400)

        self.origin_task = task_data

        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("Название:"))
        self.title_edit = QLineEdit(task_data["task"])
        layout.addWidget(self.title_edit)

        layout.addWidget(QLabel("Описание"))
        self.description_edit = QTextEdit(task_data["description"])
        layout.addWidget(self.description_edit)

        layout.addWidget(QLabel("Приоритет"))
        self.priority_edit = QComboBox()
        self.priority_edit.addItems(["Low", "Medium", "High"])
        index = self.priority_edit.findText(task_data["priority"])
        if index >= 0:
            self.priority_edit.setCurrentIndex(index)
        layout.addWidget(self.priority_edit)

        check_layout = QHBoxLayout()
        self.important_check = QCheckBox("Important")
        self.important_check.setChecked(task_data["important"] == "Yes")
        check_layout.addWidget(self.important_check)

        self.send_check = QCheckBox("Send")
        self.send_check.setChecked(task_data["send"] == "Yes")
        check_layout.addWidget(self.send_check)

        layout.addLayout(check_layout)

        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

        self.setStyleSheet("""
        QDialog{background-color: #FFB6C1}
        QPushButton{background-color: #FFFAFA; color: #C71585}
        QPushButton:hover {background-color: #D8BFD8}
        QPushButton:disabled {background-color: #f0eaee; color: #cec0c5}
        QlineEdit{background-color: #FFF0F5}
        QTextEdit{background-color: #FFF0F5}
        """)

    def get_task(self):
        title = self.title_edit.text().strip()
        if not title:
            return None
        return {
            "id": self.origin_task["id"],
            "task": title,
            "description": self.description_edit.toPlainText(),
            "priority": self.priority_edit.currentText(),
            "important": "Yes" if self.important_check.isChecked() else "No",
            "send": "Yes" if self.send_check.isChecked() else "No"
        }


if __name__ == "__main__":
    app1 = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app1.exec())
