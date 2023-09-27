from django.urls import path
from . import views

urlpatterns = [
    path("TAEUpload/", views.TAEUpload, name='TAEUpload'),
    path("deleteTAE/", views.deleteTAE, name='deleteTAE'),
    # path("mergeTAE/", views.mergeTAE, name="mergeTAE"),
    path("multiTAE/", views.upload_multiple, name="multiTAE"),
    path("downloadTAE/", views.downloadTAE, name="downloadTAE"),
    path("summaryTAE/", views.summaryTAE, name="summaryTAE"),
    path("reconTAE/<int:year>/<int:month>", views.reconTAE, name="reconTAE")

]