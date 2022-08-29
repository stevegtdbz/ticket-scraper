from task_manager import TaskManager
from new_event import NewEventUi
from settings import SettingsUi
from PyQt5 import QtWidgets, uic, QtCore
import sys, json, os

class Ui(QtWidgets.QMainWindow):
	
	def __init__(self):
		super(Ui, self).__init__() # Call the inherited classes __init__ method
		uic.loadUi('ui/main_window.ui', self) # Load the .ui file

		self.session_file = "session"
		
		# Init components
		self.btn_manager_toggle.clicked.connect(self.toggleTaskManager)
		self.btn_add_event.clicked.connect(self.drawAddEvent)
		self.btn_edit_event.clicked.connect(self.editEvent)
		self.btn_delete_event.clicked.connect(self.deleteEvent)
		self.btn_settings.clicked.connect(self.drawSettings)
		
		self.table_widget.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
		self.table_widget.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
		self.table_widget.verticalHeader().hide()

		h_header = self.table_widget.horizontalHeader()
		#h_header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
		#h_header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
		#h_header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
		#h_header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
		h_header.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
		h_header.setSectionResizeMode(5, QtWidgets.QHeaderView.Fixed)
		self.table_widget.setColumnWidth(5, 180)
		h_header.setSectionResizeMode(6, QtWidgets.QHeaderView.Fixed)
		self.table_widget.setColumnWidth(6, 180)

		self.task_manager = TaskManager(self.table_widget)

		# Load session
		if os.path.isfile(self.session_file):
			with open(self.session_file) as file:
				for line in file:
					task = json.loads(line.strip())
					self.task_manager.tasks.append(task)
					self.table_append_row(task)

		self.task_manager.start()

		# show gui
		self.show()

	# Add event
	def drawAddEvent(self):
		pop_up_window = NewEventUi()
		pop_up_window.addEventClicked.connect(self.drawAddEventCallBack)
		pop_up_window.exec_()

	def drawAddEventCallBack(self, task):
		task = json.loads(task)
		
		# Append to table widget
		self.table_append_row(task)

		# Append to task manager
		self.task_manager.tasks.append(task)

		# update session file
		self.update_session_file()

	# Edit Event
	def editEvent(self):
		for row in range(self.table_widget.rowCount()):
			item = self.table_widget.item(row, 0)
			if item.isSelected():
				task_name = item.text()
				selected_task = self.task_manager.getTaskByEventName(task_name)

				pop_up_window = NewEventUi()
				pop_up_window.setEvent(selected_task)
				pop_up_window.addEventClicked.connect(self.drawUpdateEventCallBack)
				pop_up_window.exec_()
				return
		
		QtWidgets.QMessageBox.about(self, "Warning", "Please select an event first.")

	def drawUpdateEventCallBack(self, task):
		task = json.loads(task)
		
		# update tasks
		self.task_manager.updateTask(task)

		# update session file
		self.update_session_file()

		# update ui
		self.table_widget.setRowCount(0)
		for task in self.task_manager.tasks: self.table_append_row(task)

	# Delete event
	def deleteEvent(self):
		new_tasks = self.task_manager.tasks
		del_row = -1
		for row in range(self.table_widget.rowCount()):
			item = self.table_widget.item(row, 0)
			if item.isSelected():
				del_row = row
				selected_task = self.task_manager.getTaskByEventName(item.text())
				new_tasks.remove(selected_task)
				break

		self.task_manager.tasks = new_tasks
		if del_row >= 0:
			self.table_widget.removeRow(del_row)
		else: QtWidgets.QMessageBox.about(self, "Warning", "Please select an event first.")

		# update session file
		self.update_session_file()

	def drawSettings(self):
		pop_up_window = SettingsUi()
		pop_up_window.exec_()

	def toggleTaskManager(self):
		if self.task_manager.running == False:
			self.btn_manager_toggle.setText("Stop Task(s)")
			self.task_manager.running = True
		else:
			self.btn_manager_toggle.setText("Start Task(s)")
			self.task_manager.running = False

	# Help methods
	def table_append_row(self, data):
		row_count = self.table_widget.rowCount()
		self.table_widget.insertRow(row_count)
		self.table_widget.setItem(row_count, 0, QtWidgets.QTableWidgetItem(data["event_name"]))
		self.table_widget.setItem(row_count, 1, QtWidgets.QTableWidgetItem(str(data["interval"])+" min"))
		self.table_widget.setItem(row_count, 2, QtWidgets.QTableWidgetItem("$"+str(data["max_ticket_cost"])))
		self.table_widget.setItem(row_count, 3, QtWidgets.QTableWidgetItem(data["ignore_text"]))
		self.table_widget.setItem(row_count, 4, QtWidgets.QTableWidgetItem(data["event_url"]))
		self.table_widget.setItem(row_count, 5, QtWidgets.QTableWidgetItem(data["added_on"]))
		self.table_widget.setItem(row_count, 6, QtWidgets.QTableWidgetItem(data["last_check"]))

	def update_session_file(self):
		f = open(self.session_file, "w")
		for task in self.task_manager.tasks: f.write(json.dumps(task)+"\n")
		f.close()

	# Overwrite methods
	def closeEvent(self, event):
		self.task_manager.terminate = True
		self.close()

	

app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()
