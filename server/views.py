import django
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, FileResponse
from django.contrib.auth import authenticate, login, logout
from django.core import serializers
from . import models as m
import datetime
import json

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
	username = request.GET.get("username")
	password = request.GET.get("password")
	user = authenticate(username = username, password = password)

	if user:
		login(request, user)
		response = {}
		response["username"] = request.user.username
		response["user_id"] = request.user.id
		response["user_type"] = "Manager"
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
				response = {}
				response["message"] =  "Matching query does not exist"
				return JsonResponse(response, status = 400)
		except Exception as e:
			response = {}
			response["status"] = "Failed"
			response["message"] =  str(e)
			return JsonResponse(response, status = 400)

		return JsonResponse(response, status = 400)

def list_tenant(request):
	#9 - todo
	keywords = request.GET.dict()
	try:
		tenants = m.Tenant.objects.filter(**keywords)[:20]
		response = {}
		response =  serializers.serialize('json', tenants)
		return JsonResponse(response, safe = False)
	except Exception as e:
		return HttpResponse(str(e))

def list_store_temp(request):
	stores = m.Store.objects.all()
	response = [s.store_id for s in stores]
	return JsonResponse(response, safe = False)

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
		return HttpResponse(e)
		r = {}
		r["message"] = e
		return JsonResponse(r)

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
		return HttpResponse(e)
		r = {}
		r["message"] = e
		return JsonResponse(r)


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
			showcase_dict["rental_id"] = ""
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


def list_inventory(request):
	# 5.1
	try:
		inventories = m.Inventory.objects.all()
		msg = []
		if "store_id" in request.GET:
			store_id = request.GET.get("store_id")
			inventories = inventories.filter(from_showcase__store = store_id)
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
		stock_code = request.GET.get("stock_id")
		stock = m.Stock.objects.get(stock_code = stock_code)

		response = {}
		response["stock_id"] = stock.stock_code
		response["name"] = stock.name
		response["unit_price"] = float(stock.unit_price)
		response["description"] = stock.description
		response["is_on_hold"] = stock.is_on_hold
		return JsonResponse(response, status = 400)

	except Exception as e:
		return HttpResponse(e, status = 400)

def list_stock(request):

	#3, 5
	stocks = m.Stock.objects.all()
	msg = []
	try:
		for stock in stocks:
			stock_dict = {}
			stock_dict["stock_id"] = stock.stock_code
			stock_dict["name"] = stock.name
			stock_dict["unit_price"] = float(stock.unit_price)
			stock_dict["description"] = stock.description
			stock_dict["is_on_hold"] = stock.is_on_hold
			msg.append(stock_dict)
		response = {}
		response["stock_result"] = msg
		json_msg = json.dumps(response, indent=2)
		return HttpResponse(json_msg, content_type="application/json")

	except Exception as e:
		return HttpResponse(e, status = 400)


def create_stock(request):
	#6.3 Todo
	try:
		stock = m.Stock.objects.create(**request.GET.dict()) ##should return a queryset with 0 or 1 elements.
		return HttpResponse(stock.stock_code)
	except Exception as e:
		return HttpResponse(e, status = 400)

def update_stock(request):
	#6.3, 8
	try:
		stock_code = request.GET.get("stock_code")
		stock = m.Stock.objects.filter(stock_code = stock_code) ##should return a queryset with 0 or 1 elements.
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

def get_staff(request):
	#11.1
	staff_id = request.GET.get("staff_id")

	try:
		staff = m.Staff.objects.get(staff_id = staff_id)
		response = {}
		response["status"] = "Success"
		response["staff_id"] =  staff.staff_id
		response["staff_name"] =  staff.staff_name
		response["salary"] =  staff.current_salary
		response["staff_type"] =  staff.get_staff_type_display()
		return JsonResponse(response)
	except Exception as e:
		response = {}
		response["message"] = str(e)
		return JsonResponse(response)


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

def checkout(request):
	#8
	'''

	grant_total: float
	tender: float
	'''
	try:
		if request.user.is_staff:
			with django.db.transaction.atomic():
				receipt = m.Receipt.objects.create(**request.GET.dict())
				receipt.responsible = request.user
				receipt.change = receipt.grand_total - receipt.tender
				# receipt.save()
				return HttpResponse("Todo", status = 400)
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
