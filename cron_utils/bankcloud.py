
import base64
import hashlib
import hmac
import math
import uuid
from external_services.adapters import APIManager
from cron_utils import external_constants as settings
from cron_utils.payment_receipt_posting import PaymentReceiptPostingService
from django.db import transaction
from django.db.models import Q
from cron_utils.models import Transaction
from cron_utils.constants import TRANSACTION_UPDATE_MESSAGE
from shared_config.exceptions import GenericException
from shared_config.exception_constants import STATUS_TYPE,NONRETRYABLE_CODE
from shared_config.logging import custom_log
from datetime import datetime, timedelta

import requests
import json


class BankCloudPaymentService:
    
    def __init__(self, request=None, policy_no=None, payment_data=None, txn_id=None):
        self.request = request
        self.policy_no = policy_no
        self.payload = None
        self.payment_data = payment_data
        self.txn_id = txn_id
        
        
    def generate_hash(self, payload_str, request_url):
        byte_array = payload_str.encode('UTF-8')
        data_bytes = hashlib.sha256(byte_array)
        base64string = base64.b64encode(data_bytes.digest()).decode()
        nonce = uuid.uuid4().hex
        current_ts = math.floor(datetime.now().timestamp())
        request_data = str(current_ts) + nonce + base64string + request_url
        signature = request_data.encode('utf-8')
        secret_key_bytes = self.USER_SECRET.encode('ascii')
        signature_bytes = hmac.new(secret_key_bytes, signature, digestmod=hashlib.sha256).digest()
        base64_request_data = base64.b64encode(signature_bytes).decode()
        auth_token_str = base64_request_data + ":" + nonce + ":" + str(current_ts) + ":" + self.USER_TOKEN
        plain_text_bytes = auth_token_str.encode('utf-8')
        auth_token = base64.b64encode(plain_text_bytes).decode()
        return auth_token
        
    @transaction.atomic
    def transaction_update_db(self, data):
        """
        updates transaction table
        """
        urn = data.get("consumerData", {}).get("urn") or data.get("urn")
        txn_details = data.get("transaction_details", {})
        txn_status = txn_details.get("trxn_status", {}).get("status")
        if not urn:
            raise GenericException(status_type=STATUS_TYPE["PAYMENT"], exception_code=NONRETRYABLE_CODE["BAD_REQUEST"],
                                   detail="urn not present", request=self.request)
        # kwargs = dict(status=txn_status, txn_data=request.data)
        if data.get("urn"):
            kwargs = {'status': data.get("status")}
            try:
                Transaction.objects.filter(hdfc_reference_no=urn).update(**kwargs)
            except Exception as e:
                raise GenericException(status_type=STATUS_TYPE["PAYMENT"], exception_code=NONRETRYABLE_CODE["BAD_REQUEST"],
                                       detail="Error while updating transaction details for {}".format(urn),
                                       request=self.request)

        else:
            kwargs = {'status': txn_status}
            try:
                Transaction.objects.filter(hdfc_reference_no=urn).update(**kwargs)
            except Exception as e:
                raise GenericException(status_type=STATUS_TYPE["PAYMENT"], exception_code=NONRETRYABLE_CODE["BAD_REQUEST"],
                                       detail="Error while updating transaction details for {}".format(urn),
                                       request=self.request)

            # calling payment receipt posting API
            txn_obj = Transaction.objects.filter(hdfc_reference_no=urn).last()
            if txn_obj.status == 'Success':
                PaymentReceiptPostingService(txn_obj, txn_details).update_payment_receipt_details_in_db()

        return {"status": "success", "message": TRANSACTION_UPDATE_MESSAGE['Success']}

    def get_pending_txn(self, hours, minutes=0):
        """
        returns the queryset of urn which are in processing status
        """
        to_date = datetime.now()
        from_date = to_date - timedelta(hours=hours, minutes=minutes)
        pending_txn_list = Transaction.objects.filter(Q(payment_gateway_type="bankcloud") & (Q(status="Processing") | (Q(status="Success") & Q(tebt_receipt_status=False))) )[:10]
        # pending_txn_list = Transaction.objects.filter(Q(payment_gateway_type="bankcloud") &
        #                                               Q(Q(status="Processing") | (Q(status="Success") &
        #                                                                           Q(tebt_receipt_status='false'))) & 
        #                                                Q(created_at__lte=to_date, created_at__gte=from_date))

        return pending_txn_list

    def fetch_txn_details(self, pending_txn_list):
        for txn in pending_txn_list:
            try:
                payload = {'urn': txn.hdfc_reference_no}
                payload_str = json.dumps(payload, separators=(',', ':'))
                # url = settings.BANKCLOUD_FETCH_URL

                # headers = {
                #     'Authorization': self.generate_hash(payload_str, url),
                #     'Content-Type': 'application/json'
                # }

                # response = requests.post(url, data=payload_str.encode('utf-8'), headers=headers, timeout=self.REQUEST_TIMEOUT)
                # print(response.text)
                service_type = "BANKCLOUD_FETCH_URL"
                adapter = APIManager(service_type, payload)
                response = adapter.get_data()
                if response.status_code != 200:
                    custom_log('error', request=self.request, params={'detail': 'Bankcloud fetch API response failed',
                                                                      'response': response.text, 'urn': txn.hdfc_reference_no})
                    continue
                else:
                    if not response.text:
                        custom_log('error', request=self.request, params={'detail': 'Bankcloud fetch API response, no response found',
                                                                         'urn': txn.hdfc_reference_no})
                        data = {'urn': txn.hdfc_reference_no, 'status': 'Cancelled'}
                        self.transaction_update_db(data)
                    elif response.json().get("error"):
                        custom_log('error', request=self.request, params={'detail': 'Bankcloud fetch API response error',
                                                                          'response': response.text, 'urn': txn.hdfc_reference_no})
                        data = {'urn': txn.hdfc_reference_no, 'status': response.json().get("error").get("ErrorDesc")}
                        self.transaction_update_db(data)
                    else:
                        custom_log('info', request=self.request, params={'detail': 'Bankcloud fetch API response',
                                                                         'response': response.text, 'urn': txn.hdfc_reference_no})
                        self.transaction_update_db(response.json())
            except AttributeError as e:
                custom_log('error', request=self.request, params={'detail': 'Bankcloud fetch API response error',
                                                                  'urn': txn.hdfc_reference_no,
                                                                  'response': response.text})
                continue
            except Exception as e:
                custom_log('error', request=self.request, params={'detail': 'Bankcloud fetch API response error',
                                                                  'urn': txn.hdfc_reference_no})
                continue
    
      