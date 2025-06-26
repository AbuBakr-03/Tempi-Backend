# TempiApp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # User/Company Profile endpoints
    path("profile/", views.CurrentUserProfileView.as_view(), name="user_profile"),
    path("me/", views.DetailedCurrentUserProfileView.as_view(), name="current_user"),
    path(
        "users/<int:pk>/",
        views.DetailedOtherUserProfileView.as_view(),
        name="user_detail",
    ),
    # Company endpoints (new)
    path("company/", views.CompanyView.as_view(), name="company_list"),
    path("company/<int:pk>/", views.SingleCompanyView.as_view(), name="company_detail"),
    # Category endpoints
    path("category/", views.CategoryView.as_view()),
    path("category/<int:pk>/", views.SingleCategoryView.as_view()),
    # Job Type endpoints
    path("job-type/", views.JobTypeView.as_view()),
    path("job-type/<int:pk>/", views.SingleJobTypeView.as_view()),
    # Job endpoints
    path("job/", views.JobView.as_view()),
    path("job/<int:pk>/", views.SingleJobView.as_view()),
    path("dashboard-job/", views.DashboardJobView.as_view()),
    path("dashboard-job/<int:pk>/", views.SingleDashboardJobView.as_view()),
    # Wishlist endpoints
    path("wishlist/", views.WishlistView.as_view()),
    path("wishlist/<int:pk>/", views.SingleWishlistView.as_view()),
    # Application endpoints
    path("application/", views.ApplicationView.as_view()),
    path("application/<int:pk>/", views.SingleApplicationView.as_view()),
    # Job Assignment endpoints
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
    path("ratings/", views.RatingView.as_view(), name="ratings"),
    path("ratings/<int:pk>/", views.SingleRatingView.as_view(), name="rating_detail"),
    path(
        "users/<int:user_id>/ratings/",
        views.UserRatingsView.as_view(),
        name="user_ratings",
    ),
]
