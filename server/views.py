import django
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, FileResponse
from django.contrib.auth import authenticate
from django.core import serializers
from . import models as m
import datetime

# Create your views here.
def index(request):
	return HttpResponse("API")

def login(request):
	username = request.GET.get("username")
	password = request.GET.get("password")
	user = authenticate(username = username, password = password)

	if user:
		response = {}
		response["status"] = "Success"
		response["result"] = serializers.serialize('json', [user,])
		return JsonResponse(response, safe = True)
	else:
		response = {}
		response["status"] = "Failed"
		response["message"] = "Incorrect password"
		return JsonResponse(response, safe = True)


def search(request):
	q = dict(request.GET.get("q"))

	result = user.objects.filter(username__startswith = q)

	response = {}
	response["status"] = "Success",
	response["result"] = serializers.serialize('json', [result])

	return JsonResponse(response, safe = True)

def create_tenant(request):
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
			tenant = m.Tenant(tenant_id = tenant_id, tenant_name = tenant_name, phone = phone, address = address, commission_rate = commission_rate, user = user)
			tenant.save()
			# tenant = m.Tenant.objects.get(tenant_id = tenant_id)

			response = {}
			response["status"] = "Success"
			response["result"] = serializers.serialize('json', [tenant,])
			return JsonResponse(response)
		except Exception as e:
			response = {}
			response["status"] = "Failed"
			response["message"] = str(e)
			return JsonResponse(response)


def update_tenant(request):
	#todo

	tenant_id = request.GET.get("tenant_id")

	with django.db.transaction.atomic():
		try:
			tenant = m.Tenant.objects.filter(tenant_id = tenant_id) ##should return a queryset with 0 or 1 elements.
			if tenant:
				val = request.GET.copy().dict()
				del val["tenant_id"]
				tenant.update(**val)
				response = {}
				response["status"] = "Success"
				response["result"] =  serializers.serialize('json', tenant)
				return JsonResponse(response)
			else:
				response = {}
				response["status"] = "Failed"
				response["message"] =  "Matching query does not exist"
				return JsonResponse(response)
		except Exception as e:
			response = {}
			response["status"] = "Failed"
			response["message"] =  str(e)
			return JsonResponse(response)

def get_tenant(request):
	tenant_id = request.GET.get("tenant_id")

	try:
		tenant = m.Tenant.objects.get(tenant_id = tenant_id)
		response = {}
		response["status"] = "Success"
		response["result"] =  serializers.serialize('json', [tenant,])
		return JsonResponse(response)
	except Exception as e:
		response = {}
		response["status"] = "Failed"
		response["message"] = str(e)
		return JsonResponse(response)

def list_tenant(request):
	keywords = request.GET.dict()
	try:
		tenants = m.Tenant.objects.filter(**keywords)[:20]
		response = {}
		response["status"] = "Success"
		response["result"] =  serializers.serialize('json', tenants)
		return JsonResponse(response)
	except Exception as e:
		response = {}
		response["status"] = "Failed"
		response["message"] = str(e)
		return JsonResponse(response)
