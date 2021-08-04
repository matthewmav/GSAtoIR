import re
from database import * 
from datetime import datetime, timedelta

DB_FILENAME = "app.db"

def get_task_expire_hours(task_id):
	db = Database(DB_FILENAME)

	response = db.query("SELECT hours from active_tasks WHERE id = '{0}'".format(task_id))

	db.close()

	return response[0][0]

def get_pending_tasks():
	db = Database(DB_FILENAME)

	response = db.query("select t1.id, t1.title, t1.domain, t1.[to], t1.date, t1.month from sent_tasks t1 LEFT JOIN active_tasks t2 on t1.id = t2.id LEFT JOIN done_tasks t3 on t1.id = t3.task_id where t2.id is NULL and t3.task_id is NULL")
	
	db.close()

	return response

def get_done_tasks():
	db = Database(DB_FILENAME)

	response = db.query("select t1.id, t1.title, t1.domain, t2.username, t2.date, t1.month, t2.live, t2.not_live from sent_tasks t1 LEFT JOIN done_tasks t2 on t1.id = t2.task_id LEFT JOIN active_tasks t3 on t1.id = t3.id where t2.task_id = t1.id and t2.completed = 1")
	
	db.close()

	return response

def get_task_by_href(href, ahref_words):
	db = Database(DB_FILENAME)

	response = db.query("SELECT * FROM sent_tasks WHERE href = '{0}' and words = '{1}'".format(href, ahref_words))

	db.close()

	return response

def update_done_task(task_id, status):
	db = Database(DB_FILENAME)

	if status == 1:
		db.execute("UPDATE done_tasks SET live = live + 1 WHERE task_id = '{0}'".format(task_id))
		db.execute("UPDATE done_tasks SET not_live = not_live - 1 WHERE task_id = '{0}'".format(task_id))
	else:
		db.execute("UPDATE done_tasks SET not_live = not_live + 1 WHERE task_id = '{0}'".format(task_id))
		db.execute("UPDATE done_tasks SET live = live - 1 WHERE task_id = '{0}'".format(task_id))

	db.close()

def inc_done_task_counters(task_id, status):
	db = Database(DB_FILENAME)

	if status == 1:
		db.execute("UPDATE done_tasks SET live = live + 1 WHERE task_id = '{0}'".format(task_id))
	elif status == 0:
		db.execute("UPDATE done_tasks SET not_live = not_live + 1 WHERE task_id = '{0}'".format(task_id))

	db.close()

def mark_task_done(task_id, email, status):
	db = Database(DB_FILENAME)

	# dont mark again done, if already marked
	if check_task_done(task_id):
		inc_done_task_counters(task_id, status)
		return

	# delete_task_active(task_id)
	
	db.execute("INSERT INTO done_tasks (task_id, username, date) VALUES ('{0}', '{1}', '{2}')".format(task_id, email, datetime.now()))

	inc_done_task_counters(task_id, status)
	db.close()

def check_task_done(task_id):
	db = Database(DB_FILENAME)

	response = db.query("SELECT * FROM done_tasks WHERE task_id = '{0}'".format(task_id))

	db.close()

	return len(response) != 0


def mark_mutex():
	db = Database(DB_FILENAME)

	db.execute("INSERT INTO config (key, value) VALUES ('mutex', 'on')")

	db.close()

def check_mutex():
	db = Database(DB_FILENAME)	

	result = db.query("SELECT * FROM config WHERE key = 'mutex' ")

	db.close()

	return len(result) != 0 

def delete_mutex():
	db = Database(DB_FILENAME)

	db.execute("DELETE FROM config WHERE key = 'mutex'")

	db.close()

def get_months():
	db = Database(DB_FILENAME)

	response = db.query("SELECT value FROM config WHERE key = 'months'")

	db.close()

	return response[0][0]

def get_year():
	db = Database(DB_FILENAME)

	response = db.query("SELECT value FROM config WHERE key = 'year'")

	db.close()

	if len(response):
		return response[0][0]
	else:
		return None

def update_months(months, year):
	db = Database(DB_FILENAME)

	db.execute("UPDATE config SET value = '{0}' where key = 'months'".format(months))

	response = db.query("SELECT * FROM config WHERE key = 'year'")

	if len(response):
		db.execute("UPDATE config SET value = '{0}' where key = 'year'".format(year))
	else:
		db.execute("INSERT INTO config (value, key) VALUES ('{0}', 'year')".format(year))

	db.close()

def add_user(username, fullname, priority = 0):
	"""
		Adding user to the database
	"""
	db = Database(DB_FILENAME)

	db.execute("INSERT INTO users (username, fullname, priority) \
		VALUES ('{0}', '{1}', {2})".format(username, fullname, priority))

	db.close()

def get_all_users():
	"""
		getting list of all the users 
	"""
	db = Database(DB_FILENAME)
	resonse = db.query("select * from users")
	db.close()

	return resonse

def get_priority_users():
	"""
		getting list of all the users 
	"""
	db = Database(DB_FILENAME)
	resonse = db.query("select * from users where priority = 1 ")
	db.close()

	return resonse

def delete_user(username):
	"""
		deleting user from database 
	"""
	db = Database(DB_FILENAME)

	db.execute("DELETE FROM users WHERE username = '{0}' ".format(username))

	db.close()

def get_user_info(username):
	db = Database(DB_FILENAME)

	response = db.query("SELECT * FROM users WHERE username = '{0}'".format(username))

	db.close()

	return response

def mark_task_sent(id, title, to, month, domain):
	db = Database(DB_FILENAME)

	a = "<a\\s+(?:[^>]*?\s+)?href=([\"'])(.*?)\\1"
	pattern = re.compile(a)

	link = re.findall(pattern, title)[0][1].strip()

	a = r'<([a] href=".*">)(.+?)<(\/[a])>'
	pattern = re.compile(a)

	words = re.findall(pattern, title)[0][1].strip()

	db.execute("INSERT INTO sent_tasks ('id', 'title', 'month', 'domain', 'date', 'to', 'href', 'words') \
		VALUES ('{0}', '{1}','{2}','{3}','{4}', '{5}', '{6}', '{7}')".format(id, title, month, domain, datetime.now(), to, link, words))

	db.close()

def send_task_to_priority(id, writer):
	db = Database(DB_FILENAME)

	db.execute("INSERT INTO sent_to_priority ('id', writer, date) VALUES ('{0}', '{1}', '{2}')".format(id, writer, datetime.now()))

	db.close()

def check_task_sent_to_priority(id):
	db = Database(DB_FILENAME)

	response = db.query("SELECT * FROM sent_to_priority WHERE id = '{0}'".format(id))

	db.close()

	return len(response) != 0 

def delete_task_sent(id):
	db = Database(DB_FILENAME)

	db.execute("DELETE FROM sent_tasks WHERE id = '{0}'".format(id))

	db.close()

def check_task_sent_date(task_id):
	db = Database(DB_FILENAME)

	resonse = db.query("select * from sent_tasks where id = '{0}' \
		and date < '{1}'".format(task_id, datetime.now() - timedelta(days = 1)))

	db.close()

	return len(resonse) != 0

def check_task_is_sent(id):
	"""
	
	if task not exist return False , else True
	
	Args:
	    id (STR): id of the task in wrike 
	"""
	db = Database(DB_FILENAME)

	response = db.query("SELECT date FROM sent_tasks WHERE id = '{0}'".format(id))

	db.close()

	return len(response) != 0

def mark_task_accepted(id, writer):
	"""
	insert task to accepted tasks table
	
	Args:
	    id (STR): the if of the task in wrike 
	    writer (STR): the email of the writer which accepted the task 
	"""
	db = Database(DB_FILENAME)

	db.write("accepted_tasks", "'id', writer, 'date'", 
		','.join(["'{0}'".format(val) for val in [id, writer, datetime.now()]]))

	db.close()

def check_task_is_accepted(id):
	"""
	
	if task not accepted return False , else True
	
	Args:
	    id (STR): id of the task in wrike 
	"""
	db = Database(DB_FILENAME)

	response = db.query("SELECT * FROM accepted_tasks WHERE id = '{0}'".format(id))

	db.close()

	if len(response) == 0:
		return False
	
	return response

def check_task_is_rejected(id):
	"""
	
	if task not accepted return False , else True
	
	Args:
	    id (STR): id of the task in wrike 
	"""
	db = Database(DB_FILENAME)

	response = db.query("SELECT * FROM rejected_tasks WHERE id = '{0}'".format(id))

	db.close()

	if len(response) == 0:
		return False
	
	return response

def delete_task_from_user(id, username):
	db = Database(DB_FILENAME)

	db.execute("DELETE FROM active_tasks WHERE id = '{0}' and username = '{1}'".format(id, username))

	db.close()

def mark_task_rejected(id, writer):
	"""
	insert task to c tasks table
	
	Args:
	    id (STR): the if of the task in wrike 
	    writer (STR): the email of the writer which rejected the task 
	"""
	db = Database(DB_FILENAME)

	db.write("rejected_tasks", "'id', writer, 'date'", ','.join(["'{0}'".format(val) for val in [id, writer, datetime.now()]]))

	db.close()

def update_task_title(id, title):
	"""
	Updates the title of a task in database 
	
	Args:
	    id (STR): id of the task in wrike to update
	    title (STR): the title to set on the task
	"""
	db = Database(DB_FILENAME)

	db.execute("UPDATE ahref_tasks SET title = '{0}' WHERE id = '{1}'".format(title, id))

	db.close()

def insert_ahref_link(id, project, year, month, link, keywords, source, ranking):
	"""
	Add a link to the tool database 
	
	Args:
	    id (TYPE): id of the task in wrike
	    project (TYPE): name of the project in wrike
	    year (TYPE): year in wrike
	    month (TYPE): month in wrike
	    link (TYPE): link content in wrike (the title of the task)
	    keywords (TYPE): the keywords in wrike (the description of the task), ';' seperated 
	"""
	
	db = Database(DB_FILENAME)

	original = link 

	if "/" in link and source != "DA":
		new_link = "/".join(link.split("//")[1].split("/")[1:])
		if len(new_link) != 0:
			link = new_link

	to_insert = [id, project, year, month, link, keywords, source, original, ranking]

	to_insert_string = ','.join(["'{0}'".format(str(element)) for element in to_insert])

	db.write("ahref_links", "'id', project, year, month, link, keywords, source, original, ranking", to_insert_string)

	db.close()

def insert_ahref_task(id, project, year, month, title):
	"""
	Add a task to the tool database 
	
	Args:
	    id (TYPE): id of the task in wrike
	    project (TYPE): name of the project in wrike
	    year (TYPE): year in wrike
	    month (TYPE): month in wrike
	    link (TYPE): link content in wrike (the title of the task)
	"""
	
	db = Database(DB_FILENAME)

	to_insert = [id, project, year, month, title]

	to_insert_string = ','.join(["'{0}'".format(str(element)) for element in to_insert])

	db.write("ahref_tasks", "id, project, year, month, title", to_insert_string)

	db.close()

def delete_project_ahref_links(project):
	"""
	Deletes all the ahref links from the database 
	
	Args:
	    project (str): the name of the project
	"""
	db = Database(DB_FILENAME)

	db.execute("DELETE FROM ahref_links WHERE project = '{0}'".format(project))

	db.close()
	
def delete_project_ahref_tasks(project):
	"""
	Deletes all the ahref tasks from the database 
	
	Args:
	    project (str): the name of the project
	"""
	db = Database(DB_FILENAME)

	db.execute("DELETE FROM ahref_tasks WHERE project = '{0}'".format(project))

	db.close()
	
def get_project_ahref_links(project):
	"""

	Get href links and keywords from the local db  
	
	Args:
	    project (STR): the project to fetch
	    year (STR): the year to fetch
	    month (STR): the month to fetch
	
	Returns:
	    LIST: list of tuples with the query response 
	"""
	db = Database(DB_FILENAME)

	response = db.query("SELECT * FROM ahref_links WHERE project = '{0}' ORDER BY link DESC".format(project))

	db.close()

	return response

def get_project_ahref_tasks(project, year, month):
	db = Database(DB_FILENAME)

	response = db.query("SELECT * FROM ahref_tasks WHERE project = '{0}' and year = '{1}' \
		and (month = '{2}')".format(project, year, month))

	db.close()

	return response

def get_all_projects():

	db = Database(DB_FILENAME)

	response = db.query("SELECT DISTINCT project FROM ahref_tasks")

	db.close()

	return response

def renew_task(task_id):
	db = Database(DB_FILENAME)

	db.execute("UPDATE active_tasks SET renewed = 1 where id = '{0}'".format(task_id))

	db.close()

def mark_task_as_reminded(task_id):
	db = Database(DB_FILENAME)

	db.execute("UPDATE active_tasks SET reminded = 1 where id = '{0}'".format(task_id))

	db.close()

def get_tasks_to_remind():
	db = Database(DB_FILENAME)

	date = datetime.now() - timedelta(days = 2)
	date2 = datetime.now() - timedelta(days = 3)

	response = db.query("SELECT * from active_tasks where date > '{days3}' \
		and date < '{days2}' and renewed = 0 and reminded = 0".format(days2 = date, days3= date2))

	db.close()
	
	return response

def get_active_task_info(task_id):
	"""
		adding task and username 
	"""
	db = Database(DB_FILENAME)
	
	response = db.query("select *, date(date, '+2 day') from active_tasks where id = '{0}'".format(task_id))
	
	db.close()	
	return response

def get_done_task_info(task_id):
	"""
		adding task and username 
	"""
	db = Database(DB_FILENAME)
	
	response = db.query("select * from done_tasks where task_id = '{0}'".format(task_id))
	
	db.close()	
	return response

def mark_task_renewed(task_id, username):

	db = Database(DB_FILENAME)

	response = db.query("SELECT * FROM renewed_tasks WHERE task_id = '{0}' and email = '{1}'".format(task_id, username))

	if len(response) == 0:
		db.execute("INSERT INTO renewed_tasks (task_id, email) VALUES('{0}', '{1}')".format(task_id, username))

	db.close()

def check_task_active(id):
	"""
	
	if task not accepted return False , else True
	
	Args:
	    id (STR): id of the task in wrike 
	"""
	db = Database(DB_FILENAME)

	response = db.query("SELECT date FROM active_tasks WHERE id = '{0}'".format(id))

	db.close()

	return len(response) != 0

def mark_task_active(id, username, hours):
	db = Database(DB_FILENAME)

	db.execute("INSERT INTO active_tasks ('id', username, date, hours)\
	 VALUES('{0}', '{1}', '{2}', '{3}')".format(id, username, datetime.now(), hours))

	db.close()

def delete_task_active(id):
	db = Database(DB_FILENAME)

	db.execute("DELETE FROM active_tasks WHERE id = '{0}'".format(id))

	db.close()

def mark_task_expired(id, username):
	db = Database(DB_FILENAME)

	db.execute("INSERT INTO expired_tasks ('id', username, date)\
	 VALUES('{0}', '{1}', '{2}')".format(id, username, datetime.now()))

	db.close()

def get_expired_tasks_from_table():
	db = Database(DB_FILENAME)

	response = db.query("SELECT t1.*,t2.title, t2.month from expired_tasks t1 LEFT JOIN sent_tasks t2 on t1.id  = t2.id where t2.id = t1.id")

	db.close()

	return response

def get_expired_tasks():
	"""
		Getting a list of all the expired tasks
	"""
	db = Database(DB_FILENAME)

	date = datetime.now() - timedelta(days = 3)
	date2 = datetime.now() - timedelta(days = 4)

	response = db.query("select * from active_tasks where (date < '{date}' and renewed = 0) or (date < '{date2}') ".format(date = date, date2 = date2))

	db.close()

	return response

def get_sent_all_months():
	db = Database(DB_FILENAME)
	response = db.query("select distinct(month) from sent_tasks")
	db.close()

	return response


def delete_all_domains():
	db = Database(DB_FILENAME)

	db.execute("DELETE from domains WHERE 1 = 1")

	db.close()

def get_accepted_tasks():
	db = Database(DB_FILENAME)

	response = db.query("SELECT * FROM accepted_tasks")

	db.close()

	return response

def get_rejected_tasks():
	db = Database(DB_FILENAME)

	response = db.query("SELECT * FROM rejected_tasks")

	db.close()

	return response


def add_domain(folder_id, folder_name):
	db = Database(DB_FILENAME)

	db.execute("INSERT INTO domains (folder_id, folder_name) VALUES ('{0}','{1}') ".format(folder_id, folder_name))

	db.close()

def get_all_domains():
	db = Database(DB_FILENAME)
	response = db.query("SELECT * FROM domains")
	db.close()

	return response

def get_active_tasks():
	"""
		Getting a list of all the expired tasks
	"""
	db = Database(DB_FILENAME)

	response = db.query("select * from active_tasks")

	db.close()	

	return response

def get_task_info(id):

	db = Database(DB_FILENAME)

	response = db.query("SELECT * FROM sent_tasks WHERE id = '{0}'".format(id))

	db.close()

	return response


def mark_done_task_completed(task_id):
	db = Database(DB_FILENAME)

	db.execute("UPDATE done_tasks SET completed = 1 WHERE task_id = '{0}'".format(task_id))

	db.close()

def check_task_is_completed(task_id):
	db = Database(DB_FILENAME)

	response = db.query("SELECT * FROM done_tasks WHERE task_id = '{0}' and completed = 1".format(task_id))

	db.close()

	return len(response) != 0 