import datetime
from wrike_api import * 


def parse_url(description):
	print description
	url = ("http" + description.split("http")[1]).split("<")[0].split(">")[0].replace("\"", "")
	return url

def get_links_to_index():
	api = WrikeAPI()

	root_folder = api.get_folder_id(None, "Status projects Linkbuilding")

	domains = api.get_folder_childrens([root_folder])

	tasks_links_dict = {}

	print "found {0} domains".format(len(domains))
	for domain in domains:
		print domain
		### sgy
		domain_name = api.get_folder_name(domain)
		print domain_name

		years = api.get_folder_childrens([domain])
		
		current_year = api.get_folder_id(years, str(datetime.datetime.now().year))

		months = api.get_folder_childrens([current_year])
		print months
		
		current_month = api.get_folder_id(months, datetime.datetime.now().strftime("%B").lower(), lower=True)
		#current_month = api.get_folder_id(months, "september", lower=True)

		print current_month
		#print datetime.datetime.now().strftime("%B").lower()
		if current_month:
			tasks = api.get_hold_tasks(current_month)

			for task in tasks:
				desc = api.get_task_description(task)
				try:
					url = parse_url(desc)
				except:
					print "Error in - " +desc 
					continue  
				print url
				tasks_links_dict[task] = url

	return tasks_links_dict

def upload_attachment(id, filename, target_filename):
	api  = WrikeAPI()
	return api.attach_csv_to_task(id, filename, target_filename)
