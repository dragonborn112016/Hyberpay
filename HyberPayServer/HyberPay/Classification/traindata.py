'''
Created on Oct 30, 2015

@author: SIDHARTH
'''

import numpy
import math

from HyberPay.DataProcessing.readWriteFiles import readfiles
from HyberPay.Classification.category import category
from HyberPay.Classification.classifydata import getXY

def mapclus2doc(Y,cluster):
    maping = []
    i=0
    for data in Y:
        if str(cluster) == str(data):
            maping.append(i)
        i=i+1
    return maping

def probCluster(X,Y,cluster):
    
    docs = []
    totDoc = float(len(X))
    for c in cluster:
        maping = mapclus2doc(Y,c)
        tmp=[X[i] for i in maping]
        n = float(len(maping))
        #=======================================================================
        # print "n :",n
        # print "totdoc :",totDoc
        #=======================================================================
        prob = n/totDoc
        tmp = " ".join(tmp)
        freq = compFreq(tmp)
        nfreq=float(len(freq))

        doc = [tmp,n,prob,freq,nfreq]
        docs.append(doc)
    return docs

def probAtrib(clusterProb,vocab,cluster,alpha):
    words = vocab.keys()
    probAtr={}
    lenvocab = len(words)
##    alpha = float(1)
    lencluster = len(cluster)
    for i in range(len(cluster)):

        text = clusterProb[i][0]
        freq = clusterProb[i][3]
        n=clusterProb[i][4]

        for wrd in words:
            nk=0
            if freq.has_key(wrd):
                nk = float(freq[wrd])
            prob = (nk+alpha)/(n+alpha*lenvocab)
            if probAtr.has_key(wrd):
                res = probAtr[wrd]
                res[i] = prob
                probAtr[wrd] = res
            else:
                res = numpy.zeros(lencluster)
                res[i] = prob
                probAtr[wrd] = res

    return probAtr
            
def compFreq(doc):

    freq ={}
    c = doc.split()
    for wrd in c:
        if freq.has_key(wrd):
            freq[wrd] = freq[wrd]+1
        else:
            freq[wrd]=1

    return freq
    

def compvocab(data):
    '''  details: function takes in a list of filtered messages data[]
    returns word frequency of each word in all documents
    returns dictionary(vocab)  
    '''
    vocab = {}
    tmp = " ".join(data)
    vocab = compFreq(tmp)
    return vocab


def classifydoc(doc,probAtr,clusterProb,cluster,alpha,lenvocab):
    docwords = doc.split()
    maxprob = -numpy.inf
    maxc =-1
    
    for i in range(len(cluster)):
        n =clusterProb[i][4]
        #=======================================================================
        # print "clusterprob ",i," :",clusterProb[i][2]
        #=======================================================================
        prod = math.log10(clusterProb[i][2])
        for wrd in docwords:
            if probAtr.has_key(wrd):
                res = probAtr[wrd]
                prob = res[i]
            else:
                prob = alpha/(n+alpha*lenvocab)
            prod  = prod+math.log10(prob)
        if prod>maxprob:
            maxprob = prod
            maxc = i
    return [maxc ,maxprob]

def ClassificationPreComputing():
    XY = getXY()
    X = XY[0]
    Y = XY[1]
    cluster = ['0','1','2','3']
    print "read data:",len(XY)
    
    clusterProb = probCluster(X,Y,cluster) #[docj,len(docj),probj,freqdiction,freqlen]
    print "cluster done"

    vocab = compvocab(X)
    print "vocab done :",len(vocab)
    alpha = float(1)
    probAtr = probAtrib(clusterProb,vocab,cluster,alpha)
    lenvocab = len(vocab)
    print "prob atrib done :",len(probAtr)
    res = [probAtr,clusterProb,cluster,alpha,lenvocab]
    return res
        
def getCategory(doc,probAtr,clusterProb,cluster,alpha,lenvocab):

    res = classifydoc(doc,probAtr,clusterProb,cluster,alpha,lenvocab)
##    print doc
##
##    print "cluster :",category[str(res[0])]
##    print "prob :",res[1]
    return category[str(res[0])]


