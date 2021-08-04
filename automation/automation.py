import os
import sys

sys.path.append("c:\\Users\\georg\\SywebsProjects\\hrefgen")

# import ahref_database_api as ahref_db

from indexer_automation_MOD import * 
from time import sleep
from wrike_use_script_MOD import * 
from random import randint
from threading import Thread


def run_indexer(link, task_id):
	
	# while True:
	# 	if not ahref_db.check_mutex():
	# 		ahref_db.mark_mutex()
	# 		break
	# 	sleep(randint(0, 10))

	try:
		api = WrikeAPI()

		os.system("taskkill /f /im SEO_Indexer.exe")
		print "starting indexer"
		auto = IndexerAutomation()
		pid = auto.start_indexer()
		
		filename = auto.run(pid, link).encode("utf-8")
		
		print filename
		remote_filename = link.encode("utf-8")
		for char in "<>:\"/\\|?*":
			remote_filename = remote_filename.replace(char, "_")

		remote_filename += ".csv"

		print remote_filename
		sleep(30)

		upload_attachment(task_id, filename + ".txt", remote_filename)

		print "Result Uploaded"
		os.system("taskkill /f /im SEO_Indexer.exe")
	except Exception as e:
		print e.message

	# ahref_db.delete_mutex()



if __name__ == "__main__":

	api = WrikeAPI()
	links_to_index = get_links_to_index(months_to_get="september")

	for task_id, link in links_to_index.items():
		run_indexer(link, task_id)
		break
