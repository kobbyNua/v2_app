from ..models import Hospital,Region,Staff,OPD_Vital,HospitalCardFees,HospitalCardFeesLogs,HospitalCardRenewalFees,HospitalCardRenewalFeesLogs
from django.contrib.auth.models import User,Group
from django.db.models import Count ,F,Q,Sum,Value
from django.db.models.functions import LPad
from  rest_framework.authtoken.models import Token
import json




'''
create and view regions and capital cities
'''

def view_regions():
    data=[]
    regions=Region.objects.all().order_by('region')
    for region in regions:
        data.append({'region':region.region.title(),'id':region.id})
    return data
def check_region(region):
	regions=Region.objects.filter(region=region)
	if not regions.exists():
		created_region=create_region(region)
		return created_region
	else:
		return {'status':'error','error':'region already created'}
	   
	

  
        

def create_region(region):
    regions=Region.objects.create(region=region)
    regions.save()
    region_id=Region.objects.latest('id')
    return {"status":'success','success':'region created'}


def view_hospital():
	data=[]
	hospitals=Hospital.objects.all()
	for hospital in hospitals:
		data.append({'hospital':hospital.name,'administrator':hospital.adminstrator.first_name+' '+hospital.adminstrator.last_name,'telephone':hospital.telephone,'email':hospital.adminstrator.email,'region':hospital.region.region,'town':hospital.town})
	return data

def  create_hospital_details(name,user,email,telephone,town,regions,admin_telephone):

		get_hospital_name=Hospital.objects.filter(name=name)
		if not get_hospital_name.exists():
			create_hospital=Hospital.objects.create(name=name,adminstrator=User.objects.get(pk=user),telephone=telephone,email=email,town=town,region=Region.objects.get(pk=regions))
			create_hospital.save()
			hospital_id=Hospital.objects.latest("id")
			check_admin_hospital=Staff.objects.filter(staff=user,hospital=hospital_id.id)
			if not check_admin_hospital.exists():
				hospital_staffs(user,admin_telephone,hospital_id.id)
				return {"status":'success','success':'hospital details created'}
			return {"status":'success','success':'hospital details created'}
		else:

			return {"status":'error','error':'hospital details already exists'}

def getHospital_details(user_id):
        hosptial_details=Hospital.objects.get(adminstrator=user_id)
        return {"hospital":hosptial_details.name,'administrator':hosptial_details.adminstrator.first_name+' '+hosptial_details.adminstrator.last_name,'telephone':hosptial_details.telephone,'email':hosptial_details.adminstrator.email,'region':hosptial_details.region.region,'town':hosptial_details.town}

def allSuperUser():
	get_super_user=User.objects.filter(is_superuser=True)
	data=[]

	for users in get_super_user:
		print(users.username)
		check_super_users=Staff.objects.filter(staff__id=users.id)
		if not check_super_users.exists(): 
			super_users=User.objects.get(id=users.id)
			data.append({'name':super_users.first_name+' '+super_users.last_name,'email':super_users.email,'username':super_users.username,'id':super_users.id})
		#or super_user in check_super_users:
	    
	print("am here ",data)
	return data



def view_group():
	data=[]
	groups=Group.objects.all()
	for group in groups:
		data.append({'groups':group.name,'id':group.id})
	return data
def create_groups(group_name):
 
	for groups in range(len(group_name)):
		
		
		check_groups=Group.objects.filter(name=group_name[groups])
		if not check_groups.exists():
			#print(group_name[groups],'each')
			group=Group.objects.create(name=group_name[groups])
			group.save()
		
	return {"status":'success','success':"groups created successfully"}




def edit_groups(new_group_name,group_id):
           group=Group.objects.get(pk=group_id)
           group.name=new_group_name
           group.save()
           return {"status":'success','success':"group edited successfully"}


def view_staffs(user_id):
	staff_hospital=Staff.objects.filter(user__id=user_id)
	print("okay got u ", staff_hospital.count())
	return {"total_staff":str(staff_hospital.count())}

def create_staff(first_name,last_name,email,username,telephone,group_id,user_id,super_user):
	check_user=User.objects.filter(Q(email=email)|Q(username=username))
	if not check_user.exists():
        
		
		if super_user == 'True':
			default_password='Password@1'
			users=User.objects.create_user(username=username,password=default_password,first_name=first_name,last_name=last_name,email=email,is_superuser=True)
			users.save()
			user_id=User.objects.latest('id')
			user=User.objects.get(pk=user_id.id)
			token=Token.objects.create(user=user)
			return {"status":'success','success':'user account created successfully','token':token.key}
		elif super_user == 'False':
			default_password='Password@1'
			hospital_info=get_user_hospital_details(user_id)
		    #hospital_info=Hospital.objects.filter(adminstrator__id=user_id)
			hospital_id=""
			users=User.objects.create_user(username=username,password=default_password,first_name=first_name,last_name=last_name,email=email)
			users.save()
			user_id=User.objects.latest('id')
			#get_user
			user=User.objects.get(pk=user_id.id)
			token=Token.objects.create(user=user)
			hospital_staffs(user_id.id,telephone,hospital_info["hospital_id"])
			for groups in range(len(group_id)):
				get_group=Group.objects.get(pk=group_id[groups])
				get_group.user_set.add(user_id.id)
			return {"status":'success','success':'user account created successfully','token':token.key}
		
		#print('type of value ',type(super_user))
		return {"status":'success','success':'user account created successfully'}
	else:
		return {"status":'error','error':'user account already exist'}
def check_super_user_status(user_id):
	#get_super_user=User_Groups.objects.filter(user__id=user_id)
	get_group=Group.objects.get(name="Root")
	get_group.user_set.add(user_id)
	return {"status":'success','success':'supper created'}




def get_staff(username):
	staff=Staff.objects.get(staff__username=username)
	return {'hospital':staff.hospital.name,'staff_name':staff.staff.first_name+' '+staff.staff.last_name,'telephone':staff.telephone,'username':staff.staff.username,'first_name':staff.staff.first_name,'last_name':staff.staff.last_name,'email':staff.staff.email,'user_id':staff.staff.id,'staff_id':staff.id}

def view_all_staffs(admin_id):
	data=[]
	#print('admin id',admin_id)
	staffs=Staff.objects.filter(hospital__adminstrator__id=admin_id)
	for staff in staffs:
		data.append({'staff_name':staff.staff.first_name+' '+staff.staff.last_name,'telephone':staff.telephone,'username':staff.staff.username,'user_id':staff.staff.id,'staff_id':staff.id,'email':staff.staff.email})
	return data
def staff_detail(email):
	staff=User.objects.get(email=email)
	return staff 
def  hospital_staffs(user_id,telephone,hospital_id):

	create_hospital_staff=Staff.objects.create(staff=User.objects.get(pk=user_id),telephone=telephone,hospital=Hospital.objects.get(pk=hospital_id))
	create_hospital_staff.save()

	#create_hospital_staff=Hospital_Staff.objects.create(staff=User.objects.get(pk=user_id),telephone=telephone,hospital=Hospital.objects.get(pk=hospital_id))
	#create_hospital_staff.save()   
def edit_staff(email,first_name,last_name,username,telephone,user_id,hostpital_staff_id):
    get_staff=User.objects.get(pk=user_id)
    get_staff.first_name=first_name
    get_staff.last_name=last_name
    get_staff.username=username
	#get_staff.email=email
    get_staff.save()

    get_hospital_staff_id = Staff.objects.get(pk=hostpital_staff_id)
    get_hospital_staff_id.telephone = telephone
    get_hospital_staff_id.save()
    return {"status":'success','success':'staff info edited'}
def change_staff_password(password,new_password,user_id):
	if password == new_password:
		staff_detail=User.objects.get(pk=user_id)
		staff_detail.set_password(new_password)
		staff_detail.save()
		return {"status":'success','success':'password change'}
	else:
	    return {"status":'error','error':'password mismatch'}
def reset_password(user_id):
	user=User.objects.get(pk=user_id)
	user.set_password('Password@1')
	return {"status":'success','success':'staff password reset'}


def get_user_details(user_id):
	return User.objects.get(pk=user_id)

def get_user_hospital_details(user_id):
	get_user=User.objects.get(pk=user_id)
	details={}
	if get_user.is_superuser:
		get_hospital_details=Hospital.objects.get(adminstrator__id=user_id)
		details.update({'user_id':user_id,"hospital_id":get_hospital_details.id})
	else:
		get_hospital_details=Staff.objects.get(staff__id=user_id)
		details.update({'user_id':user_id,'hospital_id':get_hospital_details.hospital.id})
	return details


def create_opd_vitals(opd_vitals,user_id):
	
	hospital=Hospital.objects.get(adminstrator__id=user_id)
	for vitals in range(len(opd_vitals)):
		
		check_vitals=OPD_Vital.objects.filter(vital=opd_vitals[vitals],hospital=hospital.id)
		if not check_vitals.exists():
			
			
			vital=OPD_Vital.objects.create(vital=opd_vitals[vitals],hospital=Hospital.objects.get(pk=hospital.id))
			vital.save()
			vital_id=OPD_Vital.objects.latest('id')
			generate_opd_serial_code(vital_id.id)
			
			return {"status":'success','success':"vitals created succesfully"}
			

	
		
    

def generate_opd_serial_code(opd_vital_id):
	generate_serial_code=OPD_Vital.objects.get(pk=opd_vital_id)
	generate_serial_code.serial_code=LPad('id',8,Value('0'))
	generate_serial_code.save()

def view_opd_vitals():
	data=[]
	vitals=OPD_Vital.objects.exclude(serial_code="")
	for vital in vitals:
		data.append({'vitals':vital.vital,'serial_code':vital.serial_code})
	return data
	

def get_vital_opd(vital_code):
	pass

def edit_opd_vitals():
	pass


'''
card fees
'''

def card_charges(fees_card,card_renewal_charges,user_id):
	new_card_charge=card_charges_set_up(fees_card,user_id)
	card_renewal_charge=card_renewal_charges_set_up(card_renewal_charges,user_id)
	if new_card_charge == True and card_renewal_charge == True:
		return {"status":'success','success':'card charges added'}
	else:
		return {"status":'error','error':'card charges added'}
    
        

def card_charges_set_up(fees_card,user_id):
	get_hospital=Staff.objects.get(staff__id=user_id)

	check_hospital_card_charges=HospitalCardFees.objects.filter(hospital__id=get_hospital.hospital.id)
	if not check_hospital_card_charges.exists():
		hospital_card_charges=HospitalCardFees.objects.create(card_fees=fees_card,hospital=Hospital.objects.get(pk=get_hospital.hospital.id))
		hospital_card_charges.save()
		get_charges_id=HospitalCardFees.objects.latest('id')
		logs=hospital_card_charges_id(get_charges_id.id,fees_card,user_id)
		return logs
		
	else:
		hospital_card_charges=HospitalCardFees.objects.get(hospital__id=get_hospital.id)
		hospital_card_charges.card_fees=fees_card
		hospital_card_charge_id=hospital_card_charges.id
		hospital_card_charges.save()
		logs=hospital_card_charges_id(hospital_card_charge_id,fees_card,user_id)
		return logs
	

def card_renewal_charges_set_up(card_renewal_fees,user_id):
	get_hospital=Staff.objects.get(staff__id=user_id)

	check_hospital_renewal_card_charges=HospitalCardRenewalFees.objects.filter(hospital__id=get_hospital.hospital.id)
	if not check_hospital_renewal_card_charges.exists():
		hospital_card_charges=HospitalCardRenewalFees.objects.create(card_renewal_fees=card_renewal_fees,hospital=Hospital.objects.get(pk=get_hospital.hospital.id))
		hospital_card_charges.save()
		get_charges_id=HospitalCardRenewalFees.objects.latest('id')
		logs=hospital_renewal_card_charges_id(get_charges_id.id,card_renewal_fees,user_id)
		return logs
		
	else:
		hospital_card_charges=HospitalCardRenewalFees.objects.get(hospital__id=get_hospital.id)
		hospital_card_charges.card_fees=card_renewal_fees
		hospital_card_charge_id=hospital_card_charges.id
		hospital_card_charges.save()
		logs=hospital_renewal_card_charges_id(hospital_card_charge_id,card_renewal_fees,user_id)
		return logs




def hospital_card_charges_id(hospital_card_charge_id,amount,user_id):
	logs=HospitalCardFeesLogs.objects.create(card_fees=HospitalCardFees.objects.get(pk=hospital_card_charge_id),amount_charged=amount,added_by=User.objects.get(pk=user_id))
	logs.save()
	#return {"status":'success','success':'card charges added'}
	return True


def hospital_renewal_card_charges_id(hospital_card_charge_id,amount,user_id):
	logs=HospitalCardRenewalFeesLogs.objects.create(card_fees=HospitalCardRenewalFees.objects.get(pk=hospital_card_charge_id),amount_charged=amount,added_by=User.objects.get(pk=user_id))
	logs.save()
	#return {"status":'success','success':'card charges added'}
	return True


def get_charges_details(user_id):
	return {'card_charge':get_card_chages(user_id),'card_renewal_fees':get_card_renewal_charges(user_id)}

def get_card_chages(user_id):
	get_hospital=Staff.objects.get(staff__id=user_id)

	charges=HospitalCardFees.objects.filter(hospital__id=get_hospital.hospital.id)[0]
	return {'fees':charges.card_fees}
def get_card_renewal_charges(user_id):
    get_hospital=Staff.objects.get(staff__id=user_id)
    charges=HospitalCardRenewalFees.objects.filter(hospital__id=get_hospital.hospital.id)[0]
    return {'fees':charges.card_renewal_fees}


def card_fees_log(user_id):
	return {'fees':get_card_charges_log(user_id),'review_fees':get_card_renewal_charges_log(user_id)}

def get_card_charges_log(user_id):
	get_hospital=Staff.objects.get(staff__id=user_id)
	data=[]
	logs=HospitalCardFeesLogs.objects.filter(card_fees__hospital__id=get_hospital.hospital.id)
	for fees_logs in logs:
		data.append({'amount':fees_logs.amount_charged,'date_charged':fees_logs.date_changed,'added_by':fees_logs.added_by.first_name+' '+fees_logs.added_by.last_name})
	return data

def get_card_renewal_charges_log(user_id):
	get_hospital=Staff.objects.get(staff__id=user_id)
	data=[]
	logs=HospitalCardRenewalFeesLogs.objects.filter(card_fees__hospital__id=get_hospital.hospital.id)
	for fees_logs in logs:
		data.append({'amount':fees_logs.amount_charged,'date_charged':fees_logs.date_changed,'added_by':fees_logs.added_by.first_name+' '+fees_logs.added_by.last_name})
	return data