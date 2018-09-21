from django.conf.urls import url
from . import views

urlpatterns=[
    url(r'^master_list',views.master_list,name='master_list'),
    url(r'^master_add',views.master_add,name='master_add'),
    url(r'^minion_auth',views.minion_auth,name='minion_auth'),
]