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
	staff_name = models.CharField(max_length = 255)
	user = models.OneToOneField(User, on_delete = models.CASCADE)
	is_active = models.BooleanField(default = True)
	current_salary = models.DecimalField(max_digits = 6, decimal_places = 1)
	date_joined = models.DateField(auto_now_add = True)
	staff_type = models.CharField(choices = sorted(staff_types), max_length = 255)
	store = models.ForeignKey("Store", null = True, on_delete = models.CASCADE, related_name = "works_in") #store_id

	def __str__(self):
		return self.staff_name

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
	def __str__(self):
		return self.tenant_name

	def get_sales(self):
		return 0

class Store(models.Model):
	store_id = models.CharField(primary_key = True, max_length = 255)
	store_name = models.CharField(max_length = 255)
	address = models.TextField(max_length = 255)
	is_active = models.BooleanField(default = True)
	manager = models.ForeignKey("Staff", on_delete = models.SET_NULL, null = True, blank = True, related_name = "manager")

	showcase_index = models.PositiveIntegerField(default=0) ## Increment the counter whenever a showcase is added

	def __str__(self):
		return self.store_name

	def get_occupancy(self):
		cases = self.showcase_set.all()
		occupied_cases = cases.filter(showcase_type = Showcase.N)

		return f"{occupied_cases.count()}/{cases.count()}"#

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

	showcase_id = models.CharField(max_length = 255, primary_key = True, blank = True)
	from_tenant = models.ForeignKey("Tenant", on_delete = models.CASCADE, null = True)
	store = models.ForeignKey("Store", on_delete = models.CASCADE)
	showcase_type = models.CharField(choices = sorted(rental_types), max_length = 255, default = V )
	# current_rent = models.DecimalField(max_digits = 6, decimal_places = 1, default = 0)
	rental_index = models.PositiveIntegerField(default = 0)

	def save(self, *args, **kwargs):
		if not self.showcase_id:
			self.store.showcase_index += 1
			self.store.save()
			self.showcase_id = f"{self.store.store_id}{str(self.store.showcase_index).zfill(3)}"
			print (self.showcase_id)
		super().save(*args, **kwargs)

	def __str__(self):
		return self.showcase_id

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
	remark = models.TextField(max_length = 4096, null = True, blank = True)
	showcase_type = models.CharField(choices = sorted(rental_types), max_length = 255, default = N )
	showcase = models.ForeignKey("Showcase", on_delete = models.CASCADE, )
	tenant = models.ForeignKey("Tenant", on_delete = models.CASCADE, null = True, blank = True)
	name = models.CharField(max_length=255, blank = True)

	def save(self, *args, **kwargs):
		if not self.pk:
			self.showcase.rental_index += 1
			self.showcase.save()
			self.name = f"{self.showcase.showcase_id}-{self.showcase.rental_index}"
		super().save(*args, **kwargs)

	def __str__(self):
		return self.name

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

	def __str__(self):
		return self.name

class Inventory(models.Model):
	inventory_id = models.AutoField(primary_key = True) ##not used
	unit_price = models.DecimalField(max_digits = 6, decimal_places = 1)
	stock_in_qty = models.PositiveIntegerField()
	remark = models.TextField(max_length = 4096, null = True, blank = True)
	from_stock = models.ForeignKey("Stock", on_delete = models.CASCADE)
	from_showcase = models.ForeignKey("Showcase", on_delete = models.CASCADE)

	class Meta:
		verbose_name_plural = "Inventories"
		constraints = [
			models.UniqueConstraint(fields=['from_stock', 'from_showcase'], name='unique_stock_per_showcase' )
		]

	def __str__(self):
		return f"{self.from_showcase.showcase_id}-{self.from_stock.stock_code}"

class Receipt(models.Model):
	receipt_id = models.IntegerField(primary_key = True)
	grand_total = models.DecimalField(max_digits = 6, decimal_places = 1)
	time = models.DateTimeField(auto_now_add = True)
	tender = models.DecimalField(max_digits = 6, decimal_places = 1)
	change = models.DecimalField(max_digits = 6, decimal_places = 1, blank = True)
	responsible = models.ForeignKey("Staff", on_delete = models.CASCADE)
	is_cancelled = models.BooleanField(default = False)

	def __str__(self):
		return str(self.receipt_id).zfill(6)

class Purchase(models.Model):
	purchase_id = models.AutoField(primary_key = True)
	quantity = models.IntegerField()
	amount = models.DecimalField(max_digits = 6, decimal_places = 1)
	remark = models.TextField(max_length = 4096)
	stock_code = models.ForeignKey("Stock", on_delete = models.CASCADE)
	receipt = models.ForeignKey("Receipt", on_delete = models.CASCADE)
