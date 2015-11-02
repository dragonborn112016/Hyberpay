'''
Created on Oct 30, 2015

@author: SIDHARTH
'''

from HyberPay.models import UserMailsModel
import re
from bs4 import BeautifulSoup             
from HyberPay.DataProcessing.readWriteFiles import writetofiles, readfiles
import django
django.setup()

def classifycleanfiles(doc,ripSpChr=False):
    
    soup = BeautifulSoup(doc,'html5lib')

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out
    
    # get text
    tmp = soup.get_text(" ",strip=False)
    tmp = tmp.replace("\n"," ")
    tmp =tmp.replace("\r"," ")
    tmp =tmp.replace("\t"," ")
    
    if ripSpChr:
        tmp = re.sub("[^a-zA-Z]"," ",tmp)
    
    tmp = tmp.lower()
    words = tmp.split()
    #=======================================================================
    # if ripSpChr:
    #     words = [w for w in words if not w in stops]
    #=======================================================================
    res = (" ".join(words))
    
    
    keyset= [
                'order',
                'booking', 
                'booked',
                'ticket',
                'pnr',
                'bill',
                'fare',
                'price',
                'total',
                'amount'
                ];
    
    emptylst = [""," ",None]
    dta = res
    fdata=''
    dta = dta.strip()
    if dta in emptylst:
        return fdata;
    else:
        wrds = dta.split();
        if len(wrds)<5:
            return fdata
        else:
            cnt =0
            minflag = False
            for wrd in wrds:
                if wrd in keyset:
                    cnt = cnt+1;
                    minflag=True
                    break
                   
                    
            if not minflag:
                return fdata
            fdata =dta

    return fdata

def do_classification():
    print "in classification"
    umms = UserMailsModel.objects.all()[415:]
    i=-1
    print "total :",len(umms)
    cat = ['0','1','2','3','4']
    for umm in umms:
        i+=1
        #=======================================================================
        # if str(umm.category) in cat:
        #     continue
        #=======================================================================
        x = umm.text_mail
        print "------------------------------------------------------"
        print "data : ",i
        print x
        print "------------------------------------------------------"
        print "enter label :"
        label = raw_input()
        umm.category=int(label)
        umm.save()
        

def mainfun():        
    do_classification()

def TestClassification():
    print "in testclassification"
    umms = UserMailsModel.objects.all()
    i=0
    for umm in umms:
        x = umm.text_mail
        print "------------------------------------------------------"
        print "data : ",i
        print x
        print "------------------------------------------------------"
        print "enter label :",umm.category
        label = raw_input()
        i+=1

def getXY():
    
    umms = UserMailsModel.objects.all()
    X = []
    Y = []
    i=0
    
    cat = ['0','1','2','3','4']
    for umm in umms:
        x = umm.text_mail
        if str(umm.category) not in cat:
            continue
            
        if x.strip() :
            
            X.append(x)
            Y.append(umm.category)
        i+=1
    print "getXY() :",len(X)
    res =[X,Y]
    return res

def redoTextMailsDB():
    umms = UserMailsModel.objects.all()
    for umm in umms:
        html_mail = umm.html_mail
        x = classifycleanfiles(html_mail)
        writetofiles([x],'temp')
        x = readfiles('temp',True)
        umm.text_mail = x[0]
        umm.save()

def delirreleventMailsDb():
    umms = UserMailsModel.objects.filter(text_mail='')
    print "no of models to be deleted :", len(umms)
    y = raw_input("enter y/n")
    if y=='y':
        UserMailsModel.objects.filter(text_mail='').delete()
        

def defaultclassification():
    umms = UserMailsModel.objects.all()[70:]
    for umm in umms:
        umm.category=-1
        umm.save()

#===============================================================================
# do_classification()
# #===============================================================================
# # defaultclassification()
# #===============================================================================
# print "done"
#===============================================================================
