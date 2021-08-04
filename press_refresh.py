from selenium import webdriver  
from time import sleep
from selenium.webdriver.common.keys import Keys


USERNAME = "anymail@anymail.com"
PASSWORD = "pass"


def refresh():
	driver = webdriver.Chrome(executable_path=r"C:\Users\Administrator\Documents\chromedriver.exe")
	#login(driver, "https://canva.com/login", "meirtolpin11@gmail.com", "kohoioki11")

	driver.get("https://serpbook.com/login?r=/serp/")

	sleep(5)
	username = driver.find_element_by_id("username")
	password = driver.find_element_by_id("password")
	
	username.send_keys(USERNAME)
	password.send_keys(PASSWORD)

	# pressw login
	driver.find_element_by_class_name("btn").click()

	sleep(5)

	driver.get("https://serpbook.com/serp/settings")

	sleep(5)
	# refresh
	while True:
		sleep(5)
		driver.find_element_by_xpath("//button[contains(.,'Refresh Monthly Searches Values')]").click()

	sleep(5)
	driver.quit()