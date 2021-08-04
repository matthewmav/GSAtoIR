import requests
import json


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


	def get_folder_id(self, parents, folder_name, lower=False):

		url = self._folders_url
		if parents != None:
			url += "/" + ",".join(parents)

		response = requests.get(url, headers = self._headers)

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

		response = requests.get(url, headers = self._headers)

		parsed_response = response.json()

		return parsed_response["data"][0]["childIds"]


	def get_hold_tasks(self, parent):
		url = self._folders_url
		#url += "/" + parent + "/tasks?status=Completed"
		url += "/" + parent + "/tasks?importance=Low"
		attachments_url = r'https://www.wrike.com/api/v4/tasks/{id}/attachments'
		
		response = requests.get(url, headers = self._headers)

		parsed_response = response.json()

		tasks_ids = []
		for task in parsed_response["data"]:
			response = requests.get(attachments_url.format(id = task["id"]), headers = self._headers)
			attachments_list = response.json()

			if len(attachments_list["data"]) == 0:
				tasks_ids.append(task["id"])

		return tasks_ids


	def get_task_description(self, id):
		url = self._tasks_url
		url += "/" + id

		response = requests.get(url, headers = self._headers)

		parsed_response = response.json()

		return parsed_response["data"][0]["description"]


	def attach_csv_to_task(self, id, filename, attachment_name):

		headers = self._headers
		headers['content-type'] = 'application/octet-stream'
		headers['X-Requested-With'] = 'XMLHttpRequest'
		headers['X-File-Name'] = attachment_name

		f = open(filename)
		data = f.read()
		f.close()

		response = requests.post('https://www.wrike.com/api/v4/tasks/{id}/attachments'.format(id = id), headers=headers, data=data)

		return response


	def update_task_status(self, task_id, status):
		url = self._tasks_url
		url += "/" + task_id + "?status=" + status

		response = requests.put(url, headers = self._headers)
		parsed_response = response.json()

		return parsed_response
