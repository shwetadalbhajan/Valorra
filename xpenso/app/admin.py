from django.contrib import admin
from .models import *

admin.site.register(CustomUser)
admin.site.register(Transaction)
admin.site.register(Budget)
admin.site.register(ContactQuery)