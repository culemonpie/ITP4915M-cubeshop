from django.urls import path, re_path
from . import views
urlpatterns = [
### 1 - PUBLIC SITE
path('', views.index, name='index'),
path('login', views.login, name='login'),
path('search', views.search, name='search'),
path('create_tenant', views.create_tenant, name='create_tenant'),
]
