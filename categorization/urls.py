from django.urls import path
from . import views

urlpatterns = [
    path("categories/", views.category_groups, name="category_groups"),
    path("categories/<int:group_id>/", views.category_group_detail, name="category_detail"),
]
