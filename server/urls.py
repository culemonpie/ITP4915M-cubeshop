from django.urls import path, re_path
from . import views
urlpatterns = [
### 1 - PUBLIC SITE
	path('', views.index, name='index'),
	path('login', views.login_view, name='login'),
	path('search', views.search, name='search'),
	path('create_tenant', views.create_tenant, name='create_tenant'),
	path('get_tenant', views.get_tenant, name='get_tenant'),
	path('update_tenant', views.update_tenant, name='get_tenant'),
	path('list_tenant', views.list_tenant, name='list_tenant'),
	path('list_store', views.list_store, name='list_store'),
]

n = [
	path('search', views.search),

]
