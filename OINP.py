import pickle
import urllib3
from bs4 import BeautifulSoup
import time
import logging
from logging.handlers import TimedRotatingFileHandler
from twilio.rest import Client

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = TimedRotatingFileHandler('########/OINP.log', when="midnight", interval=1)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)

account_sid = "########"
auth_token  = "########"

pickle_in = open("#########/OINP.pickle","rb")
archieve = pickle.load(pickle_in)
pickle_in.close()

for i in range(26):
	try:
		page_url = 'http://www.ontarioimmigration.ca/en/pnp/OI_PNPNEW.html'
		http = urllib3.PoolManager()
		request = http.request('GET', page_url)
		if request.status == 200:
			html = BeautifulSoup(request.data, 'html.parser')
			new_count = len(html.find('div', class_='main_content').find_all('p'))
			if new_count != archieve['count']:
				client = Client(account_sid, auth_token)
				message = client.messages.create(
				to="+16476762052",
				from_="+13069006383",
				body="OINP Website Updated! (" + str(archieve['count']) + " - " + str(new_count) + ")")
				logger.warning("OINP Website Updated! (" + str(archieve['count']) + " - " + str(new_count) + ")")
				archieve['count'] = new_count
			else:
				logger.info('Succeeded')
			archieve['status'] = 200
		else:
			archieve['status'] = 500
			logger.warning("OINP Website Unavailable!")
	except Exception as ex:
		if archieve['status'] != 400:
			client = Client(account_sid, auth_token)
			message = client.messages.create(
			to="+1##########",
			from_="+1##########",
			body="OINP Script Terminated! (" + str(ex) + ")")
			archieve['status'] = 400
		logger.warning(str(ex))
	if i < 25:
		time.sleep(20)

pickle_out = open("########/OINP.pickle", "wb")
pickle.dump(archieve, pickle_out)
pickle_out.close()
