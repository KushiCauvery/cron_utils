
FREQUENCY_WEEKLY_THRICE = 'Weekly_Thrice'

FREQUENCY_DAILY = 'Daily'

NOT_VALID_TABLE = 'This type of table is not present'
NOT_VALID_DATE = "Invalid from date passed"
FILE_CREATION_MESSAGE = {
    'START': 'file creation start',
    'SUCCESS': 'file created successfully',
    'ERROR': 'Unable to write file : '
}
TYPES_OF_TABLES_FOR_DOWNLOAD = {
    'dnc': 'dnc', 'qrops': 'qrops', 'email_brochure': 'email_brochure', 'app_linked_user': 'app_linked_user',
    'funemployment': 'funemployment', 'suitability': 'suitability', 'financial_consultant': 'financial_consultant',
    'group_policy': 'group_policy', 'instainsure': 'instainsure', 'monster_jobs_campaign': 'monster_jobs_campaign',
    'search_term': 'search_term', 'AppGameData': 'AppGameData', 'WhenIGrowUp': 'WhenIGrowUp', 'relationship_manager': 'relationship_manager',
    'agent_of_good': 'agent_of_good'
} 

DICT_TO_EXCEL_COL = [TYPES_OF_TABLES_FOR_DOWNLOAD['suitability'],
                     TYPES_OF_TABLES_FOR_DOWNLOAD['instainsure'],
                     TYPES_OF_TABLES_FOR_DOWNLOAD['monster_jobs_campaign'],
                     TYPES_OF_TABLES_FOR_DOWNLOAD['AppGameData'],
                     TYPES_OF_TABLES_FOR_DOWNLOAD['WhenIGrowUp'], ]

WEEKLY_THRICE_FREQUENCY = {'Sunday': 1, 'Wednesday': 2, 'Saturday': 2}

MEMORY_REPORT_FILENAME = 'Memory_report.csv'
MEMORY_REPORT_SEND_TO = ['nithin.test1234@gmail.com']

BECOME_AN_ADVISOR_REPORT_FILENAME = 'become_an_advisor'
BECOME_AN_ADVISOR_REPORT_SEND_TO = ['nithin.test1234@gmail.com']

MY_ACCOUNT_ACCESS_TOKEN_NO_OF_DAYS = 30

TXN_INIT_STATUS = "Processing"
TRANSACTION_UPDATE_MESSAGE = {
    "Success": "Transaction updated successfully",
    "Fail": "Transaction updation Failed"
}

# get -  save premium details params
PREMIUM_PAYMENT_STR_USER_ID = 'CSC'
PREMIUM_PAYMENT_STR_STATUS = 'Q'
PREMIUM_PAYMENT_STR_F_CODE = '10999'
PREMIUM_PAYMENT_PAYMENT_METHOD = '5'
PREMIUM_PAYMENT_BJ_USER_ID = 'MB08jHe794w604D'
PREMIUM_PAYMENT_REF_NO_PREFIX = 'BJHJGN'
PREMIUM_PAYMENT_CRON_REF_NO_PREFIX = 'BJHJGNPAY'
PREMIUM_SAVE_PAYMENT_USER_ID = 'BJ'

EXPERIAN_MONTHLY_REPORT_EMAIL_IDS = ['kruthibm1805@gmail.com',
                                        'nithin.test1234@gmail.com',]

EMAIL_MESSAGE = {
    'START': 'Email send start',
    'ERROR': 'Email failed ',
    'SUCCESS': 'Email sent successfully'
}

TEBT_POSTING_PAYMENT_MODE_MAPPING = {
    "creditcard": "CC",
    "debitcard": "DC",
    "netbanking": "NB",
    "wallet": "WL",
    "upi": "U",
    "upiqr": "upiqr",
    "emi": "EM",
    "paylater": "paylater",
    "upi_ppi": "U",
    "upi_cc": "U"
}

DOWNLOAD_CSV_EMAIL_SUBJECT_MESSAGES = {'email_brochure': {'subject': 'C2I Download Brochure Weekly Email',
                                                          'message': 'PFA'},
                                       'app_linked_user': {'subject': 'App linked users monthly Email',
                                                           'message': 'PFA'},
                                       'financial_consultant': {'subject': 'Financial Consultant report',
                                                                'message': 'PFA'},
                                       'monster_jobs_campaign': {'subject': 'HDFC Life Career Page Applications',
                                                                 'message': 'PFA'},
                                       'search_term': {'subject': 'Search Terms Report',
                                                       'message': 'PFA'},
                                       TYPES_OF_TABLES_FOR_DOWNLOAD["WhenIGrowUp"]: {"subject": "When I Grow Up Lead Report",
                                                                                     "message": "PFA"},
                                       'group_policy' :{'subject':'Group Policy Download Report',
                                                        'message':'PFA'}

                                       }

GENERIC_CAMPAIGN_LEAD_CAPTURE_CONSTS = {

    # NOTE: Keep campaign keys in upper case

    "CAMPAIGN_NAMES": ["HLV", ],

    "HLV": {

        "KEYS": ["first_name", "last_name", "dob", "mobile", "email", "is_assisted", "assisted_by", ],

        "SERIALIZERS": "HLVSerializer",

        "AGE_LIMIT": (18, 75, ),

        # NOTE: Below parameters are mandatory for report generation

        "REPORT_FREQUENCIES": (FREQUENCY_DAILY, FREQUENCY_WEEKLY_THRICE, ),

        "SUBJECT": "HLV Reports",

        "MESSAGE": "PFA",

    },

}