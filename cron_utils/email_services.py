from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from itertools import chain
import os
import smtplib
import requests
from shared_config.settings import settings
from shared_config.logging import custom_log
from cron_utils.constants import EMAIL_MESSAGE
from shared_config.exceptions import GenericException
from shared_config.exception_constants import STATUS_TYPE,RETRYABLE_CODE

from email.mime.multipart import MIMEMultipart
import logging


logger = logging.getLogger("default")

def initialize_mail_details(subject, from_address, to_address, cc_recipient, bcc_recipient, message):
    mail_details = MIMEMultipart('alternative')
    mail_details['subject'] = subject
    mail_details['from'] = from_address
    mail_details['to'] = ", ".join(to_address) if isinstance(to_address, list) else to_address
    if cc_recipient:
        mail_details['cc'] = ", ".join(cc_recipient)
    if bcc_recipient:
        mail_details['bcc'] = ", ".join(bcc_recipient)
    mail_details.attach(MIMEText(message, 'html'))
    return mail_details

def attach_files(mail_details, attachment):
    if not attachment:
        return
    for files in attachment:
        if 'file' in files:
            attach_file = MIMEBase('application', 'pdf')
            attach_file.set_payload(files['file'])
            encoders.encode_base64(attach_file)
            attach_file.add_header('Content-Disposition', 'attachment', filename=files.get('file_name', ''))
            mail_details.attach(attach_file)
        else:
            with open(files, 'rb') as file:
                part = MIMEBase('application', "octet-stream")
                part.set_payload(file.read())
                encoders.encode_base64(part)
                file_name = os.path.basename(files)
                part.add_header('Content-Disposition', f'attachment; filename="{file_name}"')
                mail_details.attach(part)

def send_email(mail_details, cc_recipient):
    server_class = smtplib.SMTP_SSL if settings.USE_SMTP_SSL else smtplib.SMTP
    with server_class(settings.SMTP_DOMAIN, settings.SMTP_PORT) as server:
        if not settings.USE_SMTP_SSL and settings.EMAIL_USE_TLS:
            server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_FROM_EMAIL, cc_recipient, mail_details.as_string())

def handle_exceptions(exception, request, to_address, message, subject):
    body = {
        "to_address": to_address,
        "message": message,
        "subject": subject
    }
    raise GenericException(
        status_type=STATUS_TYPE["EMAIL"],
        exception_code=RETRYABLE_CODE["EMAIL_FAILURE"],
        detail=EMAIL_MESSAGE['ERROR'] + str(exception),
        body=body,
        request=request
    )

def send_email_to_users(to_address, message, subject, request, from_address='', attachment=False, cc_recipient=None, bcc_recipient=None):
    """
    Send an email to users with optional attachments.

    :param to_address: Email address of the recipient(s)
    :param message: Message content for the email
    :param subject: Subject of the email
    :param request: HTTP request object
    :param from_address: Email address of the sender
    :param attachment: List of file paths or dictionaries with 'file' and 'file_name' keys
    :param cc_recipient: List of email addresses for CC
    :param bcc_recipient: List of email addresses for BCC
    """
    if cc_recipient is None:
        cc_recipient = []
    if bcc_recipient is None:
        bcc_recipient = []
    if isinstance(to_address, str):
        to_address = [to_address]

    try:
        from_address = from_address or settings.SMTP_FROM_EMAIL
        cc_recipient += to_address
        cc_recipient += bcc_recipient

        mail_details = initialize_mail_details(subject, from_address, to_address, cc_recipient, bcc_recipient, message)
        attach_files(mail_details, attachment)

        send_email(mail_details, cc_recipient)
        
        custom_log(level="info", request=None, params={'msg': EMAIL_MESSAGE['SUCCESS'],
                                                       'data': {'mail_details': mail_details.as_string(),
                                                                'recipient': cc_recipient}})
        return {'status': True}

    except GenericException as e:
        raise GenericException(status_type=STATUS_TYPE["EMAIL"], exception_code=RETRYABLE_CODE["EMAIL_FAILURE"],
                               detail=e.detail, request=request)
    except Exception as e:
        handle_exceptions(e, request, to_address, message, subject)
