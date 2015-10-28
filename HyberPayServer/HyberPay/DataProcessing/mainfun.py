'''
Created on Oct 24, 2015

@author: SIDHARTH
'''
from HyberPay.DataProcessing.CleanData import filteredData
from HyberPay.DataProcessing.Computetfidf import compWordFreq, compVocab,\
    compIDF, compTf, compSimmatrix
from numpy.core.numeric import Inf
from HyberPay.DataProcessing.kmeans import kmeanDocCluster

def dataProcessing(cdata,k=3):
    
    wordf = compWordFreq(cdata)
    vocab = compVocab(cdata)
    idf = compIDF(vocab,wordf)
    tflist = compTf(wordf)
    print "computing simmatrix"
    simmatrix = compSimmatrix(tflist,idf)
    dis = 1-simmatrix
    minma = Inf
    print "simmatrix done"
    a1 = [[],[]]
    print "starting kmeans"
    for j in range(20):
        res = kmeanDocCluster(k,tflist,idf,dis)
        #print "result :" ,res
        a2 = res[0]
        minma1 = res[1]
        if minma>minma1:
            a1[0]=a2
            a1[1]=minma1
            minma = minma1
    
    #print simmatrix
    a2 = a1[0]
    print a2[0][1]
    print "minma :",a1[1]
    return  a2
