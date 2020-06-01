from django.contrib import admin
from . import models as m
# Register your models here.
admin.site.register(m.Staff)
admin.site.register(m.Tenant)
admin.site.register(m.Store)
admin.site.register(m.Showcase)
admin.site.register(m.ShowcaseRental)
admin.site.register(m.Stock)
admin.site.register(m.Inventory)
admin.site.register(m.Receipt)
admin.site.register(m.Purchase)
