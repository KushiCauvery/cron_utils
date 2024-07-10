from datetime import datetime
from shared_config.exceptions import GenericException
from shared_config.exception_constants import STATUS_TYPE, NONRETRYABLE_CODE
from rest_framework import status
from shared_config.logging import custom_log


def drop_link_notifier(request=None):
    """
    method that runs through cron to send notification to users about drop link
    """
    try:
        if request is not None:
            if request.GET.get('password', '') != app_constants.PERIODIC_DROP_LINK_PASSWORD:
                return {"message": "Enter a valid password"}

        custom_log('info', request, {'detail': 'Drop link notifier method initiated.'})
        now = datetime.datetime.now()

        drop_links = DropLink.objects.filter(scheduled_time__lte=now, status=app_constants.DROP_LINK_STATUS['PENDING'])
        lead_numbers = list(drop_links.values_list('lead_number', flat=True))
        custom_log('info', request, {'detail': 'drop link quote ids fetched.', 'body': {'lead_numbers': lead_numbers}})
        if not lead_numbers:
            return {"message": "Drop Link Notifier: Nothing found"}

        lead_objs = PreQuote.objects.filter(lead_number__in=lead_numbers)
        leads = LeadSerializer(lead_objs, many=True)

        for lead in leads.data:
            send_notification_for_drop_link(lead, request)
        drop_links.update(status=app_constants.DROP_LINK_STATUS['SENT'])
        custom_log('info', request, {'detail': 'Updating sent_status for each drop link.', 'body': {'params': lead_numbers}})
        return {"message": "Drop Link Cron utility ran successfully"}
    except GenericException as e:
        raise GenericException(status_type=STATUS_TYPE["APP"], exception_code=NONRETRYABLE_CODE["BAD_REQUEST"], detail=e.detail, request=request, response_msg=getattr(e, 'response_msg', api_constants.GENERIC_ERROR_MESSAGE))
    except Exception as e:
        raise GenericException(status_type=STATUS_TYPE["APP"], exception_code=NONRETRYABLE_CODE["BAD_REQUEST"], detail="Error in drop link notifier cron:" + str(repr(e)), request=request)

def get_from_date_to_date(params):

    """
    get from date to date for filtering purposes
    :return:
    """
    from_date = params['from_date']
    to_date = params['to_date']
    if isinstance(params['from_date'], str) and isinstance(params['to_date'], str):
        from_date = datetime.strptime(params['from_date'], "%Y-%m-%d")
        to_date = datetime.strptime(str(params['to_date']) + " 23:59:59", "%Y-%m-%d %H:%M:%S")
    return from_date, to_date

