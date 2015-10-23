from django.db import models

# Create your models here.
import pickle
import base64

from django.contrib import admin
from django.contrib.auth.models import User

from oauth2client.django_orm import FlowField
from oauth2client.django_orm import CredentialsField

class UserContactModel(models.Model):
    user = models.OneToOneField(User,primary_key=True)
    contact_no = models.CharField(max_length=15)

class UserMailsModel(models.Model):
    user_id = models.ForeignKey(UserContactModel)
    orignal_mail = models.TextField()    
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
