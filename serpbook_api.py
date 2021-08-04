import requests
import logging 



class SerpBookAPI(object):
	"""docstring for SerpBookAPI"""

	api_key = r"key"

	serp_book_link = r"https://serpbook.com/serp/api/?action={action}&auth={api_key}"

	def __init__(self):
		super(SerpBookAPI, self).__init__()

	def add_keywords(self, category_name, url, keywords, region):

		# generate list of links 
		#urls_list = "&url[]={url}".format(url = url) * len(keywords)
		logging.info("Sending keywords to Serpbook ")
		logging.debug(url)
		logging.debug(keywords)

		start = 0 
		for index in xrange(10, len(keywords), 10):
			logging.info("sending keywords part to serpbook from {0} to {1}".format(start, index))
			keywords_to_post = keywords[start:index]
			urls_list = "&url[]={url}".format(url = url) * len(keywords_to_post)			
			keywords_to_post = ''.join(["&kw[]={keyword}".format(keyword = keyword) for keyword in keywords_to_post])
			
			additional_flags = r"&language=en&category={category}&ignore_local=1&region={region}".format(category = category_name, region =region)			
			final_url = self.serp_book_link.format(action = "addkeyword", api_key = self.api_key) + urls_list + keywords_to_post + additional_flags
			resp = requests.get(final_url)

			start = index

		logging.info("Sending the remaining keywords")

		keywords = keywords[start:]
		urls_list = "&url[]={url}".format(url = url) * len(keywords)
		keywords = ''.join(["&kw[]={keyword}".format(keyword = keyword) for keyword in keywords])

		additional_flags = r"&language=en&category={category}&ignore_local=1&region={region}".format(category = category_name, region =region)

		final_url = self.serp_book_link.format(action = "addkeyword", api_key = self.api_key) + urls_list + keywords + additional_flags

		resp = requests.get(final_url)

	def check_results_ready(self, category_name):

		category_viewlink_url = self.serp_book_link.format(action = "getsinglecategory", api_key = self.api_key)

		category_viewlink_url += "&category=" + category_name

		resp = requests.get(category_viewlink_url).json()

		viewlink = resp[category_name]

		
		category_data = requests.get(viewlink).json()
		granks = [keyword["grank"].strip() for keyword in category_data]
		if "??" in granks:
			return False

		
		for keyword in category_data:
			if keyword["searchvolume"] is None:
				return False

		return True

	def get_ready_results(self, category_name):

		category_viewlink_url = self.serp_book_link.format(action = "getsinglecategory", api_key = self.api_key)

		category_viewlink_url += "&category=" + category_name

		resp = requests.get(category_viewlink_url).json()
		viewlink = resp[category_name]

		category_data = requests.get(viewlink).json()
		links = [(keyword["rankingurl"], keyword["kw"], keyword["grank"]) for keyword in category_data if "NOT FOUND" not in keyword["rankingurl"]]

		return links 


	def fetch_category(self, category_name):

		keywords_data = [] 

		category_viewlink_url = self.serp_book_link.format(action = "getsinglecategory", api_key = self.api_key)

		category_viewlink_url += "&category=" + category_name

		resp = requests.get(category_viewlink_url).json()

		viewlink = resp[category_name]

		while True:
			category_data = requests.get(viewlink).json()
			granks = [keyword["grank"].strip() for keyword in category_data]
			if "??" not in granks:
				break
			logging.info("There are still empty GRANKS")


		for keyword in category_data:
			if keyword["searchvolume"] is None:
				keyword["searchvolume"] = "n/a"
			keywords_data.append([keyword["url"], keyword["kw"], keyword["grank"], keyword["searchvolume"]])

		return keywords_data

	def delete_category(self, category_name):
	
		delete_category = self.serp_book_link.format(action = "delcategory", api_key = self.api_key)
		delete_category += "&category=" + category_name

		return requests.get(delete_category).json()

	def generate_result_csv(self, category_name):
		keywords = self.fetch_category(category_name)

		keywords = sorted(keywords, key = lambda x: (x[1], int(x[3])))

		csv_data = ""
		
		
		
		prev_keyword = ""		
		for keyword in keywords:

			if keyword[-1] == "n/a":
				continue

			if int(keyword[-1]) != 0:

				if len(keyword[1].split(" ")) == 2 and len(prev_keyword.split(" ")) == 2:
					if keyword[1].split(" ")[0] != prev_keyword.split(" ")[0]:
						csv_data += "\n"

				elif len(keyword[1].split(" ")) == 3 or len(prev_keyword.split(" ")) == 3:
					if keyword[1].split(" ")[0] != prev_keyword.split(" ")[0] or keyword[1].split(" ")[1] != prev_keyword.split(" ")[1]:

						csv_data += "\n"


				csv_data += ','.join(keyword) + "\n"	
				prev_keyword = keyword[1]




		return csv_data	

	def check_category_status(self, category_name):

		# getting category status 
		resp = requests.get(self.serp_book_link.format(action="refreshremaining", api_key = self.api_key) + "&category=" + category_name)
			
		try:
			resp = resp.json()

			remaining = int(resp["remaining"])

			total = int(resp["total"])
		except:
			
			return 1,1 
	
		return remaining, total


	def get_max_number_to_upload(self):

		resp = requests.get(self.serp_book_link.format(action = "fetchaccountinfo", api_key = self.api_key))

		resp = resp.json()

		daily_added = int(resp["kw_daily_added_remaining"])
		free_on_serpbook = int(resp["kw_package"]) - int(resp["kw_used"])
		
		return min(daily_added, free_on_serpbook)
