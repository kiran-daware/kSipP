from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("modify-xml", views.modifyXml, name="modify-xml"),
    # path("show-xml-flow", views.index, name="show-xml-flow"),
    path("run-script", views.run_script_view, name='run-script'),
    path("xml-editor", views.aceXmlEditor, name="xml-editor"),
]