from sre_constants import ANY
from numpy import double, empty
from geopy.geocoders import Nominatim
import geopy
from sqlite3 import Date
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import Any, Optional, List
from make_nowcast_dataset import generate_data
from nowcast import plot_results
from catalog_search import searchcataloglatlong,searchcatalogdatetime,searchgeocoordinates
import gcsfs
from io import BytesIO
from fastapi.responses import FileResponse
from nowcast_data import run

app = FastAPI()

class Sevir(BaseModel):
    latitude: Optional[float] = None
    longitude:Optional[float] = None
    distancelimit: Optional[float] = None
    date: str
    time: str
    city: str
    state: str
   
@app.get("/")
def read_root():
    return {"message": "Welcome from the nowcast API"}

@app.post('/input/')
async def create_sevir_view(sevir: Sevir):
    fs=gcsfs.GCSFileSystem(project="sevir-data-pipeline",token="cloud_storage_creds.json")
    sevir_data="gs://sevir-data/data/"
    #sevir_data='/Users/sairaghavendraviravalli/Desktop/Projects/neurips-2020-sevir-master-3/data/' 
    # Save sevir data with name as original file.
    sevir_catalog=fs.open("gs://sevir-data/data/CATALOG.csv",'rb')
    # filter catalog.csv to have only one event id.
    output_location='/Users/sairaghavendraviravalli/Desktop/Projects/neurips-2020-sevir-master-3/data/interim/'
    if((sevir.latitude!=None) & (sevir.longitude!=None) & (sevir.distancelimit!=None)):
        lat,long=searchgeocoordinates(sevir.latitude,sevir.longitude,sevir.distancelimit)
        if(lat!=None):
            filename,idx=searchcataloglatlong(lat,long)
        else:
            return {
              "status" : "FAIL",
              "reason": "No events found within specified distance limit",
              }
    else:
        if((sevir.date!='')&(sevir.time!='')&(sevir.city!='')&(sevir.state!='')):
            filename,idx=searchcatalogdatetime(sevir.date,sevir.time,sevir.city,sevir.state)
            print(filename)
            #print(filename.type)
        else:
            return {
              "status" : "FAIL",
              "reason": "date,city,state,time cannot be empty",
              }

    if(idx):
        result=run(sevir_data,filename[0],idx)
        #generate_data(sevir_data,sevir_catalog,output_location)
         #Pass file index instead of random number
        fig=plot_results(result,output_location+'nowcast_testing.h5',idx)
        #return {
               # "status" : "SUCCESS",
               # "data" : sevir,
                #"fig": "fig"
              #}
        return FileResponse(fig)
    else:
         return {
              "status" : "FAIL",
              "reason": "matching event not found",
              }
