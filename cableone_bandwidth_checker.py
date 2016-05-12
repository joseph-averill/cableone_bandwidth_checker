import sys
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://myaccount.cableone.net/Login.aspx"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"}

if len(sys.argv) != 3:
    print("usage: {} username password".format(os.path.basename(sys.argv[0])))
    exit(0)
username = sys.argv[1]
password = sys.argv[2]

s = requests.Session()
s.headers.update(headers)
r = s.get(URL)
soup = BeautifulSoup(r.content, "html.parser")

VIEWSTATE = soup.find(id="__VIEWSTATE")['value']
EVENTVALIDATION = soup.find(id="__EVENTVALIDATION")['value']

login_data = {"__VIEWSTATE": VIEWSTATE,
              "__EVENTVALIDATION": EVENTVALIDATION,
              "ctl00$plhMain$txtUserName": username,
              "ctl00$plhMain$txtPassword": password,
              "ctl00$plhMain$btnLogin": "Log In"}

r = s.post(URL, data=login_data)
soup = BeautifulSoup(r.content, "html.parser")
start_date_string = soup.find(id="ctl00_plhMain_lblDataStartTotal")
start_date = datetime.strptime(start_date_string.text, '%m/%d/%Y')
end_date_string = soup.find(id="ctl00_plhMain_lblDataEndTotal")
end_date = datetime.strptime(end_date_string.text, '%m/%d/%Y')
this_day = datetime.today()

limit = float(soup.find(id="ctl00_plhMain_lblDataguideline").text.replace(" GB", ""))
used = float(soup.find(id="ctl00_plhMain_lblDataUsed").text.replace(" GB", ""))

days_of_bandwidth = (end_date - start_date).days + 1
if days_of_bandwidth != 0:
    bandwidth_per_day = limit / days_of_bandwidth
else:
    bandwidth_per_day = limit

days_remaining = (end_date - this_day).days + 1
available_bandwidth = limit - used
if days_remaining != 0:
    remaining_bandwidth_per_day = available_bandwidth / days_remaining
else:
    remaining_bandwidth_per_day = available_bandwidth

print("total bandwidth from {} to {}: {:.2f} GB, {:.2f} GB per day.".format(start_date.strftime("%d/%m/%Y"),
                                                                            end_date.strftime("%d/%m/%Y"),
                                                                            limit, bandwidth_per_day))

bandwidth_string = "You have {:.2f} GB left for {:,} days, {:.2f} GB per day.".format(available_bandwidth, days_remaining,
                                                                                 remaining_bandwidth_per_day)
message = ""
if remaining_bandwidth_per_day < bandwidth_per_day:
    message = "Conserve your data!"
elif remaining_bandwidth_per_day == bandwidth_per_day:
    message = "Right on target!"
else: # remaining bandwidth per day > bandwidth per day
    message = "Use more data!"
print(message + " " + bandwidth_string)
