"""
	Scraper for tix.axs.com
"""

import threading, smtplib, os, zipfile, random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.proxy import *
import selenium.webdriver.support.ui as ui
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from fake_headers import Headers


class Scraper(threading.Thread):
	
	def __init__(self, event):
		threading.Thread.__init__(self)
		self.browser = None
		self.proxy = None
		self.headless = False
		self.chromedriver = "chromedriver"
	
		self.event = event
		self.filter_max_price = None
		self.filter_ignore_text = None
		self.timeout = 30

		self.email_content = ""
		self.sender_address = ""
		self.sender_pass = ""
		self.receiver_address = ""
		self.email_subject = ""
   
	def startBrowser(self):
		profile = webdriver.ChromeOptions()
		profile.add_argument('--no-sandbox')
		profile.add_experimental_option('excludeSwitches', ['enable-automation'])
		if self.headless: profile.add_argument('--headless')
		headers = Headers().generate()
		profile.add_argument('--user-agent=%s' % headers["User-Agent"])
		browser = webdriver.Chrome(service=Service(self.chromedriver), options=profile)
		browser.set_page_load_timeout(self.timeout)
		self.browser = browser
		
	def startBrowserWithProxy(self, selected_proxy):
		
		PROXY_HOST = selected_proxy.split(":")[0]
		PROXY_PORT = selected_proxy.split(":")[1]
		PROXY_USER = selected_proxy.split(":")[2]
		PROXY_PASS = selected_proxy.split(":")[3]

		manifest_json = """
		{
			"version": "1.0.0",
			"manifest_version": 2,
			"name": "Chrome Proxy",
			"permissions": [
				"proxy",
				"tabs",
				"unlimitedStorage",
				"storage",
				"<all_urls>",
				"webRequest",
				"webRequestBlocking"
			],
			"background": {
				"scripts": ["background.js"]
			},
			"minimum_chrome_version":"22.0.0"
		}
		"""

		background_js = """
		var config = {
				mode: "fixed_servers",
				rules: {
				singleProxy: {
					scheme: "http",
					host: "%s",
					port: parseInt(%s)
				},
				bypassList: ["localhost"]
				}
			};

		chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

		function callbackFn(details) {
			return {
				authCredentials: {
					username: "%s",
					password: "%s"
				}
			};
		}

		chrome.webRequest.onAuthRequired.addListener(
					callbackFn,
					{urls: ["<all_urls>"]},
					['blocking']
		);
		""" % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)

		path = os.path.dirname(os.path.abspath(__file__))
		chrome_options = webdriver.ChromeOptions()
		pluginfile = 'proxy_auth_plugin.zip'
		with zipfile.ZipFile(pluginfile, 'w') as zp:
			zp.writestr("manifest.json", manifest_json)
			zp.writestr("background.js", background_js)
		chrome_options.add_extension(pluginfile)
		if self.headless: chrome_options.add_argument('--headless')
		chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
		headers = Headers().generate()
		chrome_options.add_argument('--user-agent=%s' % headers["User-Agent"])
		driver = webdriver.Chrome(os.path.join(path, self.chromedriver), chrome_options=chrome_options)
		
		self.browser = driver

		
	def sendGmail(self):

		#Setup the MIME
		message = MIMEMultipart()
		message['From'] = self.sender_address
		message['To'] = self.receiver_address
		message['Subject'] = self.email_subject
		
		#The body and the attachments for the mail
		message.attach(MIMEText(self.email_content, 'plain'))
		
		#Create SMTP session for sending the mail
		session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
		session.starttls() #enable security
		session.login(self.sender_address, self.sender_pass) #login with mail_id and password
		text = message.as_string()
		session.sendmail(self.sender_address, self.receiver_address, text)
		session.quit()

	def run(self):
		while(True):

			try:
				# init browser
				if self.proxy and os.path.isfile(self.proxy):

					proxies = open(self.proxy).read().splitlines()
					selected_proxy = random.choice(proxies)

					print("\t[!] Proxy enabled -> {0}".format(selected_proxy))
					self.startBrowserWithProxy(selected_proxy)
				else:
					self.startBrowser()
					
				wait = ui.WebDriverWait(self.browser, self.timeout)

			
				# navigate to link
				self.browser.get(self.event)
				wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".button--call-to-action")))
				self.browser.find_element_by_class_name("button--call-to-action").click()

				# parse results
				soup = BeautifulSoup(self.browser.page_source, "html.parser")
				scraped_date = soup.find("span", class_="event-header-date").text
				el_list = soup.find(id="resale-options-switch-pane-LOWEST_PRICE")
				el_list_items = el_list.find_all("div", class_="resale-list-item")
				for i, el_list_item in enumerate(el_list_items):
					price_level = el_list_item.find("div", class_="seat-detail-item-price-level").text
					sec = el_list_item.find_all("div", class_="seat-detail-item-sec")[-1].text
					row = el_list_item.find_all("div", class_="seat-detail-item-row")[-1].text
					ea = el_list_item.find("div", class_="seat-detail-item-ea").text
					
					ea_float = float(ea[ea.find("$")+1:ea.find("/")].replace(",",""))
					
								
					print("\t\t[{0}/{1}] Item {2}:{3}:{4}:{5}".format(i+1, len(el_list_items), price_level,sec,row,ea))
					if self.filter_ignore_text and sec.lower().find(self.filter_ignore_text.lower()) >= 0: continue
					if self.filter_max_price and ea_float <= self.filter_max_price: # trigger gmail send
						print("\t\t\tSending email..")

						self.email_subject = "Tyler Childers - Red Rocks Fan Exchange - "+scraped_date+" - Accessible "+sec+" Row "+row+" "+ea
						self.email_content = """Tyler Childers - Red Rocks Fan Exchange\n"""+scraped_date+"""\nAccessible """+sec+"""\nRow """+row+"""\n"""+ea+"""\nLINK TO EVENT: """+self.event

						try:
							self.sendGmail()
						except smtplib.SMTPAuthenticationError as e: print("\t\t\tGmail Authentication error")

				# release browser
				self.browser.quit()
				break

			except TimeoutException as ex:
				if self.proxy:
					print("\tProxy has been banned")
				else:
					print("\tTimeout Error")
				self.browser.quit()
				
			except:
				if self.browser: self.browser.quit()
