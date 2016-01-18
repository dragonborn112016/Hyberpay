'''
Created on Dec 1, 2015

@author: Sidharth
'''

from __future__ import division
from HyberPay.models import UserContactModel, UserMailsModel,\
    UserExpenseModel
from django.http.response import JsonResponse
from HyberPay.DashBoard.dashboard_utility import get_monthly_expense, IND_OTHERS,\
    IND_UTILITY, IND_TRAVEL
    

    
def make_dashboard(request,username):
    user = UserContactModel.objects.get(user = username)
    umm = UserMailsModel.objects.filter(ucm = user)
    for_months =4;
    month_dic = get_monthly_expense(umm,for_months)
    ret_dic = {"Total Expense" : month_dic}
    response = JsonResponse(ret_dic,safe=False)
    return response
    
def savedashboard(request):
    username = request.user
    user = UserContactModel.objects.get(user = username)
    umm = UserMailsModel.objects.filter(ucm = user)
    for_months =7;
    month_dic = get_monthly_expense(umm,for_months)
    resp = {}
    uems = UserExpenseModel.objects.filter(ucm = user)
    if uems:
        i=1
        for uem in uems:
            uem.month_id = i;
            uem.month = month_dic[i]['month']
            uem.others = month_dic[i]['data'][IND_OTHERS]['total']
            uem.utility = month_dic[i]['data'][IND_UTILITY]['total']
            uem.travel = month_dic[i]['data'][IND_TRAVEL]['total']
            uem.save()
            i +=1;
        
        resp['status'] = 'modified'
    else :
        
        for i in xrange (1,7):
            uem = UserExpenseModel()
            uem.ucm = user
            uem.month_id = i;
            uem.month = month_dic[i]['month']
            uem.others = month_dic[i]['data'][IND_OTHERS]['total']
            uem.utility = month_dic[i]['data'][IND_UTILITY]['total']
            uem.travel = month_dic[i]['data'][IND_TRAVEL]['total']
            uem.save()
        resp['status'] = 'created'
    return JsonResponse(resp)