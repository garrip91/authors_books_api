"""
URL configuration for authors_books_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .settings import DEBUG

from authors_books_app.views import AuthorListView, GenreViewSet, BookViewSet, AllDataViewSet


# ЭКЗЕМПЛЯР РОУТЕРА ДЛЯ ПЕРЕХОДА НА СТРАНИЦЫ СООТВЕТСТВУЮЩИХ API:
router = DefaultRouter()
router.register(r"all-data/list", AllDataViewSet, basename="all-data")
router.register(r"genres/list", GenreViewSet, basename="genre")
router.register(r"book/list", BookViewSet, basename="book")

# ВЕРСИРОВАНИЕ API:
api_version = "v1"

urlpatterns = [
    path('admin/', admin.site.urls),
    path(f"api/{api_version}/", include("authors_books_app.urls", namespace=f"api_{api_version}")), # пространство имён для API v1
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("", include("authors_books_app.urls", namespace="main")), # пространство имён для основного приложения
]

if DEBUG:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
