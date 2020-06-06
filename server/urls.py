from django.urls import path, re_path
from . import views
urlpatterns = [
	path('', views.index, name='index'), #刷存在感
	path('login', views.login_view, name='login'), #1 OK
	path('search', views.search), #global
	path('logout', views.logout_view), #global OK
	path('list_store', views.list_store), #3, 5 OK
	path('list_store_temp', views.list_store_temp), #temp
	path('get_store', views.get_store), #3.1 OK
	path('list_showcase', views.list_showcase), #3.1, 4
	path('update_store', views.update_store), #3.2 OK
	path('create_store', views.create_store), #3.3 OK
	path('get_showcase', views.get_showcase), #4.1 OK
	path('create_showcase', views.create_showcase), #4.2 OK
	path('update_showcase', views.update_showcase), #4.3 OK
	path('rent_showcase', views.rent_showcase), #4.4
	path('set_showcase_status', views.set_showcase_status), #4.4
	path('list_inventory', views.list_inventory), #5, 5.1
	path('change_inventory_quantity', views.change_inventory_quantity), #5.x
	path('list_stock', views.list_stock), #6 OK
	path('get_stock', views.get_stock), #6.1 OK
	path('update_stock', views.update_stock), #6.2, 8
	path('create_stock', views.create_stock), #6.3
	path('get_profile', views.get_profile), #7
	path('update_profile', views.todo), #suspended
	path('change_password', views.change_password), #7.4 OK
	path('checkout', views.checkout), #8 #todo

	path('list_tenant', views.list_tenant), #9
	path('get_tenant', views.get_tenant), #9.1
	path('update_tenant', views.update_tenant), #9.2
	path('create_tenant', views.create_tenant), #9.3

	path('list_sales', views.todo), #10

	path('list_staff', views.todo), #11
	path('get_staff', views.get_staff), #11.1 OK
	path('create_staff', views.create_staff), #11.2 OK
	path('update_staff', views.update_staff), #11.3 OK

	path('list_receipt', views.todo), #12
	path('get_receipt', views.todo), #12.1

	path('is_authenticated', views.is_authenticated), #test
]
