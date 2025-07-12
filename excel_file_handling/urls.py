from django.urls import path
from . import views

app_name = 'excel_file_handling'

urlpatterns = [
    # صفحه اصلی و داشبورد
    path('', views.dashboard, name='dashboard'),
    path('upload/', views.upload_excel, name='upload_excel'),
    path('files/', views.file_list, name='file_list'),
    
    # مدیریت فایل‌ها
    path('files/<int:file_id>/', views.file_detail, name='file_detail'),
    path('files/<int:file_id>/process/', views.process_file, name='process_file'),
    path('files/<int:file_id>/delete/', views.delete_file, name='delete_file'),
    path('files/<int:file_id>/preview/', views.preview_file, name='preview_file'),
    
    # دانلود قالب‌ها
    path('templates/<str:file_type>/download/', views.download_template, name='download_template'),
    
    # API endpoints
    path('api/upload/', views.api_upload_file, name='api_upload_file'),
    path('api/files/<int:file_id>/process/', views.api_process_file, name='api_process_file'),
] 