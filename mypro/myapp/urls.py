from django.contrib import admin
from django.urls import path

from .import views
urlpatterns = [
    path('backend/', admin.site.urls),
    path("", views.index,name="index"),
    path('reg/',views.register,name="reg"),
    path('login',views.login,name="log"),
    path('logout',views.logout,name="logout"),
    path('predict_full/', views.predict_student_full_detailed, name='predict_student_full'), #neww
    path("education-news/", views.education_news, name="education-news"),
  # changed
    path('survey/', views.student_survey, name='student_survey'),
    path('survey_progress/', views.student_progress_survey, name='student_progress_survey'),
    path("dropout-v2/", views.dropout_predict_v2, name="dropout_v2"),
    path("contact/", views.contact, name="contact"),
    path("suggestion/", views.suggestion, name="suggestion"),
    path("suggestionresult/", views.suggestionresult, name="suggestionresult"),

    path("adminlogin/", views.admin_login, name="admin_login"),
    path('adminlogout/', views.admin_logout, name='admin_logout'),
    path('admindashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('adminusers/', views.admin_users, name='admin_users'),
    path('admin/users/delete/<str:user_id>/', views.admin_delete_user, name='admin_delete_user'),

    path('admin/performance/', views.admin_performance, name='admin_performance'),
    path('admin/performance/delete/<str:perf_id>/', views.admin_delete_performance, name='admin_delete_performance'),


    path('adminpredictions/', views.admin_predictions, name='admin_predictions'),
    path('admin/predictions/delete/<str:pred_id>/', views.admin_delete_prediction, name='admin_delete_prediction'),
    path('admin/predictions/detail/<str:pred_id>/', views.admin_prediction_detail, name='admin_prediction_detail'),
    path('adminsurveys/', views.admin_surveys, name='admin_surveys'),
    path('admin/surveys/delete/<str:survey_id>/', views.admin_delete_survey, name='admin_delete_survey'),
    path('adminprogress/', views.admin_progress, name='admin_progress'),
    path('admin/progress/delete/<str:progress_id>/', views.admin_delete_progress, name='admin_delete_progress'),
    path('admindropout/', views.admin_dropout, name='admin_dropout'),
    path('admin/dropout/delete/<str:dropout_id>/', views.admin_delete_dropout, name='admin_delete_dropout'),
    path('admincontacts/', views.admin_contacts, name='admin_contacts'),
    path('admin/contacts/delete/<str:contact_id>/', views.admin_delete_contact, name='admin_delete_contact'),









]


