from ..models import Customer, Patient_Medical_History_Records,Customer_Inventory_Records,Customer_Inventory_Records_Details,Dietary_Sale_Inventory_Table,Dietary_Supplementary,Dietary_Supplement_Stocking_Details,Dietary_Supplementary_Details,Patient_Medical_Diagnosis_Records,Patient_Dietary_Supplementary_Records,Patient_Dietary_Supplementary_Records_Details,Dietary_Supplement_Dispenser_Records
from django.db.models.functions import LPad
from django.contrib.auth.models import User
from django.db.models import Count ,F,Q,Sum,Value
from datetime import datetime
from .sms import smscalls

'''
1. view all supplement
3. view patient supplement details and history
3. dispense patient dietary supplements
4. view all supplement sales history details
5. view all supplement that needs to be stocked
6. create dietary and update dietary 
'''





def view_dietary_list():
    '''
    view all dietary supplement list
    '''
    return Dietary_Supplementary.objects.filter(quatity_in_stocked__gt=10)

def  deitaryItemsStocking():
     '''
       all items that needs tob stocks
     '''
     return Dietary_Supplementary.objects.filter(quatity_in_stocked__lt=10)

def getDietarySupplement(serial_code):
    data=[]
    dietary=supplement_items(serial_code)
    for supplemt in dietary:
        data.append({'serial_code':supplemt.serial_code,'supplement':supplemt.supplement,'cost_per_price':supplemt.price})
    #print(data)
    return data
def filterDietarySupplement(serial_code):
    data=[]
    for supplement in range(len(serial_code)):
        supplements=supplement_items(serial_code[supplement])
        for items in supplements:
            data.append({'serial_code':items.serial_code,'supplement':items.supplement,'cost_per_price':items.price})
    return data

def supplement_items(serial_code):
    return Dietary_Supplementary.objects.filter(serial_code=serial_code)
def get_dietary_supplement(dietary_code):
     '''
       get a particular dietary item using it particular serial code
     '''

     return Dietary_Supplementary.objects.get(serial_code= dietary_code)

def view_patient_dietary_supplements():
    '''
     list of patients waiting for their dietary supplement to be dispensed to them
    '''
    data=[]
    view_patient_supplement = Patient_Dietary_Supplementary_Records.objects.filter(patient__dietary_prescription_request=True,patient__dietary_dispensed_status=False,patient__patient__checked_in=True,patient__patient__checked_out=False)
    for patient_supplement in view_patient_supplement:
        data.append({'patient_name':patient_supplement.patient.patient.patient.patient.first_name+' '+patient_supplement.patient.patient.patient.patient.last_name,'case_number':patient_supplement.patient.patient.case_number,'totalCost':patient_supplement.total_cost})
    return data
def view_patient_dispenary(case_number,user_id):
    '''
    list of all patient dispensary records
    list of patient dietary supplement wth cost and quantity
    patient dietary details
    '''
    #check if patient dispensar exis
    dietary_dispenser_checks=Dietary_Supplement_Dispenser_Records.objects.filter(patient__patient__patient__case_number=case_number,dispenser=user_id)
    get_patient_dietary=get_patient_dietary_details(case_number)
    #print(get_patient_dietary.id)
    if not dietary_dispenser_checks.exists():
        '''
         create patient dispenser obbject model and recor the function view patient dispensary
        '''
        patient_dispenser=Dietary_Supplement_Dispenser_Records.objects.create(patient=Patient_Dietary_Supplementary_Records.objects.get(pk=get_patient_dietary.id),dispenser=User.objects.get(pk=user_id))
        patient_dispenser.save()
        return view_patient_dispenary(case_number,user_id)
    else:
        #print(get_patient_dietary.patient.id)
        dietary=get_patient_dietary_details_records(get_patient_dietary.patient.id)
        patient_dietary_record=[{'patient':get_patient_dietary.patient.patient.patient.patient.first_name+' '+get_patient_dietary.patient.patient.patient.patient.last_name,'case_number':get_patient_dietary.patient.patient.case_number,'card_number':get_patient_dietary.patient.patient.patient.card_number,'total_cost':get_patient_dietary.total_cost,'date_dispenser':get_patient_dietary.date_released,'date_prescribe':get_patient_dietary.date_recieved,'payment_status':get_patient_dietary.payment_status,'dispensed_status':get_patient_dietary.date_released,'discount_rate':get_patient_dietary.discount_rate,'discount_amount':get_patient_dietary.discount_amount,'discount_status':get_patient_dietary.discount_status}]
        return {'patient_dietary_history_list':view_patient_dietary_supplement_history_records(get_patient_dietary.patient.patient.patient.card_number),'patient_dietory_records':patient_dietary_record,'patient_dietary_supplement_list':dietary}
        
        

def view_patient_dietary_supplement_history_records(patient_card_number):
    '''
    list all patient dietary supplement records of Patient
    '''
    data=[]
    patient_dietary_records=Patient_Dietary_Supplementary_Records.objects.filter(patient__patient__patient__card_number=patient_card_number,payment_status=True,dietary_supplement_dispense_viewed=True)
    for records in patient_dietary_records:
      
        data.append({'case_number':records.patient.patient.case_number,'date_prescribe':records.date_recieved,'date_dispensed':records.date_released,'dispnsed_status':records.patient.dietary_dispensed_status,'payment_status':records.payment_status})

    return data

def get_patient_dietary_details(patient_case_number):
    '''
      get a patient supplement record based on the patient case number
    '''
    return Patient_Dietary_Supplementary_Records.objects.get(patient__patient__case_number=patient_case_number)
 
    

def get_patient_dietary_details_records(patient_dietary_id):
    '''
    get all patient supplement dietary based on the patient supplement records id
    '''
 
    data=[]
    patient_dietary_list=Patient_Dietary_Supplementary_Records_Details.objects.filter(patient__patient__id=patient_dietary_id)
   
    for dietary in patient_dietary_list:
        
        data.append({'dietary':dietary.dietary_supplement.supplement,'dietary_code':dietary.dietary_supplement.serial_code,'cost':dietary.cost,'quantity_bought':dietary.quantity})
   
    return data




def dispensed_patient_dietary_supplement(patient_case_number,dietary_code,quantity,amount_paid):
    #first get  patient dietary supplemnt
    patient_dietary_record=get_patient_dietary_details(patient_case_number)
    total=0
    #print('hello')
    for items in range(len(dietary_code)):
        dispense_patient_dietary=Patient_Dietary_Supplementary_Records_Details.objects.get(patient__patient__patient__case_number=patient_case_number,dietary_supplement__serial_code=dietary_code[items])
        price_per_unit=dispense_patient_dietary.dietary_supplement.price*int(quantity[items])
        total+=dispense_patient_dietary.dietary_supplement.price*int(quantity[items])
        #print(dispense_patient_dietary.dietary_supplement.serial_code,' ',dispense_patient_dietary.dietary_supplement.price,' ',price_per_unit,'  ',int(quantity[items]))
    #print(total)
    
    #print('balance ',balance)
    #print('balance')
    if patient_dietary_record.discount_status == True :
        #print('ok')
        discount=total*(100-patient_dietary_record.discount_rate)/100
        balance=float(discount)-float(amount_paid)
        
        if balance == 0.00:
           #print(discount,balance,total)
           
           for items in range(len(dietary_code)):
               #print(items)
               print('helloo',dietary_code[items],quantity[items])
               
               dispense_patient_dietary=Patient_Dietary_Supplementary_Records_Details.objects.get(patient__patient__patient__case_number=patient_case_number,dietary_supplement__serial_code=dietary_code[items])
               dispense_patient_dietary.quantity=quantity[items]
            
               dieatry_serial_code=dispense_patient_dietary.dietary_supplement.serial_code 
               #print(dieatry_serial_code,"fine babes")
               dispense_patient_dietary.total_cost=dispense_patient_dietary.cost * int(quantity[items])
               dispense_patient_dietary.save()
               supplement_list=get_dietary_supplement(dietary_code[items])
               #print(supplement_list)
               inventory_sales=Dietary_Sale_Inventory_Table.objects.create(dietary=Dietary_Supplementary.objects.get(pk=supplement_list['id']),quantity=quantity[items],cost_per_unit=supplement_list['price'])
            
               inventory_sales.save()
               update_supplement_dietary_quantity(dietary_code[items],quantity[items])
               #print(supplement_list['id'])
           dietary_updates=status_updates(patient_case_number)
           total_costs=totalsupplementCost(patient_case_number,total)
           mediac_record_update=patient_medical_dietary_records(patient_case_number)
           checkout_patient=checkoutPatien(patient_case_number)
           if dietary_updates == True and mediac_record_update== True and total_costs==True and checkout_patient==True:
                  pds=Patient_Medical_Diagnosis_Records.objects.get(patient__case_number=patient_case_number)
                  messages='Hi {},payment of GHS {} recieved for supplement.\nbalance {}\n.invoice {}\n.AGADARKO\nAdmin'.format(pds.patient.patient.patient.first_name,amount_paid,balance,patient_case_number)
                  #smscalls(messages,pds.patient.patient.patient.telephone)
                  return {'status':'success','message':'dietary supplements dispensed'}                         
           else:
                 return {'status':'error','message':'could not dispense dietary supplement'}
               
            
        else:
                 return  {'status':'error','message':'insufficient credits'}
                
    
    else:
        balance=float(total)-float(amount_paid)
        if balance == 0.00:
        
           for items in range(len(dietary_code)):
               #supplement_list=get_dietary_supplement(dietary_code[items])
               #print('piplo',supplement_list)
               #update_supplement_dietary_quantity(dietary_code[items],quantity[items])
               #print(items)
               #print('hello ',dietary_code[items],quantity[items])
               #print('pile',dispense_patient_dietary.cost,' ' , int(quantity[items]),' ',dispense_patient_dietary.cost * int(quantity[items]),supplement_list['price'])
               
               dispense_patient_dietary=Patient_Dietary_Supplementary_Records_Details.objects.get(patient__patient__patient__case_number=patient_case_number,dietary_supplement__serial_code=dietary_code[items])
               dispense_patient_dietary.quantity=quantity[items]
            
               dieatry_serial_code=dispense_patient_dietary.dietary_supplement.serial_code 
               #print(dieatry_serial_code,"fine babes")
               dispense_patient_dietary.total_cost=dispense_patient_dietary.cost * int(quantity[items])
               dispense_patient_dietary.save()
               supplement_list=get_dietary_supplement(dietary_code[items])
               #print(supplement_list)
               inventory_sales=Dietary_Sale_Inventory_Table.objects.create(dietary=Dietary_Supplementary.objects.get(pk=supplement_list['id']),quantity=quantity[items],cost_per_unit=supplement_list['price'])
            
               inventory_sales.save()
               update_supplement_dietary_quantity(dietary_code[items],quantity[items])
               #print(supplement_list['id'])
           dietary_updates=status_updates(patient_case_number)
           total_costs=totalsupplementCost(patient_case_number,total)
           mediac_record_update=patient_medical_dietary_records(patient_case_number)
           checkout_patient=checkoutPatien(patient_case_number)
           if dietary_updates == True and mediac_record_update== True and total_costs==True and checkout_patient==True:
                  pds=Patient_Medical_Diagnosis_Records.objects.get(patient__case_number=patient_case_number)
                  messages='Hi {},payment of GHS {} recieved for supplement.\nbalance {}\n.invoice {}\n.AGADARKO\nAdmin'.format(pds.patient.patient.patient.first_name,amount_paid,balance,patient_case_number)
                  #smscalls(messages,pds.patient.patient.patient.telephone)
                  return {'status':'success','message':'dietary supplements dispensed'}                         
           else:
                 return {'status':'error','message':'could not dispense dietary supplement'}
               
        else:
                 return  {'status':'error','message':'insufficient credits'}
    

    '''
    dispensing dietary supplement to paitents
    1. loop through all the dietary supplemnt prescribe by the docot to the patient in the Patient Dietary Supplementary Records Details model
    2. each dietary supplemnet prescribe by the doctor to the patient will have default quantity of one
    3. update of the quantity of patient supplement details
    4. update the total quantity of each dietary supplement after dispensing patient supplementary dietary
    5. update patient supplement dietary request view and dietary supplement dispense view to True  
    '''
    '''
    for items in range(len(dietary_code)):
        dispense_patient_dietary=Patient_Dietary_Supplementary_Records_Details.objects.get(patient__patient__patient__case_number=patient_case_number,dietary_supplement__serial_code=dietary_code[items])
        dispense_patient_dietary.quantity=quantity[items]
        dieatry_serial_code=dispense_patient_dietary.dietary_supplement.serial_code  
        dispense_patient_dietary.total_cost=dispense_patient_dietary.cost * quantity[items]
     
        dispense_patient_dietary.save()
        supplement_list=get_dietary_supplement(dietary_code[items])
        inventory_sales=Dietary_Sale_Inventory_Table.objects.create(dietary=Dietary_Supplementary.objects.get(pk=supplement_list.id),quantity=quantity[items],cost_per_unit=supplement_list.price)
        inventory_sales.save()
        update_supplement_dietary_quantity(dieatry_serial_code,quantity[items])
    dietary_updates=status_updates(patient_case_number)
    total_costs=totalsupplementCost(patient_case_number)
    mediac_record_update=patient_medical_dietary_records(patient_case_number)
    if dietary_updates == True and mediac_record_update== True and total_costs==True:
        return {'status':'dietary supplements dispensed'}
    '''


def updateDietaryItems(seriakl_code,quantity):
    pass
def checkoutPatien(case_number):
        check_out_patient=Patient_Medical_History_Records.objects.get(case_number=case_number)
        check_out_patient.checked_out=True
        check_out_patient.save()
        return True




def totalsupplementCost(case_number,total_cost):
    update_dietary_cost=Patient_Dietary_Supplementary_Records.objects.get(patient__patient__case_number=case_number)
    if update_dietary_cost.discount_status == True:
        if int(update_dietary_cost.discount_rate) > 0:
            discount_cost=float(total_cost)*(100-int(update_dietary_cost.discount_rate))/100
    else:
        discount_cost=total_cost
    update_dietary_cost.amount_paid=total_cost
    update_dietary_cost.discount_amount=discount_cost
    update_dietary_cost.payment_status=True
    update_dietary_cost.save()
    return True

    '''
    patient_dietary_list=Patient_Dietary_Supplementary_Records_Details.objects.filter(patient__patient__patient__case_number=case_number)
    total_cost=0
    for patient_dietary in patient_dietary_list:
        total_cost+=patient_dietary.total_cost
    update_dietary_cost=Patient_Dietary_Supplementary_Records.objects.get(patient__patient__patient__case_number=case_number)
    update_dietary_cost.amount_paid=total_cost
    update_dietary_cost.payment_status=True
    update_dietary_cost.save()
    return True
    '''

def status_updates(patient_case_number):
    '''
    updating patient request and dispense view in the Patient_Dietary_Supplementary_Records model to true
    '''
    patient_dietary_status_updates=Patient_Dietary_Supplementary_Records.objects.get(patient__patient__case_number=patient_case_number)
    patient_dietary_status_updates.dietary_supplement_dispense_viewed=True
    patient_dietary_status_updates.dietary_supplement_request_view=True
    patient_dietary_status_updates.save()
    return True

def patient_medical_dietary_records(patient_case_number):
    '''
    updates patients medical diagnosis dietary dispensed status to True
    '''
    patient_dieatry_updates=Patient_Medical_Diagnosis_Records.objects.get(patient__case_number=patient_case_number)
    patient_dieatry_updates.dietary_dispensed_status=True
    patient_dieatry_updates.save()
    return True

def update_supplement_dietary_quantity(dietary_serial_code,quantity):
    print('hit',dietary_serial_code,quantity)
    '''
    dietary_quantity_update=Dietary_Supplementary.objects.get(serial_code=dietary_serial_code)
    dietary_quantity_update.quatity_in_stocked=int(dietary_quantity_update.quatity_in_stocked)-int(quantity)
    dietary_quantity_update.save()
    '''


def sales_record(case_number,amount):
    pass

'''
creating dietary supplement and stocking
'''
def viewSupplementDietary():
    pass
def create_dietary_supplement_details(supplement_name,cost,quantity_stocked,photo,stocked_by):
     '''
     creating dietary supplement
     
     '''
     #check if the quantity of dietary supplemented being created is greater than 0 
     if quantity_stocked > 0:
         #get the name of the dietary supplement in the dietary supplement
         get_dieatry_supplement_name=Dietary_Supplementary.objects.filter(supplement=supplement_name)
         if not get_dieatry_supplement_name.exists():
             #if the name doesn't exist create new dietary supplement
             create_dietary_supplement=Dietary_Supplementary.objects.create(supplement=supplement_name,quatity_in_stocked=quantity_stocked,price=cost,photo=photo)
             create_dietary_supplement.save()
             #get the last supplement dietary id
             supplement_id=Dietary_Supplementary.objects.latest("id")
             #update supplementary dietary code
             supplement_serial_code=create_supplement_serial_code(supplement_id.id)
             #create dietary supplement details this
             dietary_stocking=create_supplement_details(supplement_id.id,quantity_stocked,cost,stocked_by)

             if supplement_serial_code == True and dietary_stocking == True:
                 return {'status':'success','message':'supplement dietary created successful'}
             else:
                 return {'status':'error','message':'could not create supplement dietary'}
     else:
         return {'status':'error','message':"quantity less than 10"}

def create_supplement_serial_code(supplement_id):
    generate_serial_code=Dietary_Supplementary.objects.get(pk=supplement_id)
    generate_serial_code.serial_code=LPad('id',8,Value(0))
    generate_serial_code.save()
    return True

def create_supplement_details(supplement_id,quantity_stocked,cost,stocked_by):
    
    if quantity_stocked > 0:
        supplementary_stocked_details=Dietary_Supplementary_Details.objects.create(dietary=Dietary_Supplementary.objects.get(pk=supplement_id),quantity=quantity_stocked,quantity_stocked=quantity_stocked)
        supplementary_stocked_details.save()
        supplementary_stocked_details_id=Dietary_Supplementary_Details.objects.latest('id')
        dietary_stock_history_tracking=create_dietary_stocking_history(supplementary_stocked_details_id.id,quantity_stocked,quantity_stocked,cost,cost,quantity_stocked,stocked_by)
        return dietary_stock_history_tracking
    else:
        return False 
'''
dietary stocking
'''
def create_dietary_stocking_history(supplemetary_supplement_id,new_quantity,old_quantity,old_price,new_price,old_stocked_quantity,user_id):
    dietary_supplement_stocking=Dietary_Supplement_Stocking_Details.objects.create(dietary=Dietary_Supplementary_Details.objects.get(pk=supplemetary_supplement_id),new_quantity_stocked=new_quantity,old_quantity_stocked=old_quantity,current_cost=new_price,old_cost=old_price,quantity_at_the_time_of_stocking=old_stocked_quantity,stocked_by=User.objects.get(pk=user_id))
    dietary_supplement_stocking.save()
    return True


def update_dietary_details(supplement_name,dietary_code):
    dietary_supplement=Dietary_Supplementary.objects.get(serial_code=dietary_code)
    dietary_supplement.supplement=supplement_name
    dietary_supplement.save()
    return {'status':'success',"success":'supplement update successful'}

def dietary_supplement_stocking_details_history():
    #return all dietary supplement dietaries
    return Dietary_Supplementary_Details.objects.all()


def dietaryStockingDetails(serial_code):
    return {'history_details':viewStockingSupplementDietaryList(serial_code),'supplement_details':getSupplementDetails(serial_code)}

def viewStockingSupplementDietaryList(serial_code):
    data=[]
    supplement=Dietary_Supplement_Stocking_Details.objects.filter(dietary__dietary__serial_code=serial_code)

    for stocks in supplement:
        data.append({'date_stocked':stocks.date_stocked,'previous_price':stocks.old_cost,'quantity_at_the_time_of_stocking':stocks.quantity_at_the_time_of_stocking,'quatity_stocked':stocks.new_quantity_stocked,'previous_quantity_stocked':stocks.old_quantity_stocked,'stocked_by':stocks.stocked_by.first_name+' '+stocks.stocked_by.last_name})
    return data

def getSupplementDetails(dietary_code):
    dietary_supplement=Dietary_Supplementary.objects.get(serial_code=dietary_code)
    return {'photo':dietary_supplement.photo.url,'serial_code':dietary_supplement.serial_code,'quantity':dietary_supplement.quatity_in_stocked,'supplement':dietary_supplement.supplement,'price':dietary_supplement.price}


def dietary_pending_for_restock():
    data=[]
    supplements= Dietary_Supplementary.objects.filter(quatity_in_stocked__lte=10)

    for supplement in supplements:
        data.append({'suppleent':supplement.supplement,'quantity':supplement.quatity_in_stocked,'price':supplement.price})

    return data


def update_dietary_details_stock(serial_code,quantity,price,stock_by):
    get_dietary_supplements=get_dietary_supplement(serial_code)
    get_last_dieatry_quantity_stocked=Dietary_Supplementary_Details.objects.filter(dietary__serial_code=serial_code).order_by('-id')[0]
    total_quantity_stocked=int(get_dietary_supplements['quantity_in_stock'])+int(quantity)
    old_quantity_in_stock=get_last_dieatry_quantity_stocked.quantity_stocked
    quantity_at_the_time_of_stocking=get_dietary_supplements['quantity_in_stock']
    stocking_history=update_dietary_stock_quantity_history(get_dietary_supplements['id'],total_quantity_stocked,quantity,old_quantity_in_stock,quantity_at_the_time_of_stocking,price,get_dietary_supplements['price'],stock_by)
    if stocking_history == True:
        price_quantity_update=update_dietary_cost_price(serial_code,quantity,price)
        if price_quantity_update == True:
            return {'status':'success','message':'supplements details stocked successful'}
    else:
        return {'status':'error','message':'suppleent could not stocked succesful'}


def update_dietary_stock_quantity_history(dietary_id,total_quantity_stock,new_quantity,old_quantity,quantity_at_the_time_stocking,new_price,old_price,stock_by):
    if int(new_quantity) > 0:
        stocking_dietary=Dietary_Supplementary_Details.objects.create(dietary=Dietary_Supplementary.objects.get(pk=dietary_id),quantity=total_quantity_stock,quantity_stocked=new_quantity)
        stocking_dietary.save()
        stocking_dietary_id=Dietary_Supplementary_Details.objects.latest('id')

        stocking_history=create_dietary_stocking_history(stocking_dietary_id.id,new_quantity,old_quantity,old_price,new_price,quantity_at_the_time_stocking,stock_by)
        if stocking_history == True:
            return True
        else:
            return False
        

def update_dietary_cost_price(serial_code,quantity,cost):
    dietary=Dietary_Supplementary.objects.get(serial_code=serial_code)
    dietary.quatity_in_stocked+=int(quantity)
    dietary.price=cost
    dietary.save()
    return True

def get_dietary_supplement(serial_code):
    supplement=Dietary_Supplementary.objects.get(serial_code=serial_code)

    return {'supplement':supplement.supplement,'quantity_in_stock':supplement.quatity_in_stocked,'serial_code':supplement.serial_code,'price':supplement.price,'id':supplement.id}


'''
outsiders sales inventory

'''

def customers_inventory_sales(telephone,dietary_supplement,quantity,discount_rate,receiver):
    #check if customer exist in database
    #if customer exist in database continue with the transaction
    #if customer does not exist in database create customer inventory 
    check_customer=Customer.objects.filter(telephone=telephone)
    if not check_customer.exists():
        customer=Customer.objects.create(telephone=telephone)
        customer.save()
        customer_id=Customer.objects.latest('id')
        customer_inventory=customer_inventory_sales_details(customer_id.id,dietary_supplement,quantity,discount_rate,receiver)
        if customer_inventory == True:
            #message='invoice:'
            return {"status":'success','success':"Transaction successful"}

        else:
            return {'status':'error','error':"Transaction Failed"}
    else:
        customer_id=Customer.objects.get(telephone=telephone)
        customer_inventory=customer_inventory_sales_details(customer_id.id,dietary_supplement,quantity,discount_rate,receiver)
        if customer_inventory == True:
            return {'status':'success','success':"Transaction successful"}
        else:
            return {'status':'error','error':"Transaction Failed"}
def customer_invoive(customer_id):
    stack=[]
    inventory_details=Customer_Inventory_Records.objects.get(pk=customer_id)
    customer_inventory_details=Customer_Inventory_Records_Details.objects.filter(customer__id=inventory_details.id)
    for details in customer_inventory_details:
        stack.append([details.dietary_supplement.supplement])

def customer_inventory_sales_details(customer_id,dietary_supplement,quantity,discount_rate,receiver):

    #count total items in the list
    total_dietary_supplements_items=len(dietary_supplement)
    total_quqatity_of_dietary_supplement_items=sum(quantity)
    total_cost=0

    for items in range(len(dietary_supplement)):
        dietary_item=supplement_items(dietary_supplement[items])
        for item in dietary_item:
            total_cost_per_unit=float(item.price)*quantity[items]
            total_cost+=float(total_cost_per_unit)
    #print(' hello world ',total_cost,dietary_supplement,quantity)
    #customer_inventory_id.id

    #sales_inventory=customer_inventory_sales_record(customer_inventory_id.id,dietary_supplement,quantity)
    #return sales_inventory
    discount_cost=0
    if int(discount_rate)>0:
        discount_cost=total_cost*[(100-discount_rate)/100]
        discount_status=True
    else:
        discount_cost=total_cost
        discount_status=False
    customers_inventory=Customer_Inventory_Records.objects.create(customer=Customer.objects.get(pk=customer_id),total_dietary_supplement_items=total_dietary_supplements_items,total_quantity_of_each_supplement_item=total_quqatity_of_dietary_supplement_items,total_cost=discount_cost,discount_status=discount_status,discount_rate=discount_rate,discount_amount=discount_cost,payment_received_by=User.objects.get(pk=receiver))
    customers_inventory.save()
    customer_inventory_id=Customer_Inventory_Records.objects.latest('id')
    generate_inventory_number=inventory_number(customer_inventory_id.id)
    sales_inventory=customer_inventory_sales_record(customer_inventory_id.id,dietary_supplement,quantity)

    if sales_inventory == True and generate_inventory_number == True:
        return True
    
    return True

def inventory_number(inventory_id):
    inventory=Customer_Inventory_Records.objects.get(pk=inventory_id)
    inventory.inventory_number=LPad('id',8,Value(0))
    inventory.save()
    return True

def customer_inventory_sales_record(customer_inventory_id,dietary_supplement,quantity):
    for items in range(len(dietary_supplement)):
        #print(' dietary and quantity ',dietary_supplement,quantity)
        supplement_list=get_dietary_supplement(dietary_supplement[items])
        #print('am here ',supplement_list['supplement'],supplement_list['serial_code'],supplement_list['id'])
        
        #print('am here ',supplement_list)
        
        update_supplement_dietary_quantity(dietary_supplement[items],quantity[items])

        customer_inventory=Customer_Inventory_Records_Details.objects.create(customer=Customer_Inventory_Records.objects.get(pk=customer_inventory_id),dietary_supplement=Dietary_Supplementary.objects.get(pk=supplement_list['id']),cost=supplement_list['price'],quantity_purchased=quantity[items])
        customer_inventory.save()

        inventory_sales=Dietary_Sale_Inventory_Table.objects.create(dietary=Dietary_Supplementary.objects.get(pk=supplement_list['id']),quantity=quantity[items],cost_per_unit=supplement_list['price'])
        inventory_sales.save()
    
    return True


'''
   dientry supplement inventory
'''

def  total_number_of_supplement():
    data=[]
    supplememnt=Dietary_Supplementary.objects.filter(quatity_in_stocked__gt=10)

    for supplements in supplememnt:
        data.append({"supplement":supplements.supplement,'quantity':supplements.quatity_in_stocked})

    return data

def  total_number_of_quantity():
    data=[]
    supplements=Dietary_Supplementary.objects.filter(quatity_in_stocked__gt=10)
    for supplement in supplements:
        data.append({'quantity':supplement.quatity_in_stocked})

    return data


def daily_supplements_sales():
    current_date="{}-{}-{}".format(datetime.now().year,datetime.now().month,datetime.now().day)
    sales=Dietary_Sale_Inventory_Table.objects.values('dietary__supplement','dietary__id','dietary__serial_code','dietary__quatity_in_stocked','dietary__price').annotate(total_quantity=Sum('quantity'),total_profit_crew=Sum('total_cost')).filter(date_purschaesd=current_date)
    return sales

def daily_supplements_sales_details(serial_code):
    data=[]
    supplement=Dietary_Supplementary.objects.get(serial_code=serial_code)
    current_date="{}-{}-{}".format(datetime.now().year,datetime.now().month,datetime.now().day)
    data.append({'supplement_details':{'serial_code':supplement.serial_code,'supplement':supplement.supplement,'quantity':supplement.quatity_in_stocked,'cost':supplement.price,'date':current_date}})
    
    supplement_reports=Dietary_Sale_Inventory_Table.objects.filter(dietary__serial_code=serial_code,date_purschaesd=current_date)
    supplement_reports_details=[]
    for reports in supplement_reports:
        supplement_reports_details.append({'reports':{'quantity':reports.quantity,'cost_per_price':reports.cost_per_unit,'total_cost':reports.total_cost}})
    data.append(supplement_reports_details)

    return data

def generate_supplement_report(start_date,end_date):
    #sales=Dietary_Sale_Inventory_Table.objects.values('dietary__supplement','dietary__id','dietary__serial_code','dietary__quatity_in_stocked','dietary__price').annotate(total_quantity=Sum('quantity'),total_profit_crew=Sum('total_cost'))
    #sales=Dietary_Sale_Inventory_Table.objects.values('dietary__supplement','dietary__id','dietary__serial_code','dietary__quatity_in_stocked','dietary__price').annotate(total_quantity=Sum('quantity'),total_profit_crew=Sum('total_cost')).filter(date_purschaesd__gte=start_date,date_purschaesd__lte=end_date)
    #return sales
    
    data=[]
    supplement_reports=Dietary_Sale_Inventory_Table.objects.filter(date_purschaesd__gte=start_date,date_purschaesd__lte=end_date)
    for supplement in supplement_reports:
        data.append({'data_purchased':supplement.date_purschaesd,'serial_code':supplement.dietary.serial_code,'supplement':supplement.dietary.supplement,'cost_per_unit':supplement.cost_per_unit,'quantity_purchased':supplement.quantity,'total_cost':supplement.total_cost})
    print(data,' hello ')
    return data 
    

def generate_supplements_dietary_reports(serial_code,end_date,start_date):

    data=[]
    supplement_reports=Dietary_Sale_Inventory_Table.objects.filter(dietary__serial_code=serial_code,date_purschaesd__gte=start_date,date_purschaesd__lte=end_date)
    #print(supplement)
    for supplement in supplement_reports:

        data.append({'date_purchased':supplement.date_purschaesd,'cost_per_unit':supplement.cost_per_unit,'supplement':supplement.dietary.supplement,'quantity':supplement.quantity,'total_cost':supplement.total_cost})
    return data



'''

view all dietary transaction for today and a particular time frame
view list dietary supplement quantity

'''