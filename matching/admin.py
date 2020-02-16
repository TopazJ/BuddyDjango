from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Client)
admin.site.register(Volunteer)
admin.site.register(ClientInterest)
admin.site.register(VolunteerInterest)
admin.site.register(Call)
