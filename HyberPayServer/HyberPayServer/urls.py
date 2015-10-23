"""HyberPayServer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from HyberPay.views import main_page,portals_page, registration_page,logout_page,\
    login_page

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$',main_page,name = 'main_page'),
    url(r'^register/$',registration_page,name = 'registration_page'),
    url(r'^portals/(?P<filename>\w+)\.html$',portals_page,name = 'portals_page'),
    url(r'^login/$', login_page,name='login_page'),
    url(r'^logout/$',logout_page,name='logout_page' ),
    
]
