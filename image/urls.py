from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

app_name='image'

urlpatterns = [
    path('', views.ImageList.as_view(), name='list'),
    path('predict/', views.ImagePredict.as_view(), name='predict'),
    path('save/', views.ImageSave.as_view(), name='save'),
    path('<int:id>/', views.ImageDetail.as_view(), name='change'),
]

urlpatterns = format_suffix_patterns(urlpatterns)