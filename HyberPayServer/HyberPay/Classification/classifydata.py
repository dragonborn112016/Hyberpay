'''
Created on Oct 30, 2015

@author: SIDHARTH
'''
from django.http.response import HttpResponseRedirect
from django.template.context import RequestContext
from HyberPay.forms import RegistrationForm
from django.shortcuts import render_to_response
from HyberPay.models import UserMailsModel
import re
from bs4 import BeautifulSoup             
from nltk.corpus import stopwords
from HyberPay.DataProcessing.readWriteFiles import writetofiles, readfiles


def classifycleanfiles(doc,ripSpChr=False):
    stops = set(stopwords.words("english")) 
    dta1 = re.sub("<br>"," ",doc)
    
    soup = BeautifulSoup(dta1,'html5lib')

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

    return res

def do_classification():
    print "in classification"
    umms = UserMailsModel.objects.all()
    X = []
    Y = []
    i=0
    for umm in umms:
        x = classifycleanfiles(umm.html_mail)
        writetofiles([x],'temp')
        x = readfiles('temp',True)
        print "------------------------------------------------------"
        print "data : ",i
        print x[0]
        print "------------------------------------------------------"
        print "enter label :"
        label = raw_input()
        X.append(x[0])
        Y.append(label)
        umm.category=int(label)
        umm.save()
        i+=1

def mainfun():        
    do_classification()

def TestClassification():
    print "in testclassification"
    umms = UserMailsModel.objects.all()
    i=0
    for umm in umms:
        x = classifycleanfiles(umm.html_mail)
        writetofiles([x],'temp')
        x = readfiles('temp',True)
        print "------------------------------------------------------"
        print "data : ",i
        print x[0]
        print "------------------------------------------------------"
        print "enter label :",umm.category
        label = raw_input()
        i+=1

def getXY():
    
    umms = UserMailsModel.objects.all()
    X = []
    Y = []
    i=0
    print "getXY() :",len(umms)
    for umm in umms:
        x = classifycleanfiles(umm.html_mail)
        writetofiles([x],'temp')
        x = readfiles('temp',True)
        if x[0].strip() :
            X.append(x[0])
            Y.append(umm.category)
        i+=1
    
    res =[X,Y]
    return res
