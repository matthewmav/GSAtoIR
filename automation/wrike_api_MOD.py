import requests
import json
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
				# TODO: the next row doesn't do anything in this form, as json() is not inplace
				response.json()
				return response

			except Exception as e:
				print url
				print e
				print "Error fetching from wrike"
				sleep(5)
				continue        

	
	def perform_request_post(self, url, headers = None, data = None):
		while True:
			try:
				response = requests.post(url, headers = headers, data = data)
				response.json()
				return response
			except:
				print response.text
				print "Error fetching from wrike"
				sleep(5)
				continue

	
	def perform_request_put(self, url, headers = None, data = None, params = None):
		while True:
			try:
				response = requests.put(url, headers = headers, data = data, params = params)
				response.json()
				
				return response
			except Exception as e:
				print response.text
				print "Error fetching from wrike"
				sleep(5)
				continue			


	def get_folder_name(self, folder_id):
		url = self._folders_url
		url += "/" + folder_id

		response = requests.get(url, headers = self._headers)
		parsed_response = response.json()

		return parsed_response["data"][0]["title"]		


	def get_folder_id(self, parents, folder_name, lower=False):

		url = self._folders_url
		if parents != None:
			url += "/" + ",".join(parents)

		response = self.perform_request_get(url, headers = self._headers)

		parsed_response = response.json()

		for folder in parsed_response["data"]:
			title = folder["title"]
			if lower:
				title = title.lower()
			if title == folder_name:
				return folder["id"]
		
		return None


	def get_folder_childrens(self, parents):
		url = self._folders_url

		if parents != None:
			#sgy
			if (None not in parents):
				url += "/" + ",".join(parents)
			else:
				assert len(parents) == 1
			#sgyend

		response = self.perform_request_get(url, headers = self._headers)

		parsed_response = response.json()

		return parsed_response["data"][0]["childIds"]


	def get_hold_tasks(self, parent):
		url = self._folders_url
		#url += "/" + parent + "/tasks?status=Completed"
		url += "/" + parent + "/tasks?importance=Low"
		attachments_url = r'https://www.wrike.com/api/v4/tasks/{id}/attachments'
		
		response = self.perform_request_get(url, headers = self._headers)

		parsed_response = response.json()

		tasks_ids = []
		for task in parsed_response["data"]:
			response = self.perform_request_get(attachments_url.format(id=task["id"]), 
												headers=self._headers)
			attachments_list = response.json()

			if len(attachments_list["data"]) == 0:
				tasks_ids.append(task["id"])

		return tasks_ids


	def get_completed_tasks(self, parent):
		url = self._folders_url
		url += "/" + parent + "/tasks?status=Completed"
		attachments_url = r'https://www.wrike.com/api/v4/tasks/{id}/attachments'
		
		response = self.perform_request_get(url, headers = self._headers)

		parsed_response = response.json()

		tasks_ids = []
		for task in parsed_response["data"]:
			response = self.perform_request_get(attachments_url.format(id = task["id"]), headers = self._headers)
			attachments_list = response.json()

			#if len(attachments_list["data"]) != 0:
			tasks_ids.append(task["id"])

		return tasks_ids


	def get_task_description(self, id):
		url = self._tasks_url
		url += "/" + id

		response = requests.get(url, headers = self._headers)

		parsed_response = response.json()

		return parsed_response["data"][0]["description"]


	def get_task_info(self, id):
		url = self._tasks_url
		url += "/" + id

		response = self.perform_request_get(url, headers = self._headers)
		
		parsed_response = response.json()
		return parsed_response        


	def get_task_attachment(self, id):
		url = self._tasks_url
		url += "/" + id + "/attachments"

		response = self.perform_request_get(url, headers = self._headers)

		parsed_response = response.json()
		task_id = parsed_response["data"][0]["id"]

		url = "http://www.wrike.com/api/v4/attachments/{id}/download"
		response = self.perform_request_get(url.format(id = task_id), headers = self._headers)
		attachments = response.text
		return attachments


	def get_attachment(self, id):
		task_id = id

		url = "http://www.wrike.com/api/v4/attachments/{id}/download"
		response = self.perform_request_get(url.format(id = task_id), headers = self._headers)
		attachments = response.content
		return attachments


	def get_folder_metadata_file(self, id):
		url = self._folders_url + "/" + id + "/attachments"

		response = self.perform_request_get(url, headers = self._headers)
		parsed_response = response.json()
		for file in parsed_response["data"]:
			if file["name"] == "metadata.txt":
				return self.get_attachment(file["id"])

		return None


	def get_attachments_by_name(self, id, name):
		url = self._folders_url + "/" + id + "/attachments"

		response = self.perform_request_get(url, headers = self._headers)
		parsed_response = response.json()
		for file in parsed_response["data"]:
			if file["name"] == name:
				return self.get_attachment(file["id"])

		return None


	def upload_file_to_folder(self, id, name, data):
		headers = self._headers
		headers['content-type'] = 'application/octet-stream'
		headers['X-Requested-With'] = 'XMLHttpRequest'
		headers['X-File-Name'] = name

		response = self.perform_request_post('https://www.wrike.com/api/v4/folders/{id}/attachments'.format(id = id), headers=headers, data=data)

		return response	


	def get_folder_info(self, folder_id):
		url = self._folders_url 
		url += "/" + folder_id + '?fields=["color"]'

		response = self.perform_request_get(url, headers = self._headers)
		parsed_response = response.json()

		return parsed_response


	def upload_metadata_file_to_folder(self, id, data):
		headers = self._headers
		headers['content-type'] = 'application/octet-stream'
		headers['X-Requested-With'] = 'XMLHttpRequest'
		headers['X-File-Name'] = "metadata.txt"

		response = self.perform_request_post('https://www.wrike.com/api/v4/folders/{id}/attachments'.format(id = id), headers=headers, data=data)

		return response				


	def attach_csv_to_task(self, id, filename, attachment_name):

		headers = self._headers
		headers['content-type'] = 'application/octet-stream'
		headers['X-Requested-With'] = 'XMLHttpRequest'
		headers['X-File-Name'] = attachment_name

		f = open(filename)
		data = f.read()
		f.close()

		response = self.perform_request_post(
						'https://www.wrike.com/api/v4/tasks/{id}/attachments'.format(id=id), 
						headers=headers, 
						data=data)

		return response


	def update_task_status(self, task_id, status):
		url = self._tasks_url
		url += "/" + task_id + "?status=" + status

		response = requests.put(url, headers = self._headers)
		parsed_response = response.json()

		return parsed_response
