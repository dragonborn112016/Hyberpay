'''
Created on Oct 30, 2015

@author: SIDHARTH
'''
import os

def writetofiles(list,name):
    
    cnt = len(list)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    folder = os.path.join(BASE_DIR,name)

    if not os.path.exists(folder):
        os.makedirs(folder)

    for i in range(cnt):
        fname =os.path.join(folder,name+str(i)+'.txt') 
        fo =open(fname,'w')
        fo.write(list[i].encode('ascii', 'ignore'))
        fo.close()


def readfiles(name,isDel=False):
    list =[]
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    folder = os.path.join(BASE_DIR,name)
    for the_file in os.listdir(folder):
        fname = os.path.join(folder, the_file)
        fo =open(fname,'r')
        data = fo.read()
        list.append(data)
        fo.close()
    if isDel:
        folder = os.path.join(BASE_DIR,name)
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                #elif os.path.isdir(file_path): shutil.rmtree(file_path)
            except Exception, e:
                print e

    return list
