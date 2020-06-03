import django
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, FileResponse
from django.contrib.auth import authenticate, login, logout
from django.core import serializers
from . import models as m
import datetime
import json

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
		response["user_type"] = 1
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
	tenant_id = request.GET.get("tenant_id")
	tenant_name = request.GET.get("tenant_name")
	phone = request.GET.get("phone")
	address = request.GET.get("address")
	#date_joined = request.GET.get("tenant_id")
	# balance = request.GET.get("balance")
	commission_rate = request.GET.get("commission_rate")

	username = request.GET.get("username")
	password = request.GET.get("password")

	with django.db.transaction.atomic():
		try:
			user = m.User(username = username, password = password)
			user.save()
			tenant = m.Tenant(tenant_id = user.id, tenant_name = tenant_name, phone = phone, address = address, commission_rate = commission_rate, user = user)
			tenant.save()
			# tenant = m.Tenant.objects.get(tenant_id = tenant_id)

			response = {}
			response["tenant_id"] = tenant.tenant_id
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
		response = {}
		response["status"] = "Failed"
		response["message"] = str(e)
		return JsonResponse(response)


def get_tenant(request):
	#9.1
	tenant_id = request.GET.get("tenant_id")

	try:
		tenant = m.Tenant.objects.get(tenant_id = tenant_id)
		response = {}
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
	except Exception as e:
		response = {}
		response["message"] = str(e)

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
			store_dict["usage"] = store.get_occupancy() #todo: calculate the maximum capacity
			store_dict["manager"] = "Alan Po"
			store_dict["is_active"] = store.is_active
			msg.append(store_dict)
		json_msg = json.dumps(msg, indent=2)
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
		store_dict["usage"] = "30/32"
		store_dict["manager"] = "Alan Po"
		store_dict["is_active"] = store.is_active
		json_msg = json.dumps(store_dict, indent=2)
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
	try:
		store_id = request.GET.get("store_id")
		val = request.GET.copy().dict()
		store = m.Store.objects.create(**val) ##should return a queryset with 0 or 1 elements.
		return HttpResponse("Success")
	except Exception as e:
		return HttpResponse(e, status = 400)

def get_showcase(request):
	try:
		showcase_id = request.GET.get("showcase_id")
		showcase = m.Showcase.objects.get(showcase_id = showcase_id) ##should return a queryset with 0 or 1 elements.
		showcase_dict = {}
		showcase_dict["showcase_id"] = showcase.showcase_id
		showcase_dict["type"] = showcase.get_showcase_type_display()
		json_msg = json.dumps(showcase_dict, indent=2)
		return HttpResponse(json_msg, content_type="application/json")
	except Exception as e:
		return HttpResponse(e, status = 400)

def create_showcase(request):
	try:
		store = m.Showcase.objects.create(**request.GET.dict()) ##should return a queryset with 0 or 1 elements.
		return HttpResponse(store.store_id)
	except Exception as e:
		return HttpResponse(e, status = 400)


def update_showcase(request):
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

def create_staff(request):
	'''
	username
	password??
	current_salary
	staff_type
	store (optional)
	'''
	pass

def change_password(request):
	try:
		password = request.GET.get("password")
		request.user.set_password(password)
		user.save()
		return HttpResponse("Success")
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
