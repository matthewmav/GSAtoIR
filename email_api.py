import time
import re
import imaplib
import email
import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders 
from datetime import datetime
import email_generator as et
import ahref_database_api as ahref_db


class EmailSender(object):
	"""docstring for EmailSender"""
	def __init__(self, username, password):
		super(EmailSender, self).__init__()
		self.username = username
		self.password = password
		self.ORG_EMAIL   = "@gmail.com"
		self.FROM_EMAIL  = self.username + self.ORG_EMAIL
		self.FROM_PWD    = self.password
		self.SMTP_SERVER = "imap.gmail.com"
		self.SMTP_PORT   = 993		

	def send_offer_email(self, writers, batch, task_id, priority = False):  
		# creates SMTP session 
		s = smtplib.SMTP('smtp.gmail.com', 587) 
		  
		# start TLS for security 
		s.starttls() 
		  
		# Authentication 
		s.login(self.FROM_EMAIL, self.FROM_PWD) 
		
		# parse body and co.
		subject = " linkbuilding opdracht"

		for writer in writers:
			writer = writer[1]
			msg = MIMEMultipart()
			msg['to'] = writer
			msg['from'] = self.FROM_EMAIL

			msg['subject'] = subject

			body = et.generate_offer_email(batch, writer, task_id, priority)

			# adding task to sen't to priority list  
			if priority: 
				for task in batch:
					ahref_db.send_task_to_priority(task["id"], writer)

			msg.attach(MIMEText(body, 'html'))

			# Converts the Multipart msg into a string 
			text = msg.as_string() 
			  
			# sending the mail 
			s.sendmail(self.FROM_EMAIL, writer, text) 

		# terminating the session 
		s.quit() 

	def send_email(self, writer, subject, body, file_to_attach = ""):
		# creates SMTP session 
		s = smtplib.SMTP('smtp.gmail.com', 587) 
		  
		# start TLS for security 
		s.starttls() 
		  
		# Authentication 
		s.login(self.FROM_EMAIL, self.FROM_PWD) 

		# parse body and co.
		msg = MIMEMultipart()
		msg['to'] = writer
		msg['from'] = self.FROM_EMAIL

		msg['subject'] = subject

		msg.attach(MIMEText(body, 'html')) 
  		
  		if file_to_attach != "":
			# instance of MIMEBase and named as p 
			p = MIMEBase('application', 'octet-stream') 
	  
			# To change the payload into encoded form 
			f = open(template_name, "r")
			p.set_payload(f.read())
			f.close() 
	  
			# encode into base64 
			encoders.encode_base64(p) 
	   
			p.add_header('Content-Disposition', "attachment; filename= %s" % file) 

			# attach the instance 'p' to instance 'msg' 
			msg.attach(p) 
		

		# Converts the Multipart msg into a string 
		text = msg.as_string() 
		  
		# sending the mail 
		s.sendmail(self.FROM_EMAIL, writer, text) 

		# terminating the session 
		s.quit() 

