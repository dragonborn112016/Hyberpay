'''
Created on Oct 24, 2015

@author: SIDHARTH
'''

class MessageReader():
    
    def __init__(self):
        self.msgId=''
        self.text=''
        self.html=''
        self.no_of_files=0
        self.filename=[]
        self.att_id=[]
        self.sender=''
        self.date=0
        self.label = ''
    
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