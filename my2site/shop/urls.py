from django.urls import path  # , include

from . import views


app_name = 'shop'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('detail/<int:product_id>/', views.DetailView.as_view(), name='detail'),  #  views.detail
    path('<int:category_id>/', views.CategoryView.as_view(), name='category'),

]