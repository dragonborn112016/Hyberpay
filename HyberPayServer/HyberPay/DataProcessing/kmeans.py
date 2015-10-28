'''
Created on Oct 26, 2015

@author: SIDHARTH
'''
from random import SystemRandom
from numpy.core.numeric import Inf

def kmeanDocCluster(k,tflist,idf,dis):
    '''details: computes kmean clustering 
    k no of clusters
    dis is distance matrix
    '''
    rng = SystemRandom()
    c = rng.sample(range(0,len(tflist)-1), k)
    cluster = []
    i=0;
    while i<k:
        cluster.append([c[i],[]]) 
        i=i+1
    #print "initial cluster :" ,cluster
    n=len(tflist)
    precluster = kmeaniter(k,cluster,dis,n)
    #print "precluster : ",precluster
    iter1 =0
    while True:
        cluster = kmeaniter(k, precluster, dis, n)
        flag = False
        for i in range(k):
            if precluster[i][0] != cluster[i][0]:
                flag = True
        
        if flag or iter1>10000 or precluster == cluster:
            break
        precluster = cluster
        iter1 = iter1+1
    
    minma = 0
    for i in range(k):
        arlist =cluster[i][1]
        minma = minma+sum(dis[cluster[i][0]][[arlist]]) 
    return [cluster ,minma]



def kmeaniter(k,cluster,dis,n):
    c=[]
    for i in range(k):
        c.append(cluster[i][0])
        cluster[i][1] = []
    
    for i in range(n):
        d1 = dis[i][c]
        ind = d1.argmin()
        carr = cluster[ind][1]
        carr+=[i]
        cluster[ind][1] = carr
        #print "carr : ",carr
        #print cluster
    
    for i in range(k):
        b= Inf
        arr = cluster[i][1]
        arr.append(cluster[i][0])
        m= len(arr)
        minc = -1
        for j in range(m):
            d1 = sum(dis[arr[j]][arr])
            if min(d1,b)==b:
                continue
            else:
                minc = arr[j]
                b=d1
        
        cluster[i][0] = minc
    #print cluster    
    return cluster