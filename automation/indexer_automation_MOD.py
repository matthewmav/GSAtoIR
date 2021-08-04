from pywinauto import *
from random import randint
from time import sleep


class IndexerAutomation(object):
	_indexer_path = r"C:\Program Files (x86)\GSA SEO Indexer\SEO_Indexer.exe"
	_app = None

	def __init__(self):
		super(IndexerAutomation, self).__init__()
		self._app = Application()

	def start_indexer(self):
		self._app.start(self._indexer_path)
		return self._app.process

	def wait_for_finish(self, process_id):
		prev_process_windows = findwindows.find_windows(process = process_id)
		diff = []

		windows = Desktop(backend="uia")
		while True:
			process_windows = findwindows.find_windows(process = process_id)
			if prev_process_windows != process_windows:
				stop = False

				diff = list(set(process_windows) - set(prev_process_windows))

				for handle in diff:
					window = windows.windows(handle = handle)[0]
					try:
						if "Submission" in window.children()[2].texts()[0]:
							stop = True
							window.children()[0].click()
					except Exception as e:
						print e

				if stop:
					break

			prev_process_windows = process_windows

	def run(self, process_id, link):
		try:
			self._app.windows[0].children[1].click()
		except:
			pass
		controls = self._app[u'TForm1']

		text_box = controls.Edit 
		text_box.set_text(link)

		button = controls.ToolBar1

		windows = Desktop(backend="uia")
		try:
			button.click()
		except:
			import ipdb; ipdb.set_trace()

		try:
			a = windows.window(best_match = "URL not valid")
			a.children()[1].click()
		except:
			pass

		self.wait_for_finish(process_id)

		result_box = controls.TVirtualStringTree 
		result_box.right_click()

		sleep(2)
		
		windows_list = windows.windows()
		context_menu = windows.window(best_match = "Context")
		save_all_button = context_menu.children()[2]
		save_all_button.select()
		save_as = windows.window(best_match = "save_as")
		properties_section = save_as.children()[0]

		file_name = "C:\\Windows\\Temp\\indexer_" + str(randint(0, 10000))
		file_name_label = properties_section.children()[4].children()[0]
		file_name_label.set_text(file_name)

		save_button = save_as.children()[2]
		save_button.click()

		sleep(2)

		yes_no_dialog  = windows.window(best_match = "GSA SEO Indexer v2.54")
		yes_no_dialog.children()[0].click()

		return file_name

