#from django.shortcuts import render
from Application.models import *
from django.http import JsonResponse,HttpResponse
from django.contrib.auth.hashers import make_password,check_password
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from datetime import date, timedelta
from django.db.models import Sum

'''
Auth Level 0: Accounting Head 
Auth Level 1: General Accountant
Auth Level 2: Expense Accountant
Auth Level 3: Client Accountant
Auth Lecel 4: None
'''

AUTH_LEVEL = ['Head','General','Expense','Client', None]

DATE_FORMAT = {
	'little_endian': 'dd/mm/yyyy',
	'middle_endian': 'mm/dd/yyyy',
	'big_endian': 'yyyy/mm/dd',
}

value={

    'clientId': None,
    'secret': None,
    'accessToken': None
}

userToken={}
status=[200,403,404]

def check_user(token):
	for e,t in userToken:
		if t is token:
			del userToken[e]
			return True
	return False

def post(*oargs, **okwargs):
	def inner1(func):
		def inner2(*args, **kwargs):
			if args[0].method == 'POST' :
				for k in oargs:
					if k not in args[0].POST.keys():
						return HttpResponse('Invalid Payload',status=400)
					if k is 'token' and k in args[0].POST.keys() and not check_user(args[0].POST['token']):
						return HttpResponse('User not Logged in',status=400)
					if k is 'accessToken' and k in args[0].POST.keys() and args[0].POST['accessToken'] is not value['accessToken']:
						return HttpResponse('Invalid access token',status=400)
				return func(*args,**kwargs)
			else:
				return HttpResponse(status=status[2])
		return inner2
	return inner1

def get(func):
	def inner(*args, **kwargs):
		if args[0].method == 'GET':
			return func(*args,**kwargs)
		else:
			return HttpResponse(status=status[2])
	return inner

def get_iso_date(date_format, date_data):
	d = [ x for x in date_data.strip().split() if len( x.strip() ) != 0 ]
	if len(d) != 3:
		raise Exception('Invalid date data')
	if DATE_FORMAT.big_endian == date_format.strip(): # yyyy/mm/dd
		return date(d[0],d[1],d[2])
	elif DATE_FORMAT.little_endian == date_format.strip(): # dd/mm/yyyy
		return date(d[2],d[1],d[0])
	elif DATE_FORMAT.middle_endian == date_format.strip(): # 'mm/dd/yyyy'
		return  date(d[2],d[0],d[1])
	else :
		raise Exception('Invalid date format')

def get_date(date_format, date_data):
	if DATE_FORMAT.big_endian == date_format.strip(): # yyyy/mm/dd
		return date_data.strftime("%Y/%m/%d")
	elif DATE_FORMAT.little_endian == date_format.strip(): # dd/mm/yyyy
		return date_data.strftime("%d/%m/%Y")
	elif DATE_FORMAT.middle_endian == date_format.strip(): # 'mm/dd/yyyy'
		return date_data.strftime("%m/%d/%Y")
	else :
		raise Exception('Invalid date format')

def get_invoice(client,items,invoice):
	res = {
		'client': {
		'id': client['Client_Id'],
		'firstName': client['Fname'],
		'lastName': client['Lname'],
		'countryCode': '+65',
		'phone': client['Phone'],
		'email': client['Email'],
		'address': {
			'address1': client['Address'],
			'city': client['City'],
			'state': client['State'],
			'country': 'USA',
			'pincode': client['Pin_Code'],  
		},
		'lateFeeRate': client['Late_Fee_Rate']
		},
		'id':invoice['Invoice_Id'],
		'date': get_date( invoice['datefmt'], invoice['Date'] ),
		'amountDue': invoice['Amount_Due'],
		'items' : []
	}

	for itm in items:
		item = {
			'item': itm['Name'],
			'description': itm['Description'],
			'rate': itm['Rate'],
			'quantity': itm['Quantity'],
			'price': itm['Price'] 
		}
		res['items'].append(item)
	return res

#Create Initial init Request:
@csrf_exempt
@post('clientId','secret')
def init(request):
	clientId=request.POST['clientId']
	secret=request.POST['secret']

	if value['clientId'] is None:
    
		value['clientId'] = clientId
		value['secret'] = secret
		token=clientId+str(datetime.now())
		value['accessToken']=make_password(token)

	elif value['clientId'] is not None:

		if(secret == value['secret']):
			token=clientId+str(datetime.now())
			value['accessToken']=make_password(token)
		else:
			return HttpResponse("Invalid Authorisation", status=status[2])
	
	lastClientId = Client.objects.all().order_by('-Client_Id')
	lastExpenseId = Expense.objects.all().order_by('-Expense_Id')
	lastInvoiceId = Invoice.objects.all().order_by('-Invoice_Id')
	lastVendorId = Vendor.objects.all().order_by('-Vendor_Id')

	data={
			'accessToken' : value['accessToken'],
			'data' : {
				'lastClientId' : int(str(lastClientId[0]).split(',')[0].strip()) if len(lastClientId) > 0 else 0,
				'lastInvoiceId' : int(str(lastInvoiceId[0]).split(',')[0].strip()) if len(lastInvoiceId) > 0 else 0,
				'lastVendorId' : int(str(lastVendorId[0]).split(',')[0].strip()) if len(lastVendorId) > 0 else 0,
				'lastExpenseId' : int(str(lastExpenseId[0]).split(',')[0].strip()) if len(lastExpenseId) > 0 else 0
			}
	}

	return JsonResponse(data,safe=False)

# Create login Request:
@csrf_exempt
@post('accessToken','email','password')
def login_user(request):
	email = request.POST['email']
	password = request.POST['password']
	# Is this accessToken encrypted??
	# access_token = request.POST['accessToken']

	# if (access_token != value['accessToken']):
	# 	return HttpResponse("Invalid Authorisation ", status=status[2])
	users = User.objects.filter(Email=email).values()

	# for e,enc_p in User.objects.all().values_list('Email','Password'):
	# 	if e == email:
	if users is not None and len(users) == 1:
		user = users[0]
		companies = Company.objects.filter(Company_Id=user['Comp_Id_id']).values()
		if companies is None or len(companies) < 1:
			return HttpResponse('Company is not set', status=406 )
		
		currencies = Currency.objects.filter(Id=companies[0]['Base_Currency_id']).values()
		
		if currencies is None or len( currencies ) < 1 :
				return HttpResponse('Currency is not added', status=406 )
		currency = currencies[0]
		company = companies[0]
		if check_password(password,user['Password']):
			tokenTemp = None
			global userToken  						#Use global keyword to access global variable
			if email in userToken.keys():
				tokenTemp = userToken[email]
			else:
				token=email+str(datetime.now())
				tokenTemp = make_password(token)
				userToken[email] = tokenTemp

			data={
				'name': f"{user['Fname']} {user['Lname']}",
				'email': email,
				'company' :
					{
					'name': company['Company_Name'],
					'countryCode': company['Country_Code'],
					'phone': company['Phone'],
					'email': company['Email'],
					'address': {
						'address1': company['Address_Line'],
						'city': company['City'],
						'state': company['State'],
						'country': company['Country_Name'],
						'pincode': company['Pin_Code'],
						},
					'currency': currency['Code'],
					'datefmt': company['Date_Format'],
					'taxrate': company['Tax_Rate']
					},
				'token': tokenTemp
			}

			return JsonResponse(data,safe=False)

		else:
			return HttpResponse("Invalid Password", status=status[1])

	else:
		return HttpResponse("User Does Not Exists", status=status[2])


# Create logout Request:
@csrf_exempt
@post('accessToken','token')
def logout(request):
	if request.method == 'POST':
		access_token=request.POST['accessToken']
		uToken=request.POST['token']
		global userToken						#Use global keyword to access global variable

		if ( access_token != value['accessToken'] ):
			return HttpResponse("Invalid Authorisation ", status=status[2])

		if check_user(uToken):
			return HttpResponse('Logout successful')
		return HttpResponse('User is not logged in')


@csrf_exempt
@post('accessToken')
def country(request):
	country_code = list()
	country_name = list()
	for code, c_name in Country.objects.all().values_list('Country_Code', 'Country_Name'):
		country_code.append(code)
		country_name.append(c_name)
	data = {
		'code': country_code,
		'country': country_name
	}
	return JsonResponse(data)


@csrf_exempt
@post('accessToken')
def quote(request):
	fn = list()
	ln = list()
	quotes = list()
	for f, l, q in Quotes.objects.all().values_list('AFName', 'ALName', 'Quote'):
		fn.append(f)
		ln.append(l)
		quotes.append(q)
	data = {
		'fNme': fn,
		'lName': ln,
		'quote': quotes
	}
	return JsonResponse(data)


@csrf_exempt
@post('accessToken')
def currencies(request):
	currency_code = list()
	currency_name = list()
	for cc, c in Currency.objects.all().values_list('Code', 'Name'):
		currency_code.append(cc)
		currency_name.append(c)
	data = {
		'code': currency_code,
		'currency': currency_name
	}
	return JsonResponse(data)


@csrf_exempt
@post('accessToken')
def phones(request):
	country_name = list()
	iso = list()
	isd = list()
	for c, i, d in PhoneCode.objects.all().values_list('Country_Name', 'ISO_Code', 'ISD_Code'):
		country_name.append(c)
		iso.append(i)
		isd.append(d)
	data = {
		'countryName': country_name,
		'ISO': iso,
		'ISD': isd
	}
	return JsonResponse(data)


@csrf_exempt
@post('accessToken')
def dates(request):
	data = [v for _,v in DATE_FORMAT ]
	return JsonResponse({ 'dateFormat' : data },safe=True)

@csrf_exempt
@post('accessToken')
def company(request):
	try:
		comp=request.POST.get('company')
		chk = Company.objects.filter(Email=request.POST['email']).values()
		
		if chk is not None:
			return HttpResponse(" Company Already exists ",status=208) 
		datefmt = comp['datefmt']
		c1 = Company(Company_Name=comp['name'],Address_Line=comp['address']['address1'],City=comp['address']['city'],
			Pin_Code=comp['address']['pincode'],Country_Name=comp['address']['country'], Country_Code=comp['countryCode'],
			State=comp['address']['state'],Email=comp['email'],Phone=comp['phone'],
			Tax_Rate=comp['taxrate'],Base_Currency=comp['currency'],Date_Format=datefmt)
		c1.save()
		comp_id = c1.pk()

		if 'Head' in comp['accountants']:
			# x = Company.objects.filter(Company_Name=comp['name']).values_list('Company_Id')
			head=request.POST.get('headAcc')
			token = head['email']+str(datetime.now())
			uToken = make_password(token)
			global userToken
			
			userToken[email]=uToken

			h1 = User(Fname=head['firstName'],Lname=head['lastName'],Address_Line=head['address']['address1'],
				City=head['address']['city'],Pin_Code=head['address']['pincode'],State=head['address']['state'],
				Country_Name=head['address']['country'],Country_Code=head['countryCode'],Email=head['email'],
				Password=head['password'],Phone=head['phone'],Auth_Level=0,Comp_Id_id=comp_id)
			h1.save()
			
		if 'Client' in comp['accountants']:
			# x=Company.objects.filter(Company_Name=comp['name']).values_list('Company_Id')
			client=request.POST.get('clientAcc')

			c1 = User(Fname=client['firstName'],Lname=client['lastName'],Address_Line=client['address']['address1'],
				City=client['address']['city'],Pin_Code=client['address']['pincode'],State=client['address']['state'],
				Country_Name=client['address']['country'],Country_Code=client['countryCode'],Email=client['email'],
				Password=client['password'],Phone=client['phone'],Auth_Level=1,Comp_Id_id=comp_id)

			c1.save()
		if 'Expense' in comp['accountants']:
			# x=Company.objects.filter(Company_Name=comp['name']).values_list('Company_Id')
			expense=request.post.get('expenseAcc')
			e1 = User(Fname=expense['firstName'],Lname=expense['lastName'],Address_Line=expense['address']['address1'],
				City=expense['address']['city'],Pin_Code=expense['address']['pincode'],State=expense['address']['state'],
				Country_Name=expense['address']['country'],Country_Code=expense['countryCode'],Email=expense['email'],
				Password=expense['password'],Phone=expense['phone'],Auth_Level=2,Comp_Id_id=comp_id)
			e1.save()
		if 'Genral' in comp['accountants']:
			# x=Company.objects.filter(Company_Name=comp['name']).values_list('Company_Id')
			gen=request.post.get('genralAcc')
			g1 = User(Fname=gen['firstName'],Lname=gen['lastName'],Address_Line=gen['address']['address1'],
				City=gen['address']['city'],Pin_Code=gen['address']['pincode'],State=gen['address']['state'],
				Country_Name=gen['address']['country'],Country_Code=gen['countryCode'],Email=gen['email'],
				Password=gen['password'],Phone=gen['phone'],Auth_Level=3,Comp_Id_id=comp_id)
			g1.save()
		data={
			'token' : userToken
		}
		return JsonResponse(data)

	except:
		return HttpResponse(status=404)

@csrf_exempt
@post('accessToken','email')
def user_exists(request):
	user = User.objects.filter(Email=request.POST['email']).values()
	if user is not None:
		return JsonResponse({
			'exists': 'true' if len(user) != 0 else 'false'
		})
	else :
		return HttpResponse("Database Error",status=500)

#Creates invoice
@csrf_exempt
@post('accessToken','token','invoice')
def create_invoice(request):
	# if value['accessToken'] is not request.POST['accessToken']:
	# 	return HttpResponse('Invalid access token',status=401)
	data = request.POST['invoice']
	datefmt = data['datefmt']
	invoice = Invoice(Client_Id=data['clientId'], Date=get_iso_date(datefmt, data['date']), Amount_Due=data['amountDue'], 
					Amount_Paid=data['amountPaid'], Total=data['total'], Balance_Due=data['balanceDue'], Notes=data['notes'],
					Date_Format=datefmt)
	invoice.save()
	invoice_id = invoice.pk()

	for itm in data['items']:
		item = Item(Name=itm['item'], Description=itm['description'], Rate=itm['rate'], Quantity=itm['quantity'], Price=itm['price'], Invoice_Id=invoice_id)
		item.save()
	return JsonResponse({
		'invoiceId' : invoice_id
	})

#Fetch invoice
@csrf_exempt
@post('accessToken','token')
def fetch_invoice(request,invoice_id):
	if value['accessToken'] is not request.POST['accessToken']:
		return HttpResponse('Invalid access token',status=401)
	
	invoices = Invoice.objects.filter(Invoice_Id=invoice_id).values()
	if invoices is not None and len(invoices) > 0:
		invoice = invoices[0]
		items = Item.objects.filter(Invoice_Id_id=invoice_id).values()
		clients = Client.objects.filter(Client_Id=invoice['Client_Id_id']).values()
		if items is None or len(items) <= 0 or clients is None or len(clients) <= 0:
			return HttpResponse('Client or Items does not exits in database', status=400)

		return JsonResponse(get_invoice(clients[0],items,invoice),safe=True)
	else:
		return HttpResponse('Invalid invoice Id',status=400)

#Get latest invoice	
@csrf_exempt
@post('accessToken','token','quantity')
def latest_invoice(request):
	qty = request.POST['quantity']
	tempInvoices = Invoice.objects.all().order_by('-Invoice_Id').values()
	if tempInvoices is not None and len(tempInvoices) >= qty:
		invoices = tempInvoices[:qty]
		res = []
		for inv in invoices:
			client = Client.objects.filter(Client_Id=inv['Client_Id_id']).values()
			items = Item.objects.filter(Invoice_Id_id=inv['Invoice_Id']).values()
			if items is None or len(items) <= 0 or client is None or len(client) <= 0:
				return HttpResponse('Client or Items does not exits in database', status=400)
			res.append(get_invoice(client,items,inv))
		return JsonResponse(res,safe=True)
			
	else:
		return HttpResponse('Quantity is out of bound',status=400)

#Deletes the invoice	
@csrf_exempt
@post('accessToken','token','invoices')
def delete_invoice(request):
	resInv = request.POST['invoices']
	for i in resInv:
		Invoice.objects.filter(Invoice_Id=i).delete()
	return HttpResponse('Deleted sucessfully')

#Create Vendor
@csrf_exempt
@post('accessToken','token','vendor')
def create_vendor(request):
	ven = request.POST['vendor']
	add = ven['addresss']
	vendor = Vendor(Vendor_Name=ven['name'],Email=ven['email'],Phone=ven['phone'],Address=add['address1'],City=add['city'],State=ven['state'],
				Pin_Code=ven['pincode'], Country_Name=add['country'], Country_Code=ven['countryCode'])
	vendor.save()
	return HttpResponse('Created successfully')

#Fetch Vendor
@csrf_exempt
@post('accessToken','token')
def fetch_vendor(request):
	res = { 'vendor': [name for name in Vendor.objects.all().values_list('Vendor_Name')] }
	return JsonResponse(res,safe=True)

#Fetch Vendor
@csrf_exempt
@post('accessToken','email')
def accountant_exists(request):
	user = User.objects.filter(Email=request.POST['email']).values()
	if user is not None:
		return JsonResponse({
			'exists': 'true' if len(user) != 0 and AUTH_LEVEL[user['Auth_Level']] != None else 'false'
		})
	else :
		return HttpResponse("Database Error",status=500)



# Category routes
@csrf_exempt
@post('accessToken', 'token', 'category')
def category_create(request):
	category = request.POST['category']
	cat = Category(Type=category)
	cat.save()
	return HttpResponse('Created successfully')

@csrf_exempt
@post('accessToken', 'token')
def category_fetch(request):
	res = {'categories': [cat for cat in Category.objects.all().values_list('Type')]}
	return JsonResponse(res, safe=True)


# Expense Routes
# Creation
@csrf_exempt
@post('accessToken', 'token', 'client')
def expense_create(request):
	exp = request.POST['expense']
	expense = Expense(Category_Id=Category.objects.filter(Type=exp['category'])[0]['Type'], Date=get_iso_date(request.POST['datefmt'], exp['date']), Vendor_Id=Vendor.objects.filter(Vendor_Name=exp['vendor'])[0].Vendor_Id,Description=exp['description'], Amount=float(exp['amount']))
	expense.save();
	return HttpResponse('Created Successfully')


def _get_expense(expense):
	return {
			'category': expense['Category'],
			'date': expense['Date'],
			'description': expense['Description'],
			'amount': expense['Amount'],
			'vendor': Vendor.objects.filter(pk=expense['Vendor_Id']).values()[0]
		}

# fetch_latest
@csrf_exempt
@post('accessToken', 'token', 'quantity')
def expense_latest(request):
	qty = int(request.POST['quantity'])
	all_expense = Expense.objects.all().order_by("-Expense_Id").values()
	if all_expense is not None and len(all_expense) >= qty:
		expenses = all_expense[:qty]
		res = {'expenses': []}
		for exp in expenses:
			expense = _get_expense(exp)
			res['expenses'].append(expense)
		return (JsonResponse(res, safe=True))
	else:
		return HttpResponse('Quatity Requested is out of bounds', status=400)


@csrf_exempt
@post('accessToken', 'token')
def expense_fetch(request, expense_id):
	exp = Expense.objects.filter(Expense_Id=expense_id).values()[0]
	if (exp is not None):
		res = {'expense': _get_expense(exp)}
		return JsonResponse(res, safe=True)
	else:
		return HttpResponse('Expense does not exists', status=400)


@csrf_exempt
@post('accessToken', 'token', 'expense')
def expense_update(request, expense_id):
	exp = Expense.objects.get(pk=expense_id)
	if (exp is not None):
		new_exp = request.POST['expense']
		datefmt = request.POST['datefmt']
		exp.Category_Id = new_exp['category']
		exp.Date = get_iso_date(datefmt, new_exp['date'])
		vendors = Vendor.objects.filter(Vendor_Name=new_exp['vendor']).values()
		if (not (vendors is not None and len(vendors) > 0)):
			return HttpResponse('Vendor does not exists', status=400)
		exp.Vendor_Id = Vendor.objects.filter(Vendor_Name=new_exp['vendor']).values()[0]['Vendor_Id']
		exp.Description = new_exp['description']
		exp.Amount = new_exp['amount']
		exp.save()
		return HttpResponse('Save successfully')
	else:
		return HttpResponse('Expense does not exists', status=400)


@csrf_exempt
@post('accessToken', 'token', 'expenses')
def expense_delete(request):
	exp_ids = request.POST['expenses']
	for id in exp_ids:
		Expense.objects.filter(Expense_Id=id).delete()
	return HttpResponse('Successfully Deleted')



# Client Routes

@csrf_exempt
@post('accessToken', 'token', 'client')
def client_create(request):
	cli = request.POST['client']
	client = Client(Fname=cli['firstName'], Lname=cli['lastName'], Address_Line=cli['address']['address1'],
	 City=cli['address']['city'], Pin_Code=cli['address']['pincode'], State=cli['address']['state'], Country_Name=cli['address']['country'],
	Day_Limit=cli['dayLimit'], Email=cli['email'], Phone=cli['phone'], Country_Code=cli['countryCode'], Late_Fee_Rate=cli['lateFeeRate'])
	client.save();
	return HttpResponse('Created Successfully')


@csrf_exempt
@post('accessToken', 'token', 'quantity')
def client_latest(request):
	qty = int(request.POST['quantity'])
	all_client = Client.objects.all().order_by("-Client_Id").values()
	if all_client is not None and len(all_client) >= qty:
		clients = all_client[:qty]
		res = {'clients': clients}
		return (JsonResponse(res, safe=True))
	else:
		return HttpResponse('Quatity Requested is out of bounds', status=400)


@csrf_exempt
@post('accessToken', 'token')
def client_fetch(request, client_id):
	cli = Client.objects.filter(Client_Id=client_id).values()[0]
	if (cli is not None):
		res = {'client': cli}
		return JsonResponse(res, safe=True)
	else:
		return HttpResponse('Client does not exists', status=400)


@csrf_exempt
@post('accessToken', 'token', 'client')
def client_update(request, client_id):
	cli = Client.objects.get(pk=client_id)
	if (cli is not None):
		new_cli = request.POST['client']
		address = new_cli['address']
		cli.Fname = new_cli['firstName']
		cli.Lname = new_cli['lastName']
		cli.Address_Line = address['address1']
		cli.City = address['city']
		cli.Pin_Code = address['pincode']
		cli.State = address['State']
		cli.Country_Name = address['country']
		cli.Country_Code = new_cli['countryCode']
		cli.Late_Fee_rate = new_cli['lateFeeRate']
		cli.Phone = new_cli['phone']
		cli.Email = new_cli['email']
		cli.Day_Limit = new_cli['dayLimit']
		cli.save()
		return HttpResponse('Save successfully')
	else:
		return HttpResponse('Expense does not exists', status=400)

@csrf_exempt
@post('accessToken', 'token', 'clients')
def client_delete(request):
	cli_ids = request.POST['clients']
	for id in cli_ids:
		Client.objects.filter(Client_Id=id).delete()
	return HttpResponse('Successfully Deleted')




def _get_invoices_by_year(invoices):
	invs_y = [invoices[0]]
	invs = []
	curr_year = invs_y[0]['Date'].year
	flag = False
	for i in invoices:
		y = i['Date'].year
		invs.append(i)
		if y < curr_year:
			if flag :
				break
			invs_y.append(i)
			invs.append(i)
			curr_year = y
			flag = True
	return (len(invs_y),invs)


@csrf_exempt
@post('accessToken','token','startMonth','endMonth')
def report_outstandingRevenue(request):
	rSMonth = request.POST['startMonth']
	rEMonth = request.POST['endMonth']
	currMonth = date.today().month
	
	cycleS = True if currMonth < rSMonth else False
	cycleE = True if currMonth < rEMonth else False
	sMonth = abs( currMonth - rSMonth )
	eMonth = abs( currMonth - rEMonth )

	invoices = Invoice.objects.all().order_by('-Date').values()
	if invoices is None or len( invoices ) <= 0 :
		return HttpResponse('Invoice not found',status=400)
	
	invs_y,invs = _get_invoices_by_year(invoices)
	curr_year = invs[0]['Date'].year
	
	if invs_y == 1 and cycleS and cycleE:
		return HttpResponse('Invalid Arguments',status=400)
	
	res = {
		'revenue': 0
	}

	if not cycleE and not cycleS:
		for i in range( 0, len(invs)):
			inv = invs[i]
			if curr_year is not inv['Date'].year :
				break
			if sMonth <= inv['Date'].month and eMonth >= inv['Date'].month :
				res['revenue'] += inv['Balance_Due']
	elif cycleE and not cycleS:
		for i in range( 0 , len( invs ) ):
			inv = invs[i]
			if eMonth >= inv['Date'].month and curr_year is inv['Date'].year :
				res['revenue'] += inv['Balance_Due']
			elif sMonth <= inv['Date'].month and curr_year is not inv['Date'].year :
				res['revenue'] += inv['Balance_Due']
	elif cycleS and cycleE:
		for i in range( 0 , len( invs ) ):
			inv = invs[i]
			if sMonth <= inv['Date'].month and curr_year is not inv['Date'].year and eMonth >= inv['Date'].month :
				res['revenue'] += inv['Balance_Due']

	return JsonResponse(res,safe=True)

@csrf_exempt
@post('accessToken','token','startMonth','endMonth')
def report_overdue(request):
	rSMonth = request.POST['startMonth']
	rEMonth = request.POST['endMonth']
	currMonth = date.today().month
	
	cycleS = True if currMonth < rSMonth else False
	cycleE = True if currMonth < rEMonth else False
	sMonth = abs( currMonth - rSMonth )
	eMonth = abs( currMonth - rEMonth )

	invoices = Invoice.objects.all().order_by('-Date').values()
	if invoices is None or len( invoices ) <= 0 :
		return HttpResponse('Invoice not found',status=400)
	
	invs_y,invs = _get_invoices_by_year(invoices)
	curr_year = invs[0]['Date'].year
	
	if invs_y == 1 and cycleS and cycleE:
		return HttpResponse('Invalid Arguments',status=400)
	
	res = {
		'revenue': 0
	}

	check_limit = lambda d, limit: ( date.today() - d ).days > limit 

	if not cycleE and not cycleS:
		for i in range( 0, len(invs)):
			inv = invs[i]
			clients = Client.object().filter(Client_Id=inv['Client_Id_id'])
			if clients is None or len(clients) <= 0:
				break 
			if curr_year is not inv['Date'].year :
				break

			if sMonth <= inv['Date'].month and eMonth >= inv['Date'].month and check_limit(inv['Date'], clients[0]['Day_Limit']):
				res['revenue'] += inv['Balance_Due']
	elif cycleE and not cycleS:
		for i in range( 0 , len( invs ) ):
			inv = invs[i]
			
			clients = Client.object().filter(Client_Id=inv['Client_Id_id'])
			if clients is None or len(clients) <= 0:
				break 

			if eMonth >= inv['Date'].month and curr_year is inv['Date'].year and check_limit(inv['Date'], clients[0]['Day_Limit']):
				res['revenue'] += inv['Balance_Due']
			elif sMonth <= inv['Date'].month and curr_year is not inv['Date'].year and check_limit(inv['Date'], clients[0]['Day_Limit']):
				res['revenue'] += inv['Balance_Due']
	elif cycleS and cycleE:
		for i in range( 0 , len( invs ) ):
			inv = invs[i]
			
			clients = Client.object().filter(Client_Id=inv['Client_Id_id'])
			if clients is None or len(clients) <= 0:
				break 

			if sMonth <= inv['Date'].month and curr_year is not inv['Date'].year and eMonth >= inv['Date'].month and check_limit(inv['Date'], clients[0]['Day_Limit']):
				res['revenue'] += inv['Balance_Due']

	return JsonResponse(res,safe=True)

@csrf_exempt
@post('accessToken','token','startMonth','endMonth')
def report_profit(request):

	rSMonth = request.POST['startMonth']
	rEMonth = request.POST['endMonth']
	currMonth = date.today().month
	
	cycleS = True if currMonth < rSMonth else False
	cycleE = True if currMonth < rEMonth else False
	sMonth = abs( currMonth - rSMonth )
	eMonth = abs( currMonth - rEMonth )

	invoices = Invoice.objects.all().order_by('-Date').values()
	total_sum = Invoice.objects.aggregate(Sum('Total'))

	if invoices is None or len( invoices ) <= 0 :
		return HttpResponse('Invoice not found',status=400)
	
	invs_y,invs = _get_invoices_by_year(invoices)
	curr_year = invs[0]['Date'].year
	if invs_y == 1 and cycleS and cycleE:
		return HttpResponse('Invalid Arguments',status=400)
	
	res = {
		'profit': []
	}

	for i in range( 0, len(invs)):
		rev = 0
		inv = invs[i]
		temp_date = inv['Date']
		temp_month = temp_date.month
		temp_year = temp_date.year
		
		if not cycleE and not cycleS:
			if curr_year is not temp_year :
				break
			if sMonth <= temp_month and eMonth >= temp_month:
				rev += inv['Balance_Due']
		elif cycleE and not cycleS:
			if eMonth >= temp_month and curr_year is temp_year:
				rev += inv['Balance_Due']
			elif sMonth <= temp_month and curr_year is not temp_year:
				rev += inv['Balance_Due']
		elif cycleS and cycleE:
			if sMonth <= temp_month and curr_year is not temp_year and eMonth >= temp_month:
				rev += inv['Balance_Due']
		res['profit'].append( total_sum - rev )

	return JsonResponse(res,safe=True)

@csrf_exempt
@post('accessToken','token','startMonth','endMonth','quantity')
def report_revenue(request):

	rSMonth = request.POST['startMonth']
	rEMonth = request.POST['endMonth']
	qty = request.POST['quantity']
	currMonth = date.today().month
	
	cycleS = True if currMonth < rSMonth else False
	cycleE = True if currMonth < rEMonth else False
	sMonth = abs( currMonth - rSMonth )
	eMonth = abs( currMonth - rEMonth )

	invoices = Invoice.objects.all().order_by('-Date').values()

	if invoices is None or len( invoices ) <= 0 :
		return HttpResponse('Invoice not found',status=400)
	
	invs_y,invs = _get_invoices_by_year(invoices)
	curr_year = invs[0]['Date'].year
	if invs_y == 1 and cycleS and cycleE:
		return HttpResponse('Invalid Arguments',status=400)
	
	res = {
		'revenue':[],
		'totalRevenue': 0
	}

	'''
	revPat = {
		'client':
		'revenue':
	}
	'''
	temp_rev = []

	rev = 0
	for i in range( 0, len(invs)):
		if qty is 0:
			break
		qty -= 1

		inv = invs[i]
		temp_date = inv['Date']
		temp_month = temp_date.month
		temp_year = temp_date.year
		clients = Client.objects.filter(Client_Id=inv['Client_Id_id']).values()
		if clients is None or len(clients) <= 0:
			return HttpResponse('Database is correpted', status=500)

		name = f"{clients[0]['Fname']} {clients[0]['Lname']}"
		rev_pat = {
			'client': name,
			'revenue': 0,
			'id' : clients[0]['Client_Id']
		} 

		idx = 0
		for i in range( 0, len( temp_rev ) ):
			r = temp_rev[i]
			if r['id'] is rev_pat['id']:
				rev_pat = r
				idx = i
				break
		if idx is 0:
			temp_rev.append(rev_pat)
			idx = len( temp_rev ) - 1
			
		if not cycleE and not cycleS:
			if curr_year is not temp_year :
				break
			if sMonth <= temp_month and eMonth >= temp_month:
				rev += inv['Balance_Due']
				rev_pat['revenue'] += inv['Balance_Due']
		elif cycleE and not cycleS:
			if eMonth >= temp_month and curr_year is temp_year:
				rev += inv['Balance_Due']
				rev_pat['revenue'] += inv['Balance_Due']
			elif sMonth <= temp_month and curr_year is not temp_year:
				rev += inv['Balance_Due']
				rev_pat['revenue'] += inv['Balance_Due']
		elif cycleS and cycleE:
			if sMonth <= temp_month and curr_year is not temp_year and eMonth >= temp_month:
				rev += inv['Balance_Due']
				rev_pat['revenue'] += inv['Balance_Due']

		res['totalRevenue'] = rev
		for r in temp_rev:
			rev_pat = {
				'client': r['client'],
				'revenue': r['revenue']
			}
			res['revenue'].append(rev_pat)

	return JsonResponse(res,safe=True)



def _get_expense_by_year(expenses):
	exps_y = [expenses[0]]
	exps = []
	curr_year = exps_y[0]['Date'].year
	flag = False
	for i in invoices:
		y = i['Date'].year
		exps.append(i)
		if y < curr_year:
			if flag :
				break
			exps_y.append(i)
			exps.append(i)
			curr_year = y
			flag = True
	return (len(exps_y),exps)


@csrf_exempt
@post('accessToken','token','startMonth','endMonth','quantity')
def report_expense(request):

	rSMonth = request.POST['startMonth']
	rEMonth = request.POST['endMonth']
	qty = request.POST['quantity']
	currMonth = date.today().month
	
	cycleS = True if currMonth < rSMonth else False
	cycleE = True if currMonth < rEMonth else False
	sMonth = abs( currMonth - rSMonth )
	eMonth = abs( currMonth - rEMonth )

	expense = Expense.objects.all().order_by('-Date').values()

	if expense is None or len( expense ) <= 0 :
		return HttpResponse('Expense not found',status=400)
	
	exps_y,exps = _get_expense_by_year(expense)
	curr_year = exps[0]['Date'].year
	if invs_y == 1 and cycleS and cycleE:
		return HttpResponse('Invalid Arguments',status=400)
	
	res = {
		'expense':[],
		'totalExpense': 0
	}

	'''
	revPat = {
		'vendor':
		'expense':
	}
	'''
	temp_rev = []

	rev = 0
	for i in range( 0, len(exps)):
		if qty is 0:
			break
		qty -= 1

		exps = exps[i]
		temp_date = exps['Date']
		temp_month = temp_date.month
		temp_year = temp_date.year
		vendor = Vendor.objects.filter(Vendor_Id=exps['Vendor_Id_id']).values()
		if vendor is None or len(vendor) <= 0:
			return HttpResponse('Database is correpted', status=500)

		name = vendor[0]['Vendor_Name']

		rev_pat = {
			'vendor': name,
			'expense': 0,
			'id' : vendor[0]['Vendor_Id']
		} 

		idx = 0
		for i in range( 0, len( temp_rev ) ):
			r = temp_rev[i]
			if r['id'] is rev_pat['id']:
				rev_pat = r
				idx = i
				break
		if idx is 0:
			temp_rev.append(rev_pat)
			idx = len( temp_rev ) - 1
			
		if not cycleE and not cycleS:
			if curr_year is not temp_year :
				break
			if sMonth <= temp_month and eMonth >= temp_month:
				rev += exps['Amount']
				rev_pat['expense'] += exps['Amount']
		elif cycleE and not cycleS:
			if eMonth >= temp_month and curr_year is temp_year:
				rev += exps['Amount']
				rev_pat['expense'] += exps['Amount']
			elif sMonth <= temp_month and curr_year is not temp_year:
				rev += exps['Amount']
				rev_pat['expense'] += exps['Amount']
		elif cycleS and cycleE:
			if sMonth <= temp_month and curr_year is not temp_year and eMonth >= temp_month:
				rev += exps['Amount']
				rev_pat['expense'] += exps['Amount']

		res['totalExpense'] = rev
		for r in temp_rev:
			rev_pat = {
				'vendor': r['vendor'],
				'expense': r['expense']
			}
			res['expense'].append(rev_pat)

	return JsonResponse(res,safe=True)
