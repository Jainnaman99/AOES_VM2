from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.contracts, name="contracts"),
    path("saveContract/", views.saveContract, name="saveContract"),
    path("editContracts/", views.editContracts, name="editContracts"),
    path('dashboard/<contract_acronym>', views.contract),
    # path("newPage/", views.newPage, name="newPage"),
]
