# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 11:17:51 2019

@author: John
"""

#!pip install camelot-py[cv]
#!pip install PyPDF2
#!pip install tabula-py

import os
import PyPDF2
import re
import tabula
from tabula import wrapper
import pandas as pd
import numpy as np

#set path
os.chdir(r"C:\Users\zhuoli\Dropbox\KairongZhuoli\0_small tasks\4_python_scrape_table")

###############################################################################
# some functions for finding data: return number of page where the table locates
def find_page(searchstr,pdfobj):
    # Get number of pages
    NumPages = pdfobj.getNumPages()
    
    for i in range(0, NumPages):
        PageObj = pdfobj.getPage(i)
        # replace \n \t with a space
        Text = PageObj.extractText().replace("\n"," ").replace(".\t"," ")
        # replace multiple space with one space
        Text = ' '.join(Text.split())
        #lower cases
        Text=Text.lower()
        if re.search(searchstr,Text):
            print(i+1)
            return i+1
    return 0

# clean data and return
def dataframe_clean(df,area):
    # drop row and column whose values are missing
    df=df.dropna(axis=0,how='all')
    df=df.dropna(axis=1,how='all')
    
    templist=[]
    maxrow=0
    for i in range(df.shape[0]):
        # manipulate by row
        temp=df.iloc[i]
        # drop missing value, so that the data looks like a,b,c,...(from  a,na,b,c,na,...d...)
        temp=temp.dropna(axis=0)
        if maxrow<temp.shape[0]:
            maxrow=temp.shape[0]
        templist.append(temp)
    
    contatlist=[]
    for temp in templist:
        # drop only one observation rows
        if temp.shape[0]>1:
            # for example, (2010/2011/... only has 5 col, but others: nameA data_2010, data_2011... has 6 col)
            lag=maxrow-temp.shape[0]
            temp=pd.concat([pd.Series([""]*lag), temp])
            # change the index
            temp=temp.reset_index()
            del temp['index']
            contatlist.append(temp)
    if contatlist==[]:
        return 0
    data=pd.concat(contatlist,axis=1)
    
    new_header = data.iloc[0] #grab the first row for the header
    data = data[1:] #take the data less the header row
    data.columns = new_header #set the header row as the df header
    
    #data=data.set_index(data.columns[0])
    data['area']=area
    return data

# when there are two tables in one page
def twotableproblem(df,area,findstr):
    rowlen=df.shape[0]
    begin=[]
    end=[]
    # find the beginning and end of table we want
    for i in range(rowlen):
        for check_area in findstr:
            # for nan case
            if type(df.iat[i,0]) is float:
                continue
            if check_area in df.iat[i,0].lower() and check_area!=area:
                end.append(i)
            if check_area in df.iat[i,0].lower() and check_area==area:
                begin.append(i)
    if end==[] or max(end)<max(begin):
        df=df.loc[max(begin):]
    else:
        df=df.loc[max(begin):max(end)-1]
    return df
            

###############################################################################
# Data before 2016

# Enter code here: type in lower case!
findstr=['boston','new york','pittsburgh','atlanta','cincinnati','indianapolis','chicago','des moines','dallas','topeka','san francisco','seattle']
findstr2= " adjusted minimum collateral securing advances"

# 2014
# open the pdf file
path=r"raw\report2014.pdf"
pdfobj = PyPDF2.PdfFileReader(path)
savelist=[]
for area in findstr:
    print(area)
    tempstr=area+findstr2
    # find which page the table locates
    pagenum=find_page(tempstr,pdfobj)
    # extract that page
    df=tabula.read_pdf(path, pages=pagenum,multiple_tables=True)
    # clean data
    for j in df:
        j=dataframe_clean(j,area)
        savelist.append(j)

# 2016
# open the pdf file
path=r"raw\report2016.pdf"
pdfobj = PyPDF2.PdfFileReader(path)
for area in findstr:
    print(area)
    tempstr=area+findstr2
    # find which page the table locates
    pagenum=find_page(tempstr,pdfobj)
    if pagenum==0:
        continue
    # extract that page
    df=tabula.read_pdf(path, pages=pagenum,multiple_tables=True,lattice=True)
    # clean data
    for data in df:
        data=twotableproblem(data,area,findstr)
        j=dataframe_clean(data,area)
        if type(j) is int:
            continue
        savelist.append(j)

# change index of dataframe
savelist=[t.rename(columns={'':'year'}) for t in savelist]
data2015=savelist[0]
for df in savelist:
    data2015 = pd.merge(data2015, df , how='outer',on=['year', 'Whole Loans', 'MBS/CMO', 'Securities', 'ORERC', 'CFI', 'area'])




###############################################################################
# Data after 2016





df=tabula.read_pdf(r"raw\report2014.pdf", pages=26,multiple_tables=True)
df=tabula.read_pdf(r"raw\report2014.pdf", pages=26,multiple_tables=True,lattice=True)

df0=df[0]
df1=df0.dropna(axis=0,how='all')
df1=df1.dropna(axis=1,how='all')

ds1=df1.iloc[2]
ds2=df1.iloc[3]
ds1=ds1.dropna(axis=0)
ds2=ds2.dropna(axis=0)
ds1=pd.concat([pd.Series([""]), ds1])
ds1=ds1.reset_index()
del ds1['index']

pd.concat([ds1, ds2], axis=0).reset_index()



###############################################################################
# Data before 2016
String2= "percent of the book value of eligible collateral"
























