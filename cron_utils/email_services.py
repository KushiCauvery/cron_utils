


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


def send_email_to_users(to_address, message, subject, request, from_address = '', attachment=False, cc_recipient=[], bcc_recipient=[]):
    """
    :param to_address(str) email address of recipient
    :param message(str) message for email
    :param subject(str) subject for email
    :param request(obj) http obj
    :param from_address(str) email address of sender
    :param attachment(str) link to file
    :param cc_recipient(list) email address/es of recipients which needs to be added as CC
    :param bcc_recipient(list) email address/es of recipients which needs to be added as BCC
    helps to send mail to users with attachment
    """
    try:
        mail_details = MIMEMultipart('alternative')
        mail_details['subject'] = subject
        mail_details['from'] = from_address if from_address else settings.SMTP_FROM_EMAIL
        if cc_recipient:
            mail_details['cc'] = ", ".join(cc_recipient)
        if type(to_address) == list:
            temp_to_address = ", ".join(to_address)
            mail_details['to'] = temp_to_address
            cc_recipient = cc_recipient + to_address
        else:
            mail_details['to'] = to_address
            cc_recipient.append(to_address)
        if bcc_recipient:
            mail_details['bcc'] = ", ".join(bcc_recipient)
            # bcc_recipient.append(to_address)
            cc_recipient = list(chain(cc_recipient, bcc_recipient))
        # Record the MIME type text/html.
        HTML_BODY = MIMEText(message, 'html')
        mail_details.attach(HTML_BODY)
        file_list = []
        if attachment:
            for files in attachment:
                if 'file' in files:
                    attachFile = MIMEBase('application', 'pdf')
                    attachFile.set_payload(files['file'])
                    encoders.encode_base64(attachFile)
                    attachFile.add_header('Content-Disposition', 'attachment', filename=files.get('file_name', ''))
                    mail_details.attach(attachFile)
                else:
                    file_list.append(files)
        for files in file_list:
            part = MIMEBase('application', "octet-stream")
            part.set_payload(open(files, 'rb').read())
            encoders.encode_base64(part)
            file_name = files.split('/')[-1]
            part.add_header('Content-Disposition', 'attachment; filename="' + file_name + '"')
            mail_details.attach(part)

        if settings.USE_SMTP_SSL:
            server = smtplib.SMTP_SSL(settings.SMTP_DOMAIN, settings.SMTP_PORT)
            # server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        else:
            server = smtplib.SMTP(settings.SMTP_DOMAIN, settings.SMTP_PORT)
            if settings.EMAIL_USE_TLS:
                server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        # from_email = settings.SUPPORT_EMAIL if 'is_support_mail' in metadata and metadata['is_support_mail'] else \
        #     settings.SMTP_FROM_EMAIL
        server.sendmail(settings.SMTP_FROM_EMAIL, cc_recipient, mail_details.as_string())
        server.quit()
        custom_log(level="info", request=None, params={'msg': EMAIL_MESSAGE['SUCCESS'],
                                                       'data': {'mail_details': mail_details.as_string(),
                                                                'recipient': cc_recipient}})
        return {'status': True}
    except GenericException as e:
        raise GenericException(status_type=STATUS_TYPE["EMAIL"], exception_code=RETRYABLE_CODE[
                               "EMAIL_FAILURE"], detail=e.detail, request=request)
    except Exception as e:
        body = {
            "to_address": to_address,
            "message": message,
            "subject": subject
        }
        raise GenericException(status_type=STATUS_TYPE["EMAIL"], exception_code=RETRYABLE_CODE[
                               "EMAIL_FAILURE"], detail=EMAIL_MESSAGE['ERROR'] + str(e), body=body, request=request)


def download_file(url, path, chunk=2048):
    """
    :param url(str) link to file where it is currently present
    :param path(str) location where downloaded file needs to be kept
    helps to download files in chunk when path to file is provided
    """
    req = requests.get(url)
    local_dir = path.rsplit('/', 1)[0] + "/"
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    if req.status_code == 200:
        with open(path, 'wb') as f:
            for chunk in req.iter_content(chunk):
                f.write(chunk)
            f.close()
        return path
    raise Exception('Given url is return status code:{}'.format(req.status_code))