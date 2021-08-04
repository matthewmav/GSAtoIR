import logging
import os
import wrike_functions as wk
import ahref_database_api as ahref_db
import email_generator as et 
from wrike_api import WrikeAPI
from email_api import * 
from datetime import datetime, timedelta
from jinja2 import Template

TASKS_FOLDER = ""
USERNAME = "username"
PASSWORD = "password"

href_logger = logging.getLogger("web_logger")

def generate_report():
	#

	active = ahref_db.get_active_tasks()
	pending = ahref_db.get_pending_tasks()
	done = ahref_db.get_done_tasks()
	expired = ahref_db.get_expired_tasks_from_table()

	months = [month[0] for month in ahref_db.get_sent_all_months()]

	all_domains = [domain[1] for domain in ahref_db.get_all_domains()]

	active_tasks = {}  # accepted
	pending_tasks = {}  # not accepted
	done_tasks = {} # submitted
	expired_tasks = {}


	# by month, by Project 
	active_total_by_month = {}
	pending_total_by_month = {}
	done_total_by_month = {}

	total_active = {} # {month: length}
	total_pending = {} # {month: length}
	total_done = {} # {month: length}

	users = {}

	# initializing the dics 
	for month in months:
		month = month.lower()

		total_active[month] = 0
		total_pending[month] = 0
		total_done[month] = 0

		active_total_by_month[month] = {}
		pending_total_by_month[month] = {}
		done_total_by_month[month] = {}

		active_tasks[month] = {}
		pending_tasks[month] = {}
		done_tasks[month] = {}
		expired_tasks[month] = {}

		users[month] = {}

	for task in active:
		month = ahref_db.get_task_info(task[0].split(";")[0])[0][2]
		project = ahref_db.get_task_info(task[0].split(";")[0])[0][3]
		title = ahref_db.get_task_info(task[0])[0][1]

		if month not in months:
			continue

		# adding task to global counter 
		total_active[month] += 1 

		# adding to month counters 
		if project not in active_total_by_month[month]:
			active_total_by_month[month][project] = 1
		else:
			active_total_by_month[month][project] += 1 

		# adding to tasks report 
		task = [title] + list(task)
		if project not in active_tasks[month]:
			active_tasks[month][project] = [task]
		else:
			active_tasks[month][project].append(task)

	for task in done:
		month = ahref_db.get_task_info(task[0].split(";")[0])[0][2]
		project = ahref_db.get_task_info(task[0].split(";")[0])[0][3]


		if month not in months:
			continue

		# adding task to global counter 
		total_done[month] += 1 

		# adding to month counters 
		if project not in done_total_by_month[month]:
			done_total_by_month[month][project] = 1
		else:
			done_total_by_month[month][project] += 1 

		# adding to tasks report 
		if project not in done_tasks[month]:
			done_tasks[month][project] = [task]
		else:
			done_tasks[month][project].append(task)

	for task in pending:
		month = ahref_db.get_task_info(task[0].split(";")[0])[0][2]
		project = ahref_db.get_task_info(task[0].split(";")[0])[0][3]

		if month not in months:
			continue

		# adding task to global counter 
		total_pending[month] += 1 

		# adding to month counters 
		if project not in pending_total_by_month[month]:
			pending_total_by_month[month][project] = 1
		else:
			pending_total_by_month[month][project] += 1 

		# adding to tasks report 
		if project not in pending_tasks[month]:
			pending_tasks[month][project] = [task]
		else:
			pending_tasks[month][project].append(task)

	for task in expired:
		month = ahref_db.get_task_info(task[0].split(";")[0])[0][2]
		project = ahref_db.get_task_info(task[0].split(";")[0])[0][3]

		if month not in months:
			continue

		if project in expired_tasks[month]:
			expired_tasks[month][project].append(task)
		else:
			expired_tasks[month][project] = [task]


	for month in months:
		for domain in all_domains:
			if domain not in active_tasks[month]:
				active_tasks[month][domain] = []
				active_total_by_month[month][domain] = 0

			if domain not in pending_tasks[month]:
				pending_tasks[month][domain] = []
				pending_total_by_month[month][domain] = 0

			if domain not in done_tasks[month]:
				done_tasks[month][domain] = []
				done_total_by_month[month][domain] = 0

	accepted = ahref_db.get_accepted_tasks()
	rejected = ahref_db.get_rejected_tasks()

	for task in active:
		month = ahref_db.get_task_info(task[0].split(";")[0])[0][2]

		if month not in months:
			continue

		writer = task[1]

		if writer not in users[month]:
			users[month][writer] = {"accepted": 0, "rejected": 0, "expired": 0, "done": 0, "active": 0}

		users[month][writer]["active"] += 1


	for task in accepted:
		month = ahref_db.get_task_info(task[0].split(";")[0])[0][2]

		if month not in months:
			continue

		writer = task[1]

		if writer not in users[month]:
			users[month][writer] = {"accepted": 0, "rejected": 0, "expired": 0, "done": 0, "active": 0}
		
		
		users[month][writer]["accepted"] += len(task[0].split(";"))


	for task in rejected:
		month = ahref_db.get_task_info(task[0].split(";")[0])[0][2]

		if month not in months:
			continue

		writer = task[1]

		if writer not in users[month]:
			users[month][writer] = {"accepted": 0, "rejected": 0, "expired": 0, "done": 0, "active": 0}
		
		
		users[month][writer]["rejected"] += len(task[1].split(";"))

	for task in expired:
		month = ahref_db.get_task_info(task[0].split(";")[0])[0][2]
		writer = task[1]

		if month not in months:
			continue

		if writer not in users[month]:
			users[month][writer] = {"accepted": 0, "rejected": 0, "expired": 0, "done": 0, "active": 0}
		
		
		users[month][writer]["expired"] += 1

	for task in done:
		month = ahref_db.get_task_info(task[0].split(";")[0])[0][2]
		writer = task[3]


		if month not in months:
			continue

		if writer not in users[month]:
			users[month][writer] = {"accepted": 0, "rejected": 0, "expired": 0, "done": 0, "active": 0}
		
		
		users[month][writer]["done"] += 1

	f = open("reports/report_template.txt")
	data = f.read()
	f.close()

	data = Template(data)
	data = data.render(active_tasks = active_tasks, pending_tasks = pending_tasks, done_tasks = done_tasks, expired_tasks = 	expired_tasks, months = months)
	

	f = open("reports/short_report_template.txt")
	short_data = f.read()
	f.close()

	print total_active
	print total_done
	print total_pending

	short_data = Template(short_data)
	short_data = short_data.render(active_tasks = active_total_by_month, pending_tasks = pending_total_by_month, done_tasks = 	done_total_by_month, total_pending = total_pending, total_active = total_active, total_done = total_done, months = months, users = users)

	
	f = open("reports/summary.txt", "w")
	f.write(data)
	f.close()
	

	f = open("reports/short_summary.txt","w")
	f.write(short_data)
	f.close()

	os.system("python update_log.py")

	return done

def work_accepted_notification(task_id, username, priority = False):
	"""
	Sending a notificaition for all users (except the accepting one)
	that the task is already accepted.
	
	Args:
	    task_id (STR): the tasks ids of the accepted tasks
	    username (STR): the email of the accepted username
	    priority (bool, optional): is the user a priority user or not
	"""
	api = EmailSender(USERNAME, PASSWORD)

	tasks = list(set(task_id.split(";")))

	parsed_tasks = []
	for task in tasks:
		parsed_tasks += ahref_db.get_task_info(task)


	if priority:
		users = ahref_db.get_priority_users()
	else:
		users = ahref_db.get_all_users()



	print "sending to users"
	for user in users:
		if user[1] == username or user[1] == "anymail@anymail.com":
			continue

		api.send_email(user[1], "Schrijfopdracht is niet meer beschikbaar", et.generate_work_recieved_email(parsed_tasks, user[1]))

	api.send_email("anymail@anymail.com", "Schrijfopdracht is niet meer beschikbaar (LinkBuilding) - " + username, et.generate_work_recieved_email(parsed_tasks, "anymail@anymail.com"))

def accept_work(task_id, username, priority):
	"""
	Accepting the task if still not accepted or active. 

	
	Args:
	    task_id (STR): List of the tasks to accept concated with ';'
	    username (STR): the email of the accepted user
	    priority (STR): is the user a priority user or not 
	
	Returns:
	    STR: Error code of the functions. - indicative string.
	"""
	api = WrikeAPI()
	keyword = []
	tasks_to_accept = list(set(task_id.split(";")))

	email_api = EmailSender(USERNAME, PASSWORD)
	
	for task in tasks_to_accept:		
		if ahref_db.check_task_active(task) or ahref_db.check_task_done(task):
			return "Tasks already accepted!"

		task_details = ahref_db.check_task_is_accepted(task)

		if task_details:
			if task_details[0][1] == username:
				return "Tasks already accepted!"

		task_details = ahref_db.check_task_is_rejected(task)

		if task_details:
			if task_details[0][1] == username:
				return "Tasks already rejected!"


	# update status in wrike to 'In Progress'
	for task in tasks_to_accept:
		api.update_task_status(task, "Active")
		
		title = api.get_task_info(task)["data"][0]["title"]
		if "username:" not in title:
			api.update_task_title(task,title + " username:" + username)
		else:
			api.update_task_title(task,title.split("username:")[0].strip() + " username:" + username)

		ahref_db.mark_task_accepted(task, username)
		ahref_db.mark_task_active(task, username, len(tasks_to_accept))

	batch = [api.get_task_info(task) for task in tasks_to_accept]

	keyword = [task["data"][0]['title'].split("ahref:")[1].strip() for task in batch]

	domain = ahref_db.get_task_info(tasks_to_accept[0])[0][3]

	email_content = et.generate_accepted_email(batch, tasks_to_accept, username, domain)
	
	email_api.send_email(username, "Je mag beginnen met schrijven!", email_content)
	email_api.send_email("anymail@anymail.com", "Je mag beginnen met schrijven! by - " + username , email_content)

	work_accepted_notification(task_id, username, priority)

	return "Tasks accepted!"

def generate_ahref_and_attach(id, link, keyword):
	"""
	Generates the ahref codes and uploads to wrike 
	
	Args:
	    id (STR): The id of the task in wrike to update
	    link (STR): the link of the ahref 
	    keyword (STR): the keyword of the ahref
	"""
	ahref_template = '<a href="{0}"> {1} </a>'

	generated_ahref = ahref_template.format(link, keyword)

	wk.generate_ahref(id, generated_ahref)

def fetch_expired_tasks():
	"""
		Fetching expired tasks from DB
		and sends task expired email
	"""
	tasks = ahref_db.get_expired_tasks()

	for task in tasks:
		if api.get_task_info(task[0])["data"][0]["status"] == "Completed":
			#ahref_db.mark_task_done(task[0], task[1])
			continue

		if not ahref_db.check_task_done(task[0]):
			work_expired(task[0], task[1])

def fetch_tasks_to_remind():
	"""
		Fetches tasks from the local Database 
		and send reminding email 
	"""
	api = WrikeAPI()
	email_api = EmailSender(USERNAME, PASSWORD)
	tasks = ahref_db.get_tasks_to_remind()

	tasks_to_remind = {}

	for task in tasks:

		if api.get_task_info(task[0])["data"][0]["status"] == "Completed":
			#ahref_db.mark_task_done(task[0], task[1])
			continue

		if task[1] not in tasks_to_remind:
			tasks_to_remind[task[1]] = {}


		task_details = ahref_db.get_task_info(task[0])

		project = task_details[0][3]

		if project not in tasks_to_remind[task[1]]:
			tasks_to_remind[task[1]][project] = []

		tasks_to_remind[task[1]][project].append(task)		


	for writer in tasks_to_remind:
		for project in tasks_to_remind[writer]:
			for task in tasks_to_remind[writer][project]:
				if len(ahref_db.get_user_info(task[1])) == 0:
					ahref_db.mark_task_as_reminded(task[0])
					continue

				#logging.getLogger("tool").info("Reminding Task! Keyword - {0}\
				#(Project - {2}), To - {1}".format(task_details[0][2], task[1], task_details[0][3]))
				ahref_db.mark_task_as_reminded(task[0])

			body = et.generate_reminder_email(tasks_to_remind[writer][project], writer)
			email_api.send_email(task[1], "Herinnering E-mail", body)

def work_expired(task, username):


	api = WrikeAPI()

	email_api = EmailSender(USERNAME, PASSWORD)
	
	task_details = ahref_db.get_task_info(task)

	if ahref_db.check_task_done(task):
		return

	if len(ahref_db.get_user_info(username)) == 0:
		ahref_db.delete_task_from_user(task, username)
		ahref_db.mark_task_expired(task, username)

		api.update_task_status(task, "Deferred")
		api.update_task_title(task, 'username:'.join(api.get_task_info(task)["data"][0]["title"].split("-")[0]))

		return

	email_content = et.generate_expired_email(task_details[0], username)

	# deleting task from the local database 
	ahref_db.delete_task_from_user(task, username)
	
	api.update_task_status(task, "Deferred")
	api.update_task_title(task, 'username:'.join(api.get_task_info(task)["data"][0]["title"].split("-")[0]))

	ahref_db.mark_task_expired(task, username)

	logging.getLogger("web_logger").info(r'<span style="color: #f57c00;"> Task is expired - {0}, by - {1} </span>'.format(api.get_task_info(task)["data"][0]["title"], username))

	email_api.send_email(username, "Uw content opdracht is verlopen", email_content)


def check_and_send_tasks(months_to_fetch, force = False):
	"""
	Fetching tasks from wrike and sending the all the clients 
	
	Args:
	    months_to_fetch (TYPE): the months to query wrike on
	"""
	tasks = {}

	months_to_fetch = [month for month in months_to_fetch if month != ""]
	tasks = wk.get_task_to_send(months_to_fetch)
	
	api = EmailSender(USERNAME, PASSWORD)
	wrike_api = WrikeAPI()


	for domain in tasks.keys():
		to_all = []
		to_priority = []

		if len(tasks[domain]) == 0:
			continue

		href_logger.info("Found {1} links for {0}".format(domain, len(tasks[domain])))

		for task in tasks[domain]:
			if ahref_db.check_task_done(task["id"]):

				href_logger.info("Not sending task as it's already done - {0}, title - {1}, project - {2}".format(task["id"], task["details"]["data"][0]["title"], task["domain"]))

				continue

			# if task is needed to be sent, just delete from table and add to list
			if ahref_db.check_task_is_sent(task["id"]) \
				and ahref_db.check_task_sent_date(task["id"]) \
					and not ahref_db.check_task_active(task["id"]):
			
				ahref_db.delete_task_sent(task["id"])

				if "ahref" in task["details"]["data"][0]["title"]:

					if ahref_db.check_task_sent_to_priority(task["id"]):
						to_all.append(task)
					else:
						to_priority.append(task)

			elif not ahref_db.check_task_is_sent(task["id"]):

				if "ahref" in task["details"]["data"][0]["title"]:

					if ahref_db.check_task_sent_to_priority(task["id"]):
						to_all.append(task)
					else:
						to_priority.append(task)

			elif force:

				ahref_db.delete_task_sent(task["id"])

				if "ahref" in task["details"]["data"][0]["title"]:

					if ahref_db.check_task_sent_to_priority(task["id"]):
						to_all.append(task)
					else:
						to_priority.append(task)
		
		n = 3
		to_all = [to_all[i:i + n] for i in xrange(0, len(to_all), n)] 
		to_priority = [to_priority[i:i + n] for i in xrange(0, len(to_priority), n)] 

		for batch in to_priority:
			task_id = ';'.join([task["id"] for task in batch])
			
			users_list = ahref_db.get_priority_users()

			sent_to = [ user[1] for user in users_list]

			if users_list:
				#logging.getLogger("tool").info("New Task is sent (only to priority users) , Keyword - {0},\
				#	Writers - {1}".format(keywords, ','.join(sent_to)))

				href_logger.info("Task is sent ({0}) to (priority) {1}".format(task["details"]["data"][0]["title"] , ';'.join(sent_to)  ))

				api.send_offer_email(users_list, batch, task_id, priority = True)

				for task in batch:
					ahref_db.mark_task_sent(task["id"], task["details"]["data"][0]['title'], ';'.join(sent_to), task["month"], task["domain"])
			else:
				print "not sending"


		for batch in to_all:
			task_id = ';'.join([task["id"] for task in batch])	

			users_list = ahref_db.get_all_users()
			
			sent_to = [ user[1] for user in users_list]

			if users_list:

				href_logger.info("Task is sent ({0}) to  {1}".format(task["details"]["data"][0]["title"], ';'.join(sent_to)))

				api.send_offer_email(users_list, batch, task_id, priority = False)

				for task in batch:
					ahref_db.mark_task_sent(task["id"], task["details"]["data"][0]['title'], ';'.join(sent_to), task["month"], task["domain"])

			else:
				print "not sending"

def check_done_tasks():
	tasks = ahref_db.get_active_tasks()

	for task in tasks:
		task_id = task[0]
		hours = task[5]

		if ahref_db.check_task_done(task_id):
			date = ahref_db.get_done_task_info(task_id)[0][2]

			date_time_obj = datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
			delta = datetime.now() - date_time_obj

			if delta.seconds // 3600 > int(ahref_db.get_task_expire_hours(task_id)):
				ahref_db.mark_done_task_completed(task_id)
				ahref_db.delete_task_active(task_id)
				title = ahref_db.get_task_info(task_id)[0][1]
				href_logger.info("Task is Done, {0} hours was expired. {1}.".format(int(ahref_db.get_task_expire_hours(task_id), title)))


def main():
	"""
		Fetchs all the data from wrike in insert to the local database 
	"""
	href_logger.info("Starting Fetching links")
	

	tasks = wk.get_link_tasks(ahref_db.get_months().split(";"))
	ahref_links = wk.get_all_ahref_links()

	#import ipdb; ipdb.set_trace()
	for project in ahref_links.keys():

		# deleting all the old ahref links 
		ahref_db.delete_project_ahref_links(project)

		#href_logger.info("Found {0} links from {1}".format(len(ahref_links[project]), project))
		
		for link in ahref_links[project]: 
			print link["source"], project
			ahref_db.insert_ahref_link(link["id"], project, link["year"], 
				link["month"], link["link"], link["keywords"], link["source"], link["ranking"])

	for project in tasks.keys():

		ahref_db.delete_project_ahref_tasks(project)

		#href_logger.info("Found {0} tasks from {1}".format(len(tasks[project]), project))

		for link in tasks[project]:
			ahref_db.insert_ahref_task(link["id"], project, link["year"], 
				link["month"], link["title"])

