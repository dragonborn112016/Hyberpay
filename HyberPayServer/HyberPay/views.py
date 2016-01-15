from django.contrib.auth import logout, login, authenticate
from django.http.response import HttpResponse
from django.template.context import RequestContext
from django.template.loader import get_template

from HyberPay.Gmail_Access.getMails import *
from HyberPay.forms import *
from HyberPay.models import *
from django.shortcuts import render_to_response, redirect
from django.contrib.auth import logout as auth_logout
from fileinput import filename
import httplib2
from apiclient.discovery import build
from django.views.decorators.csrf import csrf_exempt
import json
from oauth2client import client, crypt
from HyberPayServer.config import SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,\
    ANDROID_CLIENT_ID
from apiclient import discovery
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from social.apps.django_app.utils import load_strategy
from social.apps.django_app.utils import load_backend
from social.backends.oauth import BaseOAuth1, BaseOAuth2
from social.exceptions import AuthAlreadyAssociated

from rest_framework.decorators import permission_classes
from rest_framework import permissions, status
from social.apps.django_app.utils import psa

# Create your views here.
def main_page(request):
    try:
        username =  request.user
        
        if username.username =='':
            context = RequestContext(request, {
            'request': request, 'user': request.user})   
            return render_to_response('index.html', context_instance=context)
        else:
            user = User.objects.get_by_natural_key(username=username)
            try:
                ucm = UserContactModel.objects.get(user=user)
                print 'revisited'
            except Exception,error:
                print "creating user contact model"
                ucm  = UserContactModel()
                ucm.user=user
                ucm.contact_no ='unknown'
                ucm.mailJson = "[]"
                ucm.save()
            finally:
                res =  get_credentials(request)
                print 'credentials created : '
                return res
    except Exception,error:
        print "exception :",error
    
    print 'redirecting'
    context = RequestContext(request, {
        'request': request, 'user': request.user})   
    return render_to_response('index.html', context_instance=context)


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


#for hyberpay
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


#for hyberpay
def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')

# for social apps
def logout_social(request):
    auth_logout(request)
    return redirect('/')

def get_mail_attachment(request):
    storage = Storage(CredentialsModel, 'id', request.user, 'credential')
    credential = storage.get()
    if credential is None or credential.invalid == True:
        return HttpResponseRedirect('../../accounts/credential')
    else:
        msgId = request.GET['msgId']
        #att_id = request.GET['att_id']
        umm = UserMailsModel.objects.get(msgId=msgId)
        mam = MailAttachmentModel.objects.get(umm=umm)#,att_id=att_id)# assumption
        filename = mam.fname
        att_id = mam.att_id
        http = httplib2.Http(cache='.cache')
        http = credential.authorize(http)
        service = build("gmail", "v1", http=http)
        baseDir  = settings.BASE_DIR
        baseDir = os.path.join(baseDir,'..','static/tmpAttachment')
        if not os.path.exists(baseDir):
            os.makedirs(baseDir)
        #path1 = GetAttachments(service,'me', msg_id=msgId, baseDir)#attachmentId
        path1 = GetAttachments(service, user_id='me', msg_id=msgId, att_id=att_id, filename=filename, prefix=baseDir)
        json = [{'path':path1}]
        res = JsonResponse(json,safe=False)
        return res
    return HttpResponseRedirect('/')


@permission_classes((permissions.AllowAny,))
@csrf_exempt
def authTokenCheck(request):
    
    if request.method == 'POST':
        idinfo = ''
        bulk_data = request.POST
        try:
            idinfo = client.verify_id_token(bulk_data['id_token_from_Android'], SOCIAL_AUTH_GOOGLE_OAUTH2_KEY)
            #If multiple clients access the backend server:
            if idinfo['aud'] not in [ANDROID_CLIENT_ID, SOCIAL_AUTH_GOOGLE_OAUTH2_KEY]:
                raise crypt.AppIdentityError("Unrecognized client.")
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise crypt.AppIdentityError("Wrong issuer.")
            #===================================================================
            # if idinfo['hd'] != APPS_DOMAIN_NAME:
            #     raise crypt.AppIdentityError("Wrong hosted domain.")
            #===================================================================
        except crypt.AppIdentityError:
        # Invalid token
            return HttpResponse('<html><body>Invalid token: error</body></html>')
         
        try:
            #user = oauthtoken_to_user('google-oauth2', bulk_data['id_token_from_Android'], request)
            #resp = authTokenCreateCredentials(request, authToken = bulk_data['auth_Code_from_Android'], user=user)
            print " auth token : ",bulk_data['auth_Code_from_Android']
            user = auth_by_token(request, 'google-oauth2', bulk_data['id_token_from_Android'])
            return HttpResponse('<html><body> user created  </body></html>');
        except Exception,error :
            html_cont = '<html><body>in test method  Error = ' + str(error) + '\n post data = ' + str(idinfo) + '\n userID =' + 'userid' + '\n email = '+ 'email' + '</body></html>'
            return HttpResponse(html_cont)
    
    return HttpResponse('<html><body>  </body></html>');

def authTokenCreateCredentials(request,authToken,user):
    credentials = client.credentials_from_clientsecrets_and_code(
                        CLIENT_SECRETS,
                        ['https://www.googleapis.com/auth/plus.profiles.read', 'email'],
                        authToken, 
                        redirect_uri = '')
    #https://www.googleapis.com/auth/gmail.readonly
    # Call Google API
    
    http_auth = credentials.authorize(httplib2.Http())
    #drive_service = discovery.build('drive', 'v3', http=http_auth)
       
    # Get profile info from ID token
    userid = credentials.id_token['sub']
    email = credentials.id_token['email']
    html_cont = '<html><body> credentials created = \n post data = ' + '\n userID =' + userid + '\n email = '+ email +'\n request.user = '+ str(user.get_full_name()) +  '</body></html>'
    return HttpResponse(html_cont)


@psa('social:complete')
def auth_by_token(request, backend,token):
    
    user = request.backend.do_auth(token)
    print request.backend.user_data(token)
    return user;

@psa('social:complete')
def oauthtoken_to_user(provider,token,request,*args, **kwargs):
    """Check and retrieve user with given token.
    """
    User = get_user_model()
    queryset = User.objects.all()
    
    # If this request was made with an authenticated user, try to associate this social 
    # account with it
    authed_user = request.user if not request.user.is_anonymous() else None

    # `strategy` is a python-social-auth concept referencing the Python framework to
    # be used (Django, Flask, etc.). By passing `request` to `load_strategy`, PSA 
    # knows to use the Django strategy
    strategy = load_strategy(request)
    # Now we get the backend that corresponds to our user's social auth provider
    # e.g., Facebook, Twitter, etc.
    backend = load_backend(strategy=strategy, name=provider, redirect_uri=None)
    print " backend loaded"

    user = request.backend.do_auth(token)
    print request.backend.user_data(token)
    return user;
#===============================================================================
#         # if `authed_user` is None, python-social-auth will make a new user,
#         # else this social account will be associated with the user you pass in
#         user = backend.do_auth(token, user=authed_user)
#         print 'user created'
#     except AuthAlreadyAssociated:
#         # You can't associate a social account with more than user
#         return Response({"errors": "That social media account is already in use"},
#                         status=status.HTTP_400_BAD_REQUEST)
# 
#     if user and user.is_active:
#         # if the access token was set to an empty string, then save the access token 
#         # from the request
#         auth_created = user.social_auth.get(provider=provider)
#         if not auth_created.extra_data['access_token']:
#             # Facebook for example will return the access_token in its response to you. 
#             # This access_token is then saved for your future use. However, others 
#             # e.g., Instagram do not respond with the access_token that you just 
#             # provided. We save it here so it can be used to make subsequent calls.
#             auth_created.extra_data['access_token'] = token
#             auth_created.save()
# 
#         # Set instance since we are not calling `serializer.save()`
#         return user
#     else:
#         return Response({"errors": "Error with social authentication"},
#                         status=status.HTTP_400_BAD_REQUEST)
#===============================================================================

 

def tester(request):
    print "in here"
    return HttpResponse('<html><body>in test</body></html>')