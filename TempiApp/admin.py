from django.contrib import admin
from .models import UserProfile, Company, Category, Job, JobType, Wishlist

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Company)
admin.site.register(Category)
admin.site.register(Job)
admin.site.register(JobType)
admin.site.register(Wishlist)
