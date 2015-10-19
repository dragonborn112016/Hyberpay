from django.shortcuts import render, render_to_response
from django.http import request
from django.http.response import HttpResponse
from django.template.loader import get_template

# Create your views here.
def main_page(request):
    template = get_template('index.html')
    output = template.render()
    return HttpResponse(output);

def portals_page(request,filename):
    fname ="/".join(['portals',filename]);
    fname = ".".join([fname,'html'])
    template = get_template(fname)
    output = template.render()
    return HttpResponse(output);