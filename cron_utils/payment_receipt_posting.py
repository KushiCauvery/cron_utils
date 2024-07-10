import json
import logging
import time

import requests
import xmltodict
import xml.etree.ElementTree as ET

from shared_config.logging import custom_log
from shared_config.exception_constants import STATUS_TYPE,NONRETRYABLE_CODE
from shared_config.exceptions import GenericException
from shared_config import constants as api_constants
from shared_config import external_config as settings
from external_services.adapters import APIManager
from cron_utils import constants as policy_constants
from cron_utils import constants as payments_constants
from cron_utils import external_constants
from cron_utils.utils import get_policy_premium_details


PAYMENT_POSTING_REQUEST = """
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:hdf="http://www.hdfcinsurance.com/">
   <soapenv:Header/>
   <soapenv:Body>
      <hdf:SavePaymentDetails_Health>
         <hdf:UserId>%s</hdf:UserId>
         <hdf:BJRefNo>%s</hdf:BJRefNo>
         <hdf:TxnID>%s</hdf:TxnID>
         <hdf:PolicyNo>%s</hdf:PolicyNo>
         <hdf:TID/>
         <hdf:MID>%s</hdf:MID>
         <hdf:Encryptionkey>NA</hdf:Encryptionkey>
         <hdf:Requeststring>NA</hdf:Requeststring>
         <hdf:Responsestring>NA</hdf:Responsestring>
         <hdf:Transdate>%s</hdf:Transdate>
         <hdf:StatusDate>%s</hdf:StatusDate>
         <hdf:Errorcode>%s</hdf:Errorcode>
         <hdf:Errormsg>%s</hdf:Errormsg>
         <hdf:Ptype>%s</hdf:Ptype>
         <hdf:PremDueDt>%s</hdf:PremDueDt>
         <hdf:Pstatus>%s</hdf:Pstatus>
         <hdf:IPaddress>NA</hdf:IPaddress>
         <hdf:PremAmt>%s</hdf:PremAmt>
         <hdf:SuspenseAmt>%s</hdf:SuspenseAmt>
         <hdf:Emailsent>N</hdf:Emailsent>
         <hdf:SMSsent>N</hdf:SMSsent>
         <hdf:ACKshown>N</hdf:ACKshown>
         <hdf:PHName>%s</hdf:PHName>
         <hdf:DOB>%s</hdf:DOB>
         <hdf:PremiumType>%s</hdf:PremiumType>
         <hdf:PaymentMode>%s</hdf:PaymentMode>
         <hdf:EnquiryScript1>NA</hdf:EnquiryScript1>
         <hdf:EnquiryScript2>NA</hdf:EnquiryScript2>
         <hdf:S2SResponse>NA</hdf:S2SResponse>
         <hdf:PANCARDno>NA</hdf:PANCARDno>
         <hdf:MandateID>NA</hdf:MandateID>
         <hdf:AmtPayable>%s</hdf:AmtPayable>
         <hdf:UIN>%s</hdf:UIN>
         <hdf:Cessationdt>%s</hdf:Cessationdt>
         <hdf:Mobile>%s</hdf:Mobile>
         <hdf:Email/>
         <hdf:PSource>%s</hdf:PSource>
         <hdf:PGTxnID>%s</hdf:PGTxnID>
         <hdf:CardNumber>%s</hdf:CardNumber>
         <hdf:Mandate_Flag>%s</hdf:Mandate_Flag>
         <hdf:BillPay_Flag>%s</hdf:BillPay_Flag>
         <hdf:Base_Premium>%s</hdf:Base_Premium>
         <hdf:PayNowClick>Yes</hdf:PayNowClick>
         <hdf:Can_Base_Prm>%s</hdf:Can_Base_Prm>
         <hdf:Can_Sum_Assured>%s</hdf:Can_Sum_Assured>
         <hdf:AmtPayableHealth>%s</hdf:AmtPayableHealth>
         <hdf:Can_Policy_Term>%s</hdf:Can_Policy_Term>
         <hdf:Can_Premium_Term>%s</hdf:Can_Premium_Term>
         <hdf:SMQ1_Ans>NA</hdf:SMQ1_Ans>
         <hdf:SMQ1a_Ans>NA</hdf:SMQ1a_Ans>
         <hdf:SMQ1b_Ans>NA</hdf:SMQ1b_Ans>
         <hdf:SMQ2_Ans>NA</hdf:SMQ2_Ans>
         <hdf:SMQ3_Ans>NA</hdf:SMQ3_Ans>
         <hdf:SMQ4_Ans>NA</hdf:SMQ4_Ans>
         <hdf:SMQ5_Ans>NA</hdf:SMQ5_Ans>
         <hdf:SMQ6_Ans>NA</hdf:SMQ6_Ans>
         <hdf:SMQ7_Ans>NA</hdf:SMQ7_Ans>
         <hdf:SMQ8_Ans>NA</hdf:SMQ8_Ans>
         <hdf:Can_Plan>NA</hdf:Can_Plan>
         <hdf:Can_Early_Stage>NA</hdf:Can_Early_Stage>
         <hdf:Can_Major_Can>NA</hdf:Can_Major_Can>
         <hdf:Can_Gold_Ben1>NA</hdf:Can_Gold_Ben1>
         <hdf:Can_Gold_Ben2>NA</hdf:Can_Gold_Ben2>
         <hdf:Can_Plat_Inc_Ben1>NA</hdf:Can_Plat_Inc_Ben1>
         <hdf:Can_Plat_Inc_Ben2>NA</hdf:Can_Plat_Inc_Ben2>
         <hdf:PlanDetailsDisp>No</hdf:PlanDetailsDisp>
         <hdf:SMQDisp>No</hdf:SMQDisp>
         <hdf:SummaryDisp>No</hdf:SummaryDisp>
         <hdf:AuthCode>%s</hdf:AuthCode>
         <hdf:Cheque_No></hdf:Cheque_No>
         <hdf:MICR_No></hdf:MICR_No>
         <hdf:Cheque_Date></hdf:Cheque_Date>
         <hdf:Drawee_Bank></hdf:Drawee_Bank>
         <hdf:Drawee_Branch></hdf:Drawee_Branch>
         <hdf:Deposit_Date/>
         <hdf:Udf1>NA</hdf:Udf1>
         <hdf:Udf2>NA</hdf:Udf2>
         <hdf:Udf3>NA</hdf:Udf3>
         <hdf:Udf4>NA</hdf:Udf4>
         <hdf:Udf5>NA</hdf:Udf5>
      </hdf:SavePaymentDetails_Health>
   </soapenv:Body>
</soapenv:Envelope>
"""


class PaymentReceiptPostingService:
    def __init__(self, txn_obj, txn_details):
        self.txn_obj = txn_obj
        self.txn_details = txn_details

    def update_db(self, params):
        self.txn_obj.tebt_receipt_status = params.get("status")
        self.txn_obj.save()

    def get_payment_receipt_details(self):
        """
        calls TEBT posting API and return the payment receipt details
        """
        premium_details = self.txn_obj.premium_details
        bj_user_id = policy_constants.PREMIUM_PAYMENT_BJ_USER_ID
        bj_ref_number = policy_constants.PREMIUM_PAYMENT_CRON_REF_NO_PREFIX + str(int(time.time() * 1000))
        premium_params = dict(policy_no=premium_details.get('policy_no'), str_dob=premium_details.get('str_dob'),
                              bj_user_id=bj_user_id, bj_ref_number=bj_ref_number)
        premium_details = get_policy_premium_details(premium_params, None)

        txn_status = self.txn_obj.status
        error_code = '0399'
        if txn_status.lower() == "success":
            error_code = '0300'

        # url = settings.TEBT_PAYMENT_RECEPT_POSTING_URL

        payment_mode = payments_constants.TEBT_POSTING_PAYMENT_MODE_MAPPING[self.txn_details.get("paymode_details").get("mode")]
        card_number = 'NA'
        auth_code = 'NA'
        if payment_mode in ('CC', 'DC', "EM"):
            card_number = self.txn_details.get("paymode_details").get("card_no")[-4:]
            auth_code = self.txn_details.get("trxnid_ts").get("auth_code")

        payload = PAYMENT_POSTING_REQUEST % (settings.POSTING_USER_ID,
                                             bj_ref_number,
                                             self.txn_obj.hdfc_reference_no,
                                             self.txn_obj.policy_no,
                                             self.txn_details.get("paymode_details").get("bankname"),
                                             self.txn_obj.created_at.strftime("%d/%m/%Y %H:%M:%S"),
                                             self.txn_obj.modified_at.strftime("%d/%m/%Y %H:%M:%S"),
                                             error_code,
                                             txn_status,
                                             premium_details.get("Ptype"),
                                             premium_details.get("PremDueDt"),
                                             premium_details.get("Pstatus"),
                                             premium_details.get("PremAmt"),
                                             premium_details.get("SuspenseAmt"),
                                             premium_details.get("PHName"),
                                             premium_details.get("DOB"),
                                             premium_details.get("PremiumType"),
                                             payment_mode,
                                             premium_details.get("AmtPayable"),
                                             premium_details.get("UIN"),
                                             premium_details.get("Cessationdt"),
                                             premium_details.get("Mobile"),
                                             self.txn_details.get("trxnid_ts", {}).get("payment_source"),
                                             self.txn_details.get("trxnid_ts", {}).get("txnid"),
                                             card_number,
                                             premium_details.get("Mandate_Flag"),
                                             premium_details.get("BillPay_Flag"),
                                             premium_details.get("Base_Premium"),
                                             premium_details.get("Can_Base_Prm"),
                                             0,
                                             premium_details.get("AmtPayableHealth"),
                                             0,
                                             0,
                                             auth_code
                                             )

        try:
            custom_log('info', request=None, params={'myurl': url, 'data': payload,
                                                     'detail': 'In get_payment_receipt_details: Hitting payment receipt posting API'})
            # response = requests.post(url=url, data=payload, timeout=external_constants.CUSTOMER_PORTAL_API_TIME_OUT)
            service_type = "TEBT_PAYMENT_RECEPT_POSTING_URL"
            adapter = APIManager(service_type, payload)
            response = adapter.get_data()
            if not response.status_code == external_constants.CUSTOMER_PORTAL_API_SUCCESS_CODE:
                raise GenericException(STATUS_TYPE["PAYMENT"], exception_code=NONRETRYABLE_CODE["GENERIC_FAILURE"],
                                       detail=response.text, response_msg=api_constants.GENERIC_ERROR_MESSAGE,
                                       request=None)
            custom_log('info', request=None, params={'myurl':service_type , 'response': response.text,
                                                     'detail': 'Received response from posting API'})

            json_resp = json.loads(json.dumps(xmltodict.parse(response.text)))
            try:
                # for success cases
                str_resp = json_resp['soapenv:Envelope']['soapenv:Body']['out2:SavePaymentDetails_HealthResponse'][
                    'out2:SavePaymentDetails_HealthResult']
            except KeyError:
                # for failure cases
                str_resp = json_resp['soapenv:Envelope']['soapenv:Body']['io5:SavePaymentDetails_HealthResponse'][
                    'io5:SavePaymentDetails_HealthResult']
            return str_resp
        except Exception as e:
            custom_log('error', request=None, params={'detail': 'error in get_payment_receipt_details'})
            raise GenericException(status_type=STATUS_TYPE["PAYMENT"],
                                   exception_code=NONRETRYABLE_CODE["GENERIC_FAILURE"], detail=str(e), request=None)

    def update_payment_receipt_details_in_db(self):
        """
        get payment details from TEBT payment receipt posting API and updates in DB
        """
        payment_receipt_details = self.get_payment_receipt_details()
        try:
            myroot = ET.fromstring(payment_receipt_details)
            posting_status = myroot.find('InsPolicyPremium_Output_Parameter').find('Status').text
            status = "True" if posting_status == "S" else "False"
            txn_id = myroot.find('InsPolicyPremium_Output_Parameter').find('TxnID').text
            custom_log('info', request=None, params={'txn_id': txn_id, 'response': payment_receipt_details,
                                                     'detail': 'Received success response from posting API'})
        except AttributeError:
            posting_status = myroot.find('Status').text
            status = "True" if posting_status == "S" else "False"
            txn_id = myroot.find('TxnID').text
            custom_log('error', request=None, params={'txn_id': txn_id, 'response': payment_receipt_details,
                                                      'detail': 'Received failure response from posting API'})
        except Exception as e:
            raise GenericException(status_type=STATUS_TYPE["PAYMENT"],
                                   exception_code=NONRETRYABLE_CODE["GENERIC_FAILURE"], detail=str(e),
                                   request=None)

        kwargs = {'status': status}
        self.update_db(kwargs)
