from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
# Create your models here.

class Region(models.Model):
      '''
       various region/states within the country
      '''
      region=models.TextField(max_length=200)
class Hospital(models.Model):
      '''
        Various hospital within the country and regon
      '''
      name=models.TextField(max_length=200)
      adminstrator=models.ForeignKey(User,on_delete=models.CASCADE)
      telephone=models.TextField(max_length=200)
      email=models.EmailField(max_length=200)
      town=models.TextField(max_length=200)
      region=models.ForeignKey(Region,on_delete=models.CASCADE)

class OPD_Vital(models.Model):
     '''
        this allows the storage of vitals such as temperature,weight, and Bp
     '''
     vital=models.TextField(max_length=200)
     serial_code=models.CharField(max_length=200)
     hospital=models.ForeignKey(Hospital,on_delete=models.CASCADE)
class Staff(models.Model):
      '''
       all staffs(hospital staffers) are allocatecd to a particulated hospital

      '''
      staff=models.ForeignKey(User,on_delete=models.CASCADE)
      telephone=models.TextField(max_length=200)
      hospital=models.ForeignKey(Hospital,on_delete=models.CASCADE)


class Patient(models.Model):
      '''
        records of patient 
      '''
      first_name=models.TextField(max_length=200)
      last_name=models.TextField(max_length=200)
      date_of_birth=models.DateField()
      telephone=models.TextField(max_length=200)
      region=models.ForeignKey(Region,on_delete=models.CASCADE)
class HospitalCardFees(models.Model):
      card_fees=models.FloatField(0.00)
      hospital=models.ForeignKey(Hospital,on_delete=models.CASCADE) 
          
class HospitalCardFeesLogs(models.Model):
      card_fees=models.ForeignKey(HospitalCardFees,on_delete=models.CASCADE)
      amount_charged=models.FloatField(0.00)
      added_by=models.ForeignKey(User,on_delete=models.CASCADE)
      date_changed=models.DateField()

      def save(self,*args,**kwargs):
           self.date_changed="{}-{}-{}".format(datetime.now().year,datetime.now().month,datetime.now().day)
           super().save(*args,**kwargs)
class HospitalCardRenewalFees(models.Model):
      card_renewal_fees=models.FloatField(0.00)
      hospital=models.ForeignKey(Hospital,on_delete=models.CASCADE) 

class HospitalCardRenewalFeesLogs(models.Model):
      card_fees=models.ForeignKey(HospitalCardRenewalFees,on_delete=models.CASCADE)
      amount_charged=models.FloatField(0.00)
      added_by=models.ForeignKey(User,on_delete=models.CASCADE)
      date_changed=models.DateField()

      def save(self,*args,**kwargs):
           self.date_changed="{}-{}-{}".format(datetime.now().year,datetime.now().month,datetime.now().day)
           super().save(*args,**kwargs)

class Patient_Hospital_History(models.Model):
     '''
       keeps track of hospital a patient visited
     '''
     patient=models.ForeignKey(Patient,on_delete=models.CASCADE)
     hospital=models.ForeignKey(Hospital,on_delete=models.CASCADE)
     card_number=models.TextField(max_length=255)
     card_payment_status=models.BooleanField(default=False)
     date_joined=models.DateField()

     def save(self,*args,**kwargs):
           self.date_joined="{}-{}-{}".format(datetime.now().year,datetime.now().month,datetime.now().day)
           super().save(*args,**kwargs)
class Patient_Hospital_Card_Payment(models.Model):
      patient=models.ForeignKey(Patient_Hospital_History,on_delete=models.CASCADE)
      amount=models.FloatField(default=0.00)
      date_paid=models.DateField()
      def save(self,*args,**kwargs):
           self.date_paid="{}-{}-{}".format(datetime.now().year,datetime.now().month,datetime.now().day)
           super().save(*args,**kwargs)

class Patient_Hospital_Card_Renewal_Payment(models.Model):
      patient=models.ForeignKey(Patient_Hospital_History,on_delete=models.CASCADE)
      amount=models.FloatField(default=0.00)
      date_paid=models.DateField()
      recieved_by=models.ForeignKey(User,on_delete=models.CASCADE)
      def save(self,*args,**kwargs):
           self.date_paid="{}-{}-{}".format(datetime.now().year,datetime.now().month,datetime.now().day)
           super().save(*args,**kwargs)


class Patient_Medical_History_Records(models.Model):
      '''
      to take track record of patients and the hospitals they visted
      
      '''
      patient=models.ForeignKey(Patient_Hospital_History,on_delete=models.CASCADE)
      case_number=models.TextField(max_length=200)
      opd_nurse=models.ForeignKey(User,on_delete=models.CASCADE)
      checked_in=models.BooleanField(default=False)
      checked_out=models.BooleanField(default=False)
      time_checked_in=models.DateTimeField(default=datetime.now(),blank=True)
      time_checked_out=models.DateTimeField(default=datetime.now())
      '''
       when patient checks' out checked is set  to false
      '''
class Patient_OPD_Vitals(models.Model):
      '''
      collects patient opd vitals
      '''
      patient=models.ForeignKey(Patient_Medical_History_Records,on_delete=models.CASCADE)
      vital=models.ForeignKey(OPD_Vital,on_delete=models.CASCADE)
      results=models.TextField(max_length=255)
      
class Patient_Medical_Diagnosis_Records(models.Model):
      patient=models.ForeignKey(Patient_Medical_History_Records,on_delete=models.CASCADE)
      patient_complaints=models.CharField(max_length=200)
      doctor_diagnosis=models.CharField(max_length=200)
      in_house_laboratory_test=models.BooleanField(default=True)
      laboratory_report_request_status=models.BooleanField(default=False)
      laboratory_report_received_status=models.BooleanField(default=False)
      dietary_prescription_request=models.BooleanField(default=False)
      dietary_dispensed_status=models.BooleanField(default=False)


class Patient_Medical_History_Physician_records(models.Model):
      '''
      which physician attended to a patient
      '''
      physician=models.ForeignKey(User,on_delete=models.CASCADE)
      medical_diagnosis=models.ForeignKey(Patient_Medical_Diagnosis_Records,on_delete=models.CASCADE)

class Dietary_Supplementary(models.Model):
      supplement=models.TextField(max_length=255)
      quatity_in_stocked=models.IntegerField(default=0)
      price=models.FloatField(default=0.00)
      serial_code=models.CharField(max_length=200)
      photo=models.ImageField(upload_to='uploads/dietary/supplement')
      last_date_stocked=models.DateField()
      def save(self,*args,**kwargs):
            self.last_date_stocked="{}-{}-{}".format(datetime.now().year,datetime.now().month,datetime.now().day)
            super().save(*args,**kwargs)
      
class Dietary_Supplementary_Details(models.Model):

      dietary=models.ForeignKey(Dietary_Supplementary,on_delete=models.CASCADE)
      quantity=models.IntegerField(default=0)
      quantity_stocked=models.IntegerField(default=0)
      date_stocked=models.DateField()
      def save(self,*args,**kwargs):
            self.date_stocked="{}-{}-{}".format(datetime.now().year,datetime.now().month,datetime.now().day)
            super().save(*args,**kwargs)


class Dietary_Supplement_Stocking_Details(models.Model):
      dietary=models.ForeignKey(Dietary_Supplementary_Details,on_delete=models.CASCADE)
      date_stocked=models.DateField()
      new_quantity_stocked=models.IntegerField()
      old_quantity_stocked=models.IntegerField()
      current_cost=models.FloatField(default=0.00)
      old_cost=models.FloatField(default=0.00)
      quantity_at_the_time_of_stocking=models.IntegerField()
      stocked_by=models.ForeignKey(User,on_delete=models.CASCADE)

      def save(self,*args,**kwargs):
            self.date_stocked="{}-{}-{}".format(datetime.now().year,datetime.now().month,datetime.now().day)
            super().save(*args,**kwargs)


class Patient_Dietary_Supplementary_Records(models.Model):
      patient=models.ForeignKey(Patient_Medical_Diagnosis_Records,on_delete=models.CASCADE)
      dietary_supplement_request_view=models.BooleanField(default=False)
      dietary_supplement_dispense_viewed=models.BooleanField(default=False)
      total_cost=models.FloatField(default=0.00)
      amount_paid=models.FloatField(default=0.00)
      payment_status=models.BooleanField(default=False)
      discount_status=models.BooleanField(default=False)
      discount_rate=models.IntegerField(default=0)
      discount_amount=models.FloatField(default=0.0)
      #received_by=models.ForeignKey(User,on_delete=models.CASCADE)
      date_recieved=models.DateField()
      date_released=models.DateField() 
      def save(self,*args,**kwargs):
            self.date_recieved="{}-{}-{}".format(datetime.now().year,datetime.now().month,datetime.now().day)
            self.date_released="{}-{}-{}".format(datetime.now().year,datetime.now().month,datetime.now().day)
            super().save(*args,**kwargs)     

class Dietary_Supplement_Dispenser_Records(models.Model):
      patient=models.ForeignKey(Patient_Dietary_Supplementary_Records,on_delete=models.CASCADE)
      dispenser=models.ForeignKey(User,on_delete=models.CASCADE)

class Patient_Dietary_Supplementary_Records_Details(models.Model):
      patient=models.ForeignKey(Patient_Dietary_Supplementary_Records,on_delete=models.CASCADE)
      dietary_supplement=models.ForeignKey(Dietary_Supplementary,on_delete=models.CASCADE)
      cost=models.FloatField(default=0.00)
      quantity=models.IntegerField(default=1)
      total_cost=models.FloatField(default=0.00)


class Laboratory_Test_Cost_Details(models.Model):
      test_type=models.TextField(max_length=200)
      test_cost=models.FloatField(default=0.00)
      serial_code=models.CharField(max_length=255,default="")

class Patient_Laboratory_Test_Records(models.Model):
      patient=models.ForeignKey(Patient_Medical_Diagnosis_Records,on_delete=models.CASCADE)
      lab_test_request_view=models.BooleanField(default=False)
      lab_test_released=models.BooleanField(default=False)
      total_cost=models.FloatField(default=0.00)
      payment_status=models.BooleanField(default=False)
      amount_paid=models.FloatField(default=0.00)
      discount_status=models.BooleanField(default=False)
      discount_rate=models.IntegerField(default=0)
      discount_amount=models.FloatField(default=0.0)

      #received_by=models.ForeignKey(User,on_delete=models.CASCADE)
      date_recieved=models.DateField()
      date_released=models.DateField()
      def save(self,*args,**kwargs):
            self.date_recieved="{}-{}-{}".format(datetime.now().year,datetime.now().month,datetime.now().day)
            self.date_released="{}-{}-{}".format(datetime.now().year,datetime.now().month,datetime.now().day)
            super().save(*args,**kwargs)  

      '''
      lab technician has the priviledge to review lab test result befor released
      '''
class Patient_Laboratory_Test_Records_Technician(models.Model):
      lab=models.ForeignKey(Patient_Laboratory_Test_Records,on_delete=models.CASCADE)
      technician=models.ForeignKey(User,on_delete=models.CASCADE)
class Patient_Laboratory_Test_Results_Details(models.Model):
      patient= models.ForeignKey(Patient_Laboratory_Test_Records,on_delete=models.CASCADE)
      lab_test= models.ForeignKey(Laboratory_Test_Cost_Details,on_delete=models.CASCADE)
      test_cost=models.FloatField(default=0.00)
      test_results=models.CharField(max_length=200,default="")


class Laboratory_Test_Cost_Details_log(models.Model):
      lab_test = models.ForeignKey(Patient_Laboratory_Test_Records,on_delete=models.CASCADE)
      total_cost=models.FloatField(default=0.00)
      edited_by=models.ForeignKey(User,on_delete=models.CASCADE)

      
class Out_side_Lab_test(models.Model):
      patient=models.ForeignKey(Patient_Medical_Diagnosis_Records,on_delete=models.CASCADE)
      upload_lab_photo=models.ImageField(upload_to="")


class Out_side_Lab_test_Result_Details(models.Model):
      patient= models.ForeignKey(Patient_Laboratory_Test_Records,on_delete=models.CASCADE)
      lab_test= models.ForeignKey(Laboratory_Test_Cost_Details,on_delete=models.CASCADE)
      test_results=models.CharField(max_length=200,default="")
'''
   sales marketing records on diertary

'''
class Customer(models.Model):
      telephone=models.CharField(max_length=200)
      date_joined=models.DateField()
      def save(self,*args,**kwargs):
            self.date_joined="{}-{}-{}".format(datetime.now().year,datetime.now().month,datetime.now().day)
            super().save(*args,**kwargs)
class Customer_Inventory_Records(models.Model):
      customer=models.ForeignKey(Customer,on_delete=models.CASCADE)
      inventory_number=models.CharField(max_length=200)
      total_dietary_supplement_items=models.IntegerField(default=1)
      total_quantity_of_each_supplement_item=models.IntegerField(default=1)
      total_cost=models.FloatField(default=0.00)
      amount_paid=models.FloatField(default=0.00)
      discount_status=models.BooleanField(default=False)
      discount_rate=models.IntegerField(default=0)
      discount_amount=models.FloatField(default=0.0)
      payment_received_by=models.ForeignKey(User,on_delete=models.CASCADE)
      date_time_of_purchased=models.DateField()
      def save(self,*args,**kwargs):
            self.date_time_of_purchased="{}-{}-{}".format(datetime.now().year,datetime.now().month,datetime.now().day)
            super().save(*args,**kwargs)
      

class Customer_Inventory_Records_Details(models.Model):
      customer=models.ForeignKey(Customer_Inventory_Records,on_delete=models.CASCADE)
      dietary_supplement=models.ForeignKey(Dietary_Supplementary,on_delete=models.CASCADE)
      cost=models.FloatField(default=0.00)
      quantity_purchased=models.FloatField(default=1)
      total_cost=models.FloatField(default=0.00)

      def save(self,*args,**kwargs):
            self.total_cost=self.quantity_purchased*self.cost
            super().save(*args,**kwargs)

class Dietary_Sale_Inventory_Table(models.Model):
      dietary=models.ForeignKey(Dietary_Supplementary,on_delete=models.CASCADE)
      quantity=models.IntegerField(default=0)
      cost_per_unit=models.FloatField(default=0.00)
      total_cost=models.FloatField(default=0.00)

      
      date_purschaesd=models.DateField(default="1990-08-04")
      def save(self,*args,**kwargs):
            self.total_cost=int(self.quantity)*float(self.cost_per_unit)
            self.date_purschaesd="{}-{}-{}".format(datetime.now().year,datetime.now().month,datetime.now().day)
            super().save(*args,**kwargs)


'''

    lab test patronage by outsiders

'''
class Outside_Customers_Lab_Test(models.Model):
      name=models.CharField(max_length=255)
      telephone=models.CharField(max_length=200)


class OutsideLabtestCases(models.Model):
      customer=models.ForeignKey(Outside_Customers_Lab_Test,on_delete=models.CASCADE)
      lab_case_number=models.CharField(max_length=200)
      total_cost=models.FloatField(default=0.00)
      laboratory_report_request_status=models.BooleanField(default=False)
      payment_status=models.BooleanField(default=False)
      laboratory_report_received_status=models.BooleanField(default=False)
      lab_sheet=models.ImageField(upload_to="uploads/outside_lab/")
      received_by=models.ForeignKey(User,on_delete=models.CASCADE)
      report_date=models.DateTimeField()
      def save(self,*args,**kwargs):
            self.report_date="{}-{}-{} {}:{}".format(datetime.now().year,datetime.now().month,datetime.now().day,datetime.now().hour,datetime.now().minute)
            super().save(*args,**kwargs)


class OutsideLabtestDetails(models.Model):
      outside_lab_patient=models.ForeignKey(OutsideLabtestCases,on_delete=models.CASCADE)
      laboratory=models.ForeignKey(Laboratory_Test_Cost_Details,on_delete=models.CASCADE)
      cost=models.FloatField(default=0.00)
      test_results=models.CharField(max_length=200)



'''
class DietarySupplmentarySalesSumarryDetails(models.Model):
      dietary=models.ForeignKey(Dietary_Supplementary,on_delete=models.CASCADE)
      cost_per_unit=models.FloatField(desfault=0.00)
      total_cost=models.FloatField(default=0.00)
      total_quantity_purchased=models.IntegerField(default=1)
      total_quantity_left_in_stocked=models.IntegerField(default=0.0)
      date_recored=models.DateField()

class DeitarySupplementsDeatails(models.Model):
      dietary=models.ForeignKey(Dietary_Supplementary,on_delete=models.CASCADE)
      cost_per_unit=models.FloatField(desfault=0.00)
      quantity_purchased=models.IntegerField(default=1)
      quantity_left_in_stocked=models.IntegerField(default=0.0)
      seller=models.ForeignKey(User,on_delete=models.ForeignKey)
      date_recorded=models.DateTimeField()

class DietarySupplements(models.Model):
      dietary=models.ForeignKey(Dietary_Supplementary,on_delete=models.CASCADE)
      stocked_by=models.ForeignKey(User,on_delete=models.CASCADE)
      new_cost=models.FloatField(default=0.00)
      old_cost=models.FloatField(default=0.00)
      quantity_stocked=models.IntegerField(default=1)
      quantity_in_stocked=models.IntegerField(default=1)
      date_stocked=models.DateField()
'''




