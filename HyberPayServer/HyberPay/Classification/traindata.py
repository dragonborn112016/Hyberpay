'''
Created on Oct 30, 2015

@author: SIDHARTH
'''
from __future__ import division
import numpy
import math

from HyberPay.DataProcessing.readWriteFiles import writetofiles,readfiles
from HyberPay.Classification.category import category
from HyberPay.Classification.classifydata import getXY
from HyberPay.models import UserMailsModel
from collections import defaultdict

def get_keywords():
    ''' this function returns the list of all important
    keywords required to classify the documents
    in all returns the vocab that is needed
    '''
    K = defaultdict(int)
    k1 = readfiles('Classification/vocab')
    lkv = k1[0].split('\n') + k1[1].split('\n') + k1[2].split('\n')
##    print 'len total :',len(lkv)
##    print 'len k1 : ',len(k1[0].split('\n'))
##    print 'len k2 : ',len(k1[1].split('\n'))
##    print 'len k3 : ',len(k1[2].split('\n'))
    for kv in lkv:
        if kv :
            k = kv.split()
            K[k[0]] += int(k[-1])
    return K


def mapclus2doc(Y,cluster):
    
    ''' this function returns the mapping specifying
    which doc belongs to which label/class'''
    
    maping = []
    i=0
    for data in Y:
        if cluster == data:
            maping.append(i)
        i=i+1
    return maping

def compFreq(doc,pre_vocab):
    ''' computes the frequency of all important words in the document'''

    freq = defaultdict(float)
    c = doc.split()
    for wrd in c:
        if pre_vocab.has_key(wrd):
            freq[wrd] += 1

    for k in freq.keys():
        freq[k] += pre_vocab[k]

    return freq

def compvocab(data,pre_vocab):
    '''  details: function takes in a list of filtered messages data[]
    returns word frequency of each word in all documents
    returns dictionary(vocab)  
    '''
    #vocab = {}
    tmp = " ".join(data)
    vocab = compFreq(tmp,pre_vocab)
    return vocab

def probCluster(X,Y,cluster,pre_vocab):
    ''' X is train data ,Y is label corresponding to train data,  cluster is no of clusters
    probcluster returns a set of  [docset , len of doc set , prob of cluster , vocab of cluster , len of vocab]
    for all clusters'''

    docs = []
    totDoc = len(X)
    
    for c in cluster:
        maping = mapclus2doc(Y,c)
        tmp=[X[i] for i in maping]
        n = len(maping)
        prob = math.log10(n/totDoc)
        tmp = " ".join(tmp)
        freq = compFreq(tmp,pre_vocab)
        nfreq = len(freq)

        doc = [tmp,n,prob,freq,nfreq]
        docs.append(doc)
        
    return docs

def probAtrib(clusterProb,vocab,cluster,alpha):
    ''' computes the probability of each word for being in every cluster'''

    words = vocab.keys()
    probAtr={}
    lenvocab = len(words)
##    alpha = float(1)
    lencluster = len(cluster)
    for i in xrange(lencluster):

        #text = clusterProb[i][0]
        freq = clusterProb[i][3]
        n = clusterProb[i][4]

        for wrd in words:
            nk=0
            if freq.has_key(wrd):
                nk = freq[wrd]
            prob = math.log10((nk+alpha)/(n+alpha*lenvocab))
            if probAtr.has_key(wrd):
                res = probAtr[wrd]
                res[i] = prob
                probAtr[wrd] = res
            else:
                res = numpy.zeros(lencluster)
                res[i] = prob
                probAtr[wrd] = res

    return probAtr
            


def classifydoc(doc,probAtr,clusterProb,cluster,alpha,lenvocab):
    docwords = doc.split()
    maxprob = -numpy.inf
    maxc =-1
    
    for i in xrange(len(cluster)):
        n =clusterProb[i][4]
        prod = clusterProb[i][2]
        for wrd in docwords:
            if probAtr.has_key(wrd):
                res = probAtr[wrd]
                prob = res[i]
            else:
                prob = math.log10(alpha/(n+alpha*lenvocab))
            prod  = prod+prob
        if prod>maxprob:
            maxprob = prod
            maxc = i
    return [maxc ,maxprob]



def ClassificationPreComputing():
    ''' does the precomputing required to perform classification
    returns probAtr,clusterProb,cluster,alpha,lenvocab '''
    X,Y = getXY()
      
    cluster = ['0','1','2','3']
    #print "read data"
    
    pre_vocab = get_keywords()
    
    clusterProb = probCluster(X,Y,cluster,pre_vocab) #[docj,len(docj),probj,freqdiction,freqlen]
    #print "cluster done"

    vocab = compvocab(X,pre_vocab)
    #print "vocab done"
    alpha = 1
    probAtr = probAtrib(clusterProb,vocab,cluster,alpha)
    lenvocab = len(vocab)
    
    return probAtr,clusterProb,cluster,alpha,lenvocab


        
def getCategory(doc,probAtr,clusterProb,cluster,alpha,lenvocab):
    ''' returns the catagory of document currently under observation'''
    res = classifydoc(doc,probAtr,clusterProb,cluster,alpha,lenvocab)
    return category[str(res[0])]

 
def store_data():
    ''' function to create data for training purposes''' 
    umms = UserMailsModel.objects.all()
    print "precomputing"
    precompute = ClassificationPreComputing()
    print "precomputing done"
    X = []
    Y=[]
    for umm in umms:
        X.append(umm.text_mail)
      
    print "classifying :"
    i=-1
    for data in X:
        i+=1
        label = getCategory(data,precompute[0],precompute[1],precompute[2],precompute[3],precompute[4])
        Y.append(label)
      
    # store travel data    
    travel = []
    other = []
    utility=[]
    for i in range(len(X)):
        if Y[i] == 'travel':
            travel.append(X[i])
        elif Y[i] == 'others':
            other.append(X[i])
        elif Y[i] == 'utility':
            utility.append(X[i])
      
    writetofiles(travel, 'travel')
    writetofiles(other, 'others')
    writetofiles(utility, 'utility')
  
#===============================================================================
# store_data()
# print 'done'
#===============================================================================
