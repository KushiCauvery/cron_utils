




import csv
import os
from cron_utils.bankcloud import BankCloudPaymentService
from cron_utils import external_constants as constants

from cron_utils.download_csv import download_csv_from_db
from datetime import datetime
from cron_utils.utils import send_daily_mobile_report_sftp

from shared_config.report_excel_sheet import report_excel_sheet
from Cronjob import settings
from cron_utils.models import Memory,CustomerServiceForm
from cron_utils.email_services import send_email_to_users
from shared_config.external_constants import REPORT_ACCESS_PASSWORD
from cron_utils.constants import MEMORY_REPORT_FILENAME,MEMORY_REPORT_SEND_TO,BECOME_AN_ADVISOR_REPORT_FILENAME,BECOME_AN_ADVISOR_REPORT_SEND_TO



class TaskPerformed:
    
     # to send mail for app linked users report
     def mail_app_linked_users_report(self, from_date, to_date):
        """this is a monthly reports for details of people who have requested for app-url"""
        params = {'from_date': from_date, 'to_date': to_date, 'table': 'app_linked_user', 'email':
            constants.REPORTS_FOR_APP_LINKED_USER}
        download_csv_from_db(params, None)
        
        
     def send_search_term_report_email(self, from_date, to_date):
        """this is a daily reports for search terms on global search page"""
        params = {'from_date': from_date, 'to_date': to_date, 'table': 'search_term',
                  'email': constants.REPORTS_FOR_SEARCH_TERMS
                  }
        download_csv_from_db(params, None)
    
     def send_daily_group_policy_report(self, from_date, to_date):
        params = {'from_date': from_date, 'to_date': to_date, 'table': 'group_policy',
                  'email': constants.REPORTS_FOR_GROUP_POLICY_DOWNLOAD
                  }
        print('send_daily grouppolicy')
        download_csv_from_db(params, None)
    
     def send_memory_report(self):
        """
        Abstract function to send memories created by user
        :param date_from:
        :param frequency:
        :return:
        """
        memories = Memory.objects.all().order_by('-created_at')
        file_name = MEMORY_REPORT_FILENAME
        file_path = settings.MEDIA_ROOT + file_name
        if os.path.exists(file_path):
            os.remove(file_path)
        message = "Hi, <br><br>Please find attached the memories created by users."
        subject = "Memory Report"
        with open(settings.MEDIA_ROOT + file_name, 'w') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(["Id", "Name", "mobile", "Relation", "Lost", "Story", "Image", "Video"])

            for memory in memories:
                lost_ago = datetime.today().year - memory.lost_in_year if memory.lost_in_year else None
                image_url = settings.IMAGE_URL + memory.image.url if memory.image else ''
                row = (memory.id, memory.name, memory.mobile, memory.relation, lost_ago, memory.story, image_url,
                       memory.video_url)
                writer.writerow(row)

        destination_file = str(settings.BASE_DIR) + '/' + settings.MEDIA_URL + file_name
        send_email_to_users(to_address=MEMORY_REPORT_SEND_TO, message=message, subject=subject, request=None,
                           attachment=[destination_file])
        return {'status': True, 'message': "Email sent successfully"}

    
     def send_become_an_advisor_report(self):
            """
            sends email for become an advisor page
            """
            table_obj = CustomerServiceForm
            qs = CustomerServiceForm.objects.filter(form_type='Become An Advisor')
            file_name = BECOME_AN_ADVISOR_REPORT_FILENAME + str(datetime.now().date()) + '.csv'
            file_path = settings.MEDIA_ROOT + file_name
            if os.path.exists(file_path):
                os.remove(file_path)
            message = "Hi, <br><br>PFA report"
            subject = "Become an advisor"
            with open(settings.MEDIA_ROOT + file_name, 'w') as f:
                writer = csv.writer(f, delimiter=',')
                writer.writerow(['created_at', 'form_type', 'name', 'phone', 'email', 'dob', 'city', 'state',
                                'opportunity', 'ndnc'])
                for data in qs:
                    row = (data.created_at, data.form_type, data.form_data.get('name'), data.form_data.get('phone'),
                        data.form_data.get('email'), data.form_data.get('dob'), data.form_data.get('city'),
                        data.form_data.get('state'), data.form_data.get('opportunity'), data.form_data.get('ndnc_flag'))
                    writer.writerow(row)

            destination_file = str(settings.BASE_DIR) + '/' + settings.MEDIA_URL + file_name
            send_email_to_users(to_address=BECOME_AN_ADVISOR_REPORT_SEND_TO, message=message, subject=subject,
                            request=None,
                            attachment=[destination_file])
            return {'status': True, 'message': "Email sent successfully"}
        
     def send_daily_lead_data_report(self, from_date, to_date):
            params = {'from_date': from_date, 'to_date': to_date,
                    'email': constants.REPORTS_FOR_DAILY_LEAD_REPORT,
                    'report_types': 'lead,registration', 'password':REPORT_ACCESS_PASSWORD,
                    'payment_status': 'success', 'generate_new': True,
                    'is_cron_task': True,
                    'from_time': " 12:00:00", 'to_time': " 11:59:59"
                    }
            report_excel_sheet(params, None)
    
     
        
        
        

def update_processing_txn(hours, minutes=0):
    """
    updates the BankCloud transactions which are pending in processing status
    """
    pending_txn_list = BankCloudPaymentService().get_pending_txn(hours, minutes=minutes)
    if not pending_txn_list:
        return
    BankCloudPaymentService().fetch_txn_details(pending_txn_list)
    
    

        
    
        
        