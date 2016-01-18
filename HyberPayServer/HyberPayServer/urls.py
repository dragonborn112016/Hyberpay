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
from HyberPay.views import main_page,portals_page,\
     logout_social, get_mail_attachment, authTokenCheck
from HyberPay.Gmail_Access.getMails import auth_return, get_mailIds,\
    get_credentials

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^$',main_page,name = 'main_page'),
    url(r'^portals/(?P<filename>\w+)\.html$',portals_page,name = 'portals_page'),
    url(r'^social/logout$', logout_social,name='logout_social'),
    url(r'^accounts/profile/$',get_mailIds ,name = 'gmail_getMails'),
    url(r'^accounts/credential/$',get_credentials ,name = 'gmail_getCredentials'),
    url(r'^accounts/attachment',get_mail_attachment ,name = 'gmail_getAttachment'),
    url(r'^oauth2callback',auth_return ,name = 'auth_return'),
    url(r'sendAuth/$',authTokenCheck ,name = 'authTokenCheck'),
]
