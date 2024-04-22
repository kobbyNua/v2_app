from ..models import Patient_Medical_History_Records,Patient_OPD_Vitals,OPD_Vital,Patient_Medical_History_Physician_records,Dietary_Supplementary,Patient_Dietary_Supplementary_Records,Patient_Dietary_Supplementary_Records_Details,Out_side_Lab_test,Laboratory_Test_Cost_Details,Patient_Laboratory_Test_Results_Details,Patient_Laboratory_Test_Records,Dietary_Supplementary,Patient_Medical_Diagnosis_Records
from .dietary import view_dietary_list,deitaryItemsStocking
from .laboratory import view_lab_test_cost
from .hospital import view_opd_vitals
from .patient import patient_bio_details
from django.db.models.functions import LPad
from django.contrib.auth.models import User
from django.db.models import Count ,F,Q,Sum,Value
from datetime import datetime
'''
view patients checked in
view patient lab test results

view patient medical history(diagnosis,complains,lab test,dietary)

'''


def view_checked_in_patient():
    '''
    view all patient who has checked in and ready for medical diagnosis
    '''
    
    data=[]
    out_patient=Patient_Medical_History_Records.objects.filter(checked_in=True,checked_out=False,patient__card_payment_status=True)
    for patients in out_patient:
        data.append({'patient_name':patients.patient.patient.first_name.upper()+' '+patients.patient.patient.last_name.upper(),'card_number':patients.patient.card_number,'case_number':patients.case_number,"checked_in":patients.time_checked_in})

    return data

def dietary_supplemnetary():
    data=[]
    supplement=view_dietary_list()
    for dietary in supplement:
        data.append({'supplement':dietary.supplement,'quantity':dietary.quatity_in_stocked,'price':dietary.price,'serial_code':dietary.serial_code})

    return data

def shortage_dietary_supplement():
    data=[]
    supplement=deitaryItemsStocking()
    for dietary in supplement:
        data.append({'supplement':dietary.supplement,'quantity':dietary.quatity_in_stocked,'price':dietary.price,'serial_code':dietary.serial_code})
    print(data,' over staocking')
    return data
def laboratory_test():
    data=[]
    test=view_lab_test_cost()


def opd_lists():
    return view_opd_vitals()

def getPatientOPDVitals(case_number):
    data=[]
    patient_opd_vitals=Patient_OPD_Vitals.objects.filter(patient__case_number=case_number)
  
    for vitals in patient_opd_vitals:
        data.append({"vitals":vitals.vital.vital,'result':vitals.results})
    return data

def getPatientLabReportStatus(case_number):
    data=[]
    patient_lab_test=Patient_Laboratory_Test_Records.objects.filter(patient__patient__case_number=case_number)
    if patient_lab_test.exists():
        patient_lab_test_status=Patient_Laboratory_Test_Records.objects.get(patient__patient__case_number=case_number)
        if patient_lab_test_status.patient.laboratory_report_request_status==True and patient_lab_test_status.lab_test_released == True:
            data.append({'status':'lab test ready'})
        elif patient_lab_test_status.patient.laboratory_report_request_status==True and patient_lab_test_status.lab_test_request_view == True and patient_lab_test_status.lab_test_released == False:
             
             data.append({'status':'lab test results pending'})

        elif patient_lab_test_status.patient.laboratory_report_request_status==True and patient_lab_test_status.lab_test_request_view == False and patient_lab_test_status.lab_test_released == False:
             
             data.append({'status':'lab test results pending'})             
        elif patient_lab_test_status.patient.laboratory_report_request_status==False and patient_lab_test_status.lab_test_released == False:
            data.append({'status':'no lab test'})
      
    else:
        data.append({'status':'no lab test'})
    return data



def getPatientLabReport(case_number):
    #medical_dignosis_id=Patient_Medical_Diagnosis_Records.objects.get(case_number=case_number)
    data=[]
    patient_lab_test=Patient_Laboratory_Test_Records.objects.filter(patient__patient__case_number=case_number,lab_test_released=True)
    if patient_lab_test.exists():
        patient_lab_result=Patient_Laboratory_Test_Results_Details.objects.filter(patient__patient__patient__case_number=case_number)
        for cases in patient_lab_result:

            data.append({'test':cases.lab_test.test_type,'serial_code':cases.lab_test.serial_code,'test_results':cases.test_results})
    print('helloo ',data)
    return data


def getDietaryRportStauts(case_number):
    data=[]
    patient_diet_records=Patient_Dietary_Supplementary_Records.objects.filter(patient__patient__case_number=case_number)
    if patient_diet_records.exists():
         patient_diet_status=Patient_Dietary_Supplementary_Records.objects.get(patient__patient__case_number=case_number)
         if patient_diet_status.patient.dietary_prescription_request == True and patient_diet_status.dietary_supplement_dispense_viewed == True:
              data.append({'status':'supplement dispensed'})
         elif patient_diet_status.patient.dietary_prescription_request == True and  patient_diet_status.dietary_supplement_request_view ==True and patient_diet_status.dietary_supplement_dispense_viewed == False:
              data.append({'status':'supplement pending'})
         elif patient_diet_status.patient.dietary_prescription_request == True and  patient_diet_status.dietary_supplement_request_view ==False and patient_diet_status.dietary_supplement_dispense_viewed == False:
              data.append({'status':'supplement pending'})              
         elif patient_diet_status.patient.dietary_prescription_request == False and patient_diet_status.dietary_supplement_dispense_viewed == False:
             data.append({'status':'no supplement dispensed'})
    else:
        data.append({'status':'no supplement dispensed'})
    return data
def getPatientDietarySupplement(case_number):
    data=[]
    patient_records=Patient_Dietary_Supplementary_Records.objects.filter(patient__patient__case_number=case_number,dietary_supplement_request_view=True,dietary_supplement_dispense_viewed=True)
    if patient_records.exists():
        patient_dietary=Patient_Dietary_Supplementary_Records_Details.objects.filter(patient__patient__patient__case_number=case_number)
        for supplements in patient_dietary:
            data.append({'supplements':supplements.dietary_supplement.supplement,'serial_code':supplements.dietary_supplement.serial_code})

    return data 


'''
view patient medical dignosis
'''
def patient_medical_details(case_number):
    patient_diagnosis=patient_medical_diagnosis_details(case_number)

    return {'patient_bio':patient_bio_details(case_number),'laboratory_test_list':view_lab_test_cost(),'supplement_list':dietary_supplemnetary(),'lab_test_status':getPatientLabReportStatus(case_number),'patient_dietary_status':getDietaryRportStauts(case_number),"patient_dietary":getPatientDietarySupplement(case_number),"patient_lab":getPatientLabReport(case_number),'patient_opd_vitals':getPatientOPDVitals(case_number),'patient_diagnosis':patient_diagnosis.patient_complaints,'doctor_diagnosis':patient_diagnosis.doctor_diagnosis,'patient_medical_history':view_patients_medical_history_list(case_number),'current_case':view_patient_current_case(case_number)}

def check_patient_medical_diagnosis_records(case_number,user_id):
    check_record=Patient_Medical_Diagnosis_Records.objects.filter(patient__case_number=case_number)
    if check_record.exists():
    
        return patient_medical_details(case_number)
    else:
  
        get_medical_history_id=Patient_Medical_History_Records.objects.get(case_number=case_number)
        
        patient_diagnosis=create_patients_diagnosis(get_medical_history_id.id,user_id)
        if patient_diagnosis == True:
            return check_patient_medical_diagnosis_records(case_number,user_id)
        else:
           # print('error')
           pass





def create_patients_diagnosis(case_id,user_id):
    patient_medical_history=Patient_Medical_Diagnosis_Records.objects.create(patient=Patient_Medical_History_Records.objects.get(pk=case_id))
    patient_medical_history.save()

    patient_medical_id=Patient_Medical_Diagnosis_Records.objects.latest('id')
    patient_physician=Patient_Medical_History_Physician_records.objects.create(physician=User.objects.get(pk=user_id),medical_diagnosis=Patient_Medical_Diagnosis_Records.objects.get(pk=patient_medical_id.id))
    patient_physician.save()
    return True
    #check_patient_medical_diagnosis_records(case_number,user_id)


def view_patient_current_case(case_number):
    data=[]
    patient_current_case=Patient_Medical_Diagnosis_Records.objects.filter(patient__case_number=case_number,patient__checked_in=True,patient__checked_out=False)

    if patient_current_case.exists():
        get_patient_current_case=Patient_Medical_Diagnosis_Records.objects.get(patient__case_number=case_number)
        data.append({'status':True,'current_case':get_patient_current_case.patient.case_number})
    else:
        data.append({'status':False,'current_case':'no new case'})
    return data

def view_patients_medical_history_list(case_number):
    '''
    view patient medical history list
    '''
    data=[]
    patients=Patient_Medical_Diagnosis_Records.objects.get(patient__case_number=case_number)
    #print(patients.patient.patient.card_number)
    patients_history_number=Patient_Medical_Diagnosis_Records.objects.filter(patient__patient__card_number=patients.patient.patient.card_number,patient__checked_in=True,patient__checked_out=True)
    #print('hello world',patients_history_number)
    for patient_records in patients_history_number:
        #print(patient_records.patient.case_number)
        data.append({'case_number':patient_records.patient.case_number,'checked_in_date':patient_records.patient.time_checked_in})
    #print('hello',data)
    return data

def view_patients_medical_history(case_number):
    '''
     patient medical history records
    '''
    return Patient_Medical_Diagnosis_Records.objects.filter(patient__case_number=case_number)

'''
def view_patient_complaints():
    pass

def view_patient_diagnosis():
    pass
'''
def patient_medical_diagnosis_details(case_number):
    return Patient_Medical_Diagnosis_Records.objects.get(patient__case_number=case_number)

def create_patient_complaints(case_number,complaints):
    #print(" hello world ",case_number,complaints)
    patient_complaints=patient_medical_diagnosis_details(case_number)
    patient_complaints.patient_complaints=complaints
    patient_complaints.save()
    return  {"status":'success','success':'patient complains submited'}

def create_patient_diagnosis(case_number,diagnosis):
    patient_diagnosis=patient_medical_diagnosis_details(case_number)
    patient_diagnosis.doctor_diagnosis=diagnosis
    patient_diagnosis.save()
    return {"status":'success','success':'created doctor diagnosis'}



def patient_laboratory_request(in_house,lab_request,case_number,lab_test_type,discount_rate,photo):
    '''
        -if lab test is done inside, lab test details are sent to the lab technician 
        -if lab test is not inside the details are printed out and when the results are returned it is saved as photo
    '''
    if in_house == True and lab_request == True:
        patient_lab_request=patient_medical_diagnosis_details(case_number)
        patient_lab_request.in_house_laboratory_test=True
        patient_lab_request.laboratory_report_request_status=True
        patient_med_record_id=patient_lab_request.id
        patient_lab_request.save()
        create_patient_lab_test=create_test_lab_test(patient_med_record_id,lab_test_type,discount_rate)
        return create_patient_lab_test

    elif in_house == False and lab_request == True:
        patient_lab_request=patient_medical_diagnosis_details(case_number)
        patient_lab_request.in_house_laboratory_test=False
        patient_lab_request.laboratory_report_request_status=True
        patient_med_record_id=patient_lab_request.id
        patient_lab_request.save() 
        uploads=upload_patient_lab_test(patient_med_record_id,photo) 
        return uploads      
         
def create_test_lab_test(patient_med_id,lab_test_type,discount_rate):
    doctor_patient_lab_request=Patient_Laboratory_Test_Records.objects.create(patient=Patient_Medical_Diagnosis_Records.objects.get(pk=patient_med_id),)
    doctor_patient_lab_request.save()
    patient_lab_request_id=Patient_Laboratory_Test_Records.objects.latest('id')
    lab_test_cost=patient_laboratory_test_cost(patient_lab_request_id.id,lab_test_type,discount_rate)
    selected_lab_test=patient_laboratory_test_types(patient_lab_request_id.id,lab_test_type)

    if lab_test_cost ==True and selected_lab_test==True:
        return {"status":'success','success':'laboratory test request succesful'}
    else:
        return {"status":'error','error':'laboratory test request not successful'}


def patient_laboratory_test_cost(patient_lab_request_id,lab_test_type,discount_rate):
    total_cost=0
    discount_cost=0
    for test in range(len(lab_test_type)):
        lab_test_costs=Laboratory_Test_Cost_Details.objects.filter(id=lab_test_type[test])

        for lab_test in lab_test_costs:
            total_cost+=float(lab_test.test_cost)
    patient_lab=Patient_Laboratory_Test_Records.objects.get(pk=patient_lab_request_id)
    
    if int(discount_rate) > 0 :
        patient_lab.total_cost=total_cost
        discount_cost=total_cost*(100-int(discount_rate))/100
        patient_lab.discount_rate=discount_rate
        patient_lab.discount_status=True
        patient_lab.discount_amount=discount_cost
        patient_lab.save()
        return True
    else:
        patient_lab.total_cost=total_cost
        patient_lab.save()
        return True
    '''    
    patient_lab.total_cost=total_cost
    patient_lab.save()
    return True
    '''

def patient_laboratory_test_types(patient_lab_id,lab_test_type):
    '''
    first checks all the cost of the lab test required
    and insert the cost with the lab test

    '''
    for test in range(len(lab_test_type)):
        lab_test_costs=Laboratory_Test_Cost_Details.objects.filter(id=lab_test_type[test])

        for costs in lab_test_costs:
                patient_lab_list=Patient_Laboratory_Test_Results_Details.objects.create(patient=Patient_Laboratory_Test_Records.objects.get(pk=patient_lab_id),lab_test=Laboratory_Test_Cost_Details.objects.get(pk=costs.id),test_cost=costs.test_cost)
                patient_lab_list.save()

    return True

def upload_patient_lab_test(patient_lab_id,photo):
    upload_lab_image_results=Out_side_Lab_test.objects.create(patient=Patient_Medical_Diagnosis_Records.objects.get(pk=patient_lab_id),upload_lab_photo=photo)
    upload_lab_image_results.save()
    return {"status":'success','success':'patient laboratory case succesful'}



def patient_dietory_request(case_number,dietary_supplements,discount_rate):
    patient_diagnosis_dietary=patient_medical_diagnosis_details(case_number)
    patient_diagnosis_dietary.dietary_prescription_request=True
    patient_diagnosis_dietary_id=patient_diagnosis_dietary.id
    patient_diagnosis_dietary.save()
    supplement=patient_dietary_supplement_details(patient_diagnosis_dietary_id,dietary_supplements,discount_rate)
    if supplement == True:
        return {'status':'success','success':'patient dietary supplement send successsfully'}

def patient_dietary_supplement_details(patient_id,dietary_supplements,discount_rate):
    patient_supplements=Patient_Dietary_Supplementary_Records.objects.create(patient=Patient_Medical_Diagnosis_Records.objects.get(pk=patient_id))
    patient_supplements.save()
    patient_dietary_supplement=Patient_Dietary_Supplementary_Records.objects.latest('id')
    patient_dietary_cost=patient_dietary_supplements_cost(patient_dietary_supplement.id,dietary_supplements,discount_rate)
    patient_dietary_supplement_lists=patient_dietary_supplement_list(patient_dietary_supplement.id,dietary_supplements)
    if patient_dietary_cost == True and patient_dietary_supplement_lists == True:
        return True

def patient_dietary_supplements_cost(patient_supplement_id,dietary_supplements,discount_rate):
    total_cost=0
    discount_cost=0
    for supplements in range(len(dietary_supplements)):
        patient_supplement_bill=Dietary_Supplementary.objects.filter(serial_code=dietary_supplements[supplements])
        for supplement in patient_supplement_bill:
            total_cost+=float(supplement.price)
    if int(discount_rate) > 0:
        discount_cost=float(total_cost)*(100-int(discount_rate))/100
        discount_status=True
    else:
        discount_cost=total_cost
        discount_status=False
    patient_supplement_info=Patient_Dietary_Supplementary_Records.objects.get(pk=patient_supplement_id)
    patient_supplement_info.total_cost=total_cost
    patient_supplement_info.discount_status=discount_status
    patient_supplement_info.discount_rate=discount_rate
    patient_supplement_info.discount_amount=discount_cost
    patient_supplement_info.save()
    return True

def patient_dietary_supplement_list(patient_supplement_id,dietary_supplements):
    #print(dietary_supplements)
    for items in range(len(dietary_supplements)):
        get_dietary_supplements = Dietary_Supplementary.objects.filter(serial_code=dietary_supplements[items])
        for patient_supplement in get_dietary_supplements:
            #print(patient_supplement,patient_supplement_id)
            patient_dietary_supplement=Patient_Dietary_Supplementary_Records_Details.objects.create(patient=Patient_Dietary_Supplementary_Records.objects.get(pk=patient_supplement_id),dietary_supplement=Dietary_Supplementary.objects.get(pk=patient_supplement.id),cost=patient_supplement.price)
            patient_dietary_supplement.save()
    return True


def patient_medical_dignosis_history_search(search):
    medical_history_search=Patient_Medical_Diagnosis_Records.objects.values('patient__patient__card_number','patient__patient__patient__first_name','patient__patient__patient__last_name','patient__patient__patient__telephone').annotate(total_visit=Count('patient__patient__patient__id')).filter(Q(patient__patient__card_number__contains=search)|Q(patient__patient__patient__first_name__icontains=search)|Q(patient__patient__patient__last_name__icontains=search)|Q(patient__patient__patient__telephone__contains=search)|Q(patient__patient__patient__date_of_birth__contains=search)) 
    return medical_history_search
   

def patient_medical_dignosis_history_cases(card_number):
    data=[]
    medical_history_cases=Patient_Medical_Diagnosis_Records.objects.filter(patient__patient__card_number=card_number)
    for cases in medical_history_cases:
        data.append({'case_number':cases.patient.case_number,'checked_in_time':cases.patient.time_checked_in,'time_checked_out':cases.patient.time_checked_out})
    return data
      