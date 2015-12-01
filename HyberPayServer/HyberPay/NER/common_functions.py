'''
Created on Nov 28, 2015

@author: Sidharth
'''

from __future__ import division
from collections import defaultdict
import sys
import time
import os

OTHERS_MODEL = os.path.join(os.path.dirname(__file__),'others.model')
UTILITY_MODEL = os.path.join(os.path.dirname(__file__),'utility.model')
DOA_MODEL = os.path.join(os.path.dirname(__file__),'doa.model')
DOD_MODEL = os.path.join(os.path.dirname(__file__),'dod.model')
TOA_MODEL = os.path.join(os.path.dirname(__file__),'toa.model')
TOD_MODEL = os.path.join(os.path.dirname(__file__),'tod.model')
DEPLOC_MODEL = os.path.join(os.path.dirname(__file__),'deploc.model')
ARVLOC_MODEL = os.path.join(os.path.dirname(__file__),'arvloc.model')


def argmax(ls):
    ''' takes a list of pairs (item,score) and returns argmax'''
    return max(ls,key = lambda x:x[1])

    
def viterbiGLM(glm,sentence):
    ''' x is sentence, find the tags for sentence'''
    n = len(sentence)
    #print 'len of mail :',n
    # the tag sets
    def K(k):
        if k in (-1,0):
            return ['*']
        return glm.tags()

    # pad sentence so that x[1] is the first word
    x = [""]+sentence
    y = [""]*(n+1)

    def g(h,t): return glm.fea_g(h,t)

    def dot_product(v,g):
        ''' dot product of two vectors'''
        dp = 0
        for k in g.keys():
            if k in v:
                dp +=1
        return dp
        

    # the viterbi algo
    #create and initialise chart
    pi = {}
    pi[0,'*','*']=0
    bp = {}
    v= glm.weights_V()

    # the main loop

    for k in xrange(1,n+1):
        for u in K(k-1):
            for s in K(k):
                bp[k,u,s],pi[k,u,s] = argmax([(t,pi[k-1,t,u]+dot_product(v,g((t,u,x,k),s)))
                                              for t in K(k-2)])


    # follow back pointers in the chart
    (y[n-1],y[n]),score = argmax([((u,s),pi[n,u,s]+dot_product(v,g((u,s,x,n+1),'STOP')))
                                  for u in K(n-1) for s in K(n)])

                
    for k in xrange(n-2,0,-1):
        y[k] = bp[k+2,y[k+1],y[k+2]]
    y[0] = '*'
    #scores = [pi[i,y[i-1],y[i]]for i in xrange(1,n)]

    return y[1:n+1]#,scores+[score]


def gen_fea_vec(glm,tagseq,sentence):
    fea_vec = defaultdict(int)

    # helper functions
    def g(h,t): return glm.fea_g(h,t)
    def t(k,seq=tagseq):
        if k<0:
            return '*'
        else:
            return seq[k]

        
    for k in xrange(len(sentence)):
##        h= (tagseq[k-2],tagseq[k-1],sentence,k)
##        t= tagseq[k]
        gi = g((t(k-2),t(k-1),sentence,k),t(k))
        key1 = gi.keys()
        for key in key1:
            fea_vec[key] += gi[key]

    n = len(tagseq)


    gi = g((t(n-2),t(n-1),sentence+[""],n),'STOP')
    key1 = gi.keys()
    for key in key1:
        fea_vec[key] += gi[key]

    return fea_vec

def perceptron_train(glm,sentence,tagseq):
    ''' learn the parameter vector  
    # compute gold_feature vector
    # compute the best tag sequence using viterbi
    # compare the gold and best tag sequence if there is a change then
    # update parameter vector
    # finally return glm
    '''
    def add_vec(d1,d2):
        key = d2.keys()
        res = d1.copy()
        for k in key:
            res[k] += d2[k]
        return res

    def sub_vec(v1,v2):
        key = v2.keys()
        res = v1.copy()
        for k in key:
            res[k] -= v2[k]
        return res
        
        
    V= glm.weights_V()
    gold_fea_vec = gen_fea_vec(glm,tagseq,sentence)
##        output.write("%s\n"%T)
    tagging,scores = viterbiGLM(glm,sentence)
##        output.write("done viterbi\n")
    best_fea_vec = gen_fea_vec(glm,tagging,sentence)

    if gold_fea_vec != best_fea_vec:
        V = add_vec(V,sub_vec(gold_fea_vec,best_fea_vec))

##    output.write("done parameters\n")

    return V
        
        


def read_sentences(handle):
    ''' lazily read sentence from handle'''
    sentence=[]
    for l in handle:
        if l.strip():
            sentence.append(l.strip())
        else :
            yield sentence
            sentence=[]

def print_tags(sentence, tagging,glm):
    ''' print out tagged sentence'''
    return "\n".join([w + " "+ t for w,t in zip(sentence, tagging) if t !='O'])
        

def ner(sentence_file,glm):
    ''' named entity recognizer '''
    sentence = sentence_file.split()
    #tagging,scores = viterbiGLM(glm,sentence)
    tagging = viterbiGLM(glm,sentence)
    return print_tags(sentence ,tagging,glm)


def read_train(handle):
    sen = []
    tag = []
    for l in handle:
        if l.strip():
            wrds = l.strip().split()
            sen.append(wrds[0])
            tag.append(wrds[-1])
        else:
            yield sen,tag
            sen=[]
            tag=[]

        
    
def perceptron(glm,train_file):

    for sen,tag in read_train(open(train_file)):

        V = perceptron_train(glm,sen,tag)
        glm.V=V
    return glm.V

def train(train_file,glmp):
    start_time = time.time()
    #glm = GLMP()
    output = sys.stdout
    
    sys.stderr.write("time taken : %s\n"%(time.time()-start_time))
    for T in xrange(10):
        sys.stderr.write("iteration : %s\n"%(T+1))
        glmp.V  = perceptron(glmp,train_file)


    V = glmp.V
    sys.stderr.write("time taken : %s\n"%(time.time()-start_time))
    for k in V.keys():
        output.write("%s %s\n"%(k,V[k]))

    

