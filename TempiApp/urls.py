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
]
