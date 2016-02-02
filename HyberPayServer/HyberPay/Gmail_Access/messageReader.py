'''
Created on Oct 24, 2015

@author: SIDHARTH
'''
from ssl import Purpose

class MessageReader():
    
    def __init__(self):
        self.msgId = ""
        self.text = ""
        self.html = ""
        self.no_of_files = 0
        self.filename = []
        self.att_id = []
        self.sender = ""
        self.date = 0
        self.label = ""
        
        self.amount = ""
        
        self.DOD = ""
        self.TOD = ""
        self.DEPLOC = ""
        
        self.ITEM = ""
        self.PURP = ""
        
        self.DD = ""
        
        self.category = 0
        
    
    def setMsgId(self,msgId):
        self.msgId = msgId
    
    def setText(self,text):
        self.text=text
        
    def setHtml(self,html):
        self.html=html
        
    def setNoOfFiles(self,no_of_files):
        self.no_of_files=no_of_files
        
    def setFilename(self,filename):
        self.filename = filename
    
    def setAtt_id(self,att_id):
        self.att_id = att_id
    
    
    def setSender(self,sender):
        self.sender=sender
    
    def setDate(self,date):
        self.date=date
        
    def setLabel(self,label):
        self.label=label
    
    def setAmount(self,amount):
        self.amount=amount
    
    def setDD(self,DD):
        self.DD=DD
    
    def setITEM(self,ITEM):
        self.ITEM=ITEM
        
    def setPURP(self,PURP):
        self.PURP=PURP
    
    def setDOD(self,DOD):
        self.DOD=DOD
    
    def setTOD(self,TOD):
        self.TOD=TOD
    
    def setDEPLOC(self,DEPLOC):
        self.DEPLOC=DEPLOC
        
    def setCategory(self,category):
        self.category = category
        