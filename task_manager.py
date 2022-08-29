import threading, time, datetime, os, json
from scraper import Scraper
from PyQt5 import QtWidgets

class TaskManager(threading.Thread):
	
	def __init__(self, table_widget):
		threading.Thread.__init__(self)
		self.tasks = []
		self.table_widget = table_widget
		self.running = False
		self.terminate = False
   
	def run(self):
		
		while not self.terminate:
			time.sleep(1)
			previous_time_in_minutes = 0

			while(self.running):
				
				# Read settings
				if os.path.isfile("settings.json"):
					with open('settings.json') as json_file: settings = json.load(json_file)
				else:
					print("Settings not found.")
					time.sleep(10)
					continue

				dt = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
				print("[{0}] Checking tasks..".format(dt))
				current_time_in_minutes = int(time.time() / 60)
				if previous_time_in_minutes == current_time_in_minutes:
					time.sleep(1)
					continue # in case of run same minute

				worker_pool = []
				for task in self.tasks:

					# Wait until there is space in pool
					while len(worker_pool) >= settings["number_of_threads"]:
						time.sleep(0.3)
						for worker in worker_pool:
							if not worker.is_alive():
								worker_pool.remove(worker)


					if current_time_in_minutes % task["interval"] == 0: # activate
						print("\tTask for {} activated.".format(task["event_name"]))
						scraper = Scraper(task["event_url"])
						scraper.filter_max_price = task["max_ticket_cost"]
						scraper.filter_ignore_text = task["ignore_text"]
						scraper.headless = settings["headless"]
						scraper.sender_address = settings["gmail"]
						scraper.sender_pass = settings["gmail_password"]
						scraper.receiver_address = settings["email_to_notify"]
						scraper.proxy = settings["proxy_file"]
						scraper.start()

						worker_pool.append(scraper)

						# update row table widget
						for row in range(self.table_widget.rowCount()):
							ev_name = self.table_widget.item(row, 0).text()
							if ev_name == task["event_name"]:
								self.table_widget.setItem(row, 6, QtWidgets.QTableWidgetItem(dt))
								break

				# wait until all threads end
				for worker in worker_pool: worker.join()
				previous_time_in_minutes = current_time_in_minutes
				time.sleep(1)


	def getTaskByEventName(self, event_name):
		for task in self.tasks:
			if task["event_name"] == event_name:
				return task

	def updateTask(self, new_task_data):
		new_tasks = self.tasks
		for task in self.tasks:
			if task["event_name"] == new_task_data["event_name"]:
				new_tasks.remove(task)
				break

		new_tasks.append(new_task_data)
		self.tasks = new_tasks
