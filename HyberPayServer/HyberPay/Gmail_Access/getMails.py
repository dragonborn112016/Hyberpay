
# Create your views here.
import os
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from HyberPay.models import CredentialsModel, UserContactModel, UserMailsModel
from HyberPayServer import settings
from oauth2client import xsrfutil
from oauth2client.client import flow_from_clientsecrets
from oauth2client.django_orm import Storage
import base64
from django.http.response import JsonResponse
from django.db.models import Max
#from django.shortcuts import render_to_response
#from django.template.context import RequestContext
from HyberPay.tasks import processMailsTask
import ast
from oauth2client import client, crypt


CLIENT_SECRETS = os.path.join(os.path.dirname(__file__),'client_secret.json')

FLOW =flow_from_clientsecrets(
    CLIENT_SECRETS,
    scope= "https://mail.google.com/",
    redirect_uri='http://hyberpay.herokuapp.com/oauth2callback')
    #redirect_uri='http://localhost:8000/oauth2callback')#'http://hyberpay.herokuapp.com/oauth2callback')



@login_required
def auth_return(request):
    
    #getIdDetailsHyberpayFlagOffset = request.POST.get('getIdDetailsHyberpayFlagOffset',0)
    
    if not xsrfutil.validate_token(settings.SECRET_KEY, request.POST.get('state',False),
                                   request.user):
        print request.user
        print request.REQUEST['state']
        
        try:
            error =  request.REQUEST['error']
        except Exception,er:
            print "error in authorization %s" %er
            error = ""
        lst= [""," ",None];
        if error not in lst:
            return HttpResponseRedirect("/")
        #return  HttpResponseBadRequest()
    credential = FLOW.step2_exchange(request.REQUEST)
    storage = Storage(CredentialsModel, 'id', request.user, 'credential')
    storage.put(credential)
    
    #if getIdDetailsHyberpayFlagOffset ==1 or getIdDetailsHyberpayFlagOffset == '1':
    return get_mailIds(request)
    #return get_credentials(request)


@login_required
def get_credentials(request,getIdDetailsHyberpayFlagOffset=0):
    storage = Storage(CredentialsModel, 'id', request.user, 'credential')
    credential = storage.get()
    if credential is None or credential.invalid == True:
        FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,
                                                       request.user)
        #print FLOW.params['state']
        if request.method == "POST":
            mutable = request.POST._mutable
            request.POST._mutable = True
            request.POST['getIdDetailsHyberpayFlagOffset'] = getIdDetailsHyberpayFlagOffset
            request.POST._mutable = mutable
            
        elif request.method == "GET":
            mutable = request.GET._mutable
            request.GET._mutable = True
            request.GET['getIdDetailsHyberpayFlagOffset'] = getIdDetailsHyberpayFlagOffset
            request.GET._mutable = mutable
        try:
            authorize_url = FLOW.step1_get_authorize_url()
            print 'authorizing user :',authorize_url
            return HttpResponseRedirect(authorize_url)
        except :
            print 'credentials exception'
            return HttpResponseRedirect('/')
    
    #if getIdDetailsHyberpayFlagOffset :
    return get_mailIds(request)
    #===========================================================================
    # 
    # context = RequestContext(request, {
    #     'request': request, 'user': request.user})   
    # return render_to_response('index.html', context_instance=context)
    #===========================================================================



@login_required
def get_mailIds(request):
    storage = Storage(CredentialsModel, 'id', request.user, 'credential')
    credential = storage.get()
    if credential is None or credential.invalid == True:
        FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,
                                                       request.user)
        
        try:
            authorize_url = FLOW.step1_get_authorize_url()
            print 'authorizing user :',authorize_url
            return HttpResponseRedirect(authorize_url)
        except :
            print 'credentials exception'
            return HttpResponseRedirect('/')
        
    else:
        username = request.user
        user = UserContactModel.objects.get(user=username)
        timestamp = 0
        try:
            umm = UserMailsModel.objects.filter(ucm =user).aggregate(Max('timestamp'))
            print umm
            timestamp = umm['timestamp__max']
        except Exception,error:
            print "exception while reading database %s" %error  
            
        #=======================================================================
        # http = httplib2.Http(cache='.cache')
        # http = credential.authorize(http)
        # service = build("gmail", "v1", http=http)
        #=======================================================================
        jsonlist = processMailsTask.delay(user.user_id, timestamp)
       
        if jsonlist.ready():
            response = JsonResponse(jsonlist,safe=False) 
        else:   
            
            jsonlist = ast.literal_eval(user.mailJson)
            response = JsonResponse(jsonlist,safe=False)
        return response
    


 
def get_mailIdsForAndroid(request,user,authToken):
    storage = Storage(CredentialsModel, 'id', user, 'credential')
    credential = storage.get()
    if credential is None or credential.invalid == True:
        credential = client.credentials_from_clientsecrets_and_code(
                         CLIENT_SECRETS,
                         ['https://mail.google.com/'],
                         authToken, 
                         redirect_uri = '')
        storage.put(credential)
     
    #Call Google API
     
    #http_auth = credentials.authorize(httplib2.Http())
    #drive_service = discovery.build('drive', 'v3', http=http_auth)
        
         
    else:
        username = user
        user = UserContactModel.objects.get(user=username)
        timestamp = 0
        try:
            umm = UserMailsModel.objects.filter(ucm =user).aggregate(Max('timestamp'))
            print umm
            timestamp = umm['timestamp__max']
        except Exception,error:
            print "exception while reading database %s" %error  
             
        #=======================================================================
        # http = httplib2.Http(cache='.cache')
        # http = credential.authorize(http)
        # service = build("gmail", "v1", http=http)
        #=======================================================================
        jsonlist = processMailsTask.delay(user.user_id, timestamp)
        
        if jsonlist.ready():
            response = JsonResponse(jsonlist,safe=False) 
        else:   
             
            jsonlist = ast.literal_eval(user.mailJson)
            response = JsonResponse(jsonlist,safe=False)
        return response




def GetAttachments(service, user_id, msg_id,att_id,filename, prefix=""):
    """Get and store attachment from Message with given id.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: ID of Message containing attachment.
    prefix: prefix which is added to the attachment filename on saving
    """
    try:
        #att_id=part['body']['attachmentId']
        att=service.users().messages().attachments().get(userId=user_id, messageId=msg_id,id=att_id).execute()
        data=att['data']
        file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
        path1 =os.path.join(prefix,filename) 
        
        f= open(path1, 'wb')
        f.write(file_data)
        f.close()
        print "write done :"
        return path1
    except Exception,err:
        print "not written : %s" %err
        return     
