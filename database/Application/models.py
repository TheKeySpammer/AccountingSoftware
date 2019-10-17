from django.db import models

#Utility Database:
#---------------------------------------------------------
class Country(models.Model):
	Id=models.AutoField(primary_key=True)
	Country_Code=models.CharField(max_length=10)
	Country_Name=models.CharField(max_length=50)

class Currency(models.Model):
	Id=models.AutoField(primary_key=True)
	Code=models.CharField(max_length=10)
	Name=models.CharField(max_length=50)

#In mysql client use 'alter table application_phonecode AUTO_INCREMENT=1;' to have starting value as 1
class PhoneCode(models.Model):
	Id=models.AutoField(primary_key=True)
	Country_Name=models.CharField(max_length=50)
	ISO_Code=models.CharField(max_length=10)
	ISD_Code=models.CharField(max_length=10)

#---------------------------------------------------------

class Company(models.Model):
	Company_Id=models.AutoField(primary_key=True)
	Company_Name=models.CharField(max_length=50)
	Address_Line=models.TextField()
	City=models.CharField(max_length=30)
	State=models.CharField(max_length=30)
	Email=models.EmailField()
	Phone=models.PositiveSmallIntegerField()
	Date=models.DateField()
	Tax_Rate=models.FloatField()
	Base_Currency=models.ForeignKey(Currency,on_delete=models.CASCADE,default="")

	def __str__(self):
		return (self.Company_Id+','+self.Company_Name+', ('+self.Address_Line+','+self.City+','+
			   self.State+') ,'+self.Email+','+self.Phone+','+self.Date+','+self.Tax_Rate)

class User(models.Model):
	User_Id=models.AutoField(primary_key=True)
	Fname=models.CharField(max_length=50)
	Lname=models.CharField(max_length=50)
	Address_Line=models.TextField()
	City=models.CharField(max_length=30)
	State=models.CharField(max_length=30)
	Email=models.EmailField()
	Phone=models.PositiveSmallIntegerField()
	Auth_Level=models.PositiveSmallIntegerField()
	Comp_Id = models.ForeignKey(Company, on_delete=models.CASCADE)

	def __str__(self):
		return (self.User_Id+','+self.Fname+','+self.Lname+', ('+self.Address_Line+','+self.City+','+
			   self.State+') ,'+self.Email+','+self.Phone+','+self.Auth_Level)

#------------------------------------------------------------------------------------------------------

class Client(models.Model):
	Client_Id=models.CharField(max_length=20,primary_key=True)
	Fname=models.CharField(max_length=50)
	Lname=models.CharField(max_length=50)
	Address_Line=models.TextField()
	City=models.CharField(max_length=30)
	State=models.CharField(max_length=30)
	Pin_Code=models.PositiveSmallIntegerField()
	Email=models.EmailField()
	Phone=models.PositiveIntegerField()

	def __str__(self):
		return(self.Client_Id+','+self.Fname+','+self.Lname+','+self.Address_Line+','+self.City+','+self.State+','+
			   self.Pin_Code+','+self.Email+','+self.Phone)

class Vendor(models.Model):
	Vendor_Id=models.CharField(max_length=20,primary_key=True)
	Vendor_Name=models.CharField(max_length=100)
	Vendor_Category=models.CharField(max_length=10)
	Address_Line=models.TextField()
	City=models.CharField(max_length=30)
	State=models.CharField(max_length=30)
	Pin_Code=models.PositiveSmallIntegerField()
	Email=models.EmailField()
	Phone=models.PositiveIntegerField()

	def __str__(self):
		return(self.Vendor_Id+','+self.Vendor_Name+','+self.Vendor_Category+','+self.Address_Line+','+
			   self.City+','+self.State+','+self.Pin_Code+','+self.Email+','+self.Phone)

class Account(models.Model):
	Account_Id=models.AutoField(primary_key=True)
	Tax=models.FloatField()
	Tax_type=models.CharField(max_length=20)
	Currency=models.CharField(max_length=5)
	Late_Fees=models.FloatField()
	Due_Date=models.DateField()
	Due_Amount=models.FloatField()

	def __str__(self):
		return(self.Account_Id+','+self.Currency+','+self.Tax+','+self.Tax_type+','+self.Late_Fees+','+self.Due_Amount+','+
			   self.Due_Date)

class Vendor_Account(models.Model):
    Vendor_Id=models.ForeignKey(Vendor, on_delete=models.CASCADE)
    Account_Id=models.ForeignKey(Account,on_delete=models.CASCADE)

class Client_Account(models.Model):
    Client_Id=models.ForeignKey(Client, on_delete=models.CASCADE)
    Account_Id=models.ForeignKey(Account, on_delete=models.CASCADE)
    
class Transactions(models.Model):
    Account_Id=models.ForeignKey(Account, on_delete=models.CASCADE)
    Transaction_Id=models.AutoField(primary_key=True)
    Transaction_Date=models.DateField()
    Transaction_amt=models.FloatField()

    def __str__(self):
    	return(self.Transaction_id+','+self.Transaction_amt+','+self.Transaction_Date)

