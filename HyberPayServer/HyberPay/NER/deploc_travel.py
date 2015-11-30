'''
Created on Nov 28, 2015

@author: Sidharth
'''

from __future__ import division
from collections import defaultdict

class GLMP:
    ''' stores features from corpus . Takes file handle as input'''

    def __init__(self):
        self.V=defaultdict(float)
        self.TAGS={'O':1,'DEPLOC':1}

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

    def make_map(self,w):
        ''' maps the word so that alphabets-> x numbers ->d and spcl charachters ->s'''
        mp = ''
        for let in w:
            if let.isalpha():
                mp += 'x'
            elif let.isdigit():
                mp += 'd'
            else:
                mp += 's'

        if len(mp)<=4:
            return mp
        st = set(mp[2:-2])
        mp1 = mp[:2]
        for let in st:
            mp1+=let
        mp1 +=mp[-2:]
        return mp1
        

    def fea_digit(self,h,t):
        ''' if the word contains digit'''
        i = h[3]
        n = len(h[2])
        if i<n:
            w = h[2][i]
            for l in w:
                if l.isalnum():
                    return 'DIGIT:'+w+':'+t
        return ''

    def fea_all_digit(self,h,t):
        ''' if all letters in the word are digits'''
        i = h[3]
        n = len(h[2])
        if i<n:
            w = h[2][i]
            if w.isdigit():
                return 'ALL-DIGIT:'+w+':'+t
        return ''

    def fea_map(self,h,t):
        ''' map features MAP:map(w(i)):tag(i)'''
        i = h[3]
        n = len(h[2])
        if i<n:
            w = h[2][i]
            mp1 = self.make_map(w)
            return 'MAP:'+mp1+':'+t
            
        return ''

    def fea_words(self,h,t,j):
        ''' WORD:map(w(i)):prev word at jth position:j:tag'''
        i = h[3]
        n = len(h[2])
        if i<n:
            prev = h[2][:i]
            if len(prev)<j:
                return ''
            
            w = h[2][i]
            mp = self.make_map(w)
            return 'WORD:'+mp+':'+prev[-j]+':'+str(j)+':'+t
            
        return ''

    def fea_word_map(self,h,t,j):
        ''' join of word and map features'''
        i = h[3]
        n = len(h[2])
        if i<n:
            prev = h[2][:i]
            if len(prev)<j:
                return ''
            
            w = h[2][i]
            mp = self.make_map(w)
            return 'WORD-MAP:'+mp+':'+self.make_map(prev[-j])+':'+str(j)+':'+t
            
        return ''

    def fea_Ptag(self,h,t,j):
        i = h[3]
        n = len(h[2])
        if i<n:
            prev = h[2][:i]
            if len(prev)<j:
                return ''
            
            return 'PTAG:'+prev[-j]+':'+str(j)+':'+t
            
        return 'PTAG:'+h[2][:i][-j]+':'+str(j)+':'+'STOP'

    def fea_Ftag(self,h,t,j):
        i = h[3]
        n = len(h[2])
        if i+j<n:
            fwd = h[2][i:]
            
            return 'FTAG:'+fwd[j]+':'+str(j)+':'+t
            
        return ''

    def fea_g(self,h,t):
        ''' returns a vector of features for a given history'''
##        sys.stderr.write(" history : %s len : %s \n" %(h[3],len(h[2])))

        dig = self.fea_digit(h,t)
        all_dig = self.fea_all_digit(h,t)
        mp = self.fea_map(h,t)
        g =  {
                    self.fea_Tag(h[2],t,h[3],len(h[2])):1,
                    self.fea_Trigram(h[0],h[1],t):1
                    }

        if mp !='':
            g[mp]=1
        if dig != '':
            g[dig]=1
        if all_dig !='':
            g[all_dig]=1

        for j in xrange(1,10):
            f  = self.fea_words(h,t,j)
            f1 = self.fea_word_map(h,t,j)
            f2 = self.fea_Ptag(h,t,j)
            f3 = self.fea_Ftag(h,t,j)
            if f !='':
                g[f]=1

            if f1 !='':
                g[f1] = 1
            if f2 !='':
                g[f2] =1
            if f3 !='':
                g[f3]=1
            

        return g


class GLM(GLMP):
    ''' stores features from corpus . Takes file handle as input'''

    def decode(self,handle):
        for l in handle:
            t = l.strip().split()
            fea = t[0].strip()
            val = float(t[1])
            self.V[fea] = val
