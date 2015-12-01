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
    msgId = models.TextField(null=True,blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    #catagory, orderid item etc fields to be created later on

class UserDashboardModel(models.Model):
    ucm = models.OneToOneField(UserContactModel,primary_key = True)
    month1 = models.CharField(max_length = 20)
    month2 = models.CharField(max_length = 20)
    month3 = models.CharField(max_length = 20)
    month4 = models.CharField(max_length = 20)
    month5 = models.CharField(max_length = 20)
    month6 = models.CharField(max_length = 20)

class MailAttachmentModel(models.Model):
    umm = models.ForeignKey(UserMailsModel)
    #content = models.TextField()
    fname = models.TextField()
    att_id = models.TextField()



class ContactsModel(models.Model):
    uid = models.ForeignKey(User)
    pass # contact of user friends networking model later on

    

class CredentialsModel(models.Model):
    id = models.OneToOneField(User, primary_key=True)
    credential = CredentialsField()


class CredentialsAdmin(admin.ModelAdmin):
    pass


admin.site.register(CredentialsModel, CredentialsAdmin)

 