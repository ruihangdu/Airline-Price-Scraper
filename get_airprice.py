from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import datetime
import sys
from bs4 import BeautifulSoup as bs
import re
import smtplib
from email.mime.text import MIMEText
from subprocess import Popen, PIPE
import pickle
import argparse

reload(sys)
sys.setdefaultencoding('utf-8')

options = webdriver.ChromeOptions()

# path to the chrome executable
options.binary_location = '/usr/bin/google-chrome-unstable'

# run in headless mode
options.add_argument('headless')

# set window size
options.add_argument('window-size=1200x600')


def clean(string):
    ret = ''
    in_string = False

    for c in string:
        if c in ['\n', ' ']:
            if in_string == True:
                ret += c
                in_string = False
            else:
                continue
        else:
            in_string = True
            ret += c

    return ret[:-1]


class Expedia:
    def __init__(self):
        self.driver = webdriver.Chrome(chrome_options=options)
    

    def search(self, origin_city, destination_city, start_date, return_date):
        data_storage = open('flight-price.txt', 'a')
        data_storage.write('-'*30 + '\n' + datetime.date.today().strftime('%b %d %Y result:') + '\n')

        url = "https://www.expedia.com/Flights-Search?trip=roundtrip&leg1=from:{org_city},to:{dest_city},departure:{origin_date}TANYT&leg2=from:{dest_city},to:{org_city},departure:{return_date}TTANYT&passengers=children:0,adults:1&mode=search" \
                .format(org_city=origin_city, \
                dest_city=destination_city, \
                origin_date=start_date, \
                return_date=return_date)

        search = self.driver.get(url)
        # print search
        time.sleep(10)
        content = None
        try:
            content = self.driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
            # content = self.driver.findElement(By.id('flightModuleList'))

        except Exception:
            data_storage.close()
            self.driver.quit()
            return

        # print content
        soup = bs(content, "html.parser")
        '''
        candidates = soup.find_all('a', text=re.compile(r"Satisfactory Flight(.*)"))[:5]
        topfive = []

        for first_one in candidates:
            parent = first_one.parent
            while bool(re.search(r'(.*)li(.*)', parent.name)) is False:
                parent = parent.parent
            # print str(parent)
            best_price = re.compile(r'price.*\$([+-]?[0-9]*[,]?[0-9]*[.]?[0-9]+)').findall(str(parent))
            airline = parent.find('div', {'data-test-id':'airline-name'})

            topfive.append(str(best_price[0])+" from "+str(airline.text))
        '''
        # reference: https://stackoverflow.com/questions/18733023/getting-attributes-value-using-beautifulsoup
        results = soup.find('ul', {'id':'flightModuleList'})

        # pickle.dump(results, open('airprice.p', 'wb'))

        for flight_info in results.findAll('li'):
            try:
                times = re.findall(r'(\d{4}-\d{2}-\d{2}t\d{2}:\d{2}:\d{2}\W\d{2}:\d{2})', flight_info['id'])
                if times == []:
                    continue
                else:
                    # print flight_info
                    # print times
                    # reference: https://stackoverflow.com/questions/6287529/how-to-find-children-of-nodes-using-beautiful-soup
                    try:
                        depart_time = str(times[0])
                        return_time = str(times[1])
                        carrier = clean(str(flight_info.find('div', {'data-test-id':'airline-name'}).string))
                        duration = clean(str(flight_info.find('div', {'data-test-id':'duration'}).string))
                        price = str(flight_info.find('div', {'class':'offer-price'})\
                                .find('span', {'class':'visuallyhidden'}).string)
                        rating = str(flight_info.find('span', {'class':'details-holder'}).find('span', {'class':'route-happy-superlative'}).find('a').string)
                        satisfactory = rating[:rating.index('F')-1]
                    except Exception as e:
                        continue
                    data_storage.write('\t'.join([depart_time, return_time, carrier, duration, price, satisfactory]) + '\n')
            except KeyError as e:
                # print str(e)
                continue
            # depart_time = re.findall(, flight_info['id'])
        # print topfive

        self.driver.quit()
        data_storage.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('outcity', help='the outbound city')
    parser.add_argument('incity', help='the inbound city')
    parser.add_argument('out_date', help='outbound date')
    parser.add_argument('in_date', help='inbound date')
    args = parser.parse_args()
    outcity = args.outcity
    incity = args.incity
    out_date = args.out_date
    in_date = args.in_date

    expedia = Expedia()
    expedia.search(outcity,incity,out_date,in_date)

# s.quit()
