import requests
import json
import urllib
from random import randint
import codecs
from time import sleep


class WrikeAPI(object):

	_token = r"token"

	_folders_url = r"https://www.wrike.com/api/v4/folders"
	_tasks_url = r"https://www.wrike.com/api/v4/tasks"

	_headers = {
	'Authorization': 'bearer {token}'.format(token = _token)
	}

	"""docstring for WrikeAPI"""
	def __init__(self):
		super(WrikeAPI, self).__init__()

	def perform_request_get(self, url, headers = None, data = None):
		while True:
			try:
				response = requests.get(url, headers = headers)
				response.json()
				return response
			except Exception as e:
				print e.message
				sleep(5)
				continue

	def perform_request_post(self, url, headers = None, data = None):
		while True:
			try:
				response = requests.post(url, headers = headers, data = data)
				response.json()
				return response
			except:
				sleep(5)
				continue

	def perform_request_put(self, url, headers = None, data = None, params = None):
		while True:
			try:
				response = requests.put(url, headers = headers, data = data, params = params)
				response.json()
				print "Successfully Updated"
				return response
			except Exception as e:
				print e 
				sleep(5)
				continue
		
	def get_folder_id(self, parents, folder_name, lower = False):

		if parents != None and len(parents) == 0:
			return None

		url = self._folders_url
		if parents != None:
			url += "/" + ",".join(parents)

		response = self.perform_request_get(url, headers = self._headers)

		parsed_response = response.json()

		for folder in parsed_response["data"]:
			if lower:
				if folder["title"].lower() == folder_name.lower():
					return folder["id"]

			if folder["title"] == folder_name:
				return folder["id"]
		
		return None

	def get_folder_info(self, folder_id):
		url = self._folders_url 
		url += "/" + folder_id + '?fields=["color"]'

		response = self.perform_request_get(url, headers = self._headers)
		parsed_response = response.json()

		return parsed_response

	def get_folder_childrens(self, parents):
		url = self._folders_url
		
		if parents[0] != None:
			url += "/" + ",".join(parents)
		else:
			return []

		response = self.perform_request_get(url, headers = self._headers)

		parsed_response = response.json()

		return parsed_response["data"][0]["childIds"]

	def update_task_description(self, task_id, desc, params = False):
		url = self._tasks_url
		url += "/" + task_id
		
		data = {"description": desc}

		if params:
			response = self.perform_request_put(url, headers = self._headers, data = data, params = data)
		else:
			response = self.perform_request_put(url, headers = self._headers, data = data)
		
		return response.text

	def update_task_title(self, task_id, title):
		url = self._tasks_url
		
		try:
			title = urllib.quote(title)
		except:
			title = urllib.quote(title.encode("utf-8"))
		
		url += "/" + task_id + "?title=" + title

		data = {"title": title}

		response = self.perform_request_put(url, headers = self._headers, data = data)

		return response.json()

	def update_overview(self, task_id, desc):
		url = self._tasks_url
		url += "/" + task_id

		data = {"description": desc}

		response = self.perform_request_put(url, headers = self._headers, data = data)


		return response.json()


	def get_task_id_contains(self, parents, task_title, lower = False):
		"""
		Get task by name from list of tasks.
		if task title contains the "task_title" - return the id 
		
		Args:
		    parents (TYPE): list of tasks to search in 
		    task_title (TYPE): the title of the requested task 
		    lower (bool, optional): case sensetive or not  
		
		Returns:
		    STR: if there is task who's title contains gived title, return ID, else None
		"""
		url = self._tasks_url
		if parents != None:
			url += "/" + ",".join(parents)

		response = self.perform_request_get(url, headers = self._headers)

		parsed_response = response.json()

		for folder in parsed_response["data"]:
			if lower:
				if task_title.lower() in folder["title"].lower():
					return folder["id"]

			if task_title.lower() in folder["title"]:
				return folder["id"]
		
		return None

	def create_folder(self, parent_id, folder_name):

		url = self._folders_url
		url += "/" + parent_id + "/folders"

		data = {"title": folder_name}
		response = self.perform_request_post(url, headers = self._headers, data = data)

		return response.json()

	def create_task(self, folder_id):
		url = self._folders_url
		url += "/" + folder_id + "/tasks"

		data = {"title": "title", "status": "Deferred"}
		response = self.perform_request_post(url, headers = self._headers, data = data)

		return response.json()

	def create_overview(self, folder_id, desc):
		url = self._folders_url
		url += "/" + folder_id + "/tasks"

		data = {"title": "summery overview", "description": desc, "status": "Deferred"}
		response = self.perform_request_post(url, headers = self._headers, data = data)

		return response.json()

	def get_hold_tasks(self, parent):
		url = self._folders_url
		url += "/" + parent + "/tasks?status=Deferred"
		attachments_url = r'https://www.wrike.com/api/v4/tasks/{id}/attachments'
		
		response = self.perform_request_get(url, headers = self._headers)

		parsed_response = response.json()

		tasks_ids = []
		for task in parsed_response["data"]:
			response = self.perform_request_get(attachments_url.format(id = task["id"]), headers = self._headers)
			attachments_list = response.json()

			if len(attachments_list["data"]) == 0:
				tasks_ids.append(task["id"])

		return tasks_ids

	def get_all_tasks(self, parent):
		url = self._folders_url
		url += "/" + parent + "/tasks"
		attachments_url = r'https://www.wrike.com/api/v4/tasks/{id}/attachments'
		
		response = self.perform_request_get(url, headers = self._headers)

		parsed_response = response.json()

		tasks_ids = []
		for task in parsed_response["data"]:
			tasks_ids.append(task["id"])

		return tasks_ids

	def get_all_tasks_detailed(self, parent):
		url = self._folders_url
		url += "/" + parent + "/tasks"
		attachments_url = r'https://www.wrike.com/api/v4/tasks/{id}/attachments'
		

		response = self.perform_request_get(url, headers = self._headers)

		parsed_response = response.json()

		tasks_ids = []
		for task in parsed_response["data"]:
			tasks_ids.append(task)

		return tasks_ids

	def get_active_tasks(self, parent):
		url = self._folders_url
		url += "/" + parent + "/tasks?status=Active"
		attachments_url = r'https://www.wrike.com/api/v4/tasks/{id}/attachments'
		
		response = self.perform_request_get(url, headers = self._headers)

		parsed_response = response.json()

		tasks_ids = []
		for task in parsed_response["data"]:
			response = self.perform_request_get(attachments_url.format(id = task["id"]), headers = self._headers)
			attachments_list = response.json()
			tasks_ids.append(task["id"])


		return tasks_ids

	def assign_task_to_user(self, task_id, user):
		"""
			Assigns task (by ID) to a user
		"""
		url = self._tasks_url
		url += "/" + task_id + "?addResponsibles=" + '["{0}"]'.format(user)

		response = self.perform_request_put(url, headers = self._headers)
		parsed_response = response.json()

		return parsed_response

	def unassign_task_to_user(self, id, user):
		"""
			Assigns task (by ID) to a user
		"""
		url = self._tasks_url
		url += "/" + task_id + "?removeResponsibles=" + '["{0}"]'.format(user)

		response = self.perform_request_put(url, headers = self._headers)
		parsed_response = response.json()

		return parsed_response

	def update_task_title(self, task_id, title):
		url = self._tasks_url
		url += "/" + task_id + "?title=" + title

		response = self.perform_request_put(url, headers = self._headers)
		parsed_response = response.json()

		return parsed_response

	def update_task_status(self, task_id, status):
		url = self._tasks_url
		url += "/" + task_id + "?status=" + status

		response = self.perform_request_put(url, headers = self._headers)
		parsed_response = response.json()

		return parsed_response

	def get_folder_name(self, folder_id):
		url = self._folders_url
		url += "/" + folder_id

		response = self.perform_request_get(url, headers = self._headers)
		parsed_response = response.json()

		return parsed_response["data"][0]["title"]

	def get_completed_tasks(self, parent):
		url = self._folders_url
		url += "/" + parent + "/tasks?status=Completed"
		attachments_url = r'https://www.wrike.com/api/v4/tasks/{id}/attachments'
		
		response = self.perform_request_get(url, headers = self._headers)

		parsed_response = response.json()

		tasks_ids = []
		for task in parsed_response["data"]:
			response = self.perform_request_get(attachments_url.format(id = task["id"]), headers = self._headers)
			tasks_ids.append(task["id"])

		return tasks_ids

	def get_task_attachment(self, id):
		url = self._tasks_url
		url += "/" + id + "/attachments"

		response = self.perform_request_get(url, headers = self._headers)

		parsed_response = response.json()
		task_id = parsed_response["data"][-1]["id"]

		url = "http://www.wrike.com/api/v4/attachments/{id}/download"
		response = requests.get(url.format(id = task_id), headers = self._headers)
		attachments = response.content
		return attachments

	def get_task_attachment_list(self, parentId):
		url = self._tasks_url
		url += "/" + parentId + "/attachments"

		response = self.perform_request_get(url, headers = self._headers)

		parsed_response = response.json()
		attachments = parsed_response["data"]

		return attachments		

	def download_attackment_by_id(self, attachment_id):
		url = "http://www.wrike.com/api/v4/attachments/{id}/download"

		response = requests.get(url.format(id = attachment_id), headers = self._headers)
		attachments = response.content
		return attachments

	def get_task_info(self, id):
		url = self._tasks_url
		url += "/" + id

		response = self.perform_request_get(url, headers = self._headers)
		
		parsed_response = response.json()
		return parsed_response

	def get_task_description(self, id):
		url = self._tasks_url
		url += "/" + id

		response = self.perform_request_get(url, headers = self._headers)

		parsed_response = response.json()

		return parsed_response["data"][0]["description"]

	def update_task_priority(self, task_id, priority):
		url = self._tasks_url

		url += "/" + task_id + "?importance=" + priority

		data = {"importance": priority}

		response = self.perform_request_put(url, headers = self._headers, data = data)

		return response.json()

	def attach_to_task(self, id, filename, attachment_name):

		headers = self._headers
		headers['content-type'] = 'application/octet-stream'
		headers['X-Requested-With'] = 'XMLHttpRequest'
		headers['X-File-Name'] = attachment_name

		print filename
		f = open(filename, "rb+")
		data = f.read()
		f.close()

		response = self.perform_request_post('https://www.wrike.com/api/v4/tasks/{id}/attachments'.format(id = id), headers=headers, data=data)

		return response