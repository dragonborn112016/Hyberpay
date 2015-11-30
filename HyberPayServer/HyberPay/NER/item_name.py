'''
Created on Nov 27, 2015

@author: Sidharth
'''

from __future__ import division
import re
from numpy import *
from collections import defaultdict
import sys
import time
import os


class GLMP:
    ''' stores features from corpus . Takes file handle as input'''

    def __init__(self):
        self.V=defaultdict(float)
        self.TAGS={'O':1,'S-ITEM':1,'ITEM':1,'PURP':1}

    def weights_V(self):
        ''' returns the weights'''
        return self.V


    def tags(self):
        ''' return tags in the model'''
        return self.TAGS.keys()


    def fea_Tag(self,w,t,i,n):
        ''' returns feature TAG:W:T where T is T(i)=tag  and W is W(i)=word
        at ith position in history'''
        if i<n:
            return 'TAG:'+w[i]+':'+t
        else :
            return 'TAG:'+''+':'+'STOP'

    def fea_Trigram(self,s,u,v):
        ''' returns feature TRIGRAM:S:U:V where s=T(-2) u=T(-1) v=T'''
        return 'TRIGRAM:'+s+':'+u+':'+v

    def fea_Suffix(self,h,t,j):
        '''suffix features for word len >3 SUFF:last j char of word(i) :j:t tag(i) '''
        i = h[3]
        n = len(h[2])
        if i<n:
            w = h[2][i]
            if len(w)>3:
                return 'SUFF:'+w[-j:]+':'+str(j)+':'+t
        return ''

    def fea_item(self,h,t):
        i = h[3]
        n = len(h[2])
        if i<n:
            x = h[2][:i]
            for w in x[i-10:]:
                if w == 'item' or w == 'product':
                    return 'PROD:' +h[2][i]+':'+w+':'+t
        return ''

    def fea_order(self,h,t):
        i = h[3]
        n = len(h[2])
        if i<n:
            x = h[2][:i]
            for w in x[i-10:]:
                if w == 'order' or w == 'transaction':
                    return 'ORD:' +h[2][i]+':'+w+':'+t
        return ''

    def fea_digit(self,h,t):
        i = h[3]
        n = len(h[2])
        if i<n:
            w = h[2][i]
            for l in w:
                if l.isalnum():
                    return 'DIGIT:'+w+':'+t
        return ''

    def fea_all_digit(self,h,t):
        i = h[3]
        n = len(h[2])
        if i<n:
            w = h[2][i]
            if w.isdigit():
                return 'ALL-DIGIT:'+w+':'+t
        return ''

    def fea_g(self,h,t):
        ''' returns a vector of features for a given history'''
##        sys.stderr.write(" history : %s len : %s \n" %(h[3],len(h[2])))
        suff1 = self.fea_Suffix(h,t,1)
        suff2 = self.fea_Suffix(h,t,2)
        suff3 = self.fea_Suffix(h,t,1)
        item = self.fea_item(h,t)
        dig = self.fea_digit(h,t)
        all_dig = self.fea_all_digit(h,t)
        order = self.fea_order(h,t)
        if suff1 == '':
            g =  {
                    self.fea_Tag(h[2],t,h[3],len(h[2])):1,
                    self.fea_Trigram(h[0],h[1],t):1
                    }
        else:
            g =  {
                    self.fea_Tag(h[2],t,h[3],len(h[2])):1,
                    self.fea_Trigram(h[0],h[1],t):1,
                    suff1:1,
                    suff2:1,
                    suff3:1,
                    
                    }
        if item != '':
            g[item]=1
        if dig != '':
            g[dig]=1
        if all_dig !='':
            g[all_dig]=1
        if order !='':
            g[order]=1
            
            
        return g


class GLM(GLMP):
    ''' stores features from corpus . Takes file handle as input'''

    def decode(self,handle):
        for l in handle:
            t = l.strip().split()
            fea = t[0].strip()
            val = float(t[1])
            self.V[fea] = val


