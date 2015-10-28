'''
Created on Oct 24, 2015

@author: SIDHARTH
'''
from math import log10, sqrt
from numpy.core.multiarray import zeros



def compWordFreq(data):
    ''' details: function takes in a list of filtered messages data[]
    returns word frequency per document
    returns [wordf(i),n(i)] that is wordfrequency of each document and no of words in each document
    '''
    wordf=[]
    for dta in data:
        mapd = {}
        c = dta.split()
        for wrd in c:
            if mapd.has_key(wrd):
                mapd[wrd]=mapd[wrd]+1;
            else:
                mapd[wrd]=1
        
        lst = [mapd,len(c)]
        wordf.append(lst)
    #print "word list :" ,wordf[1][0]
    #print "no: ",wordf[1][1]
    return wordf

def compTf(wordf):
    ''' details:wordf is list[dictionary(i),n(i)] of each document
    returns tflist for all documents 
    '''
    tflist =[]
    for dta in wordf:
        tfd={}
        tmp = dta[0]
        cnt = float(dta[1])
        keyset = tmp.keys()
        for wrd in keyset:
            tfd[wrd]=tmp[wrd]/cnt
        tflist.append(tfd)
    return tflist

def compIDF(vocab,wordf):
    ''' details:vocab is dictionary of words in all the messages
    wordf is list[dictionary(i),n(i)] of each document
    returns idf = total doc/no of words with word in it
    '''
    idf = {}
    keyset = vocab.keys()
    for wrd in keyset:
        cnt = float(0)
        m = float(len(wordf))
        i=0
        while i<m:
            tmp = wordf[i][0]
            if tmp.has_key(wrd):
                cnt =cnt+1;
            i=i+1
        
        idf[wrd]= 1 + log10(m/cnt)
        # print "idf :",idf[wrd]
    
    #print idf
    
    return idf

def compVocab(data):
    '''  details: function takes in a list of filtered messages data[]
    returns word frequency of each word in all documents
    returns dictionary(vocab)  
    '''
    vocab = {}
    for dta in data:
        c = dta.split()
        for wrd in c:
            if vocab.has_key(wrd):
                vocab[wrd] = vocab[wrd]+1
            else:
                vocab[wrd]=1
    
    #print vocab
    return vocab
    
def tfidfMap(tf,idf):
    '''details:tf and idf are maps of single document
    returns a map of tfidf for that document
    '''
    tfidf={}
    keyset = tf.keys()
    for wrd in keyset:
        tfidf[wrd] = tf[wrd]*idf[wrd]
    
    return tfidf

def tfidfMapList(tflist,idf):
    tfidflist = []
    for tf in tflist:
        tfidflist.append(tfidfMap(tf, idf))
    
    return tfidflist



def compSimmatrix(tflist,idf):
    ''' details:tflist is a list of dictionaries of tf of all documents
    idf is dictionary
    returns simmilarity matrix of all documents
    '''
    
    tfidflist  = tfidfMapList(tflist, idf)
    
    n = len(tflist)
    simmatrix = zeros((n,n),float)
    i=0
    while i<n :
        tfidf1 = tfidflist[i]
        simmatrix[i][i]=1
        j=i+1
        while j<n :
            tfidf2 = tfidflist[j]
            prod1 = compDotProduct(tfidf1, tfidf2)
            simmatrix[i][j]=prod1
            simmatrix[j][i]=prod1
            j=j+1
        i=i+1
    
    return simmatrix
    
            
            

def compDotProduct(tfdoc1,tfdoc2):
    '''details: compute dot product for 2 documents
    tfdoc1 is tfidf map for doc1... same for tfdoc2->doc2
    returns dot product
    '''
    m = len(tfdoc1)
    m1 = len(tfdoc2)
    pos = 0
    if m>m1:
        pos=2
    else:
        pos=1
    
    keyset1 = tfdoc1.keys()
    keyset2 = tfdoc2.keys()
    
    card1 = compCardinality(keyset1, tfdoc1)
    card2 = compCardinality(keyset2, tfdoc2)
    
    commonkeys = []
    if pos ==1:
        keyset = keyset1
        srch = tfdoc2
    else:
        keyset = keyset2
        srch = tfdoc1
    for wrd in keyset:
        if srch.has_key(wrd):
            commonkeys.append(wrd)
    fea = float(0)
    for wrd in commonkeys:
        fea = fea + tfdoc1[wrd]*tfdoc2[wrd]
    
   
    card = sqrt(float(card1))*sqrt(float(card2))
    fea = fea/card
    return fea
    
def compCardinality(keyset,tfdoc):
    '''details:computes cardinality for the doc
    tfdoc is tfidf map for doc
    returns cardinality
    '''
    card=float(0)
    for wrd in keyset:
        card = card+tfdoc[wrd]*tfdoc[wrd]
    
    #print card

    return card