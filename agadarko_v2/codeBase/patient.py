from ..models import Hospital,HospitalCardFees,HospitalCardRenewalFees,Patient_Hospital_Card_Renewal_Payment,Patient_Dietary_Supplementary_Records,Patient_Dietary_Supplementary_Records_Details,OPD_Vital,Patient_OPD_Vitals,Patient_Hospital_Card_Payment,Patient_Laboratory_Test_Results_Details,Patient_Laboratory_Test_Records,Patient,Patient_Medical_Diagnosis_Records,Patient_Medical_History_Records,Patient_Hospital_History,Patient_Medical_History_Records,Staff,Region
from django.db.models.functions import LPad
from django.contrib.auth.models import User
from django.db.models import Count ,F,Q,Sum,Value
from datetime import datetime
from .sms import smscalls
from .laboratory import make_lab_test_payment,get_patniet_lab_case,patient_lab_history
'''
====================================================
            Patient odeView Chanllenge
====================================================

1. create patient accounts based in the hospital he visited

2. able to seach for patient based on name or telephone number or dob if only the patient account is
   created else create an account

3. After the patient account is registered, a card number is automatical generated for the customer 

4. patient can attend to more than one hospital but each details is saved seperately


'''

def check_for_patient_info(first_name,last_name,telephone,dob,region,user_id):
    '''
      create patient info but before the patient info is created
      the patient record is checked based on the patient phone number and date of birth
    '''
    checked_patients_record=Patient.objects.filter(telephone=telephone,date_of_birth=dob)
    if not checked_patients_record.exists():
        patient=create_patient_info(first_name,last_name,telephone,dob,region,user_id)
        return patient
    else:
        patient=patient_hospital_info(first_name,telephone,user_id)
        return patient
def create_patient_info(first_name,last_name,telephone,dob,region,user_id):
    '''
       create patients record 
    
    '''
    patients=Patient.objects.create(first_name=first_name,last_name=last_name,telephone=telephone,date_of_birth=dob,region=Region.objects.get(pk=region))
    patients.save()
    patient_id=Patient.objects.latest('id')
    data=create_patient_hospital_info(patient_id.id,user_id)
    return data
def create_patient_hospital_info(patient_id,user_id):
    get_staff_hospital_id=Staff.objects.get(staff__id=user_id)
    '''
      create patient hospital details includeing generating card number and patient case number
    '''
    patient_hospital_history=Patient_Hospital_History.objects.create(patient=Patient.objects.get(pk=patient_id),hospital=Hospital.objects.get(pk=get_staff_hospital_id.hospital.id))
    patient_hospital_history.save()
    patient_hospital_id=Patient_Hospital_History.objects.latest('id')
    card_number=generate_patient_card_number(patient_hospital_id.id)
    case_number=create_patient_case(patient_hospital_id.id,user_id)
    if card_number == True and case_number == True:
       patient=patient_opd_card_number(patient_id,user_id)
       if patient['status'] == True:
           get_Patient=Patient_Hospital_History.objects.get(pk=patient_hospital_id.id)
           message="Hi {}\n, welcome to Agadarko Herbal Clinic.\n card number {}.\nThanks for registering with us.\nAGADARKO Admin".format(get_Patient.patient.first_name,get_Patient.card_number)
           smscalls(message,get_Patient.patient.telephone)
           return {'status':'success','message':'patient medical record created'}
       #return patient
       #if len(patient) != 0:
       #
    else: 
        return {'status':'error','message':'couldn\'t create patient medical records'}
    
def create_patient_case(patient_hospital_id,user_id):
    '''
     creating patient medical history records and generating case numbers
    '''
    #print(patient_hospital_id, 'hit')
    patient_medical_case=Patient_Medical_History_Records.objects.create(patient=Patient_Hospital_History.objects.get(pk=patient_hospital_id),opd_nurse=User.objects.get(pk=user_id),checked_in=True)
    patient_medical_case.save()
    patient_medic_history=Patient_Medical_History_Records.objects.latest('id')
    generate_case_number=generate_patient_case_number(patient_medic_history.id)
    return generate_case_number
    
    

def generate_patient_card_number(patient_id):
    '''
      generating patient card number with LPAD function 
    '''
    patient_card_number=Patient_Hospital_History.objects.get(pk=patient_id)
    patient_card_number.card_number=LPad('id',8,Value('0'))
    patient_card_number.save()
    return True
    


def generate_patient_case_number(patient_medical_history_id):
    get_patient_medical_record=Patient_Medical_History_Records.objects.get(pk=patient_medical_history_id)
    get_patient_medical_record.case_number=LPad('id',8,Value('0'))
    get_patient_medical_record.save()
    return True

def patient_opd_card_number(patient_id,user_id):
    hospital=Staff.objects.get(staff__id=user_id)
    card_number=Patient_Hospital_History.objects.get(patient__id=patient_id,hospital__id=hospital.hospital.id)
    return {'card_number':card_number.card_number,'status':True}
    #return True

'''
first vist vs. second

'''
''''
new patient case

'''

def generate_patient_new_case(patient_card_id,amount,user__id):

    get_staff_id=Staff.objects.get(staff__id=user__id)

    check_card_number=Patient_Hospital_History.objects.filter(hospital__id=get_staff_id.hospital.id,card_number=patient_card_id,card_payment_status=True)

    if check_card_number.exists():
        '''
        generate a new case

        '''
        #get patient hospital id
        get_patient_hospital_id=Patient_Hospital_History.objects.get(card_number=patient_card_id)
        
        patient=create_patient_case(get_patient_hospital_id.id,user__id)
        patient_card_renewal=patient_card_renewal_payment(patient_card_id,amount,user__id)
        if patient == True and patient_card_renewal==True:
            patient_card=patient_opd_card_number(get_patient_hospital_id.id,user__id)
            return patient_card
        
        #return {'status':'patient exist ,card number {}'.format(get_patient_hospital_id.card_number)}
    else:
        '''
         generate new card and a case
        '''
        return {'status':'error','error':'patient hospital does not exist create!create new hospital records'}
    
def patient_card_renewal_payment(patient_card_number,amount,user_id):
     get_patient=Patient_Hospital_History.objects.get(card_number=patient_card_number)
     card_payment=HospitalCardRenewalFees.objects.get(hospital__id=get_patient.hospital.id)
     balance=float(card_payment.card_renewal_fees)-float(amount)
     if balance == 0.0:
         '''
         patient_payment_update=Patient_Hospital_History.objects.get(pk=get_patient.patient.id)
         patient_payment_update.card_payment_status=True
         payment_payement_history_id=patient_payment_update.id
         patient_payment_update.save()
         '''

         payments=Patient_Hospital_Card_Renewal_Payment.objects.create(patient=Patient_Hospital_History.objects.get(pk=get_patient.id),amount=amount,recieved_by=User.objects.get(pk=user_id))
         payments.save()
         message="Hi {},\n you paid GHS {} for card renewal.\n balance GHS{}\n. AGADARKO\nAdmin".format(get_patient.patient.first_name,amount,balance)
         smscalls(message,get_patient.patient.telephone)
         #return {'status':'success','message':'card payment made successfully'}
         return True
     else:
        #return {'status':'error','message':'amount insufficient'}
         return False
def view_patient_records(card_number):
    return Patient_Hospital_History.objects.filter(card_number=card_number)

def search_patient(search):
    data=[]
    search_results=Patient_Hospital_History.objects.filter(Q(card_number__contains=search)|Q(patient__first_name__icontains=search)|Q(patient__last_name__icontains=search)|Q(patient__telephone__contains=search)|Q(patient__date_of_birth__contains=search)) 
    for patient in search_results:
        data.append({'fullname':patient.patient.first_name+' '+patient.patient.last_name,'date_of_birth':patient.patient.date_of_birth,'telephone':patient.patient.telephone,'card_number':patient.card_number})
    return data

def check_in_patient(card_number):
    Patient_Hospital_History.objects.filter()

def patient_opd_vital(patient_id,vitals,results):
    for vital in range(len(vitals)):
        patient=Patient_OPD_Vitals.objects.create(patient=Patient_Medical_History_Records.objects.get(pk=patient_id),vital=vitals[vital],results=results[vital])
        patient.save()



def create_patient_diagnosis(patient_medical_history):
    patient_diagnosis=Patient_Medical_Diagnosis_Records.objects.create(patient=Patient_Medical_History_Records.objects.get(pk=patient_medical_history),patient_complaints="",doctor_diagnosis="") 
    patient_diagnosis.save()
    return True


def patient_hospital_info(name,telephone,user_id):
    hospital=Hospital.objects.get(adminstrator__id=user_id)
    patient=Patient_Hospital_History.objects.get(patient__telephone=telephone,hospital__id=hospital.id,patient__first_name=name)
    return {'name':patient.patient.first_name+' '+patient.patient.last_name,'card_number':patient.card_number,'date_of_birth':patient.patient.date_of_birth,'telephone':patient.patient.telephone}


def view_all_patient():
    return Patient.objects.all()

def patient_opd_info(card_number):
    return {'patient_bio':patientBio(card_number),'checked_in_status':patient_checked_in_status(card_number),'payment':check_card_payement(card_number),'card_payment_renewal':patient_card_renewal_payement(card_number),'opd_vitals':get_patient_opd_vitals(card_number),'paitient_opd_history':get_opd_patient_history(card_number),'attendance':total_attendance(card_number),'active_lab_case':get_patniet_lab_case(card_number)}

def patient_checked_in_status(card_number):
    data=[]
    checked_ins=Patient_Medical_History_Records.objects.filter(checked_in=True,checked_out=False,patient__card_number=card_number)
    if not checked_ins.exists():
        data.append({'checked_in_status':False})
    else:
        checked_in_states=checked_ins[0]
    #if len(checked_ins)>0:
        if checked_in_states.checked_in == True and  checked_in_states.checked_out== False:
            data.append({'checked_in_status':True,'case_number':checked_in_states.case_number})
        elif checked_in_states.checked_in == True and  checked_in_states.checked_out== True:
            data.append({'checked_in_status':False,'case_number':checked_in_states.case_number}) 
    return data
      
def patientBio(card_number):
    data=[]   
    patient_bio=Patient_Hospital_History.objects.get(card_number=card_number)
    data.append({'first_name':patient_bio.patient.first_name,'last_name':patient_bio.patient.last_name,'telephone':patient_bio.patient.telephone,'dob':patient_bio.patient.date_of_birth,'card_number':patient_bio.card_number})
    #print(data,'hello')
    return data




def check_card_payement(card_number):
    data=[]
    card_payment=Patient_Hospital_Card_Payment.objects.filter(patient__card_number=card_number)
    if card_payment.exists():
        get_payment_details=Patient_Hospital_Card_Payment.objects.get(patient__card_number=card_number)
        data.append({'payment_state':True,'amount_paid':get_payment_details.amount})
    else:
        get_patient_details=Patient_Hospital_History.objects.get(card_number=card_number)
        card_charges=HospitalCardFees.objects.get(hospital__id=get_patient_details.hospital.id)
        data.append({'payment_state':False,'amount_paid':0.00,'card_charge':card_charges.card_fees})
    return data

def patient_card_renewal_payement(card_number):
    data=[]
    patient=Patient_Hospital_History.objects.filter(card_number=card_number)
    if patient.exists():
        get_patient_details=Patient_Hospital_History.objects.get(card_number=card_number)
        card_charges=HospitalCardRenewalFees.objects.get(hospital__id=get_patient_details.hospital.id)
        data.append({'payment_state':False,'amount_paid':0.00,'card_charge':card_charges.card_renewal_fees})
    

    return data

def make_payement(case_number,amount):
     get_patient=Patient_Medical_History_Records.objects.get(case_number=case_number)
     card_payment=HospitalCardFees.objects.get(hospital__id=get_patient.patient.hospital.id)
     balance=float(card_payment.card_fees)-float(amount)
     if balance == 0.0:
         patient_payment_update=Patient_Hospital_History.objects.get(pk=get_patient.patient.id)
         patient_payment_update.card_payment_status=True
         payment_payement_history_id=patient_payment_update.id
         patient_payment_update.save()
         #check_card_payment_status=Patient_Hospital_Card_Payment.objects.filter(patient__id=get_patient.patient.id)
         #if not check_card_payment_status.exist():
         payments=Patient_Hospital_Card_Payment.objects.create(patient=Patient_Hospital_History.objects.get(pk=get_patient.patient.id),amount=amount)
         payments.save()
         message="Hi {},\n you paid GHS {} for card registration.\n balance GHS{}\n. AGADARKO\nAdmin".format(patient_payment_update.patient.first_name,amount,balance)
         smscalls(message,patient_payment_update.patient.telephone)
         return {'status':'success','message':'card payment made successfully'}
         #else:
         #return {'status':'error','message':'card payment already made'}
     else:
        return {'status':'error','message':'amount insufficient'}
     

def get_patient_opd_vitals(card_number):
    data=[]
    patient_vitals=Patient_OPD_Vitals.objects.filter(patient__checked_in=True,patient__checked_out=False,patient__patient__card_number=card_number)
    if patient_vitals.exists():
        data.append({'vital_status':True})
        lists=[]
        for vitals in patient_vitals:
            lists.append({'vital':vitals.vital.vital,'serial_code':vitals.vital.serial_code,'result':vitals.results})
       
        data.append(lists)
            
    else:
        get_opd_vitals=OPD_Vital.objects.all()
        lists=[]
        data.append({'vital_status':False})
        for vitals in get_opd_vitals:
             
             lists.append({'vitals':vitals.vital,'serial_code':vitals.serial_code,'results':''})
       
        data.append(lists)

    return data 

def get_opd_patient_history(card_number):
    data=[]
    patient=Patient_Medical_History_Records.objects.filter(checked_in=True,checked_out=True,patient__card_number=card_number)
    for patient_opd in patient:
        data.append({'case_number':patient_opd.case_number,'date_checked_in':patient_opd.time_checked_in,'checked_out':patient_opd.time_checked_out})
    return data

def total_attendance(card_number):
    total_attendance=Patient_Medical_History_Records.objects.filter(checked_in=True,checked_out=True,patient__card_number=card_number).count()
    return [{"total_attendance":total_attendance}]
def get_case_number(card_number):
    get_patient_case_number=Patient_Medical_History_Records.objects.filter(checked_in=True,checked_out=False,patient__card_number=card_number)
    if get_patient_case_number.exists():
         patient_case_number=Patient_Medical_History_Records.objects.filter(checked_in=True,checked_out=False,patient__card_number=card_number)[0]
         return {'case_number':patient_case_number.case_number}
    
       
   
        
    #return {'case_number':patient_case_nuumber.case_number}

def create_patinet_opd(case_number,vitals,results):
    patient_opd_vital=Patient_OPD_Vitals.objects.filter(patient__case_number=case_number)
    if patient_opd_vital.exists():
        return {'status':'error',"error":"view patient opd vitals already existed"}
    else:
        patient=Patient_Medical_History_Records.objects.filter(case_number=case_number,checked_in=True,checked_out=False)
        if patient.exists():
            patients=patient_opd(case_number,vitals,results)
            return patients
        else:
            return {'status':'error','error':'patient not checked in'}
        
def patient_opd(case_number,vitals,results):
    patient_id=Patient_Medical_History_Records.objects.get(case_number=case_number)
    for vital in range(len(vitals)):
        get_opd_vitals=OPD_Vital.objects.get(serial_code=vitals[vital])
        print('vitals ',vitals[vital],' ',get_opd_vitals.id)
        patients=Patient_OPD_Vitals.objects.create(patient=Patient_Medical_History_Records.objects.get(pk=patient_id.id),vital=OPD_Vital.objects.get(pk=get_opd_vitals.id),results=results[vital])
        patients.save()

    return {'status':'success',"success":'patient opd status created successfully'}




def patient_opd_history_details(case_number):
    '''
      get patient 
    '''
    return {'patient_bio_data':patient_bio_details(case_number),'patient_opd_vitals':patient_opd_vitals(case_number),'patient_lab':patient_laboratory_history(case_number),'patient_cases':patient_cases_history(case_number),'patient_supplement':patient_supplement_dietary(case_number)}

def patient_bio_details(case_number):
    patient_bio=Patient_Medical_History_Records.objects.get(case_number=case_number)
    return {'first_name':patient_bio.patient.patient.first_name,'last_name':patient_bio.patient.patient.last_name,'card_number':patient_bio.patient.card_number,'case_number':patient_bio.case_number}

def  patient_opd_vitals(case_number):
    patient_vitals=Patient_OPD_Vitals.objects.filter(patient__case_number=case_number)
  
    
    data=[]
    for vitals in patient_vitals:
        data.append({'vital':vitals.vital.vital,'serial_code':vitals.vital.serial_code,'result':vitals.results})
   
    return data
    


def patient_laboratory_history(case_number):
    lab_test_details=[]
    lab_test_records=[]
    patient_lab_details=Patient_Laboratory_Test_Records.objects.get(patient__patient__case_number=case_number)
    lab_test_records.append({'case_number':patient_lab_details.patient.patient.case_number,'total_cost':patient_lab_details.total_cost,'amount_paid':patient_lab_details.amount_paid})

    patient_lab_details_result=Patient_Laboratory_Test_Results_Details.objects.filter(patient__patient__patient__case_number=case_number)

    for patient_labs in patient_lab_details_result:
        lab_test_details.append({'test_type':patient_labs.lab_test.test_type,'test_cost':patient_labs.lab_test.test_cost})

    return [{'lab_test_records':lab_test_records,'lab_test_details':lab_test_details}]

def patient_cases_history(case_number):
    data=[]
    retrive_patient_card=Patient_Medical_History_Records.objects.get(case_number=case_number)

    retirve_patient_history_details=Patient_Medical_History_Records.objects.filter(patient__card_number=retrive_patient_card.patient.card_number,checked_in=True,checked_out=True)

    for history in retirve_patient_history_details:
        data.append({'case_number':history.case_number,'date_checked_in':history.time_checked_in,'date_checled_out':history.time_checked_out})

    return data

def patient_supplement_dietary(case_number):

    patient_supplement_record=[]
    patient_supplement_record_details=[]
    patient_supplement=Patient_Dietary_Supplementary_Records.objects.get(patient__patient__case_number=case_number)
    patient_supplement_record.append({'case_number':patient_supplement.patient.patient.case_number,'total_cost':patient_supplement.total_cost,'amount_paid':patient_supplement.amount_paid,'payment_status':patient_supplement.payment_status})

    patient_supplement_details=Patient_Dietary_Supplementary_Records_Details.objects.filter(patient__id=patient_supplement.id)

    for supplements in patient_supplement_details:
        patient_supplement_record_details.append({'supplements':supplements.dietary_supplement.supplement,'quantity':supplements.quantity,'cost_per_unit':supplements.cost})

    return   {'patient_supplement_record':patient_supplement_record,'patient_supplement_record_details':patient_supplement_record_details} 






'''
heck patient who wants to log in

'''

