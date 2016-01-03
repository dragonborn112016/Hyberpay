
# Create your views here.
import os
import httplib2
from apiclient import errors
from apiclient.discovery import build
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from HyberPay.models import CredentialsModel, UserContactModel, UserMailsModel,\
    MailAttachmentModel
from HyberPayServer import settings
from oauth2client import xsrfutil
from oauth2client.client import flow_from_clientsecrets
from oauth2client.django_orm import Storage
from HyberPay.Gmail_Access.messageReader import MessageReader
import base64
from HyberPay.DataProcessing.CleanData import filteredData
from HyberPay.DataProcessing.getIdDetaills import fetchIdDetails, fetchAmount,\
    fetch_nertag, fetch_nertag_item
from django.http.response import JsonResponse
import time
from HyberPay.DataProcessing.readWriteFiles import writetofiles, readfiles
from django.db.models import Max
from HyberPay.Classification.traindata import ClassificationPreComputing, getCategory
from HyberPay.Classification.classifydata import classifycleanfiles
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from HyberPay.NER.common_functions import ner, OTHERS_MODEL, UTILITY_MODEL,\
     DOD_MODEL, TOD_MODEL, DEPLOC_MODEL
from HyberPay.NER import utility_bills, dod_travel,\
    tod_travel, deploc_travel,item_name
import re
from dateutil.parser import parse
from HyberPay.DashBoard.dashboard_utility import get_price


CLIENT_SECRETS = os.path.join(os.path.dirname(__file__),'client_secret.json')

FLOW =flow_from_clientsecrets(
    CLIENT_SECRETS,
    scope= "https://mail.google.com/",
    redirect_uri='http://localhost:8000/oauth2callback')



@login_required
def auth_return(request):
    
    getIdDetailsHyberpayFlagOffset = request.POST.get('getIdDetailsHyberpayFlagOffset',0)
    
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
    
    if getIdDetailsHyberpayFlagOffset ==1 or getIdDetailsHyberpayFlagOffset == '1':
        return get_mailIds(request)
    return get_credentials(request)


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
    
    if getIdDetailsHyberpayFlagOffset :
        return get_mailIds(request)
    
    context = RequestContext(request, {
        'request': request, 'user': request.user})   
    return render_to_response('index.html', context_instance=context)



@login_required
def get_mailIds(request):
    storage = Storage(CredentialsModel, 'id', request.user, 'credential')
    credential = storage.get()
    if credential is None or credential.invalid == True:
        print "in get mail ids : invalid credentials"
        return get_credentials(request,1)
        
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
    
        dbdet = getListfromdb(user)
        msglist = dbdet[0]
        mreaderlist = dbdet[1]
    
        print "retrieving data"
        jsonlist = get_gmailData(msglist, mreaderlist)
        
        print "retrieved json"
        response  = HttpResponse()
        response = JsonResponse(jsonlist,safe=False)    
        return response

def saveUserMails(usercontactmodel,mreaderlist):
    
    for mreader in mreaderlist:
        umm = UserMailsModel()
        umm.ucm = usercontactmodel
        
        x = classifycleanfiles(mreader.html)
        writetofiles([x],'temp')
        x = readfiles('temp',True)
        umm.text_mail = x[0]
        umm.html_mail = mreader.html
        umm.timestamp = mreader.date
        umm.sender = mreader.sender
        umm.noOfFiles = mreader.no_of_files
        umm.msgId = mreader.msgId
        #print 'message id: ',mreader.msgId
        umm.save()
        if mreader.no_of_files>0:
            i=0;
            att_id = mreader.att_id
            for fname in mreader.filename:
                mam = MailAttachmentModel()
                mam.umm = umm
                mam.fname = fname
                mam.att_id = att_id[i]
                i+=1
                mam.save()
        

def getListfromdb(usercontactmodel):
    res = UserMailsModel.objects.filter(ucm=usercontactmodel)
    msglist = []
    mreaderlist=[]
    
    for umm in res:
        mams = MailAttachmentModel.objects.filter(umm=umm)
        filename= []
        att_ids=[]
        for mam in mams:
            filename.append(mam.fname)
            att_ids.append(mam.att_id)
        mreader= MessageReader()
        mreader.filename=filename
        mreader.setDate(umm.timestamp)
        mreader.setHtml(umm.html_mail)
        mreader.setNoOfFiles(0)
        mreader.setSender(umm.sender)
        mreader.setText(umm.text_mail)
        mreader.setNoOfFiles(umm.noOfFiles)
        mreader.setMsgId(umm.msgId)
        mreader.setAtt_id(att_ids)
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
    filename =[]
    att_ids=[]
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
            if part['filename']:
                cnt = cnt+1;
                filename.append(part['filename'])
                mreader.setFilename(filename)
                mreader.setNoOfFiles(cnt)
                att_ids.append(part['body']['attachmentId'])
                mreader.setAtt_id(att_ids)

        except Exception,error:
            print "error occured reading mimeType %s" % error
    
    #===========================================================================
    # print "no of files :",mreader.no_of_files
    # print "filenames :", mreader.filename
    #===========================================================================
    return mreader

def fetchmails(service,timestamp):
    
    query="label:inbox ({+order +transaction +booking +booked +ticket +pnr +bill+invoice}"+" {+price +fare +amount} {+id +no})"
    if timestamp:
        query = query+" after:"+str(timestamp)
    else:
        query = query+" newer_than:1m"
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
            mreader.setMsgId(msg['id'])
            
            
        except errors.HttpError, error:
            print 'An error occurred: %s' % error
        except Exception, error:
            #print 'An error occurred: %s' % error # parts not accessible
            mreader = MessageReader()
            mime = message['payload']['mimeType']
            mreader.setMsgId(msg['id'])
        
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
    
    tot_time = time.time()
    #===========================================================================
    # det=[]
    #===========================================================================
    tdata=[]
    for mreader in mreaderlist:
        tdata.append(mreader.text)
    cdata = filteredData(tdata)
    mapping =cdata['mapping']
    fdata = cdata['fdata']
    #===========================================================================
    # mappedCdata = []
    # mappedHtmlData=[]
    #===========================================================================
    
    jsonlist = []
    precompute = ClassificationPreComputing()
    
    i=-1
    for data in fdata:
        i+=1
        label = getCategory(data,precompute[0],precompute[1],precompute[2],precompute[3],precompute[4])
        mreader1 = mreaderlist[mapping[i]]
        mreader1.setLabel(label)
        mreaderlist[mapping[i]] = mreader1
    print "done classification"
    
    
    print "len of filererd data :",len(fdata)
    
    others_glm = item_name.GLM()
    utility_glm = utility_bills.GLM()
    #doa_travel_glm = doa_travel.GLM()
    dod_travel_glm = dod_travel.GLM()
    #toa_travel_glm = toa_travel.GLM()
    tod_travel_glm = tod_travel.GLM()
    deploc_travel_glm = deploc_travel.GLM()
    #arvloc_travel_glm = arvloc_travel.GLM()
    
    others_glm.decode(open(OTHERS_MODEL))
    utility_glm.decode(open(UTILITY_MODEL))
    #doa_travel_glm.decode(open(DOA_MODEL))
    dod_travel_glm.decode(open(DOD_MODEL))
    #toa_travel_glm.decode(open(TOA_MODEL))
    tod_travel_glm.decode(open(TOD_MODEL))
    deploc_travel_glm.decode(open(DEPLOC_MODEL))
    #arvloc_travel_glm.decode(open(ARVLOC_MODEL))
    
    i=-1
    tot_labels = ['others','travel','utility']
    for data in fdata:
        
        i=i+1;
        mreader1 = mreaderlist[mapping[i]]
        if (mreader1.label not in tot_labels):
            #print mreader1.label
            continue
        jsondict = {}
        
        Iddetails = fetchIdDetails(data)
        details1 = Iddetails
        
        details1.append('total')
        
        amt = get_price(data)
        if amt:
            details1 = details1 + [amt]
        else :
            details1.append('0')
            amt=0
        
        if len(details1)<4:
            continue
        
        date  = mreader1.date
        sender =  str(mreader1.sender)
        jsondict['sender'] = sender
        jsondict['date']=date
        
        jsondict['ammount'] = amt
        jsondict['label'] = mreader1.label
        
        strt_time = time.time()
        if mreader1.label == 'others':
            
            nertags = ner(data, others_glm)
            jsondict.update(fetch_nertag_item(nertags))
            print 'time taken for others :',time.time()-strt_time
        
        elif mreader1.label == 'utility':
            nertags = ner(data, utility_glm)
            dd_dic = fetch_nertag(nertags)
            try :
                dte = parse(dd_dic["DD"])
                dd_dic["DD"] = str(dte.day) + '/' + str(dte.month) + '/' + str(dte.year)
            except Exception,e:
                print "exception parsing DD:",e
            jsondict.update(dd_dic)
            print 'time taken for utility :',time.time()-strt_time
        
        elif mreader1.label == 'travel':
            #===================================================================
            # nertags = ner(data, doa_travel_glm)
            # jsondict.update(fetch_nertag(nertags))
            #  
            #===================================================================
            nertags = ner(data, dod_travel_glm)
            dod_dic = fetch_nertag(nertags)
            try :
                dte = parse(dod_dic["DOD"])
                dod_dic["DOD"] = str(dte.day) + '/' + str(dte.month) + '/' + str(dte.year)
            except Exception,e:
                print "exception parsing DOD:",e
            jsondict.update(dod_dic)
            
            #===================================================================
            # nertags = ner(data, toa_travel_glm)
            # jsondict.update(fetch_nertag(nertags))
            # 
            #===================================================================
            nertags = ner(data, tod_travel_glm)
            jsondict.update(fetch_nertag(nertags))
            
            nertags = ner(data, deploc_travel_glm)
            jsondict.update(fetch_nertag(nertags))
            
            #===================================================================
            # nertags = ner(data, arvloc_travel_glm)
            # jsondict.update(fetch_nertag(nertags))
            # 
            #===================================================================
            
            print 'time taken for travel :',time.time()-strt_time
        
        
        #print 'dictionary : ',jsondict
        i1=0
        j1=1
        order_id = {}
        while j1 <len(Iddetails):
            order_id[Iddetails[i1]] =Iddetails[j1]
            i1+=2
            j1+=2
        jsondict['order_ids'] = order_id;
        
        filedict = {'size':mreader1.no_of_files}
        i1=0
        for fname in mreader1.filename:
            filedict[str(i1)]=fname
            filedict[str(i1)+'id']=mreader1.att_id[i1]
            i1+=1;
            
        jsondict['files']=filedict   
        jsondict['msgId']=mreader1.msgId
        #print "dictionary :", jsondict
        jsondict['html_content']=mreader1.html
        
        jsonlist.append(jsondict)
    
    print "data len :",len(jsonlist) 
    print 'total time taken :',time.time()-tot_time
    return jsonlist


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