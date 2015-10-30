'''
Created on Oct 27, 2015

@author: SIDHARTH
'''

import nltk
import os
import re
from nltk.corpus import stopwords
from nltk import FreqDist
from django.shortcuts import render_to_response
from HyberPay.DataProcessing.mainfun import dataProcessing
from HyberPay.DataProcessing.CleanData import filteredData
from HyberPay.DataProcessing.readWriteFiles import readfiles

ORDER_VOCAB = ('order','ticket','pnr','payment','paisapay','transaction','bill','payment','booking','reference')


def getbigram(dta):
    a=nltk.ngrams(dta,3)
    keywords =['bill','order','booking','booked','ticket','pnr','transaction','date',
               'time','departure','id','no','no.','dear','price','total','invoice,'
               'ammount','amount','amt','fare','item','name','details',':','-','.']
    ele = ()
    for dt in a:
        for wrd in keywords:
            if wrd in dt:
                ele =ele+dt
                print dt
                break
    return ele

def splitAndRemSp(dta):
    dta = dta.split()
    i=0
    for wrd in dta:
        if wrd is ":":
            dta[i]=" "
        elif wrd is "?":
            dta[i]=" "
        elif wrd is "-":
            dta[i]=" "
        
        i=i+1
        
    dta = (" ".join(dta))
    dta = dta.split()
    return dta

def fetchIdDetails(dta):
    dta1 = splitAndRemSp(dta)
                        
    a=nltk.ngrams(dta1,5)
    keywords =['bill','order','booking','ticket','pnr','transaction','date',
               'arrival','departure','price','total','ammount','amount','amt','fare','invoice']
    nos = ['no','no.','no:','no.-','no:-','id','id.','id:','id.-','id:-']
    details=[]
    acquired=[]
    found = False
    for row in a:
            if row[1] in nos:
                j=0
                for wrd in row:
                    if j<2:
                        j=j+1
                        continue
                    
                    lett = str(wrd)
                    if ((not lett.isalpha())and len(lett)>3) :
                        if row[0] in acquired:
                            continue
                        flag=True
                        for w in lett:
                            if w.isdigit():
                                flag=False
                                break
                        if flag:
                            continue

                        det = str(row[0])
                        
                        if det not in ORDER_VOCAB:
                            continue
                        
                        details.append(det)
                        acquired.append(det)
                        details.append(lett)
##                        print row

##    print details
##    print "acquired len : ",len(acquired)
    
    if len(acquired)==0:
        a=nltk.ngrams(dta1,5)

##        print "in here"
        for row in a:
            word1 = str(row[0])
            if row[0] in ORDER_VOCAB:
##                print row
                for wrd in row:
                    
                    lett = str(wrd)
                    if ((not lett.isalpha())and len(lett)>3) :
                        if row[0] in acquired:
                            continue
                        flag=True
                        for w in lett:
                            if w.isdigit():
                                flag=False
                                break
                        if flag:
                            continue

                        det = str(row[0])
                        
                        details.append(det)
                        acquired.append(det)
                        details.append(lett)
##                        print row

        
    return details

def fetchAmount(dta):
    dta1 = splitAndRemSp(dta)
    a=nltk.ngrams(dta1,4)
    keywords =['subtotal','fare','amount','paid']
    filter = ['distance']
    details = []
    flag=False

    for row in a:

        amt = str(row[0])
        patt = re.match('amt',amt)

        if flag:
            break
        if patt:
            for wrd in row:
                lett = str(wrd)
                if not lett.isalpha():
                    for w in lett:
                        if w.isdigit():
                            flag=True
                            break
                if flag:
##                    print row
                    details.append(wrd)
                    break
                
        if 'total' in row[0]:
            if row[1] in keywords:
                j=0

                for wrd in row:
                    if j<2:
                        j=j+1
                        continue
                    lett = str(wrd)
                    if not lett.isalpha():
                        for w in lett:
                            if w.isdigit():
                                flag=True
                                break
                    if flag:
##                        print row
                        details.append(wrd)
                        break

        if row[0] in keywords:
            j=-1

            for wrd in row:
                j=j+1;
                lett = str(wrd)
                if j==3:
                    break

                if j==1 and lett.isdigit():
                    continue

                
                if wrd in filter:
                    break
                
                if (not lett.isalpha()):
                    for w in lett:
                        if w.isdigit():
                            flag=True
                            break

                if flag:
##                    print row
                    details.append(wrd)
                    break
    return details
##    print details




def tester(request):
    i=0
    det=[]
    clus1 = readfiles('rawdata')
    mappedCdata = []
    #===========================================================================
    # a2 = dataProcessing(clus1)
    #===========================================================================
    for data in clus1:
        details1 = fetchIdDetails(data)
        details1.append('total')
        details1 = details1+fetchAmount(data)
        if len(details1)<4:
            continue # create mapping also
        details1 = " ".join(details1)
        mappedCdata.append(data)
        det.append(details1)
        i=i+1;
        
    a2 = dataProcessing(filteredData(mappedCdata,True))
    clust1  = [mappedCdata[i] for i in set(a2[0][1])]
    clust2  = [mappedCdata[i] for i in set(a2[1][1])]
    clust3  = [mappedCdata[i] for i in set(a2[2][1])]
    
    return render_to_response('registration/welcome.html', {# to be removed in future-sidharth
                'messages': clust1,
                'clust1':det,
                'clust2':clust2,
                'clust3':clust3
                })

    