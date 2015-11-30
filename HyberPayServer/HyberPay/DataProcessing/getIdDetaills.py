'''
Created on Oct 27, 2015

@author: SIDHARTH
'''

import nltk
import re

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
                #print dt
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
    a=nltk.ngrams(dta1,5)
    keywords =['subtotal','fare','amount','paid']
    filter = ['distance']
    details = []
    flag=False
    
    for row in a:
        if flag:
            break
        
        if 'total' in row[0]:
            if row[1] in keywords:
                j=0

                for wrd in row:
                    if j<2:
                        j=j+1
                        continue
                    lett = str(wrd)
                    if (not lett.isalpha())and len(lett)>1:
                        for w in lett:
                            if w.isdigit():
                                flag=True
                                break
                    if flag:
##                        print row
                        wrd1 = re.sub('^[a-z]*[^a-zA-Z0-9]*[a-z]*[^a-zA-Z0-9]*',"",wrd)
                        wrd2 = re.findall('[a-z]*$',wrd1)
                        if len(wrd2)>1:
                            flag =False
                            continue
                        
                        wrd2 = re.findall('^[a-z]+[0-9]*$',wrd)
                        if len(wrd2)>1:
                            flag =False
                            continue
                        
                        details.append(wrd1)
                        break
    
    if flag:
        return details
    
    a=nltk.ngrams(dta1,5)

    for row in a:

        amt = str(row[0])
        patt = re.match('amt',amt)

        if flag:
            break
        if patt:
            for wrd in row:
                lett = str(wrd)
                if (not lett.isalpha())and len(lett)>1:
                    for w in lett:
                        if w.isdigit():
                            flag=True
                            break
                if flag:
##                    print row
                    wrd1 = re.sub('^[a-z]*[^a-zA-Z0-9]*[a-z]*[^a-zA-Z0-9]*',"",wrd)
                    details.append(wrd1)
                    break
                

            
    if flag:
        return details
    
    a=nltk.ngrams(dta1,5)

    for row in a:
        if flag:
            break
        if row[0] in keywords:
            j=-1

            for wrd in row:
                j=j+1;
                lett = str(wrd)
                #===============================================================
                # if j==3:
                #     break
                #===============================================================

                if j==1 and lett.isdigit():
                    continue

                
                if wrd in filter:
                    break
                    
                if (not lett.isalpha())and len(lett)>1:
                    for w in lett:
                        if w.isdigit():
                            flag=True
                            break

                if flag:
                    #print row
                    wrd1 = re.sub('^[a-z]*[^a-zA-Z0-9]*[a-z]*[^a-zA-Z0-9]*',"",wrd)
                    wrd2 = re.findall('[a-z]*$',wrd1)
                    if len(wrd2)>1:
                        flag =False
                        continue
                    wrd2 = re.findall('^[a-z]+[0-9]*$',wrd)
                    if len(wrd2)>=1:
                        flag =False
                        continue
                    wrd2 = re.findall('[^a-z0-9/-]$',wrd)
                    if len(wrd2)>=1:
                        flag =False
                        continue
                    
                    details.append(wrd1)
                    break

    if flag:
        return details
    
    a=nltk.ngrams(dta1,5)

    for row in a:
        if flag:
            break
        if 'payment' in row[0]:
            #print dta1
            j=-1

            for wrd in row:
                j=j+1;
                lett = str(wrd)
                #===============================================================
                # if j==3:
                #     break
                #===============================================================
                
                if wrd in filter:
                    break
                
                if (not lett.isalpha())and len(lett)>1:
                    for w in lett:
                        if w.isdigit():
                            flag=True
                            break

                if flag:
##                    print row
                    wrd1 = re.sub('^[a-z]*[^a-zA-Z0-9]*[a-z]*[^a-zA-Z0-9]*',"",wrd)
                    wrd2 = re.findall('[a-z]*$',wrd1)
                    if len(wrd2)>1:
                        flag =False
                        continue
                    if len(wrd1)<2:
                        flag = False
                        continue
                    details.append(wrd1)
                    break

    return details
##    print details




def fetch_nertag(nertag):
    if nertag.strip()=='' or nertag.strip()== None:
        return {}
    
    res = {}
    prevwt = ['']
    iname = ''
    tag =[]
    
    
    for wt in nertag.split('\n'):
        same_flag = False
        if res.has_key(wt):
            continue
        for k,v in res.iteritems():
            if k.startswith(wt[:5]):
                same_flag = True
                break
        if same_flag:
            continue
        res[wt]=1
        tag.append(wt)
    
    res = {}
    flagtag = False
    for wt in tag:
        w = wt.split()
        if prevwt[-1] == w[-1]:
            if flagtag:
                iname += ' '+w[0]
                #print 'iname :',iname
            else:
                flagtag = True
                iname =  prevwt[0] + " " + w[0]
        else :
            #print 'else',iname , flagtag
            if flagtag:
                flagtag = False
                res[prevwt[-1]] = iname
                iname = ''
            if prevwt[-1]!='':
                res[prevwt[-1]] = prevwt[0]
        
        prevwt = w
    
    if flagtag:
        res[prevwt[-1]] = iname
    else :
        res[prevwt[-1]] = prevwt[0]
        
    print res            
    return res


def fetch_nertag_item(nertag):
    if nertag.strip()=='' or nertag.strip()== None:
        return {}

    res = {}
    prevwt = ['']
    iname = ''
    tag =[]
    
    
    for wt in nertag.split('\n'):
        same_flag = False
        if res.has_key(wt):
            continue
        for k,v in res.iteritems():
            if k.startswith(wt[:5]):
                same_flag = True
                break
        if same_flag:
            continue
        res[wt]=1
        w = wt.split()
        if w[-1]=='S-ITEM':
            w[-1] = 'ITEM'
        tag.append(" ".join(w))
    
    res = {}
    flagtag = False
    for wt in tag:
        w = wt.split()
        if prevwt[-1] == w[-1]:
            if flagtag:
                iname += ' '+w[0]
                #print 'iname :',iname
            else:
                flagtag = True
                iname =  prevwt[0] + " " + w[0]
        else :
            #print 'else',iname , flagtag
            if flagtag:
                flagtag = False
                res[prevwt[-1]] = iname
                iname = ''
            if prevwt[-1]!='':
                res[prevwt[-1]] = prevwt[0]
        
        prevwt = w
    
    if flagtag:
        res[prevwt[-1]] = iname
    else :
        res[prevwt[-1]] = prevwt[0]
    
    print res
                    
    return res
