from django.contrib import admin
from userapp.models import (Service,
                            Work,
                            Request,
                            Message,
                            ResponsibilityGroup,
                            Log)


admin.site.register(Service)
admin.site.register(Work)
admin.site.register(Request)
admin.site.register(Message)
admin.site.register(ResponsibilityGroup)
admin.site.register(Log)
