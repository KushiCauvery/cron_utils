from django.db import models
from django.db import models
from django.utils.translation import gettext_lazy as _
from cron_utils.constants import TXN_INIT_STATUS
from cron_utils import manager as account_manager
from django.contrib.postgres.fields import HStoreField
from simple_history.models import HistoricalRecords
from djutil.models import TimeStampedModel
from shared_config.models import ModelBase
from django.dispatch import receiver
from django.db.models.signals import post_save
from datetime import datetime

# Create your models here.

class AppLinkedUser(TimeStampedModel):
    """
    model to store user's phone number opting for app link
    """
    phone = models.CharField(max_length=10, default="")
    email = models.EmailField(max_length=254, null=True, blank=True)
    ndfc_flag = models.BooleanField(default=False, blank=True)
    metadata = models.JSONField(default={})


    class Meta:
        db_table = 'account_applinkeduser'
        managed = False
        app_label = 'account'
        
class SearchTerm(TimeStampedModel):
    query = models.CharField(verbose_name='Search Term', max_length=255, default=None)
    
    class Meta:
        db_table = 'page_searchterm'
        managed = False
        app_label = 'page'
        
class GroupPolicyDownloadReport(TimeStampedModel):
    """
    Model to store Group policy number, date and time of download
    """
    group_policy_number = models.CharField(max_length= 8)
    email_info = models.CharField(max_length= 254, default= "")
    
    class Meta:
        db_table = 'forms_grouppolicydownloadreport'
        managed = False
        app_label = 'forms'

class Memory(ModelBase):
    name = models.CharField(max_length=60, null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)
    mobile = models.CharField(max_length=20, null=True, blank=True)
    relation = models.CharField(max_length=60, null=True, blank=True)
    lost_in_year = models.PositiveSmallIntegerField(null=True, blank=True)
    story = models.TextField(blank=True, null=True)
    image = models.ImageField( upload_to="campaigns/memory/", blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    is_approved = models.BooleanField(default=False, help_text='Approved story will be visible on website')
    
    class Meta:
        db_table = 'campaigns_memory'
        managed = False
        app_label = 'campaigns'
        
class CustomerServiceForm(TimeStampedModel):
    """
    model class to store form data
    """
    form_type = models.CharField(max_length=255)
    form_data = models.JSONField()
    
    class Meta:
        db_table = 'forms_customerserviceform'
        managed = False
        app_label = 'forms'
        


class Transaction(ModelBase):
    """
    creates transaction models
    """
    user = models.CharField(max_length=255, default="")
    quote_id = models.CharField(max_length=255, default="")
    txn_id = models.CharField(max_length=255, default="")
    status = models.CharField(max_length=255, default=TXN_INIT_STATUS)
    txn_data = HStoreField(null=True)
    txn_type = models.CharField(max_length=255, default="")
    tebt_receipt_status = models.CharField(max_length=255, default="false")
    amount_mismatch = models.CharField(max_length=255, default="false")
    amount = models.CharField(max_length=255, default="false")
    str_reference_no = models.CharField(max_length=255, default="")
    hdfc_reference_no = models.CharField(max_length=255, default="")
    policy_no = models.CharField(max_length=255, default="")
    premium_details = models.JSONField(blank=True, null=True)
    payment_hash = models.JSONField(blank=True, null=True)
    payment_gateway_type = models.CharField(max_length=255, default="")
    application_number = models.CharField(max_length=255, default="")
    agent_code = models.CharField(max_length=255, default="", null=True)
    source_code = models.CharField(max_length=255, default="", null=True)
    reconciliation_date = models.DateTimeField(blank=True, null=True)
    is_reconciled = models.BooleanField(default=False)
    app_os = models.CharField(max_length=255, default="", null=True)
    cms_receipt_no = models.CharField(max_length=255, default="", null=True)
    reconciliation_count = models.PositiveIntegerField(blank=True, null=True, default=1)
    source = models.CharField(max_length=100, default="")
    
    class Meta:
        db_table = 'payments_transaction'
        managed = False
        app_label = 'payments'
    
    


@receiver(post_save, sender=Transaction)
def update_txn_id(sender, instance, **kwargs):
    if not instance.txn_id:
        instance.txn_id = settings.TRANSACTION_PREFIX + str(instance.pk)
        instance.save()
        
  

class User(ModelBase, TimeStampedModel):
    """
    Creates account models
    """
    email = models.CharField(max_length=254)
    first_name = models.CharField(max_length=254, default="")
    last_name = models.CharField(max_length=254, default="")
    gender = models.CharField(max_length=10, default="")
    state = models.CharField(max_length=254, default="")
    city = models.CharField(max_length=254, default="")
    dob = models.DateField(default=None, blank=True, null=True)
    phone = models.CharField(max_length=30, default="")
    facebook_id = models.CharField(max_length=254, blank=True, null=True)
    google_id = models.CharField(max_length=254, blank=True, null=True)
    is_phone_verified = models.BooleanField(default=False)
    customer_id = models.CharField(max_length=50, default="")  
    class Meta:
        db_table = 'account_user'
        managed = False
        app_label = 'account'
          
class MyAccountUsers(ModelBase):
    """
    model to store user's my account details
    """
    CLIENT_ID = 'client_id'
    POLICY_NO = 'policy_no'
    EMAIL = 'email'
    PHONE = 'phone'
    TYPES_OF_LOGIN = (
        (CLIENT_ID, _('Client Id')),
        (POLICY_NO, _('Policy Number')),
        (EMAIL, _('Email address')),
        (PHONE, _('Phone number'))
    )
    LOGIN_TYPES = {
        CLIENT_ID: str(TYPES_OF_LOGIN[0][1]),
        POLICY_NO: str(TYPES_OF_LOGIN[1][1]),
        EMAIL: str(TYPES_OF_LOGIN[2][1]),
        PHONE: str(TYPES_OF_LOGIN[3][1])
    }
    SUCCESS = 'success'
    FAIL = 'fail'
    REQUEST_GENERATED = 'request_generated'
    STATUSES = (
        (SUCCESS, _('Success')),
        (FAIL, _('Failure')),
        (REQUEST_GENERATED, _('request was generated and sent'))
    )
    APP_LOGOUT = 'app'
    CRON_LOGOUT = 'cron'
    DEACTIVATION_SOURCE = (
        (APP_LOGOUT, _('App logout')),
        (CRON_LOGOUT, _('Cron logout'))
    )
    id = models.CharField(_('myaccount users custom id - autocreated'), max_length=20, primary_key=True)
    login_type = models.CharField('LoginType', max_length=30, choices=TYPES_OF_LOGIN)
    login_username = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    oauth2_token = models.CharField(max_length=225, db_index=True)
    is_active = models.BooleanField(default=False)
    api_status = models.CharField('ApiStatus', max_length=20, choices=STATUSES, default=REQUEST_GENERATED)
    api_response = models.JSONField(default={})
    myacc_accesstoken = models.CharField(max_length=100, null=True, blank=True, unique=True, db_index=True)
    account_expires_at = models.DateTimeField(default=datetime.strptime("31/12/9999 23:59:59", "%d/%m/%Y %H:%M:%S"))
    is_activated_at = models.DateTimeField(default=datetime.strptime("31/12/9999 23:59:59", "%d/%m/%Y %H:%M:%S"))
    is_deactivated_at = models.DateTimeField(default=datetime.strptime("31/12/9999 23:59:59", "%d/%m/%Y %H:%M:%S"))
    deactivation_source_value = models.CharField('DeactivationSource', max_length=30, choices=DEACTIVATION_SOURCE, default='')

    objects = account_manager.MyAccountUsersManager()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = gen_hash(expires())
        super(MyAccountUsers, self).save(*args, **kwargs)
    
    class Meta:
        db_table = 'account_myaccountusers'
        managed = False
        app_label = 'account'
        


class CPPolicies(ModelBase):
    """
    This is cp policies
    """
    user_id = models.CharField(max_length=254, blank=False)
    customer_id = models.CharField(max_length=254, blank=True, default='')
    policy_no = models.CharField(max_length=254, blank=True, default='')
    client_name = models.CharField(max_length=254, blank=True, default='')
    risk_commencement_date = models.CharField(max_length=254, blank=True, default='')
    status = models.CharField(max_length=254, blank=True, default='')
    sum_assured = models.CharField(max_length=254, blank=True, default='')
    total_premium_payable = models.CharField(max_length=254, blank=True)
    premium_due_date = models.DateField(blank=True, default=datetime.today)
    premium_paid_upto = models.DateField(blank=True, default='9999-12-31')
    policy_maturity_date = models.DateField(blank=True, default='9999-12-31')
    dob = models.DateField(default=datetime.today)
    policy_name = models.CharField(max_length=254, blank=False)
    cp_response = models.JSONField(blank=False, null=False)
    is_fund = models.BooleanField(blank=False, null=False, default=False)
    
    class Meta:
        db_table = 'policy_cppolicies'
        managed = False
        app_label = 'policy'
    
    

    
    

