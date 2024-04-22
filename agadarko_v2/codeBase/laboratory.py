from ..models import Outside_Customers_Lab_Test,OutsideLabtestCases,OutsideLabtestDetails,Patient_Medical_Diagnosis_Records,Laboratory_Test_Cost_Details,Patient_Laboratory_Test_Records,Patient_Laboratory_Test_Records_Technician,Patient_Laboratory_Test_Results_Details
from django.db.models.functions import LPad
from django.contrib.auth.models import User
from django.db.models import Count ,F,Q,Sum,Value
from .sms import smscalls




def view_lab_test_cost():
    data=[]
    laboratory=Laboratory_Test_Cost_Details.objects.all()
    for tests in laboratory:
         data.append({'lab_test':tests.test_type,'serial_code':tests.serial_code,'cost':tests.test_cost})
    return data
def getLaboratoryList(serial_code):
     data=[]
     for tests in range(len(serial_code)):
         lab_cost=Laboratory_Test_Cost_Details.objects.filter(serial_code=serial_code[tests])
         for test in lab_cost:
             data.append({'lab_test':test.test_type,'cost':test.test_cost,'serial_code':test.serial_code})
     print(data)
     return data
def get_lab_test(serial_code):
    return Laboratory_Test_Cost_Details.objects.get(serial_code=serial_code)
def view_lab_test_cost_details(serial_code):
     lab_test=get_lab_test(serial_code)
     return {'lab_test':lab_test.test_type,'cost':lab_test.test_cost,'serial_code':lab_test.serial_code}
def create_lab_test_details(labtest,cost):
     for test in range(len(labtest)):
           lab_tests= Laboratory_Test_Cost_Details.objects.filter(test_type=labtest[test])
           if not lab_tests.exists():
              lab_test= Laboratory_Test_Cost_Details.objects.create(test_type=labtest[test],test_cost=cost[test])
              lab_test.save()
              lab_test_id=Laboratory_Test_Cost_Details.objects.latest('id')
              generate_lab_test_details_serial_code(lab_test_id.id)
     return {"status":'success','message':'lab test details created'}
def generate_lab_test_details_serial_code(lab_test_id):
     lab_test_serial_code=Laboratory_Test_Cost_Details.objects.get(pk=lab_test_id)
     lab_test_serial_code.serial_code=LPad('id',8,Value('0'))
     lab_test_serial_code.save()
     return True

def edit_lab_test_details(serial_code,cost,test_name):
     #test=get_lab_test(serial_code)
     #Laboratory_Test_Cost_Details.objects.filter(serial_code=serial_code).update(test_type=test_name,test_cost=cost)
     
     get_lab=get_lab_test(serial_code)
    
     
     get_lab.test_type=test_name
     get_lab.test_cost=cost
     get_lab.save()
     
     
     return {'status':'success','success':'lab test details changed'}




def view_waiting_patient_lab_test():
    #view all lab cases not checked out and not released
    data=[]
    waiting_patient_lab_test=Patient_Laboratory_Test_Records.objects.filter(patient__laboratory_report_request_status=True,patient__laboratory_report_received_status=False,patient__patient__checked_in=True,patient__patient__checked_out=False)
    for patient_lab in waiting_patient_lab_test:
         data.append({'patient':patient_lab.patient.patient.patient.patient.first_name+' '+patient_lab.patient.patient.patient.patient.last_name,'case_number':patient_lab.patient.patient.case_number,'total_cost':patient_lab.total_cost,'payment_status':patient_lab.payment_status,'card_number':patient_lab.patient.patient.patient.card_number,'in_house_status':patient_lab.patient.in_house_laboratory_test})
    
    return data

def view_patient_lab_test_result_history(card_number):
     data=[]
     patient_lab=Patient_Laboratory_Test_Records.objects.filter(patient__patient__patient__card_number=card_number,patient__laboratory_report_request_status=True,patient__laboratory_report_received_status=True)
     for records in patient_lab:
          data.append({'case_number':records.patient.patient.case_number,'date_release':records.date_released,'date_requested':records.date_recieved,'in_house':records.patient.in_house_laboratory_test})
     return data

def view_patient_lab_request_lists(case_number):
     data=[]
     patient_lab=Patient_Laboratory_Test_Results_Details.objects.filter(patient__patient__patient__case_number=case_number)
     for records in patient_lab:
          data.append({'lab_test_type':records.lab_test.test_type,'cost':records.test_cost,'serial_code':records.lab_test.serial_code,'results':records.test_results})
     return data
def getPatientCard(case_number):
     patient_card=get_patient_lab_test_details(case_number)
     patient_card.patient.patient.patient.card_number
     return patient_card


def get_patient_lab_test_details(case_number):
    
     return Patient_Laboratory_Test_Records.objects.get(patient__patient__case_number=case_number)

def view_patient_lab_records(case_number):
     #patient_lab=Patient_Laboratory_Test_Records_Technician.objects.filter(lab__patient__patient__case_number=case_number,technician=user_id)
     get_patient_lab=get_patient_lab_test_details(case_number)
     patient_lab_details=[{'patient_name':get_patient_lab.patient.patient.patient.patient.first_name+' '+get_patient_lab.patient.patient.patient.patient.last_name,'case_number':get_patient_lab.patient.patient.case_number,'total_cost':get_patient_lab.total_cost,'date_released':get_patient_lab.date_released,'date_requested':get_patient_lab.date_recieved,'in_housee_status':get_patient_lab.patient.in_house_laboratory_test}]
     return {'patient_lab_history':view_patient_lab_test_result_history(get_patient_lab.patient.patient.patient.card_number),'lab_tests':view_patient_lab_request_lists(case_number),'patient_lab_bio_details':patient_lab_details,'payment_status':get_patient_lab.payment_status,'released_status':get_patient_lab.lab_test_released}


def update_test_results(case_number,test,test_results,user_id):
     patient_lab_test=Patient_Laboratory_Test_Records.objects.get(patient__patient__case_number=case_number)
     for tests in range(len(test)):
          patient_lab_results=Patient_Laboratory_Test_Results_Details.objects.get(patient__patient__patient__case_number=case_number,lab_test__serial_code=test[tests])
          patient_lab_results.test_results=test_results[tests]
          patient_lab_results.save()
     lab_status_update=status_updates(patient_lab_test.id)
     medic_lab_update=update_lab_test_diagnosis(case_number)
     #print('troblue 1',lab_status_update,' trobuvle 2')
     if lab_status_update==True and medic_lab_update==True:
          patient_lab=Patient_Laboratory_Test_Records_Technician.objects.create(lab=Patient_Laboratory_Test_Records.objects.get(pk=patient_lab_test.id),technician=User.objects.get(pk=user_id))
          patient_lab.save()
          return {"status":'success','success':'patient lab test result updated'}

def status_updates(patient_lab_test_id):
     patient_lab_updates=Patient_Laboratory_Test_Records.objects.get(pk=patient_lab_test_id)
     patient_lab_updates.lab_test_released=True
     patient_lab_updates.save()
     return True

def  update_lab_test_diagnosis(case_number):
     patient_history=Patient_Medical_Diagnosis_Records.objects.get(patient__case_number=case_number)
     patient_history.laboratory_report_received_status=True
     patient_history.save()
     return True



'''
  lab payment
'''


def make_lab_test_payment(case_number,amount):
     patient=get_patient_lab_test_details(case_number)
     
     discount_status=patient.discount_status
     if discount_status == True:
        total_cost=patient.discount_amount
        balance=float(total_cost)-float(amount)
        if balance == 0.00:
          patient.amount_paid=amount
          patient.payment_status=True
          patient.save()
          messages='Hi {},payment of GHS {} recieved for lab test.\nbalance {}\n.invoice {}\n.AGADARKO\nAdmin'.format(patient.patient.patient.patient.patient.first_name,amount,balance,case_number)
          #smscalls(messages,patient.patient.patient.patient.patient.telephone)
          return {"status":'success','message':'payment successful'}
        else:
          return {"status":'error','message':"make full payment "} 
     else:
          total_cost=patient.total_cost 
          balance=float(total_cost)-float(amount)  
          if balance == 0.00:
              patient.amount_paid=amount
              patient.payment_status=True
              patient.save()
              messages='Hi {},payment of GHS {} recieved for lab test.\nbalance {}\n.invoice {}\n.AGADARKO\nAdmin'.format(patient.patient.patient.patient.patient.first_name,amount,balance,case_number)
              #smscalls(messages,patient.patient.patient.patient.patient.telephone)
              return {"status":'success','message':'payment successful'}
          else:
              return {"status":'error','message':"make full payment "} 


        


def  get_patniet_lab_case(card_number):
     data=[]
     case_id=0
     current_case=[]
     lab_test_list=[]

     current_patient_lab=Patient_Laboratory_Test_Records.objects.filter(patient__patient__checked_in=True,patient__patient__checked_out=False,patient__patient__patient__card_number=card_number)
     for patient in current_patient_lab:
          case_id=patient.id
          current_case.append({'total_cost':patient.total_cost,'case_number':patient.patient.patient.case_number,'total_amount_paid':patient.amount_paid,'date_released':patient.date_released,'date_requested':patient.date_recieved,'payment_status':patient.payment_status,'discount_status':patient.discount_status,'discount_rate':patient.discount_rate,'discount_amount':patient.discount_amount})
     patient_lab_details=Patient_Laboratory_Test_Results_Details.objects.filter(patient__id=case_id)
     for lab_details in patient_lab_details:
               lab_test_list.append({'labe_test':lab_details.lab_test.test_type,'serial_code':lab_details.lab_test.serial_code,'cost':lab_details.test_cost})
     data.append({'active_case':current_case,'active_lab_case_list':lab_test_list})

     return data


def  patient_lab_history(card_number):
   
     data=[]
     current_patient_lab=Patient_Laboratory_Test_Records.objects.filter(patient__patient__checked_in=True,patient__patient__checked_out=True,patient__patient__patient__card_number=card_number)
     for patient in current_patient_lab:
          patient_lab_details=Patient_Laboratory_Test_Results_Details.objects.filter(patient__id=current_patient_lab.id)
          for lab_details in patient_lab_details:
               data.append({'current_case':{'total_paid_amout':patient.total_cost,'case_number':patient.patient.patient.case_number,'total_cost':patient.amount_paid,'date_requested':patient.date_recieved},'labe_details':{'labe_test':lab_details.lab_test,'serial_code':lab_details.cost,'cost':lab_details.test_cost}})


     return data

'''

create outsiders lab test

'''
def listOf_OutsideLaboratoryTest():
     pass

def  create_outside_lab_test(name,telephone,lab_file_photo,lab_test_list,user_id):
     check_patient=Outside_Customers_Lab_Test.objects.filter(telephone=telephone)
     data=[]
     if check_patient.exists():
          get_patient_details=Outside_Customers_Lab_Test.objects.get(telephone=telephone)
          patient=create_outside_lab_test_case(get_patient_details.id,lab_file_photo,lab_test_list,user_id)
          if patient ==True:
               data.append({"status":'success','success':'patient_details created successfully'})

     else:
          patient=create_out_lab_patient(name,telephone,lab_file_photo,lab_test_list,user_id)
          if patient == True:
               data.append({"status":'error','error':'patient_details created successfully'})
     return data
def get_lab_customer(patient_id):
        patient=Outside_Customers_Lab_Test.objects.get(pk=patient_id)


def create_out_lab_patient(name,telephone,lab_file_photo,lab_test_list,user_id):
     customer=Outside_Customers_Lab_Test.objects.create(name=name,telephone=telephone)
     customer.save()
     customer_id=Outside_Customers_Lab_Test.objects.latest('id')
     patient = create_outside_lab_test_case(customer_id.id,lab_file_photo,lab_test_list,user_id)
     return patient

def create_outside_lab_test_case(patient_id,lab_file_photo,lab_test_list,user_id):
     patient_lab_case=OutsideLabtestCases.objects.create(customer=patient_id,laboratory_report_request_status=True,lab_sheet=lab_file_photo,received_by=User.objects.get(pk=user_id))
     patient_lab_case.save()
     our_lab_case=OutsideLabtestCases.objects.latest('id')
     case_number_generation=create_patient_lab_test_case_number(our_lab_case.id)
     create_case_details=create_outside_lab_test_details(patient_id,lab_test_list) 
     if case_number_generation == True and create_case_details == True:
          return True 
        




def create_patient_lab_test_case_number(patient_id):
    patient_ccase_number=OutsideLabtestCases.objects.get(pk=patient_id)
    patient_ccase_number.lab_case_number-LPad('id',8,Value('0'))
    patient_ccase_number.save()
    return True
def create_outside_lab_test_details(patient_id,lab_test_list):
     for test in range(len(lab_test_list)):
          lab_details=Laboratory_Test_Cost_Details.objects.get(pk=lab_test_list[test])
          create_lab_details=OutsideLabtestDetails.objects.create(customer=OutsideLabtestCases.objects.get(pk=patient_id[test]),laboratory=Laboratory_Test_Cost_Details.objects.get(pk=lab_test_list[test]),cost=lab_details.test_cost)
          create_lab_details.save()
     return True


def input_lab_test_result(case_number,lab_test_list,results):
     patient_lab_test=OutsideLabtestCases.objects.get(lab_case_number=case_number)
     for tests in range(len(lab_test_list)):
          patient_lab_results=OutsideLabtestDetails.objects.get(outside_lab_patient__lab_case_number=case_number,laboratory__serial_code=results[tests])
          patient_lab_results.test_results=results[tests]
          patient_lab_results.save()

     return {"status":'success','success':'lab test enter successfully'}

