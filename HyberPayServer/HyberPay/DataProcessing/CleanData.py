'''
Created on Oct 24, 2015

@author: SIDHARTH
'''

             
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
            tmp = re.sub("[^a-zA-Z]"," ",tmp)
        
        tmp = tmp.lower()
        words = tmp.split()
        #=======================================================================
        # if ripSpChr:
        #     words = [w for w in words if not w in stops]
        #=======================================================================
        res = (" ".join(words))
        cdata.append(res)

    return cdata

def filteredData(list,doclean = False,ripSpChr=False):
    if doclean:
        cdata = cleanfiles(list, ripSpChr)
    else:
        cdata = list
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
    mapping = []
    i=-1
    for dta in cdata:
        i=i+1
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
                mapping.append(i)
    
    return {'fdata':fdata,
            'mapping':mapping}
                        