from django.shortcuts import render

# Create your views here.
import os
import logging
import httplib2
from apiclient import errors
from apiclient.discovery import build
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from HyberPay.models import CredentialsModel
from HyberPayServer import settings
from oauth2client import xsrfutil
from oauth2client.client import flow_from_clientsecrets
from oauth2client.django_orm import Storage
from HyberPay.Gmail_Access.messageReader import MessageReader
import base64
from HyberPay.DataProcessing.CleanData import cleanfiles, filteredData
from HyberPay.DataProcessing.Computetfidf import compWordFreq, compVocab,\
    compIDF, compTf

CLIENT_SECRETS = os.path.join(os.path.dirname(__file__),'client_secret.json')

FLOW =flow_from_clientsecrets(
    CLIENT_SECRETS,
    scope= "https://mail.google.com/",
    redirect_uri='http://localhost:8000/oauth2callback')



@login_required
def auth_return(request):
    
    if not xsrfutil.validate_token(settings.SECRET_KEY, request.POST.get('state',False),
                                   request.user):
        print request.user
        print request.REQUEST['state']
        error =  request.REQUEST['error']
        lst= [""," ",None];
        if error not in lst:
            return HttpResponseRedirect("/")
        #return  HttpResponseBadRequest()
    credential = FLOW.step2_exchange(request.REQUEST)
    storage = Storage(CredentialsModel, 'id', request.user, 'credential')
    storage.put(credential)
    return HttpResponseRedirect("accounts/profile")

    

@login_required
def get_mailIds(request):
    storage = Storage(CredentialsModel, 'id', request.user, 'credential')
    credential = storage.get()
    if credential is None or credential.invalid == True:
        FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,
                                                       request.user)
        print FLOW.params['state']
        try:
            authorize_url = FLOW.step1_get_authorize_url()
            return HttpResponseRedirect(authorize_url)
        except :
            return HttpResponseRedirect('/')
    else:
        http = httplib2.Http(cache='.cache')
        http = credential.authorize(http)
        service = build("gmail", "v1", http=http)
        
        mes = ListMessagesMatchingQuery(service, 'me', query="({+order +booking +booked +ticket +pnr +bill}"
                + " {+price +fare +amount} {+id +no})")
        
        
        ###############################################################################################3
        ##get messages
        msglist=[];
        
        for msg in mes:
            try:
                message = service.users().messages().get(userId='me', id=msg['id']).execute()
                mheaders =  message['payload']['headers']
                mdate = message['internalDate']
                msender =""
                for header in mheaders:
                    name = header['name']
                    if name=="from" or name == "From":
                        msender = header['value']
                        break
                mparts =  message['payload']['parts']
                
                mreader = readparts(mparts)
                
                
            except errors.HttpError, error:
                print 'An error occurred: %s' % error
            except Exception, error:
                print 'An error occurred: %s' % error # parts not accessible
                mreader = MessageReader()
                mime = message['payload']['mimeType']
                if mime == "text/plain":
                    s = base64.urlsafe_b64decode(message['payload']['body']['data'].encode('ASCII'))  
                    mreader.setText(s)
                elif mime == "text/html":
                    s = base64.urlsafe_b64decode(message['payload']['body']['data'].encode('ASCII'))  
                    mreader.setHtml(s)
            
            mreader.setDate(mdate)
            mreader.setSender(msender)
            msglist.append(mreader.html)
                
            
        ####################################################################################################
        # think about threading
        
        cdata = filteredData(msglist)
        wordf = compWordFreq(cdata)
        vocab = compVocab(cdata)
        idf = compIDF(vocab,wordf)
        tf = compTf(wordf)

        # process and clean data 
        
        ####################################################################################################
        return render_to_response('registration/welcome.html', {# to be removed in future-sidharth
                    'messages': mes,
                    'messageInHtml':cdata,
                    'count':len(cdata),
                    })
        




def ListMessagesMatchingQuery(service, user_id, query=''):

    try:
        response = service.users().messages().list(userId=user_id,q=query).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])
        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=user_id, q=query,
                                               pageToken=page_token).execute()
            messages.extend(response['messages'])
      
        return messages
    
    except errors.HttpError, error :
        print 'An error occurred: %s' % error
    
      


def readparts(parts):
    
    mreader = MessageReader()
    cnt=0;
    for part in parts:
        try:
            mime = part['mimeType']
            if mime == "text/plain":
                s = base64.urlsafe_b64decode(part['body']['data'].encode('ASCII'))  
                mreader.setText(s)
            elif mime == "text/html":
                s = base64.urlsafe_b64decode(part['body']['data'].encode('ASCII'))  
                mreader.setHtml(s)
            elif mime == "multipart/alternative":
                subpart = part['parts']
                subreader = readparts(subpart)
                mreader.setHtml(subreader.html)
                mreader.setText(subreader.text)
            elif mime == "application/octet-stream":
                cnt = cnt+1;
                mreader.setNoOfFiles(cnt)
        except Exception,error:
            print "error occured reading mimeType %s" % error
                
    return mreader