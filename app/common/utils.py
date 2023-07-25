import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
import requests
import os
from django.conf import settings
from django.template.loader import render_to_string 
from django.core.mail import EmailMessage
from django.conf import settings
import telegram

def valid_image_extension(file_name):
	if file_name.endswith((".jpg", "jpeg", ".png")):
		return True
	else:
		return False

def sending_mail(subject, template_name, template_data, to_email):
	try:
        
		html_template = os.path.join(settings.BASE_DIR,f'templates/email_templates/{template_name}.html')
		html_message = render_to_string(html_template, { 'context': template_data})
		from_email = settings.EMAIL_HOST_USER
		message = EmailMessage(subject, html_message, from_email, [to_email])
		message.content_subtype = 'html'
		message.send()
		return True
	except Exception as msg:
		return False


def send_notification_on_discord(response_message, thumbnail = None):
	try:

		discord_webhook_url = settings.DISCORD_WEBHOOK_URL
		Message = {
		"content": response_message
		}
		if thumbnail:
			if valid_image_extension(thumbnail.name):
				files = {f'{thumbnail}': thumbnail.read()}
				file_name = files.get(thumbnail)
				requests.post(discord_webhook_url, data=Message, files=files)
			else:
				return False, 'Invalid image type.'
		requests.post(discord_webhook_url, data=Message)
		return True, 'Message sent successfully from discord api.'

	except Exception as e:
		raise e


def send_notification_on_telegram(response_message, thumbnail = None):
	TELEGRAM_URL = 'https://api.telegram.org/bot'
	try:
		TOKEN = settings.TELEGRAM_TOKEN
		chat_id = "-671876824"
		text = response_message
		if thumbnail:
			if valid_image_extension(thumbnail.name):
				bot = telegram.Bot(token=TOKEN)
				bot.send_message(chat_id=chat_id, text=response_message)
				bot.send_photo(chat_id, thumbnail)
			else:
				return False, 'Invalid image type.'
		else:
			url = f"{TELEGRAM_URL}{TOKEN}/sendMessage?chat_id={chat_id}&text={text}"
			r = requests.get(url)
		return True, 'Message successfully sent'
	except Exception as e:
		return False, str(e)


def invoice_send(pdf_name, file_link, request):
	path = settings.BASE_DIR/'static/invoice'
	pdf_name = f'{pdf_name}_invoice_info.pdf'
	filename = Path(f'{path}/{pdf_name}')
	response = requests.get(file_link)
	filename.write_bytes(response.content)
	
	fromaddr = settings.EMAIL_HOST_USER
	toaddr = request.user.email
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject'] = "Stripe Invoice"
	body = f"Invoice data for {request.user.first_name}"
	msg.attach(MIMEText(body, 'plain'))
	pdf_file_path = f'{settings.BASE_DIR}/static/invoice/{pdf_name}'
	attachment = open(pdf_file_path, "rb")
	p = MIMEBase('application', 'octet-stream')
	p.set_payload((attachment).read())
	encoders.encode_base64(p)
	p.add_header('Content-Disposition', "attachment; filename= %s" % pdf_name)
	msg.attach(p)
	s = smtplib.SMTP('smtp.gmail.com', 587)
	s.starttls()
	s.login(fromaddr, settings.EMAIL_HOST_PASSWORD)
	text = msg.as_string()
	s.sendmail(fromaddr, toaddr, text)
	s.quit()
	os.remove(pdf_file_path)