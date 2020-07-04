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
from django.core.mail import send_mail
import decimal
from django.contrib.auth.decorators import login_required
from urllib.request import urlopen

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

@csrf_exempt
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

			context = {
				'username': username,
				'password': password,
			}

			send_mail(
			'Thank you for registering on HKCS',
			render_to_string("server/register_email.txt", context) ,
			'HKFingerprint@gmail.com',
			[tenant.address],
			fail_silently=True,
			)

			return JsonResponse(response)
		except Exception as e:
			return HttpResponse(e, status = 400)

def tenant_topup(request):
	try:
		tenant_id = request.GET.get("tenant_id")
		amount = decimal.Decimal(request.GET.get("amount"))
		tenant = m.Tenant.objects.get(tenant_id = tenant_id)
		if amount > 0:
			tenant.balance += amount
			tenant.save()
		else:
			raise ValueError("Value must be larger than 0")
		return HttpResponse(tenant.balance)
	except Exception as e:
		return HttpResponse(e, status = 400)

def tenant_cashout(request):
	try:
		tenant_id = request.GET.get("tenant_id")
		amount = decimal.Decimal(request.GET.get("amount"))
		tenant = m.Tenant.objects.get(tenant_id = tenant_id)
		if amount > 0:
			tenant.balance -= amount
			tenant.save()
		else:
			raise ValueError("Value must be larger than 0")
		return HttpResponse(tenant.balance)
	except Exception as e:
		return HttpResponse(e, status = 400)



def update_tenant(request):
	#9.1 - todo

	tenant_id = request.GET.get("tenant_id")

	with django.db.transaction.atomic():
		try:
			tenants = m.Tenant.objects.filter(tenant_id = tenant_id) ##should return a queryset with 0 or 1 elements.
			if tenants:
				tenants.update(**request.GET.dict())
				return HttpResponse(tenant_id)
			else:
				message =  "Matching query does not exist"
				return HttpResponse(message, status = 400)

		except Exception as e:
			return HttpResponse(e, status = 400)


		return JsonResponse(response, status = 400)

def get_balance(request):
	try:
		if request.user.is_staff:
			return HttpResponse("/", status = 400)
		else:
			return HttpResponse(request.user.tenant.balance)
	except:
		return HttpResponse("/");



def list_tenant(request):
	#9 - todo
	#3, 5
	tenants = m.Tenant.objects.all()

	if "q" in request.GET:
		q = request.GET["q"]
		tenants = tenants.filter(Q(tenant_id__icontains = q)|Q(tenant_name__icontains = q))

	msg = []
	try:
		for tenant in tenants:
			tenant_dict = {}
			tenant_dict["tenant_id"] =  tenant.tenant_id
			tenant_dict["tenant_name"] =  tenant.tenant_name
			tenant_dict["phone"] =  tenant.phone
			tenant_dict["address"] =  tenant.address
			tenant_dict["date_joined"] =  tenant.date_joined.strftime("%Y-%m-%d %H:%M")
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
		response["date_joined"] = tenant.date_joined.strftime("%Y-%m-%d %H:%M")
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

	if "q" in request.GET:
		showcases = showcases.filter(showcase_id__icontains=request.GET["q"])

	if request.user.is_staff:
		if "store_id" in request.GET:
			store_id = request.GET.get("store_id")
			showcases = showcases.filter(store_id = store_id)

		if "showcase_id" in request.GET:
			showcase_id = request.GET.get("showcase_id")
			showcases = showcases.filter(showcase_id = showcase_id)
	else:
		try:
			showcases = showcases.filter(from_tenant__user_id = request.user.id)
		except Exception as e:
			print (e)



	msg = []
	try:
		for showcase in showcases:
			showcase_dict = {}
			showcase_dict["showcase_id"] = showcase.showcase_id
			showcase_dict["store"] = showcase.store.store_id
			showcase_dict["type"] = showcase.get_showcase_type_display()
			showcase_dict["current_rent"] = float(showcase.current_rent)
			if showcase.showcaserental_set.all():
				showcase_dict["rental_id"] = showcase.showcaserental_set.last().id
				# showcase_dict["current_rent"] = showcase.showcaserental_set.last().current_rent
				showcase_dict["owner"] = showcase.showcaserental_set.last().tenant.tenant_name
				showcase_dict["owner_id"] = showcase.showcaserental_set.last().tenant.tenant_id
			else:
				showcase_dict["rental_id"] = None
				showcase_dict["owner_id"] = None
				showcase_dict["owner"] = None
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
		# store_id = request.GET.get("store_id")
		with django.db.transaction.atomic():
			val = request.GET.copy().dict()
			store = m.Store.objects.create(**val) ##should return a queryset with 0 or 1 elements.
			return HttpResponse(store.store_id)
		return HttpResponse("Error", status = 400)
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
		showcase_dict["current_rent"] = float(showcase.current_rent)

		if showcase.showcaserental_set.all():
			showcase_dict["rental_id"] = showcase.showcaserental_set.last().id
			# showcase_dict["current_rent"] = showcase.showcaserental_set.last().current_rent
			showcase_dict["owner"] = showcase.showcaserental_set.last().tenant.tenant_name
			showcase_dict["owner_id"] = showcase.showcaserental_set.last().tenant.tenant_id
		else:
			showcase_dict["rental_id"] = None
			showcase_dict["owner_id"] = None
			showcase_dict["owner"] = None

		if showcase.showcaserental_set.all():
			showcase_dict["rental_id"] = showcase.showcaserental_set.last().id
		else:
			showcase_dict["rental_id"] = 0

		showcase_dict["inventory"] = []

		for inventory in showcase.inventory_set.all():
			inventory_dict = {}
			inventory_dict["name"] = inventory.from_stock.name
			inventory_dict["quantity"] = inventory.stock_in_qty
			inventory_dict["unit_price"] = float(inventory.unit_price)
			showcase_dict["inventory"].append(inventory_dict)

		json_msg = json.dumps(showcase_dict, indent=2)
		return HttpResponse(json_msg, content_type="application/json")
	except Exception as e:
		return HttpResponse(e, status = 400)

def get_showcase_sales(request):
	try:
		showcase_id = request.GET.get("showcase_id")
		showcase = m.Showcase.objects.get(showcase_id = showcase_id) ##should return a queryset with 0 or 1 elements.
		msg = ""

		with django.db.connection.cursor() as cursor:
			sql = f"select server_purchase.id from server_purchase inner join server_inventory on server_purchase.inventory_id = server_inventory.inventory_id where from_showcase_id = '{showcase_id}'"
			print (sql)
			cursor.execute(sql)

			sql_result = cursor.fetchall()
			# sql_result = [] #safe even when it's empty
			sql_result_list = [i[0] for i in sql_result]

			purchases = m.Purchase.objects.filter(id__in = sql_result_list)

		return HttpResponse(str(msg))
	except Exception as e:
		return HttpResponse(e, status = 400)


def view_tenant_statement(request):
	try:
		tenant_id = request.GET.get("tenant_id")
		starting_date = request.GET.get("starting_date")
		ending_date = request.GET.get("ending_date")

		tenant = m.Tenant.objects.get(tenant_id = tenant_id)
		# return HttpResponse("Success")
		with django.db.connection.cursor() as cursor:

			response = {}

			sql = f"select sum(amount) from server_receipt\
			inner join server_purchase on server_receipt.id = server_purchase.receipt_id\
			inner join server_inventory on server_purchase.inventory_id = server_inventory.inventory_id\
			inner join server_stock on server_inventory.from_stock_id = server_stock.`stock_id`\
			inner join server_tenant on server_tenant.tenant_id = server_inventory.owner_id\
			inner join server_showcase on server_inventory.from_showcase_id = server_showcase.showcase_id\
			where time between '{starting_date}' and '{ending_date}'+ INTERVAL 1 DAY and tenant_id = {tenant_id} and server_purchase.is_cancelled = 0\
			"
			cursor.execute(sql)
			income = cursor.fetchone()
			response["income"] = float(income[0] or 0)


			sql = f"select sum(monthly_rent) from server_showcaserental\
			where tenant_id = '{tenant_id}' and starting_date between '{starting_date}' and '{ending_date}' + INTERVAL 1 DAY "
			cursor.execute(sql)
			rent = cursor.fetchone()
			response["rent"] = float(rent[0] or 0)

			response["payable"] = response["income"] - response["rent"]
			response["balance"] = float(tenant.balance)

			sql = f"select server_showcase.store_id, server_receipt.time, server_stock.name, server_purchase.quantity, server_purchase.amount from server_receipt\
			inner join server_purchase on server_receipt.id = server_purchase.receipt_id\
			inner join server_inventory on server_purchase.inventory_id = server_inventory.inventory_id\
			inner join server_stock on server_inventory.from_stock_id = server_stock.`stock_id`\
			inner join server_tenant on server_tenant.tenant_id = server_inventory.owner_id\
			inner join server_showcase on server_inventory.from_showcase_id = server_showcase.showcase_id\
			where time between '{starting_date}' and '{ending_date}' + INTERVAL 1 DAY and tenant_id = '{tenant_id}' and server_purchase.is_cancelled = 0"

			cursor.execute(sql)
			sql_result = cursor.fetchall()
			# return JsonResponse(response, safe = False)
			response["record"] = []
			for record in sql_result:
				record_dict = {}
				record_dict["store_id"] = record[0]
				record_dict["datetime"] = record[1].strftime("%Y-%m-%d %H:%M")
				record_dict["name"] = record[2]
				record_dict["quantity"] = float(record[3])
				record_dict["amount"] = float(record[4])

				# record_dict = str(record)
				# record_dict["total"] = record[3]
				response["record"].append(record_dict)

			json_msg = json.dumps(response, indent=2)
			return HttpResponse(json_msg, content_type="application/json")

		return HttpResponse("Success")
	except Exception as e:
		return HttpResponse(e, status = 400)

def email_tenant_statement(request):
	try:
		tenant_id = request.GET.get("tenant_id")
		starting_date = request.GET.get("starting_date")
		ending_date = request.GET.get("ending_date")

		response = {}

		tenant = m.Tenant.objects.get(tenant_id = tenant_id)
		with django.db.connection.cursor() as cursor:

			sql = f"select sum(amount) from server_receipt\
			inner join server_purchase on server_receipt.id = server_purchase.receipt_id\
			inner join server_inventory on server_purchase.inventory_id = server_inventory.inventory_id\
			inner join server_stock on server_inventory.from_stock_id = server_stock.`stock_id`\
			inner join server_tenant on server_tenant.tenant_id = server_inventory.owner_id\
			inner join server_showcase on server_inventory.from_showcase_id = server_showcase.showcase_id\
			where time between '{starting_date}' and '{ending_date}'+ INTERVAL 1 DAY and tenant_id = {tenant_id} and server_purchase.is_cancelled = 0\
			"
			cursor.execute(sql)
			income = cursor.fetchone()
			response["income"] = float(income[0] or 0)


			sql = f"select sum(monthly_rent) from server_showcaserental\
			where tenant_id = '{tenant_id}' and starting_date between '{starting_date}' and '{ending_date}' + INTERVAL 1 DAY "
			cursor.execute(sql)
			rent = cursor.fetchone()
			response["rent"] = float(rent[0] or 0)

			response["payable"] = response["income"] - response["rent"]
			response["balance"] = float(tenant.balance)

			response["tenant_name"] = tenant.tenant_name
			response["starting_date"] = starting_date
			response["ending_date"] = ending_date

			sql = f"select server_showcase.store_id, server_receipt.time, server_stock.name, server_purchase.quantity, server_purchase.amount from server_receipt\
			inner join server_purchase on server_receipt.id = server_purchase.receipt_id\
			inner join server_inventory on server_purchase.inventory_id = server_inventory.inventory_id\
			inner join server_stock on server_inventory.from_stock_id = server_stock.`stock_id`\
			inner join server_tenant on server_tenant.tenant_id = server_inventory.owner_id\
			inner join server_showcase on server_inventory.from_showcase_id = server_showcase.showcase_id\
			where time between '{starting_date}' and '{ending_date}' + INTERVAL 1 DAY and tenant_id = '{tenant_id}' and server_purchase.is_cancelled = 0"

			cursor.execute(sql)
			sql_result = cursor.fetchall()
			# return JsonResponse(response, safe = False)
			response["record"] = []
			for record in sql_result:
				record_dict = {}
				record_dict["store_id"] = record[0]
				record_dict["datetime"] = record[1].strftime("%Y-%m-%d %H:%M")
				record_dict["name"] = record[2]
				record_dict["quantity"] = float(record[3])
				record_dict["amount"] = float(record[4])


			msg = render_to_string("server/view_tenant_statement.txt", response)
			# return HttpResponse(msg)

			send_mail(
			'Your statement',
			msg ,
			'HKFingerprint@gmail.com',
			[tenant.address],
			fail_silently=True,
			)

		return HttpResponse("Success")
	except Exception as e:
		return HttpResponse(e, status = 400)


def get_tenant_sales(request):
	#4.1
	try:
		tenant_id = request.GET.get("tenant_id")
		products = []
		for purchase in m.Purchase.objects.all():
			pass
			# if purchase.inventory.from_showcas
		# showcase = m.Showcase.objects.get(showcase_id = showcase_id) ##should return a queryset with 0 or 1 elements.



		# showcase_dict = {}
		# showcase_dict["showcase_id"] = showcase.showcase_id
		# showcase_dict["store"] = showcase.store.store_id
		# showcase_dict["type"] = showcase.get_showcase_type_display()
		# if showcase.showcaserental_set.all():
		# 	showcase_dict["rental_id"] = showcase.showcaserental_set.last().id
		# else:
		# 	showcase_dict["rental_id"] = None
		# json_msg = json.dumps(showcase_dict, indent=2)
		# return HttpResponse(json_msg, content_type="application/json")
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
			showcase.from_tenant = showcase_rental.tenant
			showcase.current_rent = showcase_rental.monthly_rent
			showcase.save()
			showcase_rental.tenant.balance -= decimal.Decimal(showcase_rental.monthly_rent)
			showcase_rental.tenant.save()

			return HttpResponse(showcase_rental.id)

	except Exception as e:
		return HttpResponse(e, status = 400)

def deactive_showcase(request):
	#todo
	try:
		with django.db.transaction.atomic():
			showcase_id = request.GET.get("showcase_id")
			return HttpResponse(showcase.showcase_id)

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

def list_rental_records(request):
	try:
		showcase_id = request.GET.get("showcase_id")
		showcase = m.Showcase.objects.get(showcase_id = showcase_id)
		response = {}
		response["result"] = []
		for rental in showcase.showcaserental_set.all():
			rental_dict = {}
			rental_dict["name"] = rental.name
			rental_dict["starting_date"] = str(rental.starting_date)
			rental_dict["ending_date"] = str(rental.ending_date)
			rental_dict["monthly_rent"] = float(rental.monthly_rent)
			rental_dict["showcase_type"] = rental.get_showcase_type_display()
			rental_dict["remark"] = rental.remark
			response["result"].append(rental_dict)

		json_msg = json.dumps(response, indent=2)
		return HttpResponse(json_msg, content_type="application/json")

	except Exception as e:
		return HttpResponse(e, status = 400)

# @login_required
def list_inventory(request):
	# 5.1
	try:
		inventories = m.Inventory.objects.all()

		if "q" in request.GET:
			q = request.GET.get("q")
			inventories = inventories.filter(Q(inventory_id__icontains=q)|Q(from_stock__name__icontains=q))

		if not request.user.is_staff:
			inventories = inventories.filter(owner_id = request.user.id)

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

# @login_required
def create_inventory(request):
	try:
		inventory = m.Inventory.objects.create(**request.GET.dict())
		inventory.save()
		return HttpResponse(inventory.inventory_id, status = 400)
	except Exception as e:
		return HttpResponse(e, status = 400)

def create_inventory_quick(request):
	try:
		# tenant_id = request.GET.get("tenant_id")
		showcase_id = request.GET.get("showcase_id")
		unit_price = request.GET.get("unit_price")
		quantity = request.GET.get("quantity")
		stock_name = request.GET.get("stock_name")
		# type = request.GET.get("type")

		with django.db.transaction.atomic():
			# tenant = m.Tenant.objects.get(tenant_id = tenant_id)
			showcase = m.Showcase.objects.get(showcase_id = showcase_id)
			tenant = showcase.from_tenant

			stock = m.Stock.objects.create(name = stock_name)
			stock.save()

			inventory = m.Inventory.objects.create(from_stock = stock, unit_price = unit_price, stock_in_qty = quantity, owner = tenant, from_showcase = showcase)
			inventory.save()

			return HttpResponse(inventory.inventory_id)
	except Exception as e:
		return HttpResponse(e, status = 400)

@csrf_exempt
def create_inventory_batch(request):
	#今次會用POST
	try:
		showcase_id = request.POST.get("showcase_id")
		content = request.POST.get("content")

		print(f"showcase id:\{showcase_id}\n\nContent:\n{content}")

		with django.db.transaction.atomic():
			showcase = m.Showcase.objects.get(showcase_id = showcase_id)
			tenant = showcase.from_tenant

			content = content.replace("\r", "")
			for line in content.split("\n"):
				if line != "":
					items = line.split(",")
					print(items)

					stock = m.Stock.objects.create(name = items[0])
					stock.save()

					inventory = m.Inventory.objects.create(from_stock = stock, unit_price = items[2], stock_in_qty = items[1], owner = tenant, from_showcase = showcase)

					inventory.save()

					# 1/0


			return HttpResponse("Success")
	except Exception as e:
		return HttpResponse(e, status = 400)


# @login_required
def change_inventory_quantity(request):
	# 5.1
	#todo: 話返啲貨喺邊度入
	try:
		with django.db.transaction.atomic():
			inventory_id = request.GET.get("inventory_id")
			changed_quantity = request.GET.get("changed_quantity")
			inventory = m.Inventory.objects.get(inventory_id = inventory_id)
			inventory.stock_in_qty += int(changed_quantity)
			if inventory.stock_in_qty <= 0:
				return HttpResponse("Quantity must be a whole number")
			inventory.save()
			response = {}
			response["inventory_id"] = inventory.inventory_id
			json_msg = json.dumps(response, indent=2)
			return HttpResponse(json_msg, content_type="application/json")
	except Exception as e:
		return HttpResponse(e)

# @login_required
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
		response["inventory"] = []
		for inventory in stock.inventory_set.all():
			inventory_dict = {}
			inventory_dict["inventory_id"] =  float(inventory.inventory_id)
			inventory_dict["unit_price"] =  float(inventory.unit_price)
			inventory_dict["stock_in_qty"] =  inventory.stock_in_qty
			inventory_dict["showcase_id"] =  inventory.from_showcase_id
			response["inventory"].append(inventory_dict)

		json_msg = json.dumps(response, indent=2)
		return HttpResponse(json_msg, content_type="application/json")

	except Exception as e:
		return HttpResponse(e, status = 400)


def dictfetchall(cursor):
	"Return all rows from a cursor as a dict"
	columns = [col[0] for col in cursor.description]
	return [
		dict(zip(columns, row))
		for row in cursor.fetchall()
	]

def view_store_performance(request):
	try:
		# store_id={}&starting_date={}&ending_date={}
		store_id = request.GET.get("store_id")
		starting_date = request.GET.get("starting_date")
		ending_date = request.GET.get("ending_date")

		# return HttpResponse("Success")
		with django.db.connection.cursor() as cursor:
			sql = f"select server_showcase.store_id, server_receipt.time, server_stock.name, server_purchase.quantity, server_purchase.amount from server_receipt\
			inner join server_purchase on server_receipt.id = server_purchase.receipt_id\
			inner join server_inventory on server_purchase.inventory_id = server_inventory.inventory_id\
			inner join server_stock on server_inventory.from_stock_id = server_stock.`stock_id`\
			inner join server_showcase on server_inventory.from_showcase_id = server_showcase.showcase_id\
			where time between '{starting_date}' and '{ending_date}' and store_id= '{store_id}' and server_purchase.is_cancelled = 0"

			print (sql)
			cursor.execute(sql)
			sql_result = cursor.fetchall()

			sql = f"select sum(amount) as p from server_receipt\
			inner join server_purchase on server_receipt.id = server_purchase.receipt_id\
			inner join server_inventory on server_purchase.inventory_id = server_inventory.inventory_id\
			inner join server_stock on server_inventory.from_stock_id = server_stock.`stock_id`\
			inner join server_showcase on server_inventory.from_showcase_id = server_showcase.showcase_id\
			where time between '{starting_date}' and '{ending_date}' and store_id= '{store_id}' and server_purchase.is_cancelled = 0"
			cursor.execute(sql)
			sum = cursor.fetchone()

			response = {}
			response["result"] = sql_result

			msg = ""
			response = {}
			response["sum"] = float(sum[0] or 0)
			response["record"] = []
			for record in sql_result:
				# server_showcase.store_id, server_receipt.time, server_stock.name, server_purchase.quantity, server_purchase.amount
				# showcase_id
				# stock_name
				# quantity
				# amount
				record_dict = {}
				record_dict["store_id"] = record[0]
				record_dict["datetime"] = record[1].strftime("%Y-%m-%d %H:%M")
				record_dict["name"] = record[2]
				record_dict["quantity"] = float(record[3])
				record_dict["amount"] = float(record[4])
				# record_dict["total"] = record[3]
				response["record"].append(record_dict)


			json_msg = json.dumps(response, indent=2)
			return HttpResponse(json_msg, content_type="application/json")

	except Exception as e:
		return HttpResponse(e, status = 400)


# @login_required
def list_stock(request):

	#3, 5
	try:
		stocks = m.Stock.objects.all()
		#for tenant
		# if not request.user.is_staff:
		# 	stocks = stocks.filter(owner_id = request.user.id)
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

# @login_required
def get_inventory(request):
	try:
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
	except Exception as e:
		return HttpResponse(e, status = 400)

def create_stock(request):
	#6.3 Todo
	try:
		if request.GET.get("name"):
			stock = m.Stock.objects.create(**request.GET.dict()) ##should return a queryset with 0 or 1 elements.
			return HttpResponse(stock.stock_id)
		else:
			return HttpResponse("Name is missing", status = 400)
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
				"id": request.user.id,
				"date_joined": request.user.date_joined.strftime("%Y-%m-%d"),
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

	if "q" in request.GET:
		q = request.GET["q"]
		staff_members = staff_members.filter(Q(staff_id__icontains = q)|Q(staff_name__icontains = q))

	msg = []
	try:
		for staff in staff_members:
			staff_dict = {}
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
			user.is_staff = True
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
	receipts = m.Receipt.objects.order_by("-id")

	if "q" in request.GET:
		receipts = receipts.filter(id__icontains = request.GET["q"])

	msg = []
	try:
		for receipt in receipts:
			receipt_dict = {}
			receipt_dict["id"] =  receipt.id
			receipt_dict["store"] =  "Kwai Fong"
			receipt_dict["time"] =  receipt.time.strftime("%Y-%m-%d %H:%M")
			receipt_dict["grand_total"] =  float(receipt.grand_total)
			receipt_dict["tender"] =  float(receipt.tender)
			receipt_dict["change"] =  float(receipt.change)
			receipt_dict["responsible"] =  receipt.responsible.staff_name
			receipt_dict["is_cancelled"] =  receipt.is_cancelled
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
		response["time"] = receipt.time.strftime("%Y-%m-%d %H:%M")
		response["tender"] = float(receipt.tender)
		response["change"] = float(receipt.change)
		response["responsible"] = receipt.responsible.staff_name
		response["is_cancelled"] = receipt.is_cancelled
		response["is_discount"] = receipt.discount > 0
		response["purchase"] = []
		for purchase in receipt.purchase_set.filter(is_cancelled = False):
		# for purchase in receipt.purchase_set.filter(is_cancelled = False):
			purchase_dict = {}
			purchase_dict["purchase_id"] = purchase.id
			purchase_dict["quantity"] = purchase.quantity
			purchase_dict["amount"] = float(purchase.amount)
			purchase_dict["remark"] = purchase.remark
			purchase_dict["stock_name"] = purchase.inventory.from_stock.name
			purchase_dict["is_cancelled"] = purchase.is_cancelled
			response["purchase"].append(purchase_dict)
		json_msg = json.dumps(response, indent=2)
		return HttpResponse(json_msg, content_type="application/json")
	except Exception as e:
		return HttpResponse(e, status = 400)

def remove_item_from_receipt(request):
	try:
		id = request.GET.get("purchase_id")
		purchase = m.Purchase.objects.get(id = id)
		if not purchase.is_cancelled:
			purchase.is_cancelled = True
			purchase.receipt.grand_total -= purchase.amount
			purchase.receipt.save()
			purchase.save()
			return HttpResponse("Success")
		else:
			return HttpResponse("Product has already been deleted", status = 400)
	except Exception as e:
		return HttpResponse(e, status = 400)


def receipt_refund(request):
	try:
		# Cancel a receipt.
		# if "return_product" is selected, the number of products will be returned to the inventory list.
		id = request.GET.get("id")
		return_product = "return_product" in request.GET
		receipt = m.Receipt.objects.get(id = id)

		if receipt.is_cancelled:
			raise ValueError("Receipt has already been cancelled")

		with django.db.transaction.atomic():
			for purchase in receipt.purchase_set.all():
				tenant = purchase.inventory.owner

				tenant.balance -= purchase.amount * (100 - tenant.commission_rate) / 100
				tenant.save()
				# deduct tenant balance by product price * 0.95 * unit price
				if return_product:
					#re-stock item
					purchase.inventory.stock_in_qty += purchase.quantity
					purchase.inventory.save()
			receipt.is_cancelled = True
			receipt.save()

		return HttpResponse("Success")
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
					if receipt.is_cancelled:
						# cancelled
						receipt.grand_total = 0
					else:
						receipt.grand_total = result_dict['total']
					receipt.tender = result_dict['tender']
					receipt.discount = result_dict['discount']
					receipt.change = receipt.tender - receipt.grand_total
					receipt.responsible = request.user.staff
					receipt.save()

					if len(result_dict["result"]) == 0:
						raise ValueError("Please enter at least one item")

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
						tenant.balance += purchase.amount * (100 - tenant.commission_rate) / 100
						tenant.save()

						## todo:
						msg += f"{inventory_string['inventory_id']} - {inventory_string['quantity']} - {inventory_string['amount']}\n"
					msg += f"Total - {receipt.grand_total}\nDiscount - {receipt.discount}\ntender: {result_dict['tender']}"

					return HttpResponse(receipt.id)
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


def generate_report(request):
	try:
		stores = m.Stores.objects.all()
	except Exception as e:
		return HttpResponse(str(e), status = 400)

def view_sales(request):
	try:
		tenant_id = request.GET.get("tenant_id")
		with django.db.connection.cursor() as cursor:
			sql = f"select server_receipt.time, server_purchase.quantity, server_purchase.amount from server_purchase inner join server_inventory on server_purchase.inventory_id = server_inventory.inventory_id inner join server_stock on server_stock.stock_id = server_inventory.`from_stock_id` inner join server_receipt on server_receipt.id = server_purchase.receipt_id where owner_id = {tenant_id}"
			cursor.execute(sql)

			sql_result = cursor.fetchall()

			msg = ""
			response = {}
			response["record"] = []
			for record in sql_result:
				record_dict = {}
				record_dict["time"] = record[0].strftime("%Y-%m-%d %H:%M")
				record_dict["quantity"] = record[1]
				record_dict["amount"] = float(record[2])
				# record_dict["total"] = record[3]
				response["record"].append(record_dict)

			json_msg = json.dumps(response, indent=2)
			return HttpResponse(json_msg, content_type="application/json")

	except Exception as e:
		return HttpResponse(e, 400)

@csrf_exempt
def test_post(request):

	print (request.POST)

	return HttpResponse(request.method)

def test_email(request):
	return HttpResponse("Success")
