from django.urls import path
from . import views

app_name = 'excel_file_handling'

urlpatterns = [
    path('', views.excel_root, name='root'),
    path('files/', views.file_list, name='file_list'),
    path('upload/', views.upload_excel, name='upload'),
    path('file/<int:file_id>/', views.file_detail, name='file_detail'),
    path('file/<int:file_id>/process/', views.process_file, name='process_file'),
    path('file/<int:file_id>/delete/', views.delete_file, name='delete_file'),
    path('file/<int:file_id>/process-ajax/', views.process_file_ajax, name='process_file_ajax'),
    path('file/<int:file_id>/status/', views.get_file_status, name='get_file_status'),
    path('template/<str:file_type>/', views.download_template, name='download_template'),
] 