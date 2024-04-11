from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.contrib.auth import authenticate,login,logout
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.models import User,Group
from .codeBase.hospital import view_opd_vitals,view_staffs,allSuperUser,edit_staff,create_opd_vitals,view_regions,check_region,view_group,create_groups,edit_groups,view_hospital,create_hospital_details,create_staff,view_all_staffs,get_staff
from .codeBase.patient import check_for_patient_info,patient_opd_history_details,generate_patient_new_case,make_payement,get_case_number,patient_opd_info,search_patient,create_patinet_opd,view_all_patient,view_patient_records
from .codeBase.doctor import patient_medical_details,shortage_dietary_supplement,patient_medical_dignosis_history_search,patient_medical_dignosis_history_cases,dietary_supplemnetary,view_checked_in_patient,check_patient_medical_diagnosis_records,create_patient_complaints,create_patient_diagnosis,patient_laboratory_request,patient_dietory_request
from  .codeBase.dietary import daily_supplements_sales,daily_supplements_sales_details,generate_supplements_dietary_reports,generate_supplement_report,filterDietarySupplement,get_dietary_supplement,getDietarySupplement,create_dietary_supplement_details,customers_inventory_sales,update_dietary_details_stock,viewStockingSupplementDietaryList,dietary_pending_for_restock,dietary_pending_for_restock,update_dietary_details,view_patient_dietary_supplements,view_patient_dispenary,dispensed_patient_dietary_supplement   
from .codeBase.laboratory import view_lab_test_cost,make_lab_test_payment,getLaboratoryList,create_lab_test_details,view_lab_test_cost_details,edit_lab_test_details,view_waiting_patient_lab_test,view_patient_lab_records,update_test_results, create_outside_lab_test,input_lab_test_result
#from rest_framework import serializers
from django.core import serializers
from  rest_framework.authtoken.models import Token
import json
# Create your views here.

def test(request):
    return HttpResponse('hello')

@api_view(['POST'])
def auth(request):
    if request.method=='POST':
       data=json.loads(request.body)
       #username='abuchain'
       #password='Password@1'
       #data={'username':username,'password':password}
       user=authenticate(username=data['username'],password=data['password'])
       if user is not None:
           get_user=User.objects.get(username=data['username'])
           token,created=Token.objects.get_or_create(user=get_user)
           return Response({'status':'success','message':'logined','token':token.key})
       else:
           return Response({'status':'error','message':'login in failed'})
          

@api_view(['GET','POST'])
def view_region(request):
    '''
    view all regions
    '''
    regions=view_regions()
    return Response(regions)

'''
creat 
'''
@api_view(['GET','POST'])
def create_regions(request):
    '''
    create region
        #region=request.GET.get('region')
    #regions=check_region(region)
    #print('hello ==== ',region)
    #return Response(regions)
    '''
    if request.method == 'POST':
        print(request.body)
        data=json.loads(request.body)
        regions=check_region(data.get('region'))  

        return Response(regions)


'''
  #create user groups
  #view groups
  #edit groups
'''

@api_view(['GET'])
def view_all_groups(request):
    groups=view_group()
    return Response(groups)


@api_view(['GET','POST'])
def create_user_groups(request):
    #['doctor','nurse','lab technician']
    #groups=create_groups()
    #return Response(groups)
    if request.method == 'POST':
        data=json.loads(request.body)
        #print(data.get('group'))
        groups=create_groups(data.get('groups'))
        return Response(groups)


'''
 
   #view hospital details
   #create hospital details

'''

@api_view(['POST','GET'])
def view_all_hospital(request):
    hosptials=view_hospital()

    return Response(hosptials)

@api_view(['POST','GET'])
def create_hospital_detail(request):
    #hospital=create_hospital_details('Agadarko',1,'agardakro@example.com','23354002345','Kwabenya',1)
    if request.method == "POST":
        data=json.loads(request.body)
        hospital=create_hospital_details(data['hospital'],data['superuser'],data['email'],data['telephone'],data['town'],data['region'],data['admin_telephone'])
        return Response(hospital)
        

    #return Response(hospital)


'''
   #view all staff
   #create staffs
   #edit staffs
'''
@api_view(['POST','GET'])
def view_total_staff(request):
    data=view_staffs(1)
    print('====hello==== ',data)
    return Response({'hello':'hii'})
@api_view(['POST','GET'])
def view_staffs(request):
    staff=view_all_staffs(1)
    return Response(staff)
@api_view(['POST','GET'])
def view_staff_details(request,username):
    staff=get_staff(username)
    
    return Response(staff)
@api_view(['POST','GET'])
def create_new_staffs(request):
    if request.method == "POST":
        data=json.loads(request.body)
        print(data)
        staffs=create_staff(data['first_name'],data['last_name'],data['email'],data['username'],data['telephone'],data['roles'],1,data['super_user_state'])
        return Response(staffs)
    #staffs=create_staff("Afrifa","Sedem","afrifa@sedem.com",'AfrifaSedem','024569010',[1],1)
    #return Response(staffs)


@api_view(['POST','GET'])
def edit_staff_info(request):
    if request.method == "POST":
        data=json.loads(request.body)
        
        edit=edit_staff(data['email'],data['first_name'],data['last_name'],data['username'],data['telephone'],data['user_id'],data['staff_id'])
        return Response(edit)


@api_view(['POST','GET'])
def allSuperUsers(request):
   
    data=allSuperUser()
    return Response(data)



@api_view(['GET','POST'])
def view_all_opd_vitals(request):
    vital=view_opd_vitals()
    return Response(vital)


@api_view(['GET','POST'])
def create_opd_vital(request):
    if request.method=="POST":
        data=json.loads(request.body)
        #print('hello world',data)
        
        vital=create_opd_vitals(data["opd_vitals"],1)
        return Response(vital)

@api_view(['GET','POST'])
def view_Checked_in_patient_lists(request):
    patient=view_checked_in_patient()
    return Response(patient)

@api_view(['GET','POST'])
def patients(request):
    '''
    view patients
    '''
    #patient=view_patient_records('00000004')
    patient=patient_medical_details('00000001')
    return Response(patient)

@api_view(['GET','POST'])
def patients_search(request):
    if request.method == "POST":
       data=json.loads(request.body)
       patient=search_patient(data['search'])
       return Response(patient)

@api_view(['GET','POST'])
def create_patient_medical_bio_info(request):
    #'John','Kuma','0204588112','1995-05-07',2,1
    if request.method == "POST":
       data=json.loads(request.body)
       patient=check_for_patient_info(data['first_name'],data['last_name'],data['telephone'],data['date_of_birth'],data['region'],1)
       return Response(patient)

@api_view(['GET','POST'])       
def patient_opd_information(request,card_number):
    
    data=patient_opd_info(card_number)
    return Response(data)

@api_view(['GET','POST']) 
def getCaseNumber(request,card_number):
    data=get_case_number(card_number)
    return Response(data)
@api_view(['GET','POST'])
def card_payment(request):
    if request.method == "POST":
        data=json.loads(request.body)
        #print(data)
        payment=make_payement(data['case_number'],data['amount'])
        return Response(payment)
@api_view(['POST','GET'])
def get_patient_opd_history_details(request,case_number):
    #print('hello')
    history_details=patient_opd_history_details(case_number)
    return Response(history_details)
@api_view(['GET','POST'])
def generate_new_case(request):
    if request.method =="POST":
        data=json.loads(request.body)
        #print(data)
        new_case=generate_patient_new_case(data['card_number'],data['amount'],1)
        return Response(new_case)
@api_view(['GET','POST'])
def create_patient_opd_vital_info(request):
    if request.method == "POST":
        data=json.loads(request.body)
        print(data)
        patient=create_patinet_opd(data['case_number'],data['serial_code'],data['result'])
        
        return Response(patient)
#patient=create_patinet_opd('00000003',['00000003','00000004','00000005'],['120/80','85kg','35'])
#patient edical diagnosis
@api_view(['GET','POST'])
def create_patient_medical_diagnosis(request,case_number):
    patient_diagnosis=check_patient_medical_diagnosis_records(case_number,1)
    return Response(patient_diagnosis)




'''
test tomorrow
'''
@api_view(['GET','POST'])
def patient_complains_medical_diagnosis(request):
    '''
    creating patient diagonal case
    '''
    if request.method == 'POST':
        data=json.loads(request.body)
        print(data)
        complaints=create_patient_complaints(data['case_number'],data['patient_complains'])
        return Response(complaints)

@api_view(['GET','POST'])
def patient_doctor_medical_diagnosis(request):
    if request.method == 'POST':
        data=json.loads(request.body)
        print(data)
        diagnosis=create_patient_diagnosis(data['case_number'],data['doctor_diagnosis'])
        return Response(diagnosis)
    
@api_view(['GET','POST'])    
def medical_diagnosis_history_search(request):
    if request.method == "POST":
        data=json.loads(request.body)
        search=patient_medical_dignosis_history_search(data['card_number'])
        return Response(search)

@api_view(['GET','POST']) 
def medical_diagnosis_history_cases(request,card_number):
    cases=patient_medical_dignosis_history_cases(card_number)
    return Response(cases)


@api_view(['GET','POST'])
def patient_lab_test(request):
    if request.method == "POST":
        data=json.loads(request.body)
        print(data)
        lab_test=patient_laboratory_request(bool(data['in_house_lab_status']),True,data['case_number'],data['serial_code'],'photo.jpg')
        return Response(lab_test)

@api_view(['GET','POST'])
def prescribe_patient_dietary_supplement(request):

    if request.method == "POST":
        data=json.loads(request.body)
        supplements=patient_dietory_request(data['case_number'],data['serial_code'])
        return Response(supplements)


@api_view(['GET','POST'])
def get_lab_test_list(request):
    if request.method == "POST":
        data=json.loads(request.body)
        lists=[]
        lists.append(data['body'])
        #print(lists)
        test_list=getLaboratoryList(lists)
        return Response(test_list)

@api_view(['GET','POST'])
def get_dietary_supplement_list(request):
    if request.method=="POST":
        data=json.loads(request.body)
        #print(data)
        supplements=getDietarySupplement(data['serial'])
        #print(supplements)
        return Response(supplements)


@api_view(['GET','POST'])
def get_filter_supplement_list(request):
    if request.method=="POST":
        data=json.loads(request.body)
        supplements=filterDietarySupplement(data['serial'])
        print(data)
        return Response(supplements)

'''
creating dieatary supplement and restocking supplement dietary
'''
@api_view(['GET','POST'])
def view_dietary_supplement(request):
    data=dietary_supplemnetary()
    #print(data,'hittttt')
    return Response(data)


@api_view(['GET','POST'])
def stocking_needing_urgent_stocking(request):

    data=shortage_dietary_supplement()
    print(data,' over ')
    return Response(data)

@api_view(['GET','POST'])
def create_dietary_supplements_details(request):
    #
    #return Response(supplement)
    if request.method == 'POST':
        print(request.data)
        #print(request.data['photo'],request.data['price'],request.data['dietary_supplement'])
        supplement=create_dietary_supplement_details(request.data['dietary_supplement'],request.data['price'],int(request.data['quantity']),request.data['photo'],1)
        #print(data,'=====helloo=====')
        return Response(supplement)
@api_view(['GET','POST'])
def stock_dieatry_supplement(request):
    if request.method == "POST":
        data=json.loads(request.body)
        supplements=update_dietary_details_stock(data['serial_code'],data['quantity'],data['price'],1)
        print(supplements,'======hello======')
        return Response(supplements)

@api_view(['GET','POST'])
def dietary_stocking_history(request,dietary_code):
    supplement=viewStockingSupplementDietaryList(dietary_code)
    return Response(supplement)

@api_view(['GET','POST'])
def dietary_which_needs_to_restock(request):
    dietary_supplement=dietary_pending_for_restock()
    return Response(dietary_supplement)

@api_view(['GET','POST'])
def updateDietarySupplementName(request):
    if request.method == "POST":
        data=json.loads(request.body)
        print(data)
        dietary=update_dietary_details(data['supplement'],data['serial_code'])
        return Response(dietary)

@api_view(['GET','POST'])
def deitary_supplement_details(request,dietary_code):
    data=get_dietary_supplement(dietary_code)
    return Response(data)

'''
patient dietary supplement dispensary
'''
@api_view(['GET','POST'])
def viewPatientDietarySupplementList(request):
    patient_dietary=view_patient_dietary_supplements()
    return Response(patient_dietary)
@api_view(['GET','POST'])
def patient_dietary_records(request,case_number):
    records=view_patient_dispenary(case_number,1)
    return Response(records)
@api_view(['GET','POST'])
def patient_dispense_dietary_supplement(request):
    if request.method == "POST":
        data=json.loads(request.body)
        print(data)
        supplement=dispensed_patient_dietary_supplement(data['case_number'],data['serial_code'],data['quantity'],data['amount'])
    return Response(supplement)
@api_view(['GET','POST'])
def create_patient_dietary_supplement(request):
    if request.method =="POST":
        data=json.loads(request.body)
        dietary_ivemtory=customers_inventory_sales(data['telephone'],data['serial_code'],data['quantity'],1)
        return Response(dietary_ivemtory)



'''
laboratory details
'''

@api_view(['GET','POST'])
def view_laboratory_list(request):
    lab_test=view_lab_test_cost()
    return Response(lab_test)

@api_view(['GET','POST'])
def create_laboratory_test_details(request):
    if request.method=="POST":
       data=json.loads(request.body)
       print(data['lab_test'],data['price'])
       lab_test=create_lab_test_details(data['lab_test'],data['price'])
       #lab_test=create_lab_test_details(['maleria','yellow fever','typhoid','blood'],[120.00,200.00,150.00,100.09])
       return Response(lab_test)

@api_view(['GET','POST'])
def view_laboratory_test_details(request,lab_code):
    lab_details=view_lab_test_cost_details(lab_code)
    return Response(lab_details)

@api_view(['GET','POST'])
def edit_laboratory_details(request):
    if request.method == "POST":
       data=json.loads(request.body)
       print(data)
       edit_lab=edit_lab_test_details(data['serial_code'],data['cost'],data['test_type'])
       return Response(edit_lab)

'''
patient laboratory codes
'''
@api_view(['GET','POST'])
def view_all_waiting_patient_laboratory(request):
    patients=view_waiting_patient_lab_test()
    return Response(patients)
@api_view(['GET','POST'])
def patient_laboratory(request,case_number):
    records=view_patient_lab_records(case_number)
    return Response(records)

@api_view(['GET','POST'])
def interperate_patient_lab_details(request):
    if request.method == "POST":
        data=json.loads(request.body)
        #print(data)
        results_interperations=update_test_results(data['case_number'],data['serial_code'],data['results'],1)
        print(results_interperations,' hello ')
        return Response(results_interperations)

@api_view(['GET','POST'])
def patient_lab_payment(request):
    if request.method == "POST":
        data=json.loads(request.body)
        
        status=make_lab_test_payment(data['case_number'],data['amount'])
        return Response(status)

@api_view(['GET','POST'])
def create_outside_lab_test_cases(request):
    lab=create_outside_lab_test('name','telephone','lab_file_photo',['lab_test_list'],'user_id')
    return Response(lab)


@api_view(['GET','POST'])
def interpertae_outside_lab_results(request):
    lab_results=input_lab_test_result('case_number',['lab_test_list'],['results'])
    return Response(lab_results)


@api_view(['GET','POST'])
def daily_inventory_sales(request):
    daily_supplement=daily_supplements_sales()
    return Response(daily_supplement)

def daily_sales_details(request,serial_code):

    daily_sales_report=daily_supplements_sales_details(serial_code)
    return Response(daily_sales_details)


@api_view(['GET','POST'])
def generate_general_sales_reports(request):
    """
    if request.method == "POST":
        data=json.loads(request.body)
        generate_report=generate_supplement_report(data['start_date'],data['end_date'])
        return Response(generate_report)
    """
    generate_report=generate_supplement_report('2023-12-05','2024-04-05')
    return Response(generate_report)

@api_view(['GET','POST'])
def general_supplement_sales_report(request):
    if request.method == "POST":
        data=json.loads(request.body)
        generate_supplement_reports=generate_supplements_dietary_reports(data['serial_code'],data['start_date'],data['end_date'])
        return Response(generate_supplement_reports)


@api_view(['GET','POST'])
def daily_supplement_sales_report(request):
    if request.method == "POST":
         data=json.loads(request.body)
         reports=daily_supplements_sales_details(data['serial_code'])
         return Response(reports)
