import datetime
import logging 
import ahref_database_api as href_db
from wrike_api import *
from serpbook_api import * 
import cgi

wrike_logger = logging.getLogger("wrike")
NOEL_ACCOUNT_ID = "999999"

def create_tasks_from_serpbook(wrike_folder, project):
	serpbook_api = SerpBookAPI()
	wrike_api = WrikeAPI()

	try:
		tasks = serpbook_api.get_ready_results(project)
	except:
		return

	all_tasks = wrike_api.get_all_tasks(wrike_folder)
	for task in tasks:
		exist = wrike_api.get_task_id_contains(all_tasks, task[0] + " - " + task[1])

		if exist:
			continue

		task_id = wrike_api.create_task(wrike_folder)["data"][0]["id"]
		wrike_api.update_task_title(task_id, task[0] + " - " + task[1] + " - " + task[2])

def get_links_from_serpbook_folder(serpbook_folder):
	api = WrikeAPI()

	tasks = api.get_all_tasks(serpbook_folder)

	serpbook_links = {}
	# url - id:keyword:ranking 

	for task in tasks:
		try:
			details = api.get_task_info(task)

			title = details["data"][0]["title"]
			title = title.split(" - ")
			print title
			url = title[0].strip()
			keyword = title[1].strip()
			ranking = title[2].strip()

			if url in serpbook_links:
				serpbook_links[url].append([task, keyword, ranking])
			else:
				serpbook_links[url] = [[task, keyword, ranking]]
		except:
			continue

	return serpbook_links


def get_task_to_send(months_to_get, folder_name = "", year = ""):
	"""
		Fetchs all the "ON- HOLD" tasks from the folders
		and return a dist of task - by domain 
	"""

	api = WrikeAPI()

	if folder_name == "":
		root_folder = api.get_folder_id(None, "Status projects Linkbuilding 2")
	else:
		root_folder = api.get_folder_id(None, folder_name)

	print root_folder

	domains = api.get_folder_childrens([root_folder])


	tasks_links_dict = {}

	print "found {0} domains".format(len(domains))

	href_db.delete_all_domains()

	for domain in domains:

		domain_info = api.get_folder_info(domain)
		domain_name = domain_info["data"][0]["title"]

		href_db.add_domain(domain, domain_name)

		if domain_info["data"][0]["color"] == "Red4":
			continue

		years = api.get_folder_childrens([domain])

		if year == "":
			current_year = api.get_folder_id(years, str(datetime.datetime.now().year))
		else:
			current_year = api.get_folder_id(years, year)


		months = api.get_folder_childrens([current_year])

		for month in months_to_get:

			month = month.strip()
			if month == "":
				current_month = api.get_folder_id(months, datetime.datetime.now().strftime("%B").lower(), lower = True)
			else:
				current_month = api.get_folder_id(months, month.lower(), lower = True)


			if current_month:
				tasks = api.get_hold_tasks(current_month)

				# if there are no tasks in the folder, I still want to return a list of the domains without tasks
				if len(tasks) == 0:
					if domain_name not in tasks_links_dict:
						tasks_links_dict[domain_name] = []


				for task in tasks:
					try:
						details = api.get_task_info(task)

						if NOEL_ACCOUNT_ID not in details["data"][0]['responsibleIds']:
							if api.get_folder_name(domain) in tasks_links_dict:
								tasks_links_dict[domain_name].append({"id": task, "details": details, "domain": domain_name, "month": month})
							else:
								tasks_links_dict[domain_name] = [{"id": task, "details": details, "domain": domain_name, "month": month}]
					except:
						print "Error Getting task details"
						

	return tasks_links_dict

def generate_ahref(id, ahref):
	"""
	uploading the generated ahref to wrike 
	
	Args:
	    id (TYPE): id of the task in wrike
	    ahref (TYPE): the genereted ahref to upload to task
	"""
	api = WrikeAPI()

	original_title = api.get_task_info(id)["data"][0]["title"]

	if " ahref:" in original_title:
		original_title = original_title.split(" ahref:")[0]

	title = original_title + " ahref:" + ahref

	api.update_task_title(id, title)

	href_db.update_task_title(id, title)

	api.update_task_priority(id, "Deffered")

def add_link_to_landing_pages(project, year, month, link, keyword, folder_name = ""):
	"""
	Added a link from writers tool to the landing pages folder 

	Args: 
		project (STR) - the project of the task 
		year (STR) - the year of the task 
		month (STR) - the month of the task 
		link (STR) - the link to create a task from 

	Returns:
		the new task id in wrike 

	"""

	
	api = WrikeAPI()

	if folder_name == "":
		root_folder = api.get_folder_id(None, "Status projects Linkbuilding 2")
	else:
		root_folder = api.get_folder_id(None, folder_name)

	print root_folder

	domain = api.get_folder_id(api.get_folder_childrens([root_folder]), project)

	if not domain:
		domain = api.create_folder(root_folder, project)["data"][0]["id"]


	years = api.get_folder_childrens([domain])

	# getting ahref folder id 
	ahref_folder = api.get_folder_id(years, "ahref", lower = True)

	if not ahref_folder or len(years) == 0:
		ahref_folder = api.create_folder(domain, "ahref")["data"][0]["id"]

	# getting DA and Landing Pages folder id's 
	ahref_children = api.get_folder_childrens([ahref_folder])

	landing_pages = api.get_folder_id(ahref_children, "Landing Pages", True)

	if not landing_pages or len(ahref_children) == 0:
		landing_pages = api.create_folder(ahref_folder, "Landing Pages")["data"][0]["id"]

	year_folder = api.get_folder_id(api.get_folder_childrens([landing_pages]), str(year))

	if not year_folder or len(api.get_folder_childrens([landing_pages])) == 0:
		year_folder = api.create_folder(landing_pages, year)["data"][0]["id"]


	month_folder = api.get_folder_id(api.get_folder_childrens([year_folder]), month, lower = True)

	if not month_folder or len(api.get_folder_childrens([year_folder])) == 0:
		month_folder = api.create_folder(year_folder, month)["data"][0]["id"]

	print month_folder
	task_details = api.create_task(month_folder)
	task_id = task_details["data"][0]["id"]

	print task_id
	api.update_task_title(task_id, link)
	api.update_task_description(task_id, keyword)

	return task_id

def get_landing_page_links(id, project, year = ""):
	"""
	Getting all the tasks (links) from landing page folder of the project
	
	Args:
	    id (TYPE): The Id of the Landing Page folder 
	    project (TYPE): name of the project - used only to insert to the task dict
	    year (str, optional): the year to fetch
	
	Returns:
	    LIST: list of task's dictionaries of type - 
	    	{"id": task_id, "details": details, 
				"project": project, "year": year, "month": month}
	"""
	api = WrikeAPI()

	landing_pages_links = []

	root_folder = id 

	years = api.get_folder_childrens([root_folder])

	if year == "":
		current_year = api.get_folder_id(years, str(datetime.datetime.now().year))
		year = str(datetime.datetime.now().year)
	else:
		current_year = api.get_folder_id(years, year)

	months = api.get_folder_childrens([current_year])

	for current_month in months:

		month = api.get_folder_name(current_month)
		print "Getting ", month

		if current_month:
			tasks = api.get_all_tasks_detailed(current_month)


		print "Got Tasks"
		for task in tasks:
			details = task
			landing_pages_links.append({"id": task["id"], "details": details, 
				"project": project, "year": year, "month": month})

	return landing_pages_links
				
def get_all_ahref_links(folder_name = "", year = ""):
	"""
	Fetch all the links and keywords from the ahref folder of all the projects (both DA and Landing page)
	
	Args:
	    folder_name (str, optional): Name of the root folder 
	    year (str, optional): the Year to fetch 
	
	Returns:
	    LIST: Dictionary of lists of links of projects 
	"""
	api = WrikeAPI()


	if folder_name == "":
		root_folder = api.get_folder_id(None, "Status projects Linkbuilding 2")
	else:
		root_folder = api.get_folder_id(None, folder_name)

	print root_folder

	domains = api.get_folder_childrens([root_folder])

	projects = {}

	wrike_logger.debug("found {0} domains".format(len(domains)))

	for domain in domains:
	 	
		try:
			links_arr = []

			domain_info = api.get_folder_info(domain)
			domain_name = domain_info["data"][0]["title"]
			
			wrike_logger.debug("Fetching domain - {0}, domain_id - {1}".format(domain_name, domain))

			# check if the folder color is red - if so, continue to the next folder 
			if domain_info["data"][0]["color"] == "Red4":
				continue

			years = api.get_folder_childrens([domain])

			if year == "":
				current_year = api.get_folder_id(years, str(datetime.datetime.now().year))
				year = str(datetime.datetime.now().year)
			else:
				current_year = api.get_folder_id(years, year)

			# getting ahref folder id 
			ahref_folder = api.get_folder_id(years, "ahref", lower = True)

			# getting DA and Landing Pages folder id's 
			ahref_children = api.get_folder_childrens([ahref_folder])

			DA = api.get_folder_id(ahref_children, "DA")
			landing_pages = api.get_folder_id(ahref_children, "Landing Pages", True)
			serpbook = api.get_folder_id(ahref_children, "serpbook")

			if not serpbook:
				serpbook = api.create_folder(ahref_folder, "serpbook")["data"][0]["id"]
			
			if not landing_pages:
				landing_pages = api.create_folder(ahref_folder, "Landing Pages")["data"][0]["id"]

			if not DA:
				DA = api.create_folder(ahref_folder, "DA")["data"][0]["id"]			

			try:
				print "Getting DA"
				da_links = api.get_all_tasks(DA)
			except:
				da_links = []

			wrike_logger.debug("Got DA tasks - " + str(len(da_links)))
			#da_links = api.get_hold_tasks(DA)

			try:
				print "Getting Landing Pages "
				

				landing_pages_links = get_landing_page_links(landing_pages, domain_name)
			except:
				landing_pages_links = []

			wrike_logger.debug("Got Landing Page tasks - " + str(len(landing_pages_links)))

			try:
				print "Getting Serpbook Pages"
				try:
					create_tasks_from_serpbook(serpbook, domain_name)
				except:
					pass

				serpbook_links = get_links_from_serpbook_folder(serpbook)
			except:
				serpbook_links = {}

			wrike_logger.debug("Got serpbook tasks - " + str(len(serpbook_links)))

			for link in serpbook_links.keys():
				keywords = ';'.join([l[1] for l in serpbook_links[link]])
				ranking = ';'.join([l[2] for l in serpbook_links[link]])

				
				links_arr.append({"id": "", "link": link, "keywords": keywords,
					"project": domain_name, "month": "any", "details": "", 
					"year": year, "ranking": ranking, "source": "S.B."})

			for link in da_links:
				task_details = api.get_task_info(link)
				
				links_arr.append({"id": link, "link": task_details["data"][0]["title"], 
					"keywords": task_details["data"][0]["description"].replace("<br />", ";"),
					"project": domain_name, "month": "any", "details": task_details, 
					"year": year, "ranking": "", "source": "DA"})
				

			for link in landing_pages_links:
				desc = api.get_task_description(link['id'])

				desc_lines = desc.split("<br />")
				keywords = []
				for line in desc_lines:
					if "article" in line:
						line = line.split(" - ")[1]
					keywords.append(line)

				links_arr.append({"id": link['id'], "link": link["details"]["title"], 
					"keywords": ';'.join(keywords),
					"project": domain_name, "month": link['month'], "details": link["details"], 
					'year': year, "ranking": "", "source": "L.P."})
				
			projects[domain_name] = links_arr
			print "project Fetched"
		except Exception as e:
			raise e 
			print e.message
			print domain_name


	return projects

def get_link_tasks(months_to_get, folder_name = "", year = ""):
	"""
	Gets all the tasks from Poject/Year/Month folder 
	
	Args:
	    months_to_get (LIST): list of months to fetch
	    folder_name (str, optional): name of the root folder
	    year (str, optional): year to fetch
	
	Returns:
	    TYPE: Dict of list of tasks per domain
	"""
	api = WrikeAPI()

	if folder_name == "":
		root_folder = api.get_folder_id(None, "Status projects Linkbuilding 2")
	else:
		root_folder = api.get_folder_id(None, folder_name)

	wrike_logger.debug("Got root folder - " + root_folder)

	domains = api.get_folder_childrens([root_folder])

	tasks_links_dict = {}

	wrike_logger.debug("found {0} domains".format(len(domains)))

	for domain in domains:
		domain_info = api.get_folder_info(domain)
		domain_name = domain_info["data"][0]["title"]

		if domain_info["data"][0]["color"] == "Red4":
			continue

		years = api.get_folder_childrens([domain])

		if year == "":
			current_year = api.get_folder_id(years, str(datetime.datetime.now().year))
			year = str(datetime.datetime.now().year) 
		else:
			current_year = api.get_folder_id(years, year)


		months = api.get_folder_childrens([current_year])

		for month in months_to_get:


			month = month.strip()
			if month == "":
				current_month = api.get_folder_id(months, datetime.datetime.now().strftime("%B").lower(), lower = True)
			else:
				current_month = api.get_folder_id(months, month.lower(), lower = True)


			if current_month:
				tasks = api.get_all_tasks(current_month)
				#tasks = api.get_hold_tasks(current_month)

				# if there are no tasks in the folder, I still want to return a list of the domains without tasks
				if len(tasks) == 0:
					if domain_name not in tasks_links_dict:
						tasks_links_dict[domain_name] = []


				for task in tasks:
					details = api.get_task_info(task)

					if api.get_folder_name(domain) in tasks_links_dict:
						tasks_links_dict[domain_name].append({"id": task, "year": year, "month": month, "title": details["data"][0]["title"], 
							"details": details, "domain": domain_name})
					else:
						tasks_links_dict[domain_name] = [{"id": task, "year": year, "month": month, "title": details["data"][0]["title"], 
							"details": details, "domain": domain_name}]
						

	return tasks_links_dict	

def get_generated_links(months_to_get, folder_name = "", year = ""):
	"""
	Gets all the tasks from Poject/Year/Month folder 
	
	Args:
	    months_to_get (LIST): list of months to fetch
	    folder_name (str, optional): name of the root folder
	    year (str, optional): year to fetch
	
	Returns:
	    TYPE: Dict of list of tasks per domain
	"""
	api = WrikeAPI()

	if folder_name == "":
		root_folder = api.get_folder_id(None, "Status projects Linkbuilding 2")
	else:
		root_folder = api.get_folder_id(None, folder_name)

	wrike_logger.debug("Got root folder - " + root_folder)

	domains = api.get_folder_childrens([root_folder])

	tasks_links_dict = {}

	wrike_logger.debug("found {0} domains".format(len(domains)))

	wrike_logger.debug("found {0} domains".format(len(domains)))
	
	for domain in domains:
		domain_info = api.get_folder_info(domain)
		domain_name = domain_info["data"][0]["title"]

		if domain_info["data"][0]["color"] == "Red4":
			continue

		years = api.get_folder_childrens([domain])

		if year == "":
			current_year = api.get_folder_id(years, str(datetime.datetime.now().year))
			year = str(datetime.datetime.now().year) 
		else:
			current_year = api.get_folder_id(years, year)


		months = api.get_folder_childrens([current_year])

		for month in months_to_get:


			month = month.strip()
			if month == "":
				current_month = api.get_folder_id(months, datetime.datetime.now().strftime("%B").lower(), lower = True)
			else:
				current_month = api.get_folder_id(months, month.lower(), lower = True)


			if current_month:
				tasks = api.get_all_tasks(current_month)
				#tasks = api.get_hold_tasks(current_month)

				# if there are no tasks in the folder, I still want to return a list of the domains without tasks
				if len(tasks) == 0:
					if domain_name not in tasks_links_dict:
						tasks_links_dict[domain_name] = []


				for task in tasks:
					details = api.get_task_info(task)

					if api.get_folder_name(domain) in tasks_links_dict:
						tasks_links_dict[domain_name].append(cgi.escape(details["data"][0]["title"]))
					else:
						tasks_links_dict[domain_name] = [cgi.escape(details["data"][0]["title"])]

						

	return tasks_links_dict	


def upload_attachment(id, filename, target_filename):
	api  = WrikeAPI()
	return api.attach_csv_to_task(id, filename, target_filename)
