import datetime
from wrike_api_MOD import * 



NOEL_ACCOUNT_ID = "999999"


def parse_url(description):
	print description
	url = ("http" + description.split("http")[1]).split("<")[0].split(">")[0].replace("\"", "")
	return url

### sgy icluded params years month
def get_links_to_index(years_to_get=None, months_to_get=None):
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
		### sgyend

		years = api.get_folder_childrens([domain])
		
		### sgy
		if not years_to_get:
			current_year = api.get_folder_id(years, str(datetime.datetime.now().year))
		else:
			current_year = api.get_folder_id(years, years_to_get)
		### sgyend

		months = api.get_folder_childrens([current_year])
		
		### sgy
		if not months_to_get:
			month = api.get_folder_id(months, datetime.datetime.now().strftime("%B").lower(), lower=True)

		else: 
			month = api.get_folder_id(months, months_to_get.lower(), lower=True)
		### sgyend

		if month:
			tasks = api.get_hold_tasks(month)

			for task in tasks:
				try:
					details = api.get_task_info(task)
					
					if NOEL_ACCOUNT_ID in details["data"][0]['responsibleIds']:

						desc = details["data"][0]["description"]
						try:
							url = parse_url(desc)
						except:
							print "Error in - " + desc 
							continue  
						print url
						tasks_links_dict[task] = url

				except:
					print "Error Getting task details"

	return tasks_links_dict


def upload_attachment(id, filename, target_filename):
	api = WrikeAPI()

	return api.attach_csv_to_task(id, filename, target_filename)
