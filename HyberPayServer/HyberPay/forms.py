'''
Created on Oct 21, 2015

@author: SIDHARTH
'''
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
import re

class LoginForm(forms.Form):
    username = forms.CharField(max_length=40)
    password = forms.CharField(max_length=20,
                               widget=forms.PasswordInput)
    

class RegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=15)
    last_name = forms.CharField(max_length=15)
    email_id = forms.EmailField()
    password1 = forms.CharField(max_length=20,
                                widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=20,
                                widget=forms.PasswordInput)
    contact_no = forms.CharField(max_length=15)
    
    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            User.objects.get_by_natural_key(username)
        except ObjectDoesNotExist:
            return username
        raise forms.ValidationError('Username already exists')
        
    
    def clean_contact_no(self):
        contact_no = self.cleaned_data['contact_no']
        if not re.search(r'^[0-9]+$',contact_no):
            raise forms.ValidationError('contact no. should be valid')
        else:
            return contact_no
        
        
    def clean_password2(self):
        
        if 'password1' in self.cleaned_data:
            password1 = self.cleaned_data['password1']
            password2 = self.cleaned_data['password2']
            if password1==password2:
                return password2
        raise forms.ValidationError('passwords do not match')
        
class ClassificationForm(forms.Form):
    category = forms.CharField(max_length=10)