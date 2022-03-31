from sre_constants import ANY
from numpy import double, empty
from geopy.geocoders import Nominatim
import geopy
from sqlite3 import Date
from fastapi import FastAPI, Depends,HTTPException,Body
from pydantic import BaseModel
from typing import Any, Optional, List
from make_nowcast_dataset import generate_data
from nowcast import plot_results
from catalog_search import searchcataloglatlong,searchcatalogdatetime,searchgeocoordinates,searchincache
import gcsfs
from io import BytesIO
from fastapi.responses import FileResponse
from nowcast_data import run
from google.cloud import storage
from PIL import Image
from auth.model import  UserSchema, UserLoginSchema
from auth.auth_bearer import JWTBearer
from auth.auth_handler import signJWT
from datetime import datetime

import csv

app = FastAPI()

class Sevir(BaseModel):
    latitude: Optional[float] = None
    longitude:Optional[float] = None
    distancelimit: Optional[float] = None
    date: str
    time: str
    city: str
    state: str
    refresh_flag: str
    threshold_time: str
    SearchBy: str

users = []
   
@app.get("/")
def read_root():
    return {"Initialize message": "Welcome to Nowcast API"}

def check_user(data: UserLoginSchema):
    for user in users:
        if user.email == data.email and user.password == data.password:
            return True
    return False



def search_by_loc(date,time,city,state):
    fs=gcsfs.GCSFileSystem(project="sevir-project-bdia",token="cloud_storage_creds.json")
    sevir_data="gs://sevir-data-2/data/"
    sevir_catalog=fs.open("gs://sevir-data-2/data/CATALOG.csv",'rb')
    output_location='gs://sevir-data-2/output/'
    print('In search by Location function')
    if((date!='')&(time!='')&(city!='')&(state!='')):
        filename,event_id,idx=searchcatalogdatetime(date,time,city,state)
        print(filename)
        if(idx is None):
            raise HTTPException(status_code=406, detail="No event found matching the given Date,City,State and Time")
        else:
            result=run(sevir_data,filename[0],idx)
            fig=plot_results(result,output_location+'nowcast_testing.h5',idx,event_id)
        
            data={
            'result':'SUCCESS',
            'detail':fig
            }
        
            return data
    else:
        raise HTTPException(status_code=405, detail="Date,City,State and Time cannot be empty")


def search_by_lat_long(latitude,longitude,distancelimit):
    fs=gcsfs.GCSFileSystem(project="sevir-project-bdia",token="cloud_storage_creds.json")
    sevir_data="gs://sevir-data-2/data/"
    sevir_catalog=fs.open("gs://sevir-data-2/data/CATALOG.csv",'rb')
    output_location='gs://sevir-data-2/output/'
    print('In Search by latlong function')
    if((latitude!=None) & (longitude!=None) & (distancelimit!=None)):
        lat,long,event_id,filename,idx=searchgeocoordinates(latitude,longitude,distancelimit)
        if(lat is None):
            raise HTTPException(status_code=404, detail="No events found within specified distance limit. Try increasing limit.")
        else:
            print('Got stuff - ',filename)
            result=run(sevir_data,filename,idx)
            fig=plot_results(result,output_location+'nowcast_testing.h5',idx,event_id)
            client = storage.Client.from_service_account_json('cloud_storage_creds.json')
            # bucket = client.bucket('sevir-data-2')
            # blob=bucket.get_blob('result_plot.png')
            # img = Image.open(BytesIO(blob.download_as_bytes()))        
            data={
            'result':'SUCCESS',
            'detail':fig
            }
        
            return data

    else:
        raise HTTPException(status_code=407, detail="Please pass valid values for Lat,Long and DistanceLimit")


@app.post('/input/',dependencies=[Depends(JWTBearer())], tags=["posts"])
async def create_sevir_view(sevir: Sevir):

    SearchBy=sevir.SearchBy
    refresh_flag=sevir.refresh_flag
    threshold_time=sevir.threshold_time
    #Case 1: Search by Location (No Cache logic)
    if ((SearchBy == 'Loc')):
        return search_by_loc(sevir.date,sevir.time,sevir.city,sevir.state)
    #Case 2 : Search by latlong and refresh is Y - Hit model
    elif((SearchBy == 'LatLong') &(refresh_flag=='Y')):
        return search_by_lat_long(sevir.latitude,sevir.longitude,sevir.distancelimit)
    #Case 3 : Search by Latlong and refresh is N - Check Cache first for matching point.
    elif((SearchBy=='LatLong')&(refresh_flag=='N')):
        FoundInCache,timestamp,fileloc = searchincache(sevir.latitude,sevir.longitude,sevir.distancelimit)
        #Found in Cache, check for threshold
        if(FoundInCache=='Y'):
            now  = datetime.now()     
            newtimestamp=datetime.strptime(timestamp,'%Y-%m-%d %H:%M:%S')                    
            duration = now - newtimestamp                        
            duration_min = duration.total_seconds()/60
            #If threshold is okay, return image
            if(duration_min<=int(sevir.threshold_time)):
                resultval={ 'result':'SUCCESS-FOUND IN CACHE',
                'detail':fileloc}
                return resultval
            #if Above threshold - hit model
            else:
                return search_by_lat_long(sevir.latitude,sevir.longitude,sevir.distancelimit)
        #Not found in cache - so hit model
        else:
            return search_by_lat_long(sevir.latitude,sevir.longitude,sevir.distancelimit)
    #Fell through all input possibilities
    else:
            raise HTTPException(status_code=408, detail="Full fallthrough")




@app.post('/input/airflow/')
async def create_sevir_view(sevir: Sevir):

    SearchBy=sevir.SearchBy
    refresh_flag=sevir.refresh_flag
    threshold_time=sevir.threshold_time
    #Case 1: Search by Location (No Cache logic)
    if ((SearchBy == 'Loc')):
        return search_by_loc(sevir.date,sevir.time,sevir.city,sevir.state)
    #Case 2 : Search by latlong and refresh is Y - Hit model
    elif((SearchBy == 'LatLong') &(refresh_flag=='Y')):
        return search_by_lat_long(sevir.latitude,sevir.longitude,sevir.distancelimit)
    #Case 3 : Search by Latlong and refresh is N - Check Cache first for matching point.
    elif((SearchBy=='LatLong')&(refresh_flag=='N')):
        FoundInCache,timestamp,fileloc = searchincache(sevir.latitude,sevir.longitude,sevir.distancelimit)
        #Found in Cache, check for threshold
        if(FoundInCache=='Y'):
            now  = datetime.now()     
            newtimestamp=datetime.strptime(timestamp,'%Y-%m-%d %H:%M:%S')                    
            duration = now - newtimestamp                        
            duration_min = duration.total_seconds()/60
            #If threshold is okay, return image
            if(duration_min<=int(sevir.threshold_time)):
                resultval={ 'result':'SUCCESS-FOUND IN CACHE',
                'detail':fileloc}
                return resultval
            #if Above threshold - hit model
            else:
                return search_by_lat_long(sevir.latitude,sevir.longitude,sevir.distancelimit)
        #Not found in cache - so hit model
        else:
            return search_by_lat_long(sevir.latitude,sevir.longitude,sevir.distancelimit)
    #Fell through all input possibilities
    else:
            raise HTTPException(status_code=408, detail="Full fallthrough")





@app.post("/user/signup", tags=["user"])
async def create_user(user: UserSchema = Body(...)):
    # fs=gcsfs.GCSFileSystem(project="sevir-project-bdia",token="cloud_storage_creds.json")
    users.append(user) # replace with db call, making sure to hash the password first
    # fs.open(f'gs://sevir-data-2/user_details.csv','rb')
    #print(list(user))   
    user1=dict(user)
    #print(dict(user))
    #print(user1.values())
    #print(signJWT(user.email))
    p=signJWT(user.email)
    #d={'token':p}
    user1.update(p)
    #user1.append(p)
    #print(list(user1.values()))
    c=list(user1.values())
    #print(c)
    print(user1)
    #user.append(p)
    fields=['fullname','email','password','access_token']
    #df
    # with open('user_details.csv', 'w') as f: 

    #     Dict_obj=csv.DictWriter(f, fieldnames=fields)
    #     Dict_obj.writerow(user1)
    #     f.close()
    #     # write = csv.writer(f) 
    #     # write.writerow(fields) 
    #     # #append_list_as_row('user_details.csv', c)
    #     # write.writerows(c) 
    # client = storage.Client.from_service_account_json('cloud_storage_creds.json')
    # bucket=client.bucket('sevir-data-2')
    # blob=bucket.blob('user_details.csv')
    # blob.upload_from_filename('user_details.csv')
    #print(p)
    return p



@app.post("/user/login", tags=["user"])
async def user_login(user: UserLoginSchema = Body(...)):
    if check_user(user):
        return signJWT(user.email)
    return {
        "error": "Wrong login details!"
    }

