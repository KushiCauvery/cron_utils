import datetime
from .app_utils import get_from_date_to_date
from django.conf import settings
from . import constants  
from shared_config import exceptions as ex, exception_constants as ec, email_service
from shared_config.logging import custom_log
from shared_config.utils import export_csv

def download_csv_from_db(params, request):
    
    remove_arr = []
    extra_fields = []
    remove_arr_for_form_data = []
    if params['table'] not in list(constants.TYPES_OF_TABLES_FOR_DOWNLOAD.keys()) + \
                constants.GENERIC_CAMPAIGN_LEAD_CAPTURE_CONSTS["CAMPAIGN_NAMES"]:
            raise ex.GenericException(status_type=ec.STATUS_TYPE["PAYMENT"], exception_code=ec.NONRETRYABLE_CODE["BAD_REQUEST"],
                                detail=constants.NOT_VALID_TABLE, request=request, response_msg=constants.NOT_VALID_TABLE)
    
    elif constants.TYPES_OF_TABLES_FOR_DOWNLOAD.get(params['table'], '') == 'app_linked_user':
        from .models import AppLinkedUser
        table_obj = AppLinkedUser
        filename = 'app_linked_user_'
        remove_arr = ['ndfc_flag', 'metadata']
    
    elif constants.TYPES_OF_TABLES_FOR_DOWNLOAD.get(params['table'], '') == 'search_term':
            from .models import SearchTerm
            table_obj = SearchTerm
            filename = 'SearchTermReport'
            remove_arr = ['modified_at']
    
    elif constants.TYPES_OF_TABLES_FOR_DOWNLOAD.get(params.get('table'), '') == 'group_policy':
        from .models import GroupPolicyDownloadReport
        table_obj = GroupPolicyDownloadReport
        filename = 'GroupPolicyDownload'
        remove_arr = ['id', 'modified_at']
        extra_fields = ['date', 'time']
        if not params.get('from_date'):
            raise ex.GenericException(status_type=ec.STATUS_TYPE["APP"], exception_code=ec.NONRETRYABLE_CODE["BAD_REQUEST"],
                                   detail=constants.NOT_VALID_DATE, request=None, response_msg=constants.NOT_VALID_DATE)
    
            
    # write correct sequence here
    fieldnames = [f.name for f in table_obj._meta.get_fields()]
    final_fields = [x for x in fieldnames if x not in remove_arr]
    final_fields = final_fields + extra_fields
    
    kwargs = {}
    if params.get('from_date', '') and params.get('to_date', ''):
        from_date, to_date = get_from_date_to_date(params)
        kwargs['created_at__gte'] = from_date
        kwargs['created_at__lte'] = to_date
        if params['table'] in constants.DICT_TO_EXCEL_COL + constants.GENERIC_CAMPAIGN_LEAD_CAPTURE_CONSTS["CAMPAIGN_NAMES"]:
            kwargs['form_type__iexact'] = params['table']
        if params.get('city_id'):
            kwargs['manager_city_mapper_id'] = params.get('city_id')
        filename += params['from_date'] + '_' + params['to_date']
    else:
        filename += str(datetime.datetime.now().date())

    result = table_obj.objects.filter(**kwargs).values()
    
    data = []
    for x in range(0, len(result)):
        form_list = {}
        for key, val in result[x].items():
            if val is None:
                val = ''
            if isinstance(val, datetime.datetime):
                if val.tzname() == 'UTC':
                    val += datetime.timedelta(hours=5, minutes=30)
                val = str(val.strftime('%d-%m-%Y %H:%M:%S'))
            elif isinstance(val, dict) and params['table'] in constants.DICT_TO_EXCEL_COL + \
                    constants.GENERIC_CAMPAIGN_LEAD_CAPTURE_CONSTS["CAMPAIGN_NAMES"]:
                val = dict(val)
            elif not isinstance(val, str):
                val = str(val)
            if isinstance(val, dict) and params['table'] in constants.DICT_TO_EXCEL_COL + \
                    constants.GENERIC_CAMPAIGN_LEAD_CAPTURE_CONSTS["CAMPAIGN_NAMES"] and key not in remove_arr_for_form_data:
                form_list = result[x][key]
            else:
                if key == "created_at":
                    if params['table'].upper() == "GROUP_POLICY":
                        date_split = val.split(" ")
                        date= date_split[0]
                        time = date_split[1]
                    else:
                        result[x][key] = val
                else:
                    result[x][key] = val
        if params['table'].upper() == "GROUP_POLICY":
            result[x]['date'] = date
            result[x]['time'] = time
        result[x].update(form_list)
        data.append(result[x])
    if final_fields:
        if params['table'].upper() == "GROUP_POLICY":
            final_fields.remove('created_at')
        export_params = {'file_name': filename, 'fieldnames': final_fields, 'data': data,
                         'sheetname': 'Report'}
    else:
        export_params = {'file_name': filename, 'fieldnames': fieldnames, 'data': data,
                         'sheetname': 'Report'}
    file_details = export_csv(export_params, request, offline_forms_data=True)
    custom_log(level='info', request=request, params={'body': {'file_details': file_details},
                                                      'detail': 'file generated for db report'})
    
    if 'email' in params:
        custom_log(level='info', request=request, params={'body': {'params': params},
                                                          'detail': 'email found in params so sending email'})
        
        try:
            if params['table'] in constants.GENERIC_CAMPAIGN_LEAD_CAPTURE_CONSTS["CAMPAIGN_NAMES"]:
                subject, message = constants.GENERIC_CAMPAIGN_LEAD_CAPTURE_CONSTS[params['table']]["SUBJECT"], \
                                   constants.GENERIC_CAMPAIGN_LEAD_CAPTURE_CONSTS[params['table']]["MESSAGE"]

            else:
                subject, message = constants.DOWNLOAD_CSV_EMAIL_SUBJECT_MESSAGES[params['table']]['subject'], \
                                   constants.DOWNLOAD_CSV_EMAIL_SUBJECT_MESSAGES[params['table']]['message']
            destination_file = settings.BASE_URL + settings.MEDIA_URL + 'reports/' + file_details['file_name']
            email_service.send_email_to_user(params['email']['to'], message, subject,
                               params['table'], request, [destination_file],
                               cc_recipient=params['email']['cc'],
                               bcc_recipient=params.get('email', {}).get('bcc', []), download_file=False)

        except ex.GenericException as e:
           custom_log(level='info', request=request,
                       params={'body': {}, 'detail': 'error in sending mail due to ' + repr(e.detail)})

        except Exception as e:
            custom_log(level='info', request=request, params={'body': {},
                                                              'detail': 'error in sending mail due to ' + repr(e)})
    return file_details
    