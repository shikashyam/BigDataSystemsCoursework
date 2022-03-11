#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 10 14:24:15 2022

@author: shshyam
"""

from importlib.resources import path
import h5py
import boto3
from botocore.handlers import disable_signing
from os import walk
import os
import pandas as pd

def searchcataloglatlong(lat, long):
    filename=None
    #Search catalog for respective Event ID
    event_id,date=get_event_id(lat,long)
    print(event_id)
    if(event_id!='None'):
        filename,fileindex,catalog=get_filename_index(event_id)
        #event_id=835047
        #Create H5 with only that event        
        print(filename,fileindex)
        catalog.to_csv('/Users/sairaghavendraviravalli/Desktop/Projects/neurips-2020-sevir-master-3/src/data/CATALOG.csv')
        #rpath=download_hf(filename)
        #newfilepath=One_Sample_HF('/Users/sairaghavendraviravalli/Desktop/Projects/neurips-2020-sevir-master-3/src/data/', fileindex, filename)
        return filename,fileindex[0]
    else:
        return None,None
    
    #Filter catalog to include only that event
    
def searchcatalogdatetime(date,time,city,state):
    stormdetails = pd.read_csv('/Users/sairaghavendraviravalli/Desktop/Projects/neurips-2020-sevir-master-3/src/data/StormEvents_details-ftp_v1.0_d2019_c20220214.csv')
    date=date.replace('-','')
    yrmonth=date[0:6]
    day=date[6:8]
    time=time.replace(':','')
    event_id = stormdetails[(stormdetails['BEGIN_YEARMONTH'] == int(yrmonth)) & (stormdetails['BEGIN_DAY']==int(day))& (stormdetails['BEGIN_TIME']==int(time)) & (stormdetails['CZ_NAME']==city)& (stormdetails['STATE']==state)]['EVENT_ID'].unique()[0]  
    print(event_id)
    if(event_id):
        filename,fileindex,catalog=get_filename_index(event_id)
        #event_id=835047
        #Create H5 with only that event        
        print(filename,fileindex)
        catalog.to_csv('/Users/sairaghavendraviravalli/Desktop/Projects/neurips-2020-sevir-master-3/src/data/CATALOG.csv')
        #rpath=download_hf(filename)
        #newfilepath=One_Sample_HF('/Users/sairaghavendraviravalli/Desktop/Projects/neurips-2020-sevir-master-3/src/data/', fileindex, filename)
        return filename,fileindex[0]
    else:
        return None,None
def get_event_id(lat,lon):
    df1 = pd.read_csv("https://raw.githubusercontent.com/MIT-AI-Accelerator/eie-sevir/master/CATALOG.csv")
    df1= df1.round({'llcrnrlat':6,'llcrnrlon':6})
    
    try:
      date = df1[(df1['llcrnrlon']== lon) & ( df1['llcrnrlat']==lat)]['time_utc'].unique()[0]
      event_id = df1[(df1['llcrnrlon']== lon) & ( df1['llcrnrlat']==lat)]['event_id'].unique()[0]
    
    except:
      print('Lat and long not found')
      date= 'None'
      event_id = 'None'
    return event_id,date

def get_filename_index(event_id):
    catlog = pd.read_csv("https://raw.githubusercontent.com/MIT-AI-Accelerator/eie-sevir/master/CATALOG.csv")
    filtered = pd.DataFrame()
    filtered = pd.concat([filtered,catlog[(catlog["event_id"] == int(event_id))]])
    allfilenames = filtered['file_name'].unique()
    
    vilpd=catlog[(catlog["event_id"] == int(event_id)) & (catlog['img_type']=='vil')]
    filename=vilpd['file_name'].unique()
    fileindex = vilpd['file_index'].to_list()
    #newcatalog=filtered[filtered['img_type']=='vil']
    #print(newcatalog.head())
    catalog = pd.read_csv("https://raw.githubusercontent.com/MIT-AI-Accelerator/eie-sevir/master/CATALOG.csv")
    newcatalog=catalog[(catalog['file_name'].isin(allfilenames))]
    print(newcatalog.shape)
    print(newcatalog.head())
    print("We have got the locations, Lets Download the files")    
    return filename, fileindex,newcatalog
    
def download_hf(filename):
    resource = boto3.resource('s3')
    resource.meta.client.meta.events.register('choose-signer.s3.*', disable_signing)
    bucket=resource.Bucket('sevir')
    
    for i in range(len(filename)):
        filename1 = "data/" + filename[i]
        print("Downloading",filename1)    
       # os.mkdir('/Users/sairaghavendraviravalli/Desktop/Projects/neurips-2020-sevir-master-3/data/newh5')
        os.mkdir('/Users/sairaghavendraviravalli/Desktop/Projects/neurips-2020-sevir-master-3/data/vil/'+filename[i].split('/')[1])
        bucket.download_file(filename1 , '/Users/sairaghavendraviravalli/Desktop/Projects/neurips-2020-sevir-master-3/data/'+filename[i]) 
        #path needs to be changed
        return '/Users/sairaghavendraviravalli/Desktop/Projects/neurips-2020-sevir-master-3/data/'+filename[i]
    
def One_Sample_HF(directory,fileindex,filenames):
    #filenames = next(walk(directory), (None, None, []))[2]  # [] if no file
    newfilepath=''
    for i in range(len(filenames)):
        print(directory+filenames[i])
        # if filenames[i] == '.DS_Store':
        #     continue
        with h5py.File(directory+filenames[i],'r') as hf:
            print(directory+"/"+filenames[i])
            image_type = filenames[i].split('_')[1]
            
            if image_type == "VIL":
                VIL = hf['vil'][int(fileindex[0])]
                os.mkdir('/Users/sairaghavendraviravalli/Desktop/Projects/neurips-2020-sevir-master-3/data/newh5')
                os.mkdir('/Users/sairaghavendraviravalli/Desktop/Projects/neurips-2020-sevir-master-3/data/newh5/vil')
                os.mkdir('/Users/sairaghavendraviravalli/Desktop/Projects/neurips-2020-sevir-master-3/data/newh5/vil/'+filenames[i].split('/')[1])
                hf2 = h5py.File('/Users/sairaghavendraviravalli/Desktop/Projects/neurips-2020-sevir-master-3/data/newh5/'+filenames[i], 'w')
                hf2.create_dataset('vil', data=VIL)
                newfilepath='/Users/sairaghavendraviravalli/Desktop/Projects/neurips-2020-sevir-master-3/data/vil/'+filenames[i].split('/')[1]+filenames[i].split('/')[2]       
                
    return newfilepath 

    
