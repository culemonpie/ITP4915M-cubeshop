import django
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, FileResponse
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login, logout
from django.core import serializers
from . import models as m
from django.db.models import Q
import datetime
import json
from django.views.decorators.csrf import csrf_exempt


def get_user_subclass(user):
	try:
		staff = m.Staff.object.get(id = user.id)
		return staff
	except Exception as e:
		tenant = m.Tenant.object.get(id = user.id)
		return tenant

# Create your views here.
def index(request):
	#0
	if request.user.is_authenticated:
		return HttpResponse(request.user.username)
	else:
		return HttpResponse("Welcome")

def login_view(request):
	#1
	username = request.GET.get("username") or request.POST.get("username")
	password = request.GET.get("password") or request.POST.get("password")
	user = authenticate(username = username, password = password)

	if user:
		login(request, user)
		response = {}
		response["username"] = request.user.username
		response["user_id"] = request.user.id
		try:
			if request.user.is_staff:
				response["user_level"] = request.user.staff.get_user_level()
			else:
				response["user_level"] = 6
		except:
			response["user_level"] = 7
		return JsonResponse(response)
	else:
		response = {}
		response["message"] = "Incorrect password"
		return JsonResponse(response, status = 400)


def search(request):
	#global
	q = dict(request.GET.get("q"))

	result = user.objects.filter(username__startswith = q)

	response = {}
	response["status"] = "Success",
	response["result"] = serializers.serialize('json', [result])

	return JsonResponse(response, safe = True)

def logout_view(request):
	#global
	logout(request)
	return HttpResponse("Success")


def create_tenant(request):
	#3, 5
	tenant_name = request.GET.get("tenant_name")
	phone = request.GET.get("phone")
	address = request.GET.get("address")
	commission_rate = request.GET.get("commission_rate")

	username = request.GET.get("username")
	password = django.utils.crypto.get_random_string(length=6, allowed_chars='1234567890')

	with django.db.transaction.atomic():
		try:
			user = m.User.objects.create_user(username = username, password = password)
			user.save()
			tenant = m.Tenant(tenant_id = user.id, tenant_name = tenant_name, phone = phone, address = address, commission_rate = commission_rate, user = user)
			tenant.save()

			response = {}
			response["tenant_id"] = tenant.tenant_id
			response["password"] = password
			return JsonResponse(response)
		except Exception as e:
			return HttpResponse(e, status = 400)


def update_tenant(request):
	#9.1 - todo

	tenant_id = request.GET.get("tenant_id")

	with django.db.transaction.atomic():
		try:
			tenant = m.Tenant.objects.filter(tenant_id = tenant_id) ##should return a queryset with 0 or 1 elements.
			if tenant:
				val = request.GET.copy().dict()
				tenant.update(**val)
				response = {}
				response["status"] = "Success"
				response["tenant_id"] =  tenant.tenant_id
				response["tenant_name"] =  tenant.tenant_name
				response["phone"] =  tenant.phone
				response["address"] =  tenant.address
				response["date_joined"] =  tenant.date_joined
				response["balance"] =  tenant.balance
				response["commission_rate"] =  tenant.commission_rate
				return JsonResponse(response)
			else:
				message =  "Matching query does not exist"
				return HttpResponse(message, status = 400)

		except Exception as e:
			return HttpResponse(e, status = 400)


		return JsonResponse(response, status = 400)

def list_tenant(request):
	#9 - todo
	#3, 5
	tenants = m.Tenant.objects.all()
	msg = []
	try:
		for tenant in tenants:
			tenant_dict = {}
			tenant_dict["tenant_id"] =  tenant.tenant_id
			tenant_dict["tenant_name"] =  tenant.tenant_name
			tenant_dict["phone"] =  tenant.phone
			tenant_dict["address"] =  tenant.address
			tenant_dict["date_joined"] =  str(tenant.date_joined)
			tenant_dict["balance"] =  float(tenant.balance)
			tenant_dict["commission_rate"] =  float(tenant.commission_rate)
			tenant_dict["is_active"] =  True #tenant.is_active
			msg.append(tenant_dict)
		response = {}
		response["result"] = msg
		json_msg = json.dumps(response, indent=2)
		return HttpResponse(json_msg, content_type="application/json")
	except Exception as e:
		return HttpResponse(e, status = 400)

#
# def list_store_temp(request):
# 	stores = m.Store.objects.all()
# 	response = [s.store_id for s in stores]
# 	return JsonResponse(response, safe = False)

def get_tenant(request):
	#9.1
	tenant_id = request.GET.get("tenant_id")

	try:
		tenant = m.Tenant.objects.get(tenant_id = tenant_id)
		response = {}
		response["tenant_id"] =  tenant.tenant_id
		response["tenant_name"] =  tenant.tenant_name
		response["phone"] =  tenant.phone
		response["address"] =  tenant.address
		response["date_joined"] =  str(tenant.date_joined)
		response["balance"] =  float(tenant.balance)
		response["commission_rate"] =  float(tenant.commission_rate)
		response["is_active"] =  True #tenant.is_active
		json_msg = json.dumps(response, indent=2)
		return HttpResponse(json_msg, content_type="application/json")
	except Exception as e:
		return HttpResponse(e, status  = 400)

def list_store(request):
	#3, 5
	stores = m.Store.objects.all()
	msg = []
	try:
		for store in stores:
			store_dict = {}
			store_dict["store_id"] = store.store_id
			store_dict["name"] = store.store_name
			store_dict["address"] = store.address
			store_dict["usage"] = store.get_occupancy()
			if store.manager:
				store_dict["manager"] = store.manager.staff_name
			else:
				store_dict["manager"] = ""
			store_dict["is_active"] = store.is_active
			msg.append(store_dict)
		response = {}
		response["result"] = msg
		json_msg = json.dumps(response, indent=2)
		return HttpResponse(json_msg, content_type="application/json")
	except Exception as e:
		return HttpResponse(e, status = 400)


def get_store(request):
	#3.1
	try:
		store_id = request.GET.get("store_id")
		store = m.Store.objects.get(store_id= store_id)
		store_dict = {}
		store_dict["store_id"] = store.store_id
		store_dict["name"] = store.store_name
		store_dict["address"] = store.address
		store_dict["usage"] = store.get_occupancy()
		if store.manager:
			store_dict["manager"] = store.manager.staff_name
		else:
			store_dict["manager"] = ""
		store_dict["is_active"] = store.is_active
		json_msg = json.dumps(store_dict, indent=2)
		return HttpResponse(json_msg, content_type="application/json")
	except Exception as e:
		return HttpResponse(e, status = 400)

def list_showcase(request):
	#3.1, 4
	showcases = m.Showcase.objects.all()
	if "store_id" in request.GET:
		store_id = request.GET.get("store_id")
		showcases = showcases.filter(store_id = store_id)

	if "showcase_id" in request.GET:
		showcase_id = request.GET.get("showcase_id")
		showcases = showcases.filter(showcase_id = showcase_id)


	msg = []
	try:
		for showcase in showcases:
			showcase_dict = {}
			showcase_dict["showcase_id"] = showcase.showcase_id
			showcase_dict["store"] = showcase.store.store_id
			showcase_dict["type"] = showcase.get_showcase_type_display()
			if showcase.showcaserental_set.all():
				showcase_dict["rental_id"] = showcase.showcaserental_set.last().id
			else:
				showcase_dict["rental_id"] = None
			json_msg = json.dumps(showcase_dict, indent=2)
			msg.append(showcase_dict)
		response = {}
		response["result"] = msg
		json_msg = json.dumps(response, indent=2)
		return HttpResponse(json_msg, content_type="application/json")
	except Exception as e:
		return HttpResponse(e, status = 400)

def update_store(request):
	#3.2
	try:
		store_id = request.GET.get("store_id")
		store = m.Store.objects.filter(store_id = store_id) ##should return a queryset with 0 or 1 elements.
		if store:
			val = request.GET.copy().dict()
			store.update(**val)
			return HttpResponse("Success")
		else:
			return HttpResponse("Object not found", status = 400)
	except Exception as e:
		return HttpResponse(e, status = 400)

def create_store(request):
	#3.3
	try:
		store_id = request.GET.get("store_id")
		val = request.GET.copy().dict()
		store = m.Store.objects.create(**val) ##should return a queryset with 0 or 1 elements.
		return HttpResponse("Success")
	except Exception as e:
		return HttpResponse(e, status = 400)

def get_showcase(request):
	#4.1
	try:
		showcase_id = request.GET.get("showcase_id")
		showcase = m.Showcase.objects.get(showcase_id = showcase_id) ##should return a queryset with 0 or 1 elements.
		showcase_dict = {}
		showcase_dict["showcase_id"] = showcase.showcase_id
		showcase_dict["store"] = showcase.store.store_id
		showcase_dict["type"] = showcase.get_showcase_type_display()
		if showcase.showcaserental_set.all():
			showcase_dict["rental_id"] = showcase.showcaserental_set.last().id
		else:
			showcase_dict["rental_id"] = None
		json_msg = json.dumps(showcase_dict, indent=2)
		return HttpResponse(json_msg, content_type="application/json")
	except Exception as e:
		return HttpResponse(e, status = 400)

def create_showcase(request):
	#4.2
	try:
		showcase = m.Showcase.objects.create(**request.GET.dict()) ##should return a queryset with 0 or 1 elements.
		return HttpResponse(showcase.showcase_id)
	except Exception as e:
		return HttpResponse(e, status = 400)

def update_showcase(request):
	#4.3
	try:
		showcase_id = request.GET.get("showcase_id")
		showcase = m.Showcase.objects.filter(showcase_id = showcase_id) ##should return a queryset with 0 or 1 elements.
		if showcase:
			val = request.GET.copy().dict()
			showcase.update(**val)
			return HttpResponse("Success")
		else:
			return HttpResponse("Object not found", status = 400)
	except Exception as e:
		return HttpResponse(e, status = 400)

def rent_showcase(request):
	#4.4
	try:
		with django.db.transaction.atomic():
			showcase_rental = m.ShowcaseRental.objects.create(**request.GET.dict()) ##should return a queryset with 0 or 1 elements.
			showcase_rental.save()
			showcase = showcase_rental.showcase
			showcase.showcase_type = showcase_rental.showcase_type
			showcase.save()
			return HttpResponse(showcase_rental.id)

	except Exception as e:
		return HttpResponse(e, status = 400)

def set_showcase_status(request):
	# 4.5
	try:
		showcase_id = request.GET.get("showcase_id")
		showcase_type = request.GET.get("showcase_type")

		with django.db.transaction.atomic():
			showcase = m.Showcase.objects.get(showcase_id = showcase_id)
			showcase.showcase_type = showcase_type
			showcase.save()
			return HttpResponse(showcase.showcase_id)

	except Exception as e:
		return HttpResponse(e, status = 400)

def list_rental(request):
	try:
		rentals = m.ShowcaseRental.objects.all()
		msg = []
		if "showcase_id" in request.GET:
			store_id = request.GET.get("store_id")
			rentals = rental.filter(showcase_id = store_id)
		for rental in rentals:
			rental_dict = {}
			rental_dict["name"] = rental.name
			rental_dict["starting_date"] = str(rental.starting_date)
			rental_dict["ending_date"] = str(rental.ending_date)
			rental_dict["monthly_rent"] = float(rental.monthly_rent)
			rental_dict["showcase_type"] = rental.get_showcase_type_display()
			rental_dict["remark"] = rental.remark
			msg.append(rental_dict)
		response = {}
		response["result"] = msg
		json_msg = json.dumps(response, indent=2)
		return HttpResponse(json_msg, content_type="application/json")
	except Exception as e:
		return HttpResponse(e)


def list_inventory(request):
	# 5.1
	try:
		inventories = m.Inventory.objects.all()
		msg = []
		if "from_showcase_id" in request.GET:
			from_showcase_id = request.GET.get("from_showcase_id")
			inventories = inventories.filter(from_showcase_id = from_showcase_id)
		for inventory in inventories:
			inventory_dict = {}
			inventory_dict["inventory_id"] = inventory.inventory_id
			if inventory.from_showcase:
				inventory_dict["from_showcase"] = inventory.from_showcase.showcase_id
			else:
				inventory_dict["from_showcase"] = ""
			inventory_dict["name"] = inventory.from_stock.name
			inventory_dict["unit_price"] = float(inventory.unit_price)
			inventory_dict["current_stock"] = inventory.stock_in_qty
			msg.append(inventory_dict)
		response = {}
		response["result"] = msg
		json_msg = json.dumps(response, indent=2)
		return HttpResponse(json_msg, content_type="application/json")
	except Exception as e:
		return HttpResponse(e)

def create_inventory(request):
	try:
		inventory = m.Inventory.objects.create(**request.GET.dict())
		inventory.save()
		return HttpResponse(inventory.inventory_id, status = 400)
	except Exception as e:
		return HttpResponse(e, status = 400)

def change_inventory_quantity(request):
	# 5.1
	#todo: 話返啲貨喺邊度入
	try:
		with django.db.transaction.atomic():
			inventory_id = request.GET.get("inventory_id")
			changed_quantity = request.GET.get("changed_quantity")
			inventory = m.Inventory.objects.get(inventory_id = inventory_id)
			inventory.stock_in_qty += int(changed_quantity)
			# if inventory.stock_in_qty <= 0: inventory.stock_in_qty=0
			inventory.save()
			response = {}
			response["inventory_id"] = inventory.inventory_id
			json_msg = json.dumps(response, indent=2)
			return HttpResponse(json_msg, content_type="application/json")
	except Exception as e:
		return HttpResponse(e)

def get_stock(request):
	#6.1
	try:
		stock_id = request.GET.get("stock_id")
		stock = m.Stock.objects.get(stock_id = stock_id)

		response = {}
		response["stock_id"] = stock.stock_id
		response["name"] = stock.name
		response["unit_price"] = 0 #deprecarted
		response["description"] = stock.description
		response["is_on_hold"] = False #deprecarted
		return JsonResponse(response)

	except Exception as e:
		return HttpResponse(e, status = 400)

def list_stock(request):

	#3, 5
	try:
		stocks = m.Stock.objects.all()
		msg = []
		if "q" in request.GET:
			q = request.GET.get("q")
			stocks = stocks.filter(Q(stock_id__icontains=q)|Q(name__icontains=q))

		for stock in stocks:
			stock_dict = {}
			stock_dict["stock_id"] = stock.stock_id
			stock_dict["name"] = stock.name
			stock_dict["unit_price"] = 0
			stock_dict["description"] = stock.description
			stock_dict["is_on_hold"] = False #deprecated
			msg.append(stock_dict)
		response = {}
		response["stock_result"] = msg
		json_msg = json.dumps(response, indent=2)
		return HttpResponse(json_msg, content_type="application/json")

	except Exception as e:
		return HttpResponse(e, status = 400)

	staff_id = request.GET.get("staff_id")

def get_inventory(request):
	# try:
		inventory_id = request.GET.get("inventory_id")
		inventory = m.Inventory.objects.get(inventory_id = inventory_id)
		response = {}
		response["inventory_id"] =  inventory.inventory_id
		response["unit_price"] =  float(inventory.unit_price)
		response["stock_in_qty"] =  inventory.stock_in_qty
		response["remark"] =  inventory.remark or ""
		response["stock_id"] =  inventory.from_stock_id
		response["name"] =  inventory.from_stock.name
		response["showcase_id"] =  inventory.from_showcase_id
		json_msg = json.dumps(response, indent=2)
		return HttpResponse(json_msg, content_type="application/json")
	# except Exception as e:
	# 	return HttpResponse(e, status = 400)

def create_stock(request):
	#6.3 Todo
	try:
		stock = m.Stock.objects.create(**request.GET.dict()) ##should return a queryset with 0 or 1 elements.
		return HttpResponse(stock.stock_id)
	except Exception as e:
		return HttpResponse(e, status = 400)

def update_stock(request):
	#6.3, 8
	try:
		stock_id = request.GET.get("stock_id")
		stock = m.Stock.objects.filter(stock_id = stock_id) ##should return a queryset with 0 or 1 elements.
		if stock:
			val = request.GET.copy().dict()
			stock.update(**val)
			return HttpResponse("Success")
		else:
			return HttpResponse("Object not found", status = 400)
	except Exception as e:
		return HttpResponse(e, status = 400)

def get_profile(request):
	try:

		if request.user.is_authenticated:
			try:
				if request.user.staff:
					name = request.user.staff.staff_name
					type = request.user.staff.get_staff_type_display()
			except:
				name = request.user.tenant.tenant_name
				type = "Tenant"
			response = {
				"name": name,
				"username": request.user.username,
				"date_joined": request.user.date_joined,
				"type": type,
			}

			return JsonResponse(response)
		else:
			return HttpResponse("User not logged in", status = 400)
	except Exception as e:
		return HttpResponse(e, status = 400)


def list_staff(request):
	#3.1, 4
	staff_members = m.Staff.objects.all()

	msg = []
	try:
		for staff in staff_members:
			staff_dict = {}
			staff_dict["status"] = "Success"
			staff_dict["staff_id"] =  staff.staff_id
			staff_dict["staff_name"] =  staff.staff_name
			staff_dict["salary"] =  float(staff.current_salary)
			staff_dict["staff_type"] =  staff.get_staff_type_display()
			json_msg = json.dumps(staff_dict, indent=2)
			msg.append(staff_dict)
		response = {}
		response["result"] = msg
		json_msg = json.dumps(response, indent=2)
		return HttpResponse(json_msg, content_type="application/json")
	except Exception as e:
		return HttpResponse(e, status = 400)


def get_staff(request):
	#11.1
	staff_id = request.GET.get("staff_id")

	try:
		staff = m.Staff.objects.get(staff_id = staff_id)
		response = {}
		response["staff_id"] =  staff.staff_id
		response["staff_name"] =  staff.staff_name
		response["salary"] =  float(staff.current_salary)
		response["staff_type"] =  staff.get_staff_type_display()
		return JsonResponse(response)
	except Exception as e:
		return HttpResponse(e, status = 400)

def create_staff(request):
	#11.2
	'''
	username
	current_salary
	staff_type
	store (optional)
	'''
	username = request.GET.get("username")
	current_salary = request.GET.get("current_salary")
	staff_name = request.GET.get("staff_name")
	staff_type = request.GET.get("staff_type")
	store_id = request.GET.get("store")

	password = django.utils.crypto.get_random_string(length=6, allowed_chars='1234567890')

	with django.db.transaction.atomic():
		try:
			user = m.User.objects.create_user(username = username, password = password)
			user.save()
			staff = m.Staff(staff_id = user.id, staff_name = staff_name,  user = user, current_salary = current_salary, staff_type = staff_type, store_id = store_id)
			staff.save()

			response = {}
			response["staff_id"] = staff.staff_id
			response["password"] = password
			return JsonResponse(response)
		except Exception as e:
			return HttpResponse(e, status = 400)


def update_staff(request):
	#11.3
	'''
	username
	current_salary
	staff_type
	store (optional)
	'''
	staff_id = request.GET.get("staff_id")

	current_salary = request.GET.get("current_salary")
	staff_name = request.GET.get("staff_name")
	staff_type = request.GET.get("staff_type")
	store_id = request.GET.get("store")

	with django.db.transaction.atomic():
		try:
			user = m.User.objects.get(id = staff_id) ## not used?
			staff = m.Staff.objects.get(staff_id = user.id)
			if current_salary: staff.current_salary = current_salary
			if staff_type: staff.staff_type = staff_type
			if store_id: staff.store_id = store_id
			staff.save()
			response = {}
			response["staff_id"] = staff.staff_id
			return JsonResponse(response)
		except Exception as e:
			return HttpResponse(e, status = 400)


def list_receipt(request):
	#9 - todo
	#3, 5
	receipts = m.Receipt.objects.all()
	msg = []
	try:
		for receipt in receipts:
			receipt_dict = {}
			receipt_dict["id"] =  receipt.id
			receipt_dict["store"] =  "Kwai Fong"
			receipt_dict["time"] =  str(receipt.time)
			receipt_dict["grand_total"] =  float(receipt.grand_total)
			receipt_dict["tender"] =  float(receipt.tender)
			receipt_dict["change"] =  float(receipt.change)
			receipt_dict["responsible"] =  receipt.responsible.staff_name
			msg.append(receipt_dict)
		response = {}
		response["result"] = msg
		json_msg = json.dumps(response, indent=2)
		return HttpResponse(json_msg, content_type="application/json")
	except Exception as e:
		return HttpResponse(e, status = 400)



def get_receipt(request):
	'''
	12.1
	receipt_id
	'''

	try:
		id = request.GET.get("id")
		receipt = m.Receipt.objects.get(id = id)
		response = {}
		response["id"] = receipt.id
		response["grand_total"] = float(receipt.grand_total)
		response["time"] = str(receipt.time)
		response["tender"] = float(receipt.tender)
		response["change"] = float(receipt.change)
		response["responsible"] = receipt.responsible.staff_name
		response["purchase"] = []
		for purchase in receipt.purchase_set.all():
			purchase_dict = {}
			purchase_dict["quantity"] = purchase.quantity
			purchase_dict["amount"] = float(purchase.amount)
			purchase_dict["remark"] = purchase.remark
			purchase_dict["stock_name"] = purchase.inventory.from_stock.name
			response["purchase"].append(purchase_dict)
		json_msg = json.dumps(response, indent=2)
		return HttpResponse(json_msg, content_type="application/json")
	except Exception as e:
		return HttpResponse(e, status = 400)

def get_receipt_print(request):
	try:
		id = request.GET.get("id")
		receipt = m.Receipt.objects.get(id = id)
		context = {
			"receipt": receipt,
		}
		msg = render_to_string("server/receipt.txt", context).replace("\n","<br>")
		return HttpResponse(msg)
	except Exception as e:
		return HttpResponse(e, status = 400)


def change_password(request):
	#7.4
	try:
		user = request.user
		if not request.user.is_authenticated:
			return HttpResponse("User not logged in", status = 400)
		original_password = request.GET.get("original_password")
		new_password = request.GET.get("new_password")
		print (f"username: {user.username}, password: {original_password}, new_password: {new_password}")
		if authenticate(username = user.username, password = original_password):
			user.set_password(new_password)
			user.save()
			return HttpResponse("Success")
		else:
			return HttpResponse("Original password is incorrect.", status = 400)
	except Exception as e:
		return HttpResponse(e, status = 400)


@csrf_exempt
def checkout(request):
	#8
	'''

	grant_total: float
	tender: float
	'''
	try:
		if request.user.is_staff:
			with django.db.transaction.atomic():
				payload_content = request.POST.get("data")
				# payload_content = r'{"result":[{"inventory_id":6,"quantity":2,"amount":30},{"inventory_id":1,"quantity":3,"amount":294}],"total":304,"discount":20,"tender":400}'
				if True or request.method == "POST":

					result_dict = json.loads(payload_content)
					msg = ""
					receipt = m.Receipt()
					receipt.grand_total = result_dict['total']
					receipt.tender = result_dict['tender']
					receipt.discount = result_dict['discount']
					receipt.change = receipt.tender - receipt.grand_total
					receipt.responsible = request.user.staff
					receipt.save()
					for inventory_string in result_dict["result"]:
						purchase = m.Purchase()
						purchase.quantity = inventory_string['quantity']
						purchase.amount = inventory_string['amount']
						purchase.inventory_id = inventory_string['inventory_id']
						purchase.receipt = receipt
						purchase.save()

						inventory = purchase.inventory
						inventory.stock_in_qty -= purchase.quantity
						inventory.save()

						tenant = inventory.from_showcase.from_tenant
						tenant.balance += purchase.amount * tenant.commission_rate / 100
						tenant.save()

						## todo:
						msg += f"{inventory_string['inventory_id']} - {inventory_string['quantity']} - {inventory_string['amount']}\n"
					msg += f"Total - {receipt.grand_total}\nDiscount - {receipt.discount}\ntender: {result_dict['tender']}"

					return HttpResponse(msg)
				else:
					return HttpResponse(status = 405)
		else:
			return HttpResponse("Please login as a staff to perform checkout", status = 400)
	except Exception as e:
		return HttpResponse(e, status = 400)

def is_authenticated(request):
	if request.user.is_authenticated:
		msg = f"Logged in as {request.user}"
	else:
		msg = f"Anonymous"
	return HttpResponse(msg)

def todo(request):
	return HttpResponse("Todo")

def test_db_integrity(request):
	if request.user.is_superuser:
		users = m.User.objects.filter()
		count = 0
		msg = ""
		for user in users:
			if user.is_staff:
				if user.id !=user.staff.staff_id: ##ensure that all staff has a staff subclass
					raise(ValueError)
				count+=1
				msg+=f"{user.id}, {user.staff.staff_id}\n"

			else:
				msg+=f"{user.id}, {user.tenant.tenant_id}\n"
				# if user.id != user.tenant.tenant_id: ##ensure that all staff has a staff subclass
					# raise(ValueError, f"{user.tenant.tenant_id}")
				count+=1
					# user.delete()
		msg += f"Successfully checked {count} records\n"
		return HttpResponse(msg)
	else:
		return HttpResponse("Please login as a superuser", status = 400)

def test_json(request):
	response = {

	}
	return HttpResponse("Success")

@csrf_exempt
def test_post(request):

	print (request.POST)

	return HttpResponse(request.method)
