'''
Created on Dec 14, 2015

@author: Sidharth
'''
from __future__ import division
import time
from HyberPay.DataProcessing.getIdDetaills import fetchAmount
from HyberPay.Classification.category import category
import re
from HyberPay.Classification.traindata import ClassificationPreComputing,\
    getCategory

month_map = {1 : 'Jan',
             2 : 'Feb',
             3 : 'Mar',
             4 : 'Apr',
             5 : 'May',
             6 : 'Jun',
             7 : 'Jul',
             8 : 'Aug',
             9 : 'Sep',
             10 : 'Oct',
             11 : 'Nov',
             12 : 'Dec'
             }

IND_OTHERS = 0
IND_UTILITY =1
IND_TRAVEL =2


def get_price(data):
    amt = fetchAmount(data)
    if not amt:
        return []
    amt1= re.sub('^[a-zA-Z]*[^a-zA-Z0-9]*','',amt[0])
    amt2 = re.sub('[a-zA-Z]*[^a-zA-Z0-9]*$','',amt1)
    return re.sub('[,]', '', amt2)
    

def get_month_dic():
    return {'month':0,
            'data':[{'label':category['1'],'total':0},
                    {'label':category['2'],'total':0},
                    {'label':category['3'],'total':0}
                    ]
            }



def get_monthly_expense(umm,for_months):
    
    # precomppute to classify mails
    precompute = ClassificationPreComputing();
    month_dic = {i: get_month_dic() for i in xrange(1,for_months)}
    cur_time = int(time.time()*1000)
    
    i=1
    dte = time.strftime('%d/%m/%Y',  time.gmtime(int(cur_time)/1000))
    dte1 = dte.split('/')
    cur_month = int(dte1[1])
    for j in xrange(1,for_months):
        month_dic[j]['month'] = month_map[cur_month]
        cur_month -=1;
        if cur_month ==0:
            cur_month = 12;
    
    cur_month = int(dte1[1])
    
    mCatKeys = category.keys()
    mCatVal = [category['1'],category['2'],category['3']]
    for m in umm:
        timestamp = m.timestamp
        dte = time.strftime('%d/%m/%Y',  time.gmtime(int(timestamp)/1000))
        dte1 = dte.split('/')
        price = get_price(m.text_mail)
        if not price:
            continue
        m_month = int(dte1[1])
        m_label = getCategory(m.text_mail,precompute[0],precompute[1],precompute[2],precompute[3],precompute[4])
        if cur_month == m_month:
            
            for j in xrange(len(mCatKeys)):
                if category[str(j)] == m_label: 
                    if m_label in mCatVal:
                        month_dic[i]['data'][j-1]['total'] += float(price)
        else:
            #month_dic[i['month']] = cur_month
            
            skp = cur_month - m_month
            print "Before cur month :",cur_month," mail month : ",m_month," skp :",skp," i:",i
            cur_month = m_month
            if skp < 0:
                skp += 12
            i +=int(skp)
            if i>for_months-1:
                break
            for j in xrange(len(mCatKeys)):
                if category[str(j)] == m_label: 
                    if m_label in mCatVal:
                        print "month dic i : ",i," j-1 : ",j-1
                        print "After cur month :",cur_month," mail month : ",m_month
                        month_dic[i]['data'][j-1]['total'] += float(price)
    
    return month_dic
