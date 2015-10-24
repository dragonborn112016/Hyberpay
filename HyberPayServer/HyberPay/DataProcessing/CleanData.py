'''
Created on Oct 24, 2015

@author: SIDHARTH
'''


from bs4 import BeautifulSoup             
import nltk
import os
import re
from bs4 import BeautifulSoup             
from nltk.corpus import stopwords

def cleanfiles(list,ripSpChr=False):
    cdata = []
    stops = set(stopwords.words("english")) 
    for dta in list:
        dta1 = re.sub("<br>"," ",dta)
        
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
            tmp = re.sub("[^a-zA-Z0-9]"," ",tmp)
        
        tmp = tmp.lower()
        words = tmp.split()
##        words = [w for w in words if not w in stops]
        res = (" ".join(words))
        cdata.append(res)

    return cdata

def filteredData(list,ripSpChr=False):
    cdata = cleanfiles(list, ripSpChr)
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
    fdata=[]
    emptylst = [""," ",None]
    
    for dta in cdata:
        dta = dta.strip()
        if dta in emptylst:
            continue;
        else:
            wrds = dta.split();
            if len(wrds)<5:
                continue
            else:
                cnt =0
                minflag = False
                for wrd in wrds:
                    if wrd in keyset:
                        cnt = cnt+1;
                        minflag=True
                        break
                       
                        
                if not minflag:
                    continue
                fdata.append(dta)
    
    return fdata
                        