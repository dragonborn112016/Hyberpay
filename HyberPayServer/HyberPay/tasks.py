'''
Created on Jan 6, 2016

@author: Sidharth

this file contains functions corresponding to downloading mails and processing them
these functions are a part of threads and in a direct link with Gmail_Access/getMails.py

'''

from HyberPay.NER.common_functions import ner, OTHERS_MODEL, UTILITY_MODEL,\
     DOD_MODEL, TOD_MODEL, DEPLOC_MODEL, ARVLOC_MODEL
from HyberPay.NER import utility_bills, dod_travel,\
    tod_travel, deploc_travel,item_name, arvloc_travel
from dateutil.parser import parse
from HyberPay.DashBoard.dashboard_utility import get_price
from HyberPay.Classification.traindata import ClassificationPreComputing, getCategory
from HyberPay.Classification.classifydata import classifycleanfiles
import time
from HyberPay.DataProcessing.readWriteFiles import writetofiles, readfiles
from HyberPay.DataProcessing.CleanData import filteredData
from HyberPay.DataProcessing.getIdDetaills import fetchIdDetails,\
    fetch_nertag, fetch_nertag_item
from HyberPay.Gmail_Access.messageReader import MessageReader
from HyberPay.models import MailAttachmentModel, UserMailsModel,\
    UserContactModel, CredentialsModel
from apiclient import errors
import base64
from apiclient.discovery import build
from celery import task
from celery.utils.log import get_task_logger
import httplib2
from oauth2client.django_orm import Storage
from oauth2client.client import flow_from_clientsecrets
import os

logger = get_task_logger(__name__)

CLIENT_SECRETS = os.path.join(os.path.dirname(__file__),'Gmail_Access/client_secret.json')

@task(name="processMailsTask")
def processMailsTask(user_id, timestamp,authToken):
    ''' 
    this function downloads mails save them to database 
    and processes them to produce a json
    @params user : it is an instance of UserContactModel
    service : it is an instance of gmailService
    timestamp : this is the timestamp of last downloaded mail
    '''
    tot_time = time.time()
    user = UserContactModel.objects.get(user_id = user_id)
    
    username = user.user 
#     storage = Storage(CredentialsModel, 'id', username, 'credential')
#     credential = storage.get()
    credential = generateCredentialsFromAuthToken(authToken, user = username)
    http = httplib2.Http(cache='.cache')
    http = credential.authorize(http)
    service = build("gmail", "v1", http=http)
    
    print "fetching mails"
    res = fetchmails(service,timestamp)
    
    print "saving mails"
    saveUserMails(user,res[1])
 
    dbdet = getListfromdb(user)
    msglist = dbdet[0]
    mreaderlist = dbdet[1]
 
    print "retrieving data"
    jsonlist = get_gmailData(user,msglist, mreaderlist)
    probableJsonList = get_probableMails(user,msglist, mreaderlist)
    datalist = {"classified data" : jsonlist,
                "probable data" : probableJsonList}
    user.mailJson = datalist.__str__()
    user.save()
    print "write done :"
    print 'total time taken :',time.time()-tot_time
    return None

def generateCredentialsFromAuthToken(authToken,user):
    
    storage = Storage(CredentialsModel, 'id', user, 'credential')
    credential = storage.get()
    if credential is None :
        
        print " recreating credentials"    
        flow = flow_from_clientsecrets(
                                        CLIENT_SECRETS,
                                        scope= "https://mail.google.com https://mail.google.com/ https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.profile",
                                        redirect_uri='')
     
        credential = flow.step2_exchange(authToken)
        storage.put(credential)
    else:
        print "refreshing access token"
        http = httplib2.Http(cache='.cache')
        credential.get_access_token(http)
        storage.put(credential)
        
    print " credential created"
    return credential


def saveUserMails(usercontactmodel,mreaderlist):
    
    for mreader in mreaderlist:
        msgId = mreader.msgId
        try:
            umm = UserMailsModel.objects.get(msgId = msgId,ucm=usercontactmodel)
            sen = umm.sender
            continue
        except:
            pass
        
        umm = UserMailsModel()
        umm.ucm = usercontactmodel
        
        x = classifycleanfiles(mreader.html)
        writetofiles([x],'temp')
        x = readfiles('temp',True)
        umm.text_mail = x[0] if x else "" # previously error here
        umm.html_mail = mreader.html
        umm.timestamp = mreader.date
        umm.sender = mreader.sender
        umm.noOfFiles = mreader.no_of_files
        umm.msgId = mreader.msgId
        
        umm.DD = mreader.DD
        
        umm.DOD = mreader.DOD
        umm.TOD = mreader.TOD
        umm.DEPLOC = mreader.DEPLOC
        umm.ARVLOC = mreader.ARVLOC
        
        umm.ITEM = mreader.ITEM
        umm.PURP = mreader.PURP
        
        #print 'message id: ',mreader.msgId
        try:
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
        except:
            pass
                    

def UpdateUserMails(usercontactmodel,mreaderlist):
    
    for mreader in mreaderlist:
        msgId = mreader.msgId
        umm = UserMailsModel.objects.filter(msgId=msgId, ucm = usercontactmodel)[0]
        
        umm.DD = mreader.DD
        
        umm.DOD = mreader.DOD
        umm.TOD = mreader.TOD
        umm.DEPLOC = mreader.DEPLOC
        umm.ARVLOC = mreader.ARVLOC
        
        umm.ITEM = mreader.ITEM
        umm.PURP = mreader.PURP
        umm.category = mreader.category
        
        
        #print 'message id: ',mreader.msgId
        umm.save()
        

def getListfromdb(usercontactmodel):
    res = UserMailsModel.objects.filter(ucm=usercontactmodel)
    msglist = []
    mreaderlist=[]
    
    for umm in res:
#         if umm.category ==1:
#             continue
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
        
        mreader.setDD(umm.DD)
        
        mreader.setDOD(umm.DOD)
        mreader.setTOD(umm.TOD)
        mreader.setDEPLOC(umm.DEPLOC)
        mreader.setARVLOC(umm.ARVLOC)
        
        mreader.setITEM(umm.ITEM)
        mreader.setPURP(umm.PURP)
        
        mreader.setCategory(umm.category)
        
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
            print "error occurred reading mimeType " , error
    
    return mreader

def fetchmails(service,timestamp):
    
    query="label:inbox ({+order +transaction +booking +booked +ticket +pnr +bill+invoice}"+" {+price +fare +amount} {+id +no})"
    if timestamp:
        query = query+" after:"+str(timestamp/1000)
    else:
        print "first time downloaded"
        query = query+" newer_than:4m"
    mes = ListMessagesMatchingQuery(service, 'me', query)
    
    print " no of messeges to be fetched: ",len(mes)
    
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

def get_gmailData(usercontactmodel,msglist,mreaderlist):
    
    
    tdata=[]
    for mreader in mreaderlist:
        tdata.append(mreader.text)
    cdata = filteredData(tdata)
    mapping =cdata['mapping']
    fdata = cdata['fdata']
    
    jsonlist = []
    precompute = ClassificationPreComputing()
    
    i=-1
    for data in fdata:
        i+=1
        label = getCategory(data,precompute[0],precompute[1],precompute[2],precompute[3],precompute[4])
        mreader1 = mreaderlist[mapping[i]]
        mreader1.setLabel(label)
        mreaderlist[mapping[i]] = mreader1
#     print "done classification"
    
    
#     print "len of filererd data :",len(fdata)
    
    others_glm = item_name.GLM()
    utility_glm = utility_bills.GLM()
    #doa_travel_glm = doa_travel.GLM()
    dod_travel_glm = dod_travel.GLM()
    #toa_travel_glm = toa_travel.GLM()
    tod_travel_glm = tod_travel.GLM()
    deploc_travel_glm = deploc_travel.GLM()
    arvloc_travel_glm = arvloc_travel.GLM()
    
    others_glm.decode(open(OTHERS_MODEL))
    utility_glm.decode(open(UTILITY_MODEL))
    #doa_travel_glm.decode(open(DOA_MODEL))
    dod_travel_glm.decode(open(DOD_MODEL))
    #toa_travel_glm.decode(open(TOA_MODEL))
    tod_travel_glm.decode(open(TOD_MODEL))
    deploc_travel_glm.decode(open(DEPLOC_MODEL))
    arvloc_travel_glm.decode(open(ARVLOC_MODEL))
    
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
        mreader1.amount = amt
        jsondict['label'] = mreader1.label
        
#         print mreader1.category
        
        if mreader1.category == 2:
            
            
            jsondict.update({
                                "ITEM" : mreader1.ITEM,
                                "PURP" : mreader1.PURP,
                                "DD" : mreader1.DD,
                                "DOD" : mreader1.DOD,
                                "TOD" : mreader1.TOD,
                                "DEPLOC" : mreader1.DEPLOC,
                                "ARVLOC" : mreader1.ARVLOC
                            })
        else :
        
            if mreader1.label == 'others':
                
                #print mreader1.ITEM
                #print type(mreader1.ITEM)
                if not mreader1.ITEM :
                    nertags = ner(data, others_glm)
                    jsondict.update(fetch_nertag_item(nertags))
                    mreader1.ITEM = jsondict["ITEM"] if jsondict.has_key("ITEM") else ""
                    mreader1.PURP = jsondict["PURP"] if jsondict.has_key("PURP") else ""
                else:
                    jsondict.update({"ITEM" : mreader1.ITEM,
                                     "PURP" : mreader1.PURP})
                #print 'time taken for others :',time.time()-strt_time
            
            elif mreader1.label == 'utility':
                if not mreader1.DD :
                    nertags = ner(data, utility_glm)
                    dd_dic = fetch_nertag(nertags)
                    try :
                        dte = parse(dd_dic["DD"])
                        dd_dic["DD"] = str(dte.day) + '/' + str(dte.month) + '/' + str(dte.year)
                    except Exception,e:
                        print "exception parsing DD: error :",dd_dic," : Error :" ,e
                    jsondict.update(dd_dic)
                    mreader1.DD = jsondict["DD"] if jsondict.has_key("DD") else ""
                else:
                    jsondict.update({"DD" : mreader1.DD})
                #print 'time taken for utility :',time.time()-strt_time
            
            elif mreader1.label == 'travel':
                
                if not mreader1.DOD :
                    
                    nertags = ner(data, dod_travel_glm)
                    dod_dic = fetch_nertag(nertags)
                    try :
                        dte = parse(dod_dic["DOD"])
                        print  " orignal date : ",dod_dic["DOD"]
                        print  " parsed date : ",dte
                        dod_dic["DOD"] = str(dte.day) + '/' + str(dte.month) + '/' + str(dte.year)
                    except Exception,e:
                        print "exception parsing DOD: error:",dod_dic," : Error: " ,e
                    jsondict.update(dod_dic)
                    
                    nertags = ner(data, tod_travel_glm)
                    jsondict.update(fetch_nertag(nertags))
                    
                    nertags = ner(data, deploc_travel_glm)
                    jsondict.update(fetch_nertag(nertags))

                    nertags = ner(data, arvloc_travel_glm)
                    jsondict.update(fetch_nertag(nertags))

                    
                    mreader1.DOD = jsondict["DOD"] if jsondict.has_key("DOD") else ""
                    mreader1.TOD = jsondict["TOD"] if jsondict.has_key("TOD") else ""
                    mreader1.DEPLOC = jsondict["DEPLOC"] if jsondict.has_key("DEPLOC") else ""
                    mreader1.ARVLOC = jsondict["ARVLOC"] if jsondict.has_key("ARVLOC") else ""
                   
#                     print " time of departure :",  mreader1.TOD
#                     print " departure date :",  mreader1.DOD
#                     print " departure location :",  mreader1.DEPLOC
#                     print " Arrival location :",  mreader1.ARVLOC
                    
                else:
                    jsondict.update({"DOD" : mreader1.DOD,
                                     "TOD" : mreader1.TOD,
                                     "DEPLOC" : mreader1.DEPLOC,
                                     "ARVLOC" : mreader1.ARVLOC})
                #print 'time taken for travel :',time.time()-strt_time
                    
        
        
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
        mreader1.category = 1
        mreaderlist[mapping[i]] = mreader1
    
    print "data len :",len(jsonlist) 
    UpdateUserMails(usercontactmodel, mreaderlist)
    return jsonlist



def get_probableMails(usercontactmodel,msglist,mreaderlist):
        
    tdata=[]
    for mreader in mreaderlist:
        tdata.append(mreader.text)
    cdata = filteredData(tdata)
    mapping =cdata['mapping']
    fdata = cdata['fdata']
    
    jsonlist = []
    precompute = ClassificationPreComputing()
    
    i=-1
    for data in fdata:
        i+=1
        label = getCategory(data,precompute[0],precompute[1],precompute[2],precompute[3],precompute[4])
        mreader1 = mreaderlist[mapping[i]]
        mreader1.setLabel(label)
        mreaderlist[mapping[i]] = mreader1
#     print "done classification"
    
    
#     print "len of filererd data :",len(fdata)
    
    i=-1
    tot_labels = ['others','travel','utility']
    for data in fdata:
        
        i=i+1;
        mreader1 = mreaderlist[mapping[i]]
        if (mreader1.label not in tot_labels or mreader1.category==1):
            #print mreader1.label
            continue
        jsondict = {}
        
        
        date  = mreader1.date
        sender =  str(mreader1.sender)
        jsondict['sender'] = sender
        jsondict['date']=date
        jsondict['label'] = mreader1.label
        
        #print 'dictionary : ',jsondict
        
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
#         mreader1.category = 0
        mreaderlist[mapping[i]] = mreader1
    
    print "data len :",len(jsonlist) 
#     UpdateUserMails(usercontactmodel, mreaderlist)
    return jsonlist
