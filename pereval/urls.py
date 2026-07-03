from django.urls import path
from . import views

urlpatterns = [
    path('submitData/', views.submit_data, name='submit_data'),
    path('submitData/<int:pereval_id>/', views.pereval_detail, name='pereval_detail'),
    path('docs/', views.swagger_ui, name='swagger_ui'),
]