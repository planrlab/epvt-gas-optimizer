'''
Created on Mar 21, 2023

@author: ACER
'''
import pickle

class SagObjReader(object):
   
    def __init__(self, params):
        '''
        Constructor
        '''
        

class Company(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

mylist = []
with open('company_data.pkl', 'wb') as outp:
    company1 = Company('banana', 40)
    pickle.dump(company1, outp, pickle.HIGHEST_PROTOCOL)
    mylist.append(company1)
    company2 = Company('spam', 42)
    pickle.dump(company2, outp, pickle.HIGHEST_PROTOCOL)
    mylist.append(company2)

   

del company1
del company2








exlist = []
with open('company_data.pkl', 'rb') as inp:
    try:
        while True:
            c = pickle.load(inp)
            exlist.append(c)
    except EOFError:
        print("Done with Processing")

print(exlist)
    
    







    