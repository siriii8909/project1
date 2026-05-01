from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_image, name='upload'),
    path('results/<int:pk>/', views.results, name='results'),
    path('history/', views.history, name='history'),
    path('report/pdf/<int:pk>/', views.download_report_pdf, name='report_pdf'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
]
