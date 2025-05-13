from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('xml/<str:xmlname>/', views.serveXmlFile, name='xml-file'),
    path('edit-xml/', views.xmlEditor, name='edit-xml'),
    path('log/<int:pid>/<str:xml>/', views.display_sipp_screen, name='display_sipp_screen'),
    path('xml-management/', views.xml_management, name='xml-management'),
    path('xml-list/', views.xml_list_view, name='xml-list'),
    path('create-scenario-xml/', views.create_scenario_xml_view, name='create_scenario_xml'),
]