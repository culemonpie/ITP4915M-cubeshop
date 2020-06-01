from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Staff(models.Model):
	PTS = "PTS"
	FTS = "FTS"
	STM = "STM"
	HRM = "HRM"
	SLM = "IT"
	D = "D"


	staff_types = (
		(PTS, "Part time staff"),
		(FTS, "Full time staff"),
		(STM, "Store manager"),
		(HRM, "Human resources manager"),
		(SLM, "Part time staff"),
		(D, "Director"),
	)


	staff_id = models.IntegerField(primary_key = True)
	user = models.OneToOneField(User, on_delete = models.CASCADE)
	staff_name = models.CharField(max_length = 255)
	is_active = models.BooleanField(default = True)
	current_salary = models.DecimalField(max_digits = 6, decimal_places = 1)
	date_joined = models.DateField(auto_now_add = True)
	staff_type = models.CharField(choices = sorted(staff_types), max_length = 255)
	store = models.ForeignKey("Store", on_delete = models.CASCADE, related_name = "works_in") #store_id

class Tenant(models.Model):
	tenant_id = models.IntegerField(primary_key = True)
	user = models.OneToOneField(User, on_delete = models.CASCADE)
	tenant_name = models.CharField(max_length = 255)
	phone = models.CharField(max_length = 255)
	address = models.TextField(max_length = 255)
	date_joined = models.DateField(auto_now_add = True)
	balance = models.DecimalField(max_digits = 6, decimal_places = 1, default = 0)
	commission_rate = models.DecimalField(max_digits = 6, decimal_places = 1, default = 5)
	#user = models.OneToOneField(User, on_delete = models.CASCADE) #user_id

class Store(models.Model):
	store_id = models.CharField(primary_key = True, max_length = 255)
	store_name = models.CharField(max_length = 255)
	address = models.TextField(max_length = 255)
	is_active = models.BooleanField(default = True)
	manager = models.ForeignKey("Staff", on_delete = models.SET_NULL, null = True, blank = True, related_name = "manager")

class Showcase(models.Model):
	N = "N"
	A = "A"
	P = "P"
	R = "R"
	V = "V"

	rental_types = {
		(N, "Normal"),
		(A, "Advertisement"),
		(P, "Private Label"),
		(R, "Repair"),
		(V, "Vacant"),
	}


	showcase_id = models.CharField(max_length = 255, primary_key = True)
	from_tenant = models.ForeignKey("Tenant", on_delete = models.CASCADE, null = True)
	store = models.ForeignKey("Store", on_delete = models.CASCADE)
	showcase_type = models.CharField(choices = sorted(rental_types), max_length = 255, default = N )


class ShowcaseRental(models.Model):
	N = "N"
	A = "A"
	P = "P"
	R = "R"
	V = "V"

	rental_types = {
		(N, "Normal"),
		(A, "Advertisement"),
		(P, "Private Label"),
		(R, "Repair"),
		(V, "Vacant"),
	}

	starting_date = models.DateField()
	ending_date = models.DateField()
	monthly_rent = models.DecimalField(max_digits = 6, decimal_places = 1)
	remark = models.TextField(max_length = 4096)
	showcase_type = models.CharField(choices = sorted(rental_types), max_length = 255, default = N )
	showcase = models.ForeignKey("Showcase", on_delete = models.CASCADE, )

class Stock(models.Model):
	stock_types = {
		(1, "Toys"),
		(2, "Accessories"),
		(3, "Electronics"),
		(4, "Handcraft"),
		(5, "Books"),
		(6, "Other"),
	}

	stock_code = models.CharField(primary_key = True, max_length = 255)
	name = models.CharField(max_length = 255)

	unit_price = models.DecimalField(max_digits = 6, decimal_places = 1)
	# current_rent = models.DecimalField(max_digits = 6, decimal_places = 1)
	##image_url
	description = models.TextField(max_length = 4096)
	is_on_hold = models.BooleanField()

class Inventory(models.Model):
	inventory_id = models.IntegerField(primary_key = True)
	unit_price = models.DecimalField(max_digits = 6, decimal_places = 1)
	stock_in_qty = models.PositiveIntegerField()
	remark = models.TextField(max_length = 4096)
	from_stock = models.ForeignKey("Stock", on_delete = models.CASCADE)
	from_showcase = models.ForeignKey("Showcase", on_delete = models.CASCADE)

class Receipt(models.Model):
	receipt_id = models.IntegerField(primary_key = True)
	grand_total = models.DecimalField(max_digits = 6, decimal_places = 1)
	time = models.DateTimeField()
	tender = models.DecimalField(max_digits = 6, decimal_places = 1)
	change = models.DecimalField(max_digits = 6, decimal_places = 1)
	responsible = models.ForeignKey("Staff", on_delete = models.CASCADE)
	is_cancelled = models.BooleanField(default = False)

class Purchase(models.Model):
	purchase_id = models.IntegerField(primary_key = True)
	quantity = models.IntegerField()
	amount = models.DecimalField(max_digits = 6, decimal_places = 1)
	remark = models.TextField(max_length = 4096)
	stock_code = models.ForeignKey("Stock", on_delete = models.CASCADE)
	receipt = models.ForeignKey("Receipt", on_delete = models.CASCADE)
