from datetime import datetime
from shared_config.exception_constants import STATUS_TYPE, NONRETRYABLE_CODE

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

