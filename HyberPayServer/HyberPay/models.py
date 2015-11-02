from django.db import models

# Create your models here.

from django.contrib import admin
from django.contrib.auth.models import User

from oauth2client.django_orm import CredentialsField

class UserContactModel(models.Model):
    user = models.OneToOneField(User,primary_key=True)
    contact_no = models.CharField(max_length=15)

class UserMailsModel(models.Model):
    ucm = models.ForeignKey(UserContactModel)
    html_mail = models.TextField()    
    timestamp = models.IntegerField()
    sender = models.TextField()
    text_mail = models.TextField()
    noOfFiles = models.IntegerField()
    category = models.IntegerField(null = True,blank=True)
    #catagory, orderid item etc fields to be created later on

class ContactsModel(models.Model):
    uid = models.ForeignKey(User)
    pass # contact of user friends networking model later on

    

class CredentialsModel(models.Model):
    id = models.OneToOneField(User, primary_key=True)
    credential = CredentialsField()


class CredentialsAdmin(admin.ModelAdmin):
    pass


admin.site.register(CredentialsModel, CredentialsAdmin)

