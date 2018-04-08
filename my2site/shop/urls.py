from django.urls import path  # , include
from django.conf import settings
from django.conf.urls.static import static
from . import views


app_name = 'shop'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('detail/<int:product_id>/', views.DetailView.as_view(), name='detail'),  #  views.detail
    path('<int:category_id>/', views.CategoryView.as_view(), name='category'),
    path('<int:category_id>/page<int:page>/', views.CategoryView.as_view(), name='category'),
    path('<int:category_id>/page<int:page>/size<int:size>/', views.CategoryView.as_view(), name='category'),
    path('login/', views.LoginGuestView.as_view(), name='login_guest'),
] # + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)