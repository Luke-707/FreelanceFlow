from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='project_list'),
    path('marketplace/', views.project_marketplace, name='project_marketplace'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('create/', views.project_create, name='project_create'),
    path('<int:pk>/delete/', views.project_delete, name='project_delete'),
    path('<int:pk>/respond/<str:response>/', views.project_respond, name='project_respond'),
    path('<int:pk>/apply/', views.apply_to_project, name='apply_to_project'),
    path('application/<int:pk>/<str:action>/', views.respond_to_application, name='respond_to_application'),
    path('<int:pk>/upload-deliverable/', views.upload_deliverable, name='upload_deliverable'),
    path('<int:pk>/download-deliverable/', views.download_deliverable, name='download_deliverable'),
    path('<int:pk>/set-payment/', views.set_payment_details, name='set_payment_details'),
    path('<int:pk>/pay-to-unlock/', views.pay_to_unlock, name='pay_to_unlock'),
    path('<int:project_id>/add-milestone/', views.add_milestone, name='add_milestone'),
]
