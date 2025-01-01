from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/results/<str:query>", views.results_view, name="results"),
    path("wiki/create", views.create_view, name="create"),
    path("wiki/edit/<str:entry_name>", views.edit_view, name="edit"),
    path("wiki/random", views.random, name="random"),
    path("wiki/<str:entry_name>", views.entry_view, name="entry"),
]
