# TempiApp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("profile/", views.CurrentUserProfileView.as_view(), name="user_profile"),
    path("me/", views.DetailedCurrentUserProfileView.as_view(), name="current_user"),
    path(
        "users/<int:pk>/",
        views.DetailedOtherUserProfileView.as_view(),
        name="user_detail",
    ),
    path("company/", views.CompanyView.as_view()),
    path("company/<int:pk>/", views.SingleCompanyView.as_view()),
    path("category/", views.CategoryView.as_view()),
    path("category/<int:pk>/", views.SingleCategoryView.as_view()),
    path("job-type/", views.JobTypeView.as_view()),
    path("job-type/<int:pk>/", views.SingleJobTypeView.as_view()),
    path("job/", views.JobView.as_view()),
    path("dashboard-job/", views.DashboardJobView.as_view()),
    path("dashboard-job/<int:pk>", views.SingleDashboardJobView.as_view()),
    path("wishlist/", views.WishlistView.as_view()),
    path("wishlist/<int:pk>/", views.SingleWishlistView.as_view()),
    path("application", views.ApplicationView.as_view()),
    path("application/<int:pk>/", views.SingleApplicationView.as_view()),
    path("assignments/", views.JobAssignmentView.as_view()),
    path(
        "assignments/<int:pk>/",
        views.SingleJobAssignmentView.as_view(),
    ),
    path(
        "assignments-status/",
        views.JobAssignmentStatusView.as_view(),
    ),
    path(
        "assignments-status/<int:pk>/",
        views.SingleJobAssignmentStatusView.as_view(),
    ),
]
