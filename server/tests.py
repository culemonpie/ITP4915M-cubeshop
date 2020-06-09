from django.test import TestCase, Client
from django.contrib.auth import authenticate
import json
from . import models as m
import pprint
# Create your tests here.

client = Client()

class APITest(TestCase):
	def test_login(self):
		### Create user
		user = m.User.objects.create_user(username = "4915m", password = "4915m2020")
		user.is_staff = True
		user.save()

		### Test if user has been created
		expected_output = "4915m"
		self.assertEqual(expected_output, user.username)

		### Test if user can be authenticated through the system
		session = authenticate(username = "4915m", password = "password")
		expected_output = "4915m"
		self.assertIsNotNone(expected_output, session)

		## login with correct password
		url = '/login?username=4915m&password=4915m2020'
		expected_output = "Success"
		json_response = json.loads(client.get(url).content)
		self.assertEqual(expected_output, json_response["status"])

		## login with incorrect password
		expected_output = "Failed"
		url = '/login?username=4915m&password=4915m2019'
		json_response = json.loads(client.get(url).content)
		self.assertEqual(expected_output, json_response["status"])

	def test_CRU_tenant(self):
		## create tenant object
		expected_output = "Success"
		url = '/create_tenant?tenant_id=2&tenant_name=Jack&phone=12345678&address=hello%020world&balance=0&commission_rate=5&username=jack&password=test'
		json_response = json.loads(client.get(url).content)
		self.assertEqual(expected_output, json_response["status"])

		## creating another tenant object (won't be tested)
		url = '/create_tenant?tenant_id=3&tenant_name=Joey%020Chu&phone=12345678&address=hello%020world&balance=0&commission_rate=5&username=joey&password=test2'
		client.get(url)


		## duplicate creation on id = 2
		expected_output = "Failed"
		url = '/create_tenant?tenant_id=2&tenant_name=Robert&phone=12345678&address=hello%020world&balance=0&commission_rate=5&username=jack'
		json_response = json.loads(client.get(url).content)
		self.assertEqual(expected_output, json_response["status"])

		## making a query on a tenant that exists
		expected_output = "Success"
		url = '/get_tenant?tenant_id=2'
		json_response = json.loads(client.get(url).content)
		self.assertEqual(expected_output, json_response["status"])

		## Checks if the name of the tenant equals to the one we previously entered
		expected_output = "Jack"
		actual_output = json.loads(json_response["result"])[0]["fields"]["tenant_name"]
		self.assertEqual(expected_output, actual_output)

		## making a query on a tenant that does not exist
		expected_output = "Failed"
		url = '/get_tenant?tenant_id=16'
		json_response = json.loads(client.get(url).content)
		self.assertEqual(expected_output, json_response["status"])

		## changing the name of tenant with tenant_id 2
		expected_output = "Joe"
		url = '/update_tenant?tenant_id=2&tenant_name=Joe'
		json_response = json.loads(client.get(url).content)
		actual_output = str(json.loads(json_response["result"])[0]["fields"]["tenant_name"])
		self.assertEqual(expected_output, actual_output)

		## trying to change the name of a tenant
		expected_output = "Failed"
		url = '/update_tenant?tenant_id=5&tenant_name=Joe'
		json_response = json.loads(client.get(url).content)
		self.assertEqual(expected_output, json_response["status"])

		## get the list of tenants
		##A: without any parameter
		expected_output = "Success"
		url = '/list_tenant'
		json_response = json.loads(client.get(url).content)
		self.assertEqual(expected_output, json_response["status"])
		##B: with a filter
		expected_output = "Success"
		url = '/list_tenant?tenant_id__gte=1'
		json_response = json.loads(client.get(url).content)
		self.assertEqual(expected_output, json_response["status"])
		##C: Incorrect parameter
		expected_output = "Failed"
		url = '/list_tenant?wrong=9'
		json_response = json.loads(client.get(url).content)
		self.assertEqual(expected_output, json_response["status"])
