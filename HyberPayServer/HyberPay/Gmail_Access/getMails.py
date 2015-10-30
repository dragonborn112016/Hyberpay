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
from HyberPay.models import CredentialsModel, UserContactModel, UserMailsModel
from HyberPayServer import settings
from oauth2client import xsrfutil
from oauth2client.client import flow_from_clientsecrets
from oauth2client.django_orm import Storage
from HyberPay.Gmail_Access.messageReader import MessageReader
import base64
from HyberPay.DataProcessing.CleanData import cleanfiles, filteredData
from HyberPay.DataProcessing.Computetfidf import compWordFreq, compVocab,\
    compIDF, compTf
from HyberPay.DataProcessing.mainfun import dataProcessing
from HyberPay.DataProcessing.getIdDetaills import fetchIdDetails, fetchAmount
from django.core.files import File
from django.http.response import JsonResponse
from django.db.models.expressions import Date
import datetime
import time
from HyberPay.DataProcessing.readWriteFiles import writetofiles, readfiles
from HyberPay.Classification.classifydata import do_classification
from django.db.models import Max
from HyberPay.Classification.traindata import ClassificationPreComputing, getCategory
from HyberPay.Classification.category import category
from inspect import getcallargs

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
        username = request.user
        user = UserContactModel.objects.get(user=username)
        timestamp = 0
        try:
            umm = UserMailsModel.objects.filter(ucm =user).aggregate(Max('timestamp'))
            print umm
            timestamp = umm['timestamp__max']
        except Exception,error:
            print "exception while reading database %s" %error  
            
        http = httplib2.Http(cache='.cache')
        http = credential.authorize(http)
        service = build("gmail", "v1", http=http)
        
        print "fetching mails"
        res = fetchmails(service,timestamp)
        print "got mails"
        
        print "saving mails"
        saveUserMails(user,res[1])
        print "saved"
        
        
        ##res[0]=msglist res[1]=mreaderlist
        ## msglist = msg in html
        msglist = res[0]
        mreaderlist = res[1]
        if timestamp:
            dbdet = getListfromdb(user)
            msglist = msglist+dbdet[0]
            mreaderlist = mreaderlist+dbdet[1]
        
        #=======================================================================
        # redir = do_classification(request,msglist,mreaderlist)
        # print "done classification"
        # 
        #=======================================================================
        print "retrieving data"
        jsonlist = get_gmailData(msglist, mreaderlist)
        
        print "retrieved json"
        response  = HttpResponse()
        response = JsonResponse(jsonlist,safe=False)    
        return response
        #=======================================================================
        # return render_to_response('registration/welcome.html', {# to be removed in future-sidharth
        #             'messages': clus1,
        #             'clust1':det,
        #             'clust2':mappedHtmlData,
        #             'clust3':mappedCdata
        #             })
        #=======================================================================

         #=======================================================================
        # cdata = filteredData(msglist)
        # writetofiles(cdata, 'rawdata')    
        # return render_to_response('registration/welcome.html', {# to be removed in future-sidharth
        #         'messages': mes,
        #         'messageInHtml':cdata,
        #         'count':len(msglist),
        #         })
        #         
        #=======================================================================
            
#===============================================================================
#         ####################################################################################################
#         # think about threading
#         
#         cdata = filteredData(msglist,True)
#         a2 = dataProcessing(cdata)
#         cdata1 = cleanfiles(msglist)
#         print "clusteres processing"
#         clus1 = [cdata1[i] for i in a2[0][1]]
#         clus2 = [cdata1[i] for i in a2[1][1]]
#         clus3 = [cdata1[i] for i in a2[2][1]]
#         clus4 = [cdata1[i] for i in a2[3][1]]
#         #clus3 =clus3 + [" new cluster started"] +clus4
#         i=0
#         det1 = []
#         for data in clus1:
#             try:
#                 d  = data.encode("unicode-escape")
#                 details1 = fetchIdDetails(d)
#                 details1.append('total')
#                 details1 = details1+fetchAmount(d)
#             except Exception, error :
#                 details1 = []
#                 print "cluster 1 : error %s" %error 
#                 continue
#             details1 = " ".join(details1)
#             det1.append(details1)
#             i=i+1;
#         
#         
#         print "done clus1"
#         i=0
#         det2 = []
#         for data in clus2:
#             try:
#                 d  = data.encode("unicode-escape")
#                 details2 = fetchIdDetails(d)
#                 details2.append('total')
#                 details2 = details2+fetchAmount(d)
#             except Exception,error:
#                 details2=[]
#                 d  = data.encode("unicode-escape")
#                 print "cluster 2: %s" %error
#                 continue
#             details2 =" ".join(details2)
#             det2.append(details2)
#             i=i+1;
#         
#         i=0
#         det3 = []
#         for data in clus3:
#             try:
#                 d  = data.encode("unicode-escape")
#                 details3 = fetchIdDetails(d)
#                 details3.append('total')
#                 details3 = details3+fetchAmount(d)
#             except Exception,error:
#                 details3=[]
#                 
#                 print "cluster 3: %s" %error
#                 continue
#             details3 =" ".join(details3)
#             det3.append(details3)
#             i=i+1;
#         
#         i=0
#         det4 = []
#         for data in clus4:
#             try:
#                 d  = data.encode("unicode-escape")
#                 details4 = fetchIdDetails(d)
#                 details4.append('total')
#                 details4 = details4+fetchAmount(d)
#             except Exception,error:
#                 details4=[]
#                 d  = data.encode("unicode-escape")
#                 print "cluster 4: %s " %error
#                 continue
#             details4=" ".join(details4) 
#             det4.append(details4)
#             
#             i=i+1;
#         
#         clus1 = [msglist[i] for i in a2[0][1]]
#         clus2 = [msglist[i] for i in a2[1][1]]
#         clus3 = [msglist[i] for i in a2[2][1]]
#         clus4 = [msglist[i] for i in a2[3][1]]
# 
#         # process and clean data 
#         
#         ####################################################################################################
#         return render_to_response('registration/welcome.html', {# to be removed in future-sidharth
#                     'messages': mes,
#                     'messageInHtml':msglist,
#                     'cluster1':clus1,
#                     'cluster2':clus2,
#                     'cluster3':clus3,
#                     'cluster4':clus4,
#                     'count':len(cdata),
#                     'details1':det1,
#                     'details2':det2,
#                     'details3':det3,
#                     'details4':det4,
#                     'len1':len(det1),
#                     'len2':len(det2),
#                     'len3':len(det3),
#                     'len4':len(det4)
#                     })
#         
#===============================================================================

def saveUserMails(usercontactmodel,mreaderlist):
    
    for mreader in mreaderlist:
        umm = UserMailsModel()
        umm.ucm = usercontactmodel
        umm.html_mail = mreader.html
        umm.timestamp = mreader.date
        umm.sender = mreader.sender
        umm.noOfFiles = mreader.no_of_files
        umm.save()

def getListfromdb(usercontactmodel):
    res = UserMailsModel.objects.filter(ucm=usercontactmodel)
    msglist = []
    mreaderlist=[]
    
    for umm in res:
        mreader= MessageReader()
        mreader.setDate(umm.timestamp)
        mreader.setHtml(umm.html_mail)
        mreader.setNoOfFiles(0)
        mreader.setSender(umm.sender)
        mreader.setText("")
        mreader.setNoOfFiles(umm.noOfFiles)
        mreaderlist.append(mreader)
        msglist.append(umm.html_mail)
    res = [msglist,mreaderlist]
    return res


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

def fetchmails(service,timestamp):
    
    query="({+order +booking +booked +ticket +pnr +bill}"+" {+price +fare +amount} {+id +no})"
    if timestamp:
        query = query+" after:"+str(timestamp)
    
    mes = ListMessagesMatchingQuery(service, 'me', query)
    
    msglist=[];
    mreaderlist = []
    
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
            #print 'An error occurred: %s' % error # parts not accessible
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
        mreaderlist.append(mreader)
    
    res = [msglist,mreaderlist]
    return res    

def get_gmailData(msglist,mreaderlist):
    
    det=[]
    cdata = filteredData(msglist)
    mapping =cdata['mapping']
    fdata = cdata['fdata']
    writetofiles(fdata, 'rawdata')
    mappedCdata = []
    mappedHtmlData=[]
    clus1 = readfiles('rawdata', isDel=True)
    #=======================================================================
    # print "clus1 :" ,len(clus1)
    # print "msglist :" ,len(msglist)
    # #===========================================================================
    #=======================================================================
    # a2 = dataProcessing(clus1)
    #===========================================================================
    i=-1
    jsonlist = []
    print "precomputing"
    precompute = ClassificationPreComputing()
    print "precomputing done"
    
    for data in clus1:
        jsondict = {}
        Iddetails = fetchIdDetails(data)
        details1 = Iddetails
        details1.append('total')
        amt = fetchAmount(data)
        details1 = details1+amt
        i=i+1;
        if len(details1)<4:
            continue # create mapping also
        mappedCdata.append(data)
        mappedHtmlData.append(msglist[mapping[i]])
        mreader1 = mreaderlist[mapping[i]]
        details1.append("date")
        date  = mreader1.date
        dte = time.strftime('%d/%m/%Y',  time.gmtime(int(date)/1000))
        #datetime.datetime.fromtimestamp(int(date)).strftime('%Y-%m-%d %H:%M:%S')
        details1.append(dte)
        details1.append("sender")
        label = getCategory(data,precompute[0],precompute[1],precompute[2],precompute[3],precompute[4])
        sender =  str(mreader1.sender)
        jsondict['sender'] = sender
        jsondict['date']=dte
        jsondict['ammount'] = amt[0]
        jsondict['label'] = label
        i1=0
        j1=1
        while j1 <len(Iddetails):
            jsondict[Iddetails[i1]] =Iddetails[j1]
            i1+=2
            j1+=2
            
        jsondict['html_content']=mreader1.html
        #===================================================================
        # print type(sender)
        #===================================================================
        details1.append(sender)
        details1 = " ".join(details1)
        det.append(details1)
        jsonlist.append(jsondict)
    
    #=======================================================================
    # print jsonlist
    #=======================================================================
    print "det :",len(det)
    print "mappedhtml :",len(mappedHtmlData)
    print "mapped cdata :",len(mappedCdata)
    return jsonlist
