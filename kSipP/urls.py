from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('modify-xml', views.modifyXml, name='modify-xml'),
    # path("show-xml-flow", views.index, name="show-xml-flow"),
    path('run-script', views.run_script_view, name='run-script'),
    path('xml-editor', views.aceXmlEditor, name='xml-editor'),
    path('log/<int:pid>/<str:xml>/', views.display_sipp_screen, name='display_sipp_screen'),
    path('xml-management', views.xml_management, name='xml-management'),
    path('xml-list', views.xml_list_view, name='xml-list'),
    path('create-scenario-xml', views.create_scenario_xml_view, name='create_scenario_xml'),
]