from PyQt5 import QtCore, QtWidgets, uic
import json, datetime

class NewEventUi(QtWidgets.QDialog):
	addEventClicked = QtCore.pyqtSignal(str)

	def __init__(self):
		super(NewEventUi, self).__init__() # Call the inherited classes __init__ method
		uic.loadUi('ui/new_event.ui', self) # Load the .ui file
		
		self.setFixedSize(self.size())
		self.btn_add_event.clicked.connect(self.addEvent)
		self.btn_reset.clicked.connect(self.reset)
		self.btn_cancel.clicked.connect(self.close)
		
		self.le_event_url.setText("https://tix.axs.com/Q8AgOAAAAADD2kl0CwAAAADB%2fv%2f%2f%2fwD%2f%2f%2f%2f%2fDENpdHlPZkRlbnZlcgD%2f%2f%2f%2f%2f%2f%2f%2f%2f%2fw%3d%3d/shop/search?locale=en-US")

		self.show()

		
	def addEvent(self):
		event_name = self.le_event_name.text()
		event_url = self.le_event_url.text()
		max_ticket_cost = self.le_max_ticket_cost.text()
		ignore_text = self.le_ignore_text.text()
		event_interval = self.le_interval.text()

		if len(event_name) > 0:
			if event_url.find("tix.axs.com") > 0:

				try:
					max_ticket_cost = int(max_ticket_cost)
					if max_ticket_cost < 1 or max_ticket_cost > 1000: raise ValueError("")

					try:
						event_interval = int(event_interval)
						if event_interval < 1 or event_interval > 30: raise ValueError("")
						new_event = {
							"event_name":event_name,
							"event_url":event_url,
							"max_ticket_cost":max_ticket_cost,
							"ignore_text":ignore_text,
							"interval":event_interval,
							"last_check": "-",
							"added_on": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
						}

						self.addEventClicked.emit(json.dumps(new_event))
						self.close()
					except (TypeError, ValueError): QtWidgets.QMessageBox.about(self, "Error", "Interval must be an integer in range 1-30")
				except (TypeError, ValueError): QtWidgets.QMessageBox.about(self, "Error", "Max ticket cost must be an integer in range 1-1000")
			else: QtWidgets.QMessageBox.about(self, "Error", "Invalid URL")
		else: QtWidgets.QMessageBox.about(self, "Error", "Event name cannot be empty.")

	def reset(self):
		self.le_event_name.setText("")
		self.le_event_url.setText("")
		self.le_max_ticket_cost.setText("")
		self.le_ignore_text.setText("")
		self.le_interval.setText("")

	def setEvent(self, task):
		self.setWindowTitle("Update Event")
		self.le_event_name.setEnabled(False)
		self.btn_add_event.setText("Update")
		self.btn_reset.setEnabled(False)
		
		self.le_event_name.setText(task["event_name"])
		self.le_event_url.setText(task["event_url"])
		self.le_max_ticket_cost.setText(str(task["max_ticket_cost"]))
		self.le_ignore_text.setText(task["ignore_text"])
		self.le_interval.setText(str(task["interval"]))
