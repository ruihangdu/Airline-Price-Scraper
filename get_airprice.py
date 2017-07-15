from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import sys
from bs4 import BeautifulSoup as bs
import re
import smtplib
from email.mime.text import MIMEText
from subprocess import Popen, PIPE

from pyvirtualdisplay import Display
import os

reload(sys)
sys.setdefaultencoding('utf-8')

# s = smtplib.SMTP('localhost')
# p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
# driver = webdriver.Chrome()

def get_expedia(origin_city, destination_city, start_date, return_date):
# origin_city = "ORD"
# destination_city = "PEK"
# start_date = "12/17/17"
# return_date = "01/06/18"
	# options = webdriver.ChromeOptions()
	# options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
	# options.add_argument('headless')

	# options.add_argument('window-size=1200x600	')
	# os.environ['webdriver.chrome.driver'] = './chromedriver'
	# display = Display(visible=0, size=(800,600))

	# display.start()
	driver = webdriver.Chrome()
	url = "https://www.expedia.com/Flights-Search?trip=roundtrip&leg1=from:{org_city},to:{dest_city}," \
	           "departure:{origin_date}TANYT&" \
	           "leg2=from:{dest_city},to:{org_city},departure:{return_date}TTANYT&passengers=adults:1&mode=search" \
	        .format(org_city=origin_city, dest_city=destination_city, origin_date=start_date, return_date=return_date)

	search = driver.get(url)
	time.sleep(25)
	content = None
	try:
		content = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")

		# with open("expedia.txt", "wb") as f:
		# 	f.write(content)
		
	except Exception:
		driver.quit()

	soup = bs(content)
	candidates = soup.find_all('a', text=re.compile(r"Satisfactory Flight(.*)"))[:5]
	# first_one = soup.find('a', text=re.compile(r"Satisfactory Flight(.*)"))
	# print first_one
	topfive = []

	for first_one in candidates:
		parent = first_one.parent
		while bool(re.search(r'(.*)li(.*)', parent.name)) is False:
			parent = parent.parent
		# print str(parent)
		best_price = re.compile(r'price.*\$([+-]?[0-9]*[,]?[0-9]*[.]?[0-9]+)').findall(str(parent))
		# print best_price[0]
		# airline = re.compile(r'airline.*name.*>(.*)').findall(str(parent))
		airline = parent.find('div', {'data-test-id':'airline-name'})

		# print airline.text
		topfive.append(str(best_price[0])+" from "+str(airline.text))

	# msg = MIMEText("The top 5 choices are:\n" + "\n".join(topfive))

	# email = "du113@purdue.edu"
	# msg['Subject'] = "Airline Information"
	# msg['From'] = email
	# msg['To'] = email

	
	# # s.sendmail(email, [email],  msg.as_string())
	# p.communicate(msg.as_string())
	print topfive
	
	# except Exception:
	# 	driver.quit()
	# elem = driver.find_element_by_xpath("//button[contains(@data-test-id, 'select-button')]")

	# elem.send_keys(Keys.RETURN)
	# driver.quit()

get_expedia("ORD","PEK","12/17/17","01/06/18")

# s.quit()