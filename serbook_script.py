from serpbook_api import * 
from time import sleep
from email_sender import * 
import press_refresh as sel
import logging 

USERNAME = "mail"
PASSWORD = "pass"
TO = ["mail"]


def send_keywords_to_serpbook(url, keywords, thread_id, emails, region):
	global TO
	TO += emails
	api = SerpBookAPI()
	logging.info("Sending Keywords to serpbook")

	category_name = url.replace("http://", "").replace("https://", "").split("/")[0] + "_" + thread_id
	category_exist = False

	result = ""
	counter = 0 

	while True: 

		max_number_of_keywords = api.get_max_number_to_upload()
		logging.info("max number to upload is - {0}".format(max_number_of_keywords))

		if len(keywords) <= max_number_of_keywords and max_number_of_keywords != 0 and len(keywords) != 0:
			logging.info("there are less keywords than max to upload")

			resp = api.add_keywords(category_name, url, keywords, region)		
			category_exist = True

			while True:

				# sleep 10 minutes between checks 
				sleep(600)
				remaining, total = api.check_category_status(category_name)
				logging.info("remaining - {0}".format(remaining))

				if remaining == 0 and category_exist and api.check_results_ready(category_name):
					logging.info("Results are ready")

					sleep(600)
					result += api.generate_result_csv(category_name)
					api.delete_category(category_name)
					category_exist = False
					break 
			break

		elif max_number_of_keywords != 0 and len(keywords) != 0:
			logging.info("there are more keywords than max to upload")

			resp = api.add_keywords(category_name, url, keywords[:max_number_of_keywords], region)
			category_exist = True

			logging.info("updating keywords list")

			keywords = keywords[max_number_of_keywords:]
			logging.debug(keywords)

		sleep(600)
		remaining, total = api.check_category_status(category_name)
		logging.info("remaining - {0}".format(remaining))
		

		if remaining == 0 and category_exist and api.check_results_ready(category_name):
			logging.info("Results are ready")
			sleep(600)
			result += api.generate_result_csv(category_name)
			api.delete_category(category_name)
			category_exist = False

	send_result(category_name, result)
	return result
			