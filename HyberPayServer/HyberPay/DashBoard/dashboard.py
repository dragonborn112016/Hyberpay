'''
Created on Dec 1, 2015

@author: Sidharth
'''

from __future__ import division
from HyberPay.models import UserContactModel, UserMailsModel, UserDashboardModel
import time
import re
from HyberPay.DataProcessing.getIdDetaills import fetchAmount
from django.http.response import JsonResponse


def get_price(data):
    amt = fetchAmount(data)
    if not amt:
        return []
    amt1= re.sub('^[a-zA-Z]*[^a-zA-Z0-9]*','',amt[0])
    amt2 = re.sub('[a-zA-Z]*[^a-zA-Z0-9]*$','',amt1)
    return re.sub('[,]', '', amt2)
    
    
def get_monthly_expense(umm):
    
    
    month_dic = {i:[] for i in xrange(1,7)}
    cur_time = int(time.time()*1000)
    
    i=1
    dte = time.strftime('%d/%m/%Y',  time.gmtime(int(cur_time)/1000))
    dte1 = dte.split('/')
    cur_month = int(dte1[1])
    for m in umm:
        timestamp = m.timestamp
        dte = time.strftime('%d/%m/%Y',  time.gmtime(int(timestamp)/1000))
        dte1 = dte.split('/')
        price = get_price(m.text_mail)
        if not price:
            continue
        m_month = int(dte1[1])
        if cur_month == m_month:
            month_dic[i] += [float(price)]
        else:
            skp = cur_month - m_month
            cur_month = m_month
            i +=int(skp)
            if i>6:
                break
            month_dic[i] += [float(price)]
    
    for k in month_dic:
        month_dic[k] = sum(month_dic[k])
    
    return month_dic

    
def make_dashboard(request):
    username = request.user
    user = UserContactModel.objects.get(user = username)
    
    umm = UserMailsModel.objects.filter(ucm = user)
    month_dic = get_monthly_expense(umm)
    response = JsonResponse(month_dic)
    return response
    
def savedashboard(request):
    username = request.user
    user = UserContactModel.objects.get(user = username)
    umm = UserMailsModel.objects.filter(ucm = user)
    month_dic = get_monthly_expense(umm)
    resp = {}
    try :
        udb = UserDashboardModel.objects.get(ucm=user)
        resp['status'] = 'modified'
    except :
        udb = UserDashboardModel()
        udb.ucm = user
        resp['status'] = 'created'
        
    udb.month1 = month_dic[1]
    udb.month2 = month_dic[2]
    udb.month3 = month_dic[3]
    udb.month4 = month_dic[4]
    udb.month5 = month_dic[5]
    udb.month6 = month_dic[6]
    udb.save()
    return JsonResponse(resp)