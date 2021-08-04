import os
import sys

sys.path.append("c:\\Users\\georg\\SywebsProjects\\hrefgen")

# import ahref_database_api as ahref_db

from indexer_automation_MOD import * 
from wrike_use_script_MOD import * 
from time import sleep
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

		# update Wrike task status
		api.update_task_status(task_id, "Completed")
		
	except Exception as e:
		print e

	# ahref_db.delete_mutex()


def index_all_tasks(month):
	"""
	Param:
		month: string 
		# note: with full name e.g.: february

	"""
	api = WrikeAPI()
	links_to_index = get_links_to_index(months_to_get=month)

	print "### Total number of links: {}".format(len(links_to_index))
	for i, (task_id, link) in enumerate(links_to_index.items()):
		run_indexer(link, task_id)
		print "### Number of links remained: {}".format(len(links_to_index) - (i + 1))



if __name__ == "__main__":
	
	api = WrikeAPI()
	links_to_index = get_links_to_index(months_to_get="february")

	print "### Total number of links: {}".format(len(links_to_index))
	for i, (task_id, link) in enumerate(links_to_index.items()):
		run_indexer(link, task_id)
		print "### Number of links remained: {}".format(len(links_to_index) - (i + 1))

