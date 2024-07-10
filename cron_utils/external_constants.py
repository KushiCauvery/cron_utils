import os


ABODE_DOCUMENT_SERVER_DETAILS = {
    'address': '10.10.38.7',
    'port': 8019,
    'username': 'om_adobe_uat',
    'password': 'Sec@#$!@1278',
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





#=================================Bankcloud Payment Integration===================================
BANKCLOUD_GENERATE_ORDER_URL = "https://cvh05ghrzc.execute-api.ap-south-1.amazonaws.com/uat/pg/createorders"
BANKCLOUD_USER_TOKEN = "77443eb9-eec7-4ca6-a4ac-3c3ff4fded9d"
BANKCLOUD_USER_SECRET = "04fd0e09-f8a0-4bf2-bf13-33dd63b2a16d"
BANKCLOUD_FETCH_URL = "https://cvh05ghrzc.execute-api.ap-south-1.amazonaws.com/uat/fetch"
ULIP_ROUTE_ID = 265
CONVENTIONAL_ROUTE_ID = 264


