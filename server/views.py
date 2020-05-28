import django
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, FileResponse
from django.contrib.auth import authenticate
from django.core import serializers
from . import models as m

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
	q = request.GET.get("q")

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
	balance = request.GET.get("balance")
	commission_rate = request.GET.get("commission_rate")

	username = request.GET.get("username")
	password = request.GET.get("password")

	with django.db.transaction.atomic():
		try:
			user = m.User.objects.create(username = username, password = password)

			tenant = m.Tenant.objects.create(tenant_id = tenant_id, tenant_name = tenant_name, phone = phone, address = address, balance = balance, commission_rate = commission_rate)


			response = {}
			response["status"] = "Success"
			response["result"] = serializers.serialize('json', [result])
			return JsonResponse(response)
		except Exception as e:
			response = {}
			response["status"] = "Failed"
			response["message"] = str(e)
			return JsonResponse(response)

def view_tenant(request):
	tenant_id = request.GET.get("tenant_id")

	try:
		tenant = m.Tenant.objects.get(tenand_id = tenand_id)
		response = {}
		response["status"] = "Success"
		response["result"] =  serializers.serialize('json', [tenant,])
		return JsonResponse(response)
	except Exception as e:
		response = {}
		response["status"] = "Failed"
		response["message"] = str(e)
		return JsonResponse(response)
