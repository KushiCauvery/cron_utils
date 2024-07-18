import os

ABODE_DOCUMENT_PASSWORD = os.getenv("ABODE_DOCUMENT_PASSWORD")
ABODE_DOCUMENT_IP = os.getenv("ABODE_DOCUMENT_IP")
ABODE_DOCUMENT_SERVER_DETAILS = {
    'address': ABODE_DOCUMENT_IP,
    'port': 8019,
    'username': 'om_adobe_uat',
    'password': ABODE_DOCUMENT_PASSWORD,
    'directory': '/adobe/'
}


REPORTS_FOR_APP_LINKED_USER = {'to': 'kruthibm1805@gmail.com',
                               'cc': ['nithin.test1234@gmail.com']}

REPORTS_FOR_SEARCH_TERMS = {'to': ['kruthibm1805@gmail.com'],
                            'cc': ['nithin.test1234@gmail.com'],
                            'bcc': ['nithin.test1234@gmail.com']
                            }

REPORTS_FOR_GROUP_POLICY_DOWNLOAD = {'to':['nithin.test1234@gmail.com'],
                                     'cc':['kruthibm1805@gmail.com']}

CRON_SUCCESS_NOTIFICATIONS_TO_EMAIL = 'nithin.test1234@gmail.com'

CRON_SUCCESS_NOTIFICATIONS_CC_LIST = ['kruthibm1805@gmail.com']

REPORTS_FOR_DAILY_LEAD_REPORT = ['kruthibm1805@gmail.com', 'nithin.test1234@gmail.com' ]





