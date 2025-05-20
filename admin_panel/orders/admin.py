from django.contrib import admin
from .models import Client, Order, Mailing

admin.site.register(Client)
admin.site.register(Order)
admin.site.register(Mailing) 