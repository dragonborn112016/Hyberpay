'''
Created on Oct 24, 2015

@author: SIDHARTH
'''

class MessageReader():
    
    def __init__(self):
        self.text=''
        self.html=''
        self.no_of_files=0
        self.sender=''
        self.date=0
    
    def setText(self,text):
        self.text=text
        
    def setHtml(self,html):
        self.html=html
        
    def setNoOfFiles(self,no_of_files):
        self.no_of_files=no_of_files
    
    def setSender(self,sender):
        self.sender=sender
    
    def setDate(self,date):
        self.date=date