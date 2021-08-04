import cgi
import re
import ahref_database_api as db
from datetime import *
from jinja2 import Template

TEMPLATES_FOLDER = "email_template/"


def generate_work_recieved_email(tasks, username):

	user = db.get_user_info(username)

	f = open(TEMPLATES_FOLDER + "accepted_by_writer.html", "r")
	body = f.read()	
	f.close()

	links = list(set([t[1].split("ahref:")[1].strip().split("username:")[0] for t in tasks]))


	domain = tasks[0][3]

	body = Template(body)

	if username == "anymail@anymail.com":
		body = body.render(writer_name = "Noel", links = links, domain_name = domain, username = username)
	else:
		body = body.render(writer_name = user[0][0], links = links, domain_name = domain, username = username)

	return body 

def generate_offer_email(batch, writer, task_id, priority = False):
	"""
	Generates an offer email from a jinja2 template 
	
	Args:
	    batch (LIST): LIST of task to be sent 
	    writer (STR): the email of the recepient 
	    task_id (STR): all the tasks ids concated with ;
	
	Returns:
	    STR: Generated email content
	"""
	f = open(TEMPLATES_FOLDER + "offer.html", "r")
	body = f.read()	
	f.close()

	links = []

	for task in batch:
		title = task["details"]["data"][0]['title']

		if "ahref" in title:
			a = "<a\\s+(?:[^>]*?\s+)?href=([\"'])(.*?)\\1"
			pattern = re.compile(a)

			link = re.findall(pattern, title)[0][1].strip()

			a = r'<([a] href=".*">)(.+?)<(\/[a])>'
			pattern = re.compile(a)

			words = re.findall(pattern, title)[0][1].strip()

			links.append([link, words])

	#links = [cgi.escape(task["details"]["data"][0]['title'].split("ahref:")[1]) for task in batch if "ahref" in ]

	
	body = Template(body)

	body = body.render(priority = priority, writer_name = db.get_user_info(writer)[0][0], 
		links = links, domain_name = batch[0]['domain'], username = writer, id = task_id)

	return body 


def generate_accepted_email(batch, task_id, writer, domain):
	f = open(TEMPLATES_FOLDER + "accepted.html", "r")
	body = f.read()
	f.close()

	links = list(set([t["data"][0]["title"].split("ahref:")[1].strip().split("username:")[0] for t in batch]))

	body = Template(body)
	
	body = body.render(username = writer, writer_name = db.get_user_info(writer)[0][1], links = links, domain_name = domain)

	return body 


def generate_expired_email(task, writer):
	f = open(TEMPLATES_FOLDER + "expired.html", "r")
	body = f.read()
	f.close()

	link = task[1]

	task_info = db.get_active_task_info(task[0])

	first_date = task_info[0][2]
	reminder_date = task_info[0][5]

	body = Template(body)

	first_date = ':'.join(first_date.split(":")[:-1])	
	first_date = '-'.join([first_date.split(" ")[0].split("-")[2], first_date.split(" ")[0].split("-")[1], first_date.split(" ")[0].split("-")[0]]) + " " + first_date.split(" ")[1]

	reminder_date = '-'.join([reminder_date.split(" ")[0].split("-")[2], reminder_date.split(" ")[0].split("-")[1], reminder_date.split(" ")[0].split("-")[0]])

	body = body.render(username = writer, writer_name = db.get_user_info(writer)[0][1], 
		link = link, first_date = first_date, reminder_date = reminder_date)

	return body 


def generate_reminder_email(tasks, writer):
	f = open(TEMPLATES_FOLDER + "reminder.html", "r")
	body = f.read()
	f.close()

	links = [cgi.escape(db.get_task_info(task[0])[0][1]) for task in tasks]
	task_info = db.get_active_task_info(tasks[0][0])

	first_date = task_info[0][2]
	first_date = ':'.join(first_date.split(":")[:-1])	
	first_date = '-'.join([first_date.split(" ")[0].split("-")[2], first_date.split(" ")[0].split("-")[1], first_date.split(" ")[0].split("-")[0]]) + " " + first_date.split(" ")[1]
		
	body = Template(body)

	body = body.render(username = writer, writer_name = db.get_user_info(writer)[0][1], 
		links = links, date = first_date, task_id = ';'.join([task[0] for task in tasks]))

	return body 