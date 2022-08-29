from PyQt5 import QtWidgets, uic
import json, os

class SettingsUi(QtWidgets.QDialog):

	def __init__(self):
		super(SettingsUi, self).__init__() # Call the inherited classes __init__ method
		uic.loadUi('ui/settings.ui', self) # Load the .ui file
	
		self.setFixedSize(self.size())
		self.btn_save.clicked.connect(self.save)
		self.btn_proxy_selection.clicked.connect(self.select_proxy)
		self.btn_clear_proxy.clicked.connect(self.clear_proxy)
		self.btn_cancel.clicked.connect(self.close)

		self.le_gpassword.setEchoMode(QtWidgets.QLineEdit.Password)

		self.loadSettings()
		self.show()

		
	def save(self):
		settings = {
			"proxy_file":self.lb_proxy_selection.text(),
			"gmail":self.le_gmail.text(),
			"gmail_password":self.le_gpassword.text(),
			"email_to_notify":self.le_email_to_notify.text(),
			"number_of_threads":self.le_number_of_threads.text(),
			"headless":self.cb_headless.isChecked()
		}

		if os.path.isfile(settings["proxy_file"]) or settings["proxy_file"] == "-":
			if(len(settings["gmail"]) > 0 and settings["gmail"].find("@gmail.com") > 0):
				if(len(settings["gmail_password"]) == 16):
					if(len(settings["email_to_notify"]) > 0 and settings["email_to_notify"].find("@") > 0):
						
						try:
							settings["number_of_threads"] = int(settings["number_of_threads"])
							if settings["number_of_threads"] < 1 or settings["number_of_threads"] > 100: raise ValueError("")
							with open('settings.json', 'w') as outfile: json.dump(settings, outfile)
							QtWidgets.QMessageBox.about(self, "Success", "Settings Updated!")
							self.close()

						except (ValueError, TypeError):  QtWidgets.QMessageBox.about(self, "Error", "Threads must be a number between 1 - 100")

					else: QtWidgets.QMessageBox.about(self, "Error", "Email to notify is invalid.")
				else: QtWidgets.QMessageBox.about(self, "Error", "Gmail password is invalid.")
			else: QtWidgets.QMessageBox.about(self, "Error", "Gmail is invalid.")
		else: QtWidgets.QMessageBox.about(self, "Error", "Proxy file not found.")

	def loadSettings(self):
		if os.path.isfile("settings.json"):
			
			with open('settings.json') as json_file: settings = json.load(json_file)
			self.lb_proxy_selection.setText(settings["proxy_file"])
			self.le_gmail.setText(settings["gmail"])
			self.le_gpassword.setText(settings["gmail_password"])
			self.le_email_to_notify.setText(settings["email_to_notify"])
			self.le_number_of_threads.setText(str(settings["number_of_threads"]))
			self.cb_headless.setChecked(settings["headless"])

		else: QtWidgets.QMessageBox.about(self, "Warning", "It seems that it's you first time running this app, please fill settings.")

	def select_proxy(self):
		dlg = QtWidgets.QFileDialog()
		dlg.setNameFilters(["Text files (*.txt)"])
		dlg.selectNameFilter("Text files (*.txt)")

		if dlg.exec_():
			filenames = dlg.selectedFiles()
			self.lb_proxy_selection.setText(filenames[0])

	def clear_proxy(self):
		self.lb_proxy_selection.setText("-")