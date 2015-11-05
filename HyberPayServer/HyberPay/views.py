from django.contrib.auth import logout, login, authenticate
from django.http import request
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.template.context import RequestContext
from django.template.loader import get_template

from HyberPay.Gmail_Access.getMails import *
from HyberPay.forms import *
from HyberPay.models import *


# Create your views here.
def main_page(request):
    template = get_template('index.html')
    output = template.render()
    return HttpResponse(output);

def portals_page(request,filename):
    fname ="/".join(['portals',filename]);
    fname = ".".join([fname,'html'])
    template = get_template(fname)
    output = template.render()
    return HttpResponse(output);

def registration_page(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username =form.cleaned_data['email_id']
            try:
                User.objects.get_by_natural_key(username)
                errors = "EmailId already exists"
                variables = RequestContext(request,{
                     'form':form,
                     'errors':errors
                     }) 
                return render_to_response('registration/registration.html', variables)
            except:
                user = User.objects.create_user(
                                                username =form.cleaned_data['email_id'],
                                                email = form.cleaned_data['email_id'],
                                                password = form.cleaned_data['password2']
                                                )
                
                ucm  = UserContactModel()
                ucm.user=user
                ucm.user.first_name=form.cleaned_data['first_name']
                ucm.user.last_name =form.cleaned_data['last_name']
                ucm.contact_no =form.cleaned_data['contact_no']
                ucm.save()
                return HttpResponseRedirect('/') # redirect to success page indicating user profile created
        # also may be can send a verification link later
        else:
            variables = RequestContext(request,{
                 'form':form
                 }) 
            return render_to_response('registration/registration.html', variables)
            
    
    else:
        form = RegistrationForm()
        variables = RequestContext(request,{
                     'form':form
                     }) 
        return render_to_response('registration/registration.html', variables)

def login_page(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    # do something here : maybe needed in future
                    nexturl = request.POST['next']
                    nxturls=[""," ",None];
                    if nexturl in nxturls:
                        return HttpResponseRedirect('../profile')
                    else:
                        return HttpResponseRedirect(nexturl)
                    
                else:
                    # Return a 'disabled account' error message
                    errors = "disabled account"
                    variables = RequestContext(request,{
                                                        'form':form ,
                                                        'errors':errors
                                                        }) 
                    return render_to_response('registration/login.html', variables)

                   
            else:
                # Return an 'invalid login' error message.
                errors = "invalid Login"
                variables = RequestContext(request,{
                                                     'form':form ,
                                                     'errors':errors
                                                     }) 
                return render_to_response('registration/login.html', variables)
            
    form = LoginForm()
    variables = RequestContext(request,{
                     'form':form
                     }) 
    return render_to_response('registration/login.html', variables)

def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')
def tester(request):
    print "in here"
    return HttpResponse('<html><body>in test</body></html>')