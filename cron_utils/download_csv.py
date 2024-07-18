import datetime
from .app_utils import get_from_date_to_date
from django.conf import settings
from . import constants  
from shared_config import exceptions as ex, exception_constants as ec, email_service
from shared_config.logging import custom_log
from shared_config.utils import export_csv

def validate_table(params, request):
    if params['table'] not in list(constants.TYPES_OF_TABLES_FOR_DOWNLOAD.keys()) + \
            constants.GENERIC_CAMPAIGN_LEAD_CAPTURE_CONSTS["CAMPAIGN_NAMES"]:
        raise ex.GenericException(status_type=ec.STATUS_TYPE["PAYMENT"],
                                  exception_code=ec.NONRETRYABLE_CODE["BAD_REQUEST"],
                                  detail=constants.NOT_VALID_TABLE, request=request,
                                  response_msg=constants.NOT_VALID_TABLE)
def get_table_details(params):
    if constants.TYPES_OF_TABLES_FOR_DOWNLOAD.get(params['table'], '') == 'app_linked_user':
        from .models import AppLinkedUser
        return AppLinkedUser, 'app_linked_user_', ['ndfc_flag', 'metadata'], []
    elif constants.TYPES_OF_TABLES_FOR_DOWNLOAD.get(params['table'], '') == 'search_term':
        from .models import SearchTerm
        return SearchTerm, 'SearchTermReport', ['modified_at'], []
    elif constants.TYPES_OF_TABLES_FOR_DOWNLOAD.get(params.get('table'), '') == 'group_policy':
        from .models import GroupPolicyDownloadReport
        return GroupPolicyDownloadReport, 'GroupPolicyDownload', ['id', 'modified_at'], ['date', 'time']
    return None, '', [], []

def prepare_export_params(table_obj, params, filename):
    kwargs = {}
    if params.get('from_date') and params.get('to_date'):
        from_date, to_date = get_from_date_to_date(params)
        kwargs['created_at__gte'] = from_date
        kwargs['created_at__lte'] = to_date
        if params['table'] in constants.DICT_TO_EXCEL_COL + constants.GENERIC_CAMPAIGN_LEAD_CAPTURE_CONSTS["CAMPAIGN_NAMES"]:
            kwargs['form_type__iexact'] = params['table']
        if params.get('city_id'):
            kwargs['manager_city_mapper_id'] = params.get('city_id')
        filename += f"{params['from_date']}_{params['to_date']}"
    else:
        filename += str(datetime.datetime.now().date())
    result = table_obj.objects.filter(**kwargs).values()
    return result, filename

def adjust_datetime(val):
    if val.tzname() == 'UTC':
        val += datetime.timedelta(hours=5, minutes=30)
    return val.strftime('%d-%m-%Y %H:%M:%S')

def adjust_value(val, params):
    if val is None:
        return ''
    if isinstance(val, datetime.datetime):
        return adjust_datetime(val)
    if isinstance(val, dict) and params['table'] in constants.DICT_TO_EXCEL_COL + \
            constants.GENERIC_CAMPAIGN_LEAD_CAPTURE_CONSTS["CAMPAIGN_NAMES"]:
        return dict(val)
    if not isinstance(val, str):
        return str(val)
    return val

def process_row(row, params, remove_arr_for_form_data):
    form_list = {}
    for key, val in row.items():
        val = adjust_value(val, params)
        if isinstance(val, dict) and key not in remove_arr_for_form_data:
            form_list = row[key]
        else:
            row[key] = val
    row.update(form_list)
    return row

def process_group_policy(row):
    date, time = row['created_at'].split(" ")
    row['date'] = date
    row['time'] = time
    del row['created_at']
    return row


def flatten_result(result, params, remove_arr_for_form_data):
    data = []
    for row in result:
        row = process_row(row, params, remove_arr_for_form_data)
        if params['table'].upper() == "GROUP_POLICY":
            row = process_group_policy(row)
        data.append(row)
    return data


def send_email(params, request, file_details):
    custom_log(level='info', request=request, params={'body': {'params': params},
                                                      'detail': 'email found in params so sending email'})
    try:
        if params['table'] in constants.GENERIC_CAMPAIGN_LEAD_CAPTURE_CONSTS["CAMPAIGN_NAMES"]:
            subject = constants.GENERIC_CAMPAIGN_LEAD_CAPTURE_CONSTS[params['table']]["SUBJECT"]
            message = constants.GENERIC_CAMPAIGN_LEAD_CAPTURE_CONSTS[params['table']]["MESSAGE"]
        else:
            subject = constants.DOWNLOAD_CSV_EMAIL_SUBJECT_MESSAGES[params['table']]['subject']
            message = constants.DOWNLOAD_CSV_EMAIL_SUBJECT_MESSAGES[params['table']]['message']
        destination_file = settings.BASE_URL + settings.MEDIA_URL + 'reports/' + file_details['file_name']
        email_service.send_email_to_user(params['email']['to'], message, subject, params['table'], request,
                                         [destination_file], cc_recipient=params['email']['cc'],
                                         bcc_recipient=params.get('email', {}).get('bcc', []), download_file=False)
    except ex.GenericException as e:
        custom_log(level='info', request=request,
                   params={'body': {}, 'detail': 'error in sending mail due to ' + repr(e.detail)})
    except Exception as e:
        custom_log(level='info', request=request, params={'body': {},
                                                          'detail': 'error in sending mail due to ' + repr(e)})

def download_csv_from_db(params, request):
    remove_arr = []
    extra_fields = []
    validate_table(params, request)
    table_obj, filename, remove_arr, extra_fields = get_table_details(params)
    if not table_obj:
        raise ex.GenericException(status_type=ec.STATUS_TYPE["PAYMENT"],
                                  exception_code=ec.NONRETRYABLE_CODE["BAD_REQUEST"],
                                  detail=constants.NOT_VALID_TABLE, request=request,
                                  response_msg=constants.NOT_VALID_TABLE)
    result, filename = prepare_export_params(table_obj, params, filename)       
    # write correct sequence here
    fieldnames = [f.name for f in table_obj._meta.get_fields()]
    final_fields = [x for x in fieldnames if x not in remove_arr]
    final_fields = final_fields + extra_fields
    data = flatten_result(result, params, remove_arr)
   
    if final_fields and params['table'].upper() == "GROUP_POLICY":
        final_fields.remove('created_at')
    export_params = {'file_name': filename, 'fieldnames': final_fields, 'data': data, 'sheetname': 'Report'}
 
    file_details = export_csv(export_params, request, offline_forms_data=True)
    custom_log(level='info', request=request, params={'body': {'file_details': file_details},
                                                      'detail': 'file generated for db report'})
    
    if 'email' in params:
        send_email(params, request, file_details)
    
    return file_details