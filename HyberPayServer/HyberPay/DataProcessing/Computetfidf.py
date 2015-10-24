'''
Created on Oct 24, 2015

@author: SIDHARTH
'''
from cmath import log10



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
    returns tf 
    '''
    tf =[]
    for dta in wordf:
        tfd={}
        tmp = dta[0]
        cnt = float(dta[1])
        keyset = tmp.keys()
        print "count" ,cnt
        for wrd in keyset:
            tfd[wrd]=tmp[wrd]/cnt
        tf.append(tfd)
    return tf

def compIDF(vocab,wordf):
    ''' details:vocab is dictionary of words in all the messages
    wordf is list[dictionary(i),n(i)] of each document
    returns idf = total doc/no of words with word in it
    '''
    idf = {}
    keyset = vocab.keys()
    for wrd in keyset:
        cnt = 0
        m = len(wordf)
        i=0
        while i<m:
            tmp = wordf[i][0]
            if tmp.has_key(wrd):
                cnt =cnt+1;
            i=i+1
        
        idf[wrd]= 1 + log10(m/float(cnt))
    
    #print idf
    
    return idf

def compSimmatrix():
    ''' details:
    '''
    pass

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
    
