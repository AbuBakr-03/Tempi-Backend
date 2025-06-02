from django.contrib import admin
from .models import (
    UserProfile,
    Company,
    Category,
    Job,
    JobType,
    Wishlist,
    Application,
    Status,
)

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Company)
admin.site.register(Category)
admin.site.register(Job)
admin.site.register(JobType)
admin.site.register(Wishlist)
admin.site.register(Application)
admin.site.register(Status)
