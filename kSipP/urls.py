from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("modify-xml", views.modifyXml, name="modify-xml"),
    path("run-script", views.run_script_view, name='run-script')
]