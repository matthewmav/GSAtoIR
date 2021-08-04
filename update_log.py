from wrike_api import * 
from wrike_functions import * 

api = WrikeAPI()

overview = r"IEACKIKHKQMJLFKZ"
short_overview = r"IEACKIKHKQMJLFNK"
href_log = r"IEACKIKHKQMJN7KD"

f = open("reports/summary.txt", "r")
data = f.read()
f.close()

f = open("reports/short_summary.txt", "r")
short_data = f.read()
f.close()

f = open("logs/href.log", "r")
href = f.read()
f.close()

api.update_task_description(overview, data.replace("\n", "<br>"))
api.update_task_description(short_overview, short_data.replace("\n", "<br>"))
api.update_task_description(href_log, href.replace("\n", "<br><br>"))
