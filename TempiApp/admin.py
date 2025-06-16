from django.contrib import admin
from .models import (
    CompanyProfile,
    UserProfile,
    Category,
    Job,
    JobType,
    Wishlist,
    Application,
    Status,
    JobAssignment,
    JobAssignmentStatus,
)

# Register your models here.
admin.site.register(CompanyProfile)
admin.site.register(UserProfile)
admin.site.register(Category)
admin.site.register(Job)
admin.site.register(JobType)
admin.site.register(Wishlist)
admin.site.register(Application)
admin.site.register(Status)
admin.site.register(JobAssignmentStatus)
admin.site.register(JobAssignment)
