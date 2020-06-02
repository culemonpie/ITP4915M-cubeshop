from django.urls import path, re_path
from . import views
urlpatterns = [
### 1 - PUBLIC SITE
	path('', views.index, name='index'),
	path('login', views.login_view, name='login'), #1
	path('search', views.search), #global
	path('logout', views.logout_view), #global
	path('list_store', views.list_store), #3, 5
	path('get_store', views.get_store), #3.1
	path('update_store', views.update_store), #3.2
	path('create_store', views.todo), #3.3
	path('get_showcase', views.todo), #4.1
	path('create_showcase', views.todo), #4.2
	path('update_showcase', views.todo), #4.3
	path('list_inventory', views.todo), #5.1
	path('list_stock', views.todo), #6
	path('get_stock', views.todo), #6.1
	path('update_stock', views.todo), #6.2, 8
	path('create_stock', views.todo), #6.3
	path('get_profile', views.todo), #7
	path('change_password', views.todo), #7.4
	path('checkout', views.todo), #8

	path('list_tenant', views.list_tenant), #9
	path('get_tenant', views.get_tenant), #9.1
	path('update_tenant', views.update_tenant), #9.1
	path('create_tenant', views.create_tenant), #9.3

	path('list_sales', views.todo), #9
	path('list_staff', views.todo), #
	path('list_receipt', views.todo), #9
	path('get_receipt', views.todo), #9
	path('update_staff', views.todo), #9


	path('is_authenticated', views.is_authenticated), #test
]
