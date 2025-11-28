from django.contrib import admin
from django.urls import path

from .import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path("index", views.index,name="index"),
    path('reg',views.register,name="reg"),
    path('log',views.login,name="log"),
    path('logout',views.register,name="logout"),
    path('studentpre', views.StudentPerformancePrediction, name="spredict"),  # changed
    path('survey/', views.student_survey, name='student_survey'),
    path('survey_progress/', views.student_progress_survey, name='student_progress_survey'),
    path("dropout/", views.dropout_form, name="dropout"),
]