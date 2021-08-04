
import sys
import os

if sys.executable.endswith("pythonw.exe"):
#   sys.stdout = open(os.devnull, "w")
#   sys.stderr = open(os.path.join(os.getenv("TEMP"), "stderr-"+os.path.basename(sys.argv[0])), "w")
  sys.stdout = open("nohup", "w")
  sys.stderr = open("nohup", "w")

import logging



sys.path.append(os.path.join(os.getcwd(), "automation"))

#logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

web_logger = logging.getLogger("web_logger")
href_logger = logging.getLogger("href")
wrike_logger = logging.getLogger("wrike")

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)

web_file = logging.FileHandler(filename = r"logs/web.log")
web_file.setFormatter(formatter)
web_file.setLevel(logging.DEBUG)

href_file = logging.FileHandler(filename = r"logs/href.log")
href_file.setFormatter(formatter)
href_file.setLevel(logging.DEBUG)

wrike_file = logging.FileHandler(filename = r"logs/wrike.log")
wrike_file.setFormatter(formatter)
wrike_file.setLevel(logging.DEBUG)

web_logger.addHandler(handler)
web_logger.addHandler(href_file)
web_logger.setLevel(logging.DEBUG)

href_logger.addHandler(handler)
href_logger.addHandler(href_file)
href_logger.setLevel(logging.DEBUG)

wrike_logger.addHandler(handler)
wrike_logger.addHandler(wrike_file)
wrike_logger.setLevel(logging.DEBUG)

import ahref_database_api as ahref_db
import wrike_functions as wk
import href_tool
import json
import collections
from flask import Flask, render_template, session, request, redirect, flash, url_for, jsonify
from flask_basicauth import BasicAuth
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_httpauth import HTTPBasicAuth
from threading import Thread
from time import sleep
from wrike_api import *
from datetime import *
from automation_MOD import run_indexer, index_all_tasks
from email_api import * 



USERNAME = "johndoe"
PASSWORD = "xxxxxx"

EMAIL_USERNAME = "username"
EMAIL_PASSWORD = "9999999999999"

app = Flask(__name__)
auth = HTTPBasicAuth()


@app.route("/get_csv_links")
def get_csv_links():
	Thread(target=send_csv).start()

	return redirect("/")


def send_csv():
	tasks = wk.get_generated_links(ahref_db.get_months().split(";"))

	data = "" 

	for project in tasks.keys():
		data += project + ": \n"
		data += '\n'.join(tasks[project])

	api = EmailSender(EMAIL_USERNAME, EMAIL_PASSWORD)

	api.send_email("anymail@anymail.com", "Links List", data.replace("\n", "<br>"))

@app.route("/api_mark_task_done", methods = ["POST"])
def api_task_done():

	href = request.form["href"]
	link = request.form["link"]
	is_live = bool(int(request.form["status"]))
	ahref_words = request.form["words"].strip()

	web_logger.info("Got API request - task in done")
	web_logger.debug(href)
	web_logger.debug(link)
	web_logger.debug(str(bool(is_live)))
	
	results = ahref_db.get_task_by_href(href, ahref_words)

	if len(results) > 1:
		result = None
		for task in results:
			if ahref_db.check_task_active(task[0]):
				result = task
				break
		if result == None:
			for task in results:
				if ahref_db.check_task_is_completed(task[0]):
					result = task
					break

	else:
		result = results[0]


	if result == None:
		web_logger.info("Task is already completed, not adding")
		return jsonify(status = -2, task_id = "")

	if not result:
		web_logger.info("No sent task with such href, Not updating.")
		return jsonify(status = -1, task_id = "")

	task_id = result[0]

	if is_live:
		t = Thread(target = run_indexer, args = (link, task_id))
		t.start()

	if ahref_db.check_task_is_completed(task_id):
		web_logger.info("Task is already completed, not adding")
		return jsonify(status = -2, task_id = task_id)

	if not ahref_db.check_task_active(task_id):
		web_logger.info("Task is not active, not adding")
		return jsonify(status = -3, task_id = task_id)

	task = ahref_db.get_active_task_info(task_id)[0]

	username = task[1]

	api = WrikeAPI()

	old_desc = api.get_task_description(task_id)

	link = link.encode("utf-8")

	new_desc = old_desc + "<br /> {0} - {1}".format(link, str(is_live))

	ahref_db.mark_task_done(task_id, username, int(is_live))

	api.update_task_description(task_id, new_desc)

	web_logger.info(r'<span style="color:#43a047;"> Task is updated and uploaded to wrike. {0}, by - {1}</span>'.format(link, username))

	return jsonify(status = 0, task_id = task_id)

@app.route("/api_update_task_done", methods = ["POST"])
def api_update_task_done():
	href = request.form["href"]
	link = request.form["link"]
	is_live = bool(int(request.form["status"]))
	ahref_words = request.form["words"].strip()
	
	web_logger.info("Got API request - update links status")
	web_logger.debug(href)
	web_logger.debug(link)
	web_logger.debug(str(bool(is_live)))
	
	result = ahref_db.get_task_by_href(href, ahref_words)

	if not result:
		web_logger.info("No sent task with such href, Not updating.")
		return jsonify(status = "error", task_id = "")

	task_id = result[0][0]

	if not ahref_db.check_task_done(task_id):
		web_logger.info("Task not marked to be done, Not updating.")
		return jsonify(status = "error", task_id = task_id)

	username = ahref_db.get_done_task_info(task_id)[0][1]	

	api = WrikeAPI()

	link = link.encode("utf-8")

	old_desc = api.get_task_description(task_id)
	old_desc_list = old_desc.split("<br />")
	old_desc = old_desc_list
	
	for line in old_desc_list:
		if (link in line or line == ''):
			old_desc.remove(line)

	old_desc = "<br />".join(old_desc)

	new_desc = old_desc + "<br /> {0} - {1}".format(link, str(is_live))

	ahref_db.update_done_task(task_id, int(is_live))

	#api.update_task_status(task_id, "Completed")
	api.update_task_description(task_id, new_desc)

	return jsonify(status = "ok", task_id = task_id)


@app.route("/api_index_all_tasks", methods = ["POST"])
def api_index_all_tasks():

	month = request.form.get('month', None)
	if month:
		t = Thread(target = index_all_tasks, args = (month,))
		t.start()
	
	return redirect(url_for("main", started=True))

	
@app.route("/force_send")
def force_send():
	web_logger.info("Force sending tasks to clients")

	t = Thread(target = href_tool.check_and_send_tasks, args = (ahref_db.get_months().split(";"), True))
	t.start()
	
	return redirect("/")

@app.route("/add_link_landing_page")
def add_link_landing_page():
	project = request.args.get("project")
	year = request.args.get("year")
	month = request.args.get("month")
	link = request.args.get("link")
	keyword = request.args.get("keyword")

	web_logger.info("Adding link to landing page folder (API request from VA)")
	wk.add_link_to_landing_pages(project, year, month, link, keyword)

	return "OK"

@app.route("/manual_add_link", methods = ["POST", "GET"])
def manual_add_link():
	if request.method == "POST":
		project = request.form["project"]
		year = request.form["year"]
		month = request.form["month"]
		link = request.form["link"]
		keyword = request.form["keyword"]

		web_logger.info("Adding link to landing page folder (Manual request)")
		wk.add_link_to_landing_pages(project, year, month, link, keyword)

		return redirect("/")

	return render_template("manual_add_link.html")


@app.route("/project_selector", methods = ["GET", "POST"])
@auth.login_required
def project_selector():
	projects = ahref_db.get_all_projects()

	if request.method == "POST":
		project = request.form["project"]
		year = request.form["year"]
		month = request.form["month"]
		month = month.lower()

		url = r"/ahref_selector?project={0}&year={1}&month={2}".format(project, year, month)

		return redirect(url)

	return render_template("project_selector.html", projects = projects)

@auth.verify_password
def verify_password(username, password):
	if username == USERNAME and password == PASSWORD:
		return True

	return False

@app.route("/ahref_selector", methods = ["GET", "POST"])
@auth.login_required
def ahref_selector():
	"""
		Gets the user selection, generates ahref codes and updates in wrike	
	"""
	project = request.args.get("project")
	year = request.args.get("year")
	month = request.args.get("month")
	month = month.lower()

	if request.method == "GET":
		links = ahref_db.get_project_ahref_links(project)
		tasks = ahref_db.get_project_ahref_tasks(project, year, month)

		link_keywords_dict = {}

		for link in links:
			if link[8] != "":
				link_keywords_dict[str(link[6]) + ": " + str(link[4]) + ": " + max(link[8].split(";"))] = [[str(l) for l in link[5].split(";") if l != ""], str(link[7]), [str(l) for l in link[8].split(";") if l != ""]]
			else:
				link_keywords_dict[str(link[6]) + ": " + str(link[4])] = [[str(l) for l in link[5].split(";") if l != ""], str(link[7]), [str(l) for l in link[8].split(";") if l != ""]]

		link_keywords_dict = collections.OrderedDict(sorted(link_keywords_dict.items()))		

		return render_template("ahref_selector.html", ahref_links = link_keywords_dict, ahref_links_string = json.dumps(link_keywords_dict), tasks = tasks)

	if request.method == "POST":
		link_num = 0 

		links_dict = {}
		
		run = True
		while run:
			try:
				if "input_link_id_" + str(link_num) not in request.form:
					run = False
					break


				# getting field values from the submit form 
				id = request.form["input_link_id_" + str(link_num)]
				value = request.form["input_link_value_" + str(link_num)]
				link = request.form["dropdown_" + str(link_num)]
				if link == "":
					link_num += 1
					continue

				keyword = request.form["dropdown_keywords_" + str(link_num)]

				web_logger.info("uploading selected href code to wrike.")
				links_dict[id] = (value, link, keyword)
				link_num += 1

			except:
				run = False
				break

		t = Thread(target=update_ahref_in_wrike, args=(links_dict, ))
		t.start()
		

	return redirect("/project_selector")

@app.route("/accept")
def accept_task():
	"""
	accept sent task
	
	ARGS:
		task_id (STR): the id of the task is wrike and db
		email (STR): the email of the client (the username)

	Returns:
	    TYPE: Description
	"""
	task_id = request.args.get("task_id")
	email = request.args.get("username")
	priority = request.args.get("priority")

	for task in task_id.split(';'):

		title = ahref_db.get_task_info(task)[0][1]

		web_logger.info(r'<span style="color:#1e88e5;"> Task is accepted {0}, by {1} </span>'.format(title, email))

	return render_template("response.html", response = href_tool.accept_work(task_id, email, priority))

@app.route("/reject")
def reject_task():
	task_id = request.args.get("task_id")
	email = request.args.get("username")

	for task in task_id.split(";"):
		task_details = ahref_db.check_task_is_accepted(task)

		if task_details:
			if task_details[0][1] == email:
				return render_template("response.html", response = "Task is already accepted") 

		rejected_task_details = ahref_db.check_task_is_rejected(task)



		if rejected_task_details:
			if rejected_task_details[0][1] == email:
				return render_template("response.html", response = "Task is already rejected") 

	for task in task_id.split(";"):
		ahref_db.mark_task_rejected(task, email)

	title = ahref_db.get_task_info(task_id)[0][1]

	web_logger.info(r'<span style="color: #f57c00;"> Task is rejected - {0}, by - {1}</span>'.format(title, email))

	return render_template("response.html", response = "Task is Rejected")

@app.route("/delete_user", methods = ["GET"])
def delete_user():
	username = request.args.get("username")

	ahref_db.delete_user(username)

	return redirect("/")

@app.route("/add_user", methods = ["GET", "POST"])
@auth.login_required
def add_user():
	
	if request.method == "GET":
		return render_template('add_user.html')

	username = request.form['username']
	fullname = request.form['fullname']
	
	ispriority = False
	if 'ispriority' in request.form:
		ispriority = True

	ahref_db.add_user(username, fullname, int(ispriority))

	"""
	if not isspecial:
		t = Thread(target = wt.send_to_user, args = (username, ispriority))
		t.start()
	"""

	return redirect("/")

@app.route("/update_months", methods = ["POST"])
@auth.login_required
def update_months():

	months = [month.strip() for month in request.form['months'].split(',')]
	year = request.form["year"]

	ahref_db.update_months(','.join(months), year)

	return redirect("/")


@app.route("/", methods = ["GET"])
@auth.login_required
def main():

	started = request.args.get('started', False)

	month = datetime.now().strftime("%B").lower()
	year = datetime.now().year

	return render_template(
		"gsa_indexer.html", 
		month = month, 
		year = year, 
		started=started)

	
# @app.route("/", methods = ["GET"])
# @auth.login_required
# def main():
# 	users = ahref_db.get_all_users()

# 	months = ahref_db.get_months()
# 	year = ahref_db.get_year()

# 	#projects = db.get_all_domains()

# 	return render_template("main.html", users = users, months = months, year = year)

def update_ahref_in_wrike(links_dict):
	for task_id in links_dict.keys():
		# updating task titles in wrike 
		href_tool.generate_ahref_and_attach(task_id, links_dict[task_id][1], links_dict[task_id][2])

def update_tasks():
	"""
		Calls function from href_tool.py to fetch tasks and links from wrike 
	"""
	while True:
		try:
			href_tool.main()
			t = Thread(target = href_tool.generate_report)
			t.start()

			t = Thread(target = href_tool.check_done_tasks)
			t.start()

			sleep(600)
		except:
			pass

@app.route("/renew_job", methods = ["GET"])
def renew_job():
	task_id = request.args.get("task_id")
	task_id = task_id.split(";")
	username = request.args.get("username")

	for task in task_id:
		ahref_db.renew_task(task)
		ahref_db.mark_task_renewed(task, username)

	#logging.getLogger("tool").info("Task is renewed - {0}, by - {1}".format(db.get_task_info(task_id)[0][3], username))
	return render_template("response.html", response = "The Task is renewed")

@app.route("/expire_job", methods = ["GET"])
def expire_job():
	task_id = request.args.get("task_id")
	task_id = task_id.split(";")
	username = request.args.get("username")

	for task in task_id:
		try:
			href_tool.work_expired(task, username)
		except:
			pass

	web_logger.info("User decided to not reniew task after 2 days. " + username)

	return render_template("response.html", response = "Work Expired")

# def main():
# 	t = Thread(target= update_tasks)
# 	t.start()



	# app.run(host="0.0.0.0", port = 7000)

if __name__ == '__main__':
	# main()
	app.run(host="0.0.0.0", port = 7000)