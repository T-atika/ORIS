import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QRadioButton, \
    QHBoxLayout, QCheckBox, QPushButton, QComboBox, QListWidget, QListWidgetItem, QMessageBox


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tasks = []
        self.tasks_cnt = 0

        self.counter_label = QLabel("Created tasks: 0")

        self.setWindowTitle("To-Do List")
        self.resize(400, 300)

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

        self.check_box_1 = QCheckBox("Important")
        self.check_box_2 = QCheckBox("Send notification")

        self.button_layout = QHBoxLayout()
        self.button_create = QPushButton("Create task")
        self.button_remove = QPushButton("Delete last task")
        self.button_clear = QPushButton("Clear form")
        self.button_clear_list = QPushButton("Clear list")
        self.button_layout.addWidget(self.button_create)
        self.button_layout.addWidget(self.button_remove)
        self.button_layout.addWidget(self.button_clear)
        self.button_layout.addWidget(self.button_clear_list)

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
        self.vbox.addWidget(self.check_box_1)
        self.vbox.addWidget(self.check_box_2)
        self.vbox.addLayout(self.button_layout)
        self.vbox.addWidget(self.status_task)
        self.vbox.addWidget(self.filter_task)
        self.vbox.addWidget(self.task_list)
        self.vbox.addWidget(self.counter_label)

        self.filter_task.currentTextChanged.connect(self.update_tasks)
        self.button_create.clicked.connect(self.create_task)
        self.button_remove.clicked.connect(self.delete_task)
        self.button_clear.clicked.connect(self.clear_form)
        self.line_edit_task.textChanged.connect(self.title_changed)
        self.button_clear_list.clicked.connect(self.clear_list)

        self.setStyleSheet("""
        QMainWindow{background-color: #FFB6C1}
        QPushButton{background-color: #FFFAFA; color: #C71585}
        """)

    def create_task(self):
        line = self.line_edit_task.text().strip()

        if not line:
            QMessageBox.warning(self, "Ошибка валидации", "Название задачи не должно быть пустым" )
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
            "task": line,
            "description": text,
            "priority": priority,
            "important": important_cb,
            "send": send_cb,
        }

        self.tasks.append(task_data)
        self.tasks_cnt += 1

        self.update_tasks()
        self.counter_label.setText(f"Created tasks: {self.tasks_cnt}")
        self.clear_form()
        self.status_task.setText(f"Задача создана")

    def delete_task(self):
        if not self.tasks:
            self.status_task.setText("Задач: 0")
            return

        self.tasks.pop()
        self.tasks_cnt -= 1

        self.update_tasks()
        self.counter_label.setText(f"Created tasks: {self.tasks_cnt}")
        self.status_task.setText("Status: Task deleted")

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
            item = QListWidgetItem(f'№{i}. {task["task"]} - {task["priority"]}')
            decs = task["description"] if "description" in task else ""
            item.setToolTip(f'Описание: {decs} \nВажная: {task["important"]}\nУведомление: {task["send"]}')

            self.task_list.addItem(item)

    def clear_form(self):
        reply = QMessageBox.question(self, "Подтверждение", "Хотите очистить форму?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:

            self.line_edit_task.clear()
            self.line_edit_description.clear()

            self.medium.setChecked(True)
            self.check_box_1.setChecked(False)
            self.check_box_2.setChecked(False)

            self.status_task.setText("Status: Task cleared")

        else:
            self.status_task.setText("Отмена отчистки")

    def clear_list(self):
        if not self.tasks:
            QMessageBox.warning(self, "Внимание", "Список задач и так пуст")
            return

        reply = QMessageBox.question(self, "Подтверждение", "Хотите удалить все задачи?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.tasks.clear()
            self.task_list.clear()
            self.tasks_cnt = 0

            self.update_tasks()
            self.counter_label.setText(f"Created tasks: {self.tasks_cnt}")
            self.status_task.setText("Status: Task cleared")

        else:
            self.status_task.setText("Отмена отчистки")

    def title_changed(self, text):
        self.char_cnt_label.setText(f"Название: {len(text)} символов")


if __name__ == "__main__":
    app1 = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app1.exec())
