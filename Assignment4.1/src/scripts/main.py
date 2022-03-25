from sre_constants import ANY
from numpy import double, empty
from geopy.geocoders import Nominatim
import geopy
from sqlite3 import Date
from fastapi import FastAPI, Depends,HTTPException
from pydantic import BaseModel
from typing import Any, Optional, List
from make_nowcast_dataset import generate_data
from nowcast import plot_results
from catalog_search import searchcataloglatlong,searchcatalogdatetime,searchgeocoordinates
import gcsfs
from io import BytesIO
from fastapi.responses import FileResponse
from nowcast_data import run
from google.cloud import storage
from PIL import Image

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
    return {"Initialize message": "Welcome to Nowcast API"}

@app.post('/input/')
async def create_sevir_view(sevir: Sevir):
    fs=gcsfs.GCSFileSystem(project="sevir-data-pipeline",token="cloud_storage_creds.json")
    sevir_data="gs://sevir-data/data/"
    #sevir_data='/Users/sairaghavendraviravalli/Desktop/Projects/neurips-2020-sevir-master-3/data/' 
    # Save sevir data with name as original file.
    sevir_catalog=fs.open("gs://sevir-data/data/CATALOG.csv",'rb')
    # filter catalog.csv to have only one event id.
    output_location='gs://sevir-data/output/'
    if((sevir.latitude!=None) & (sevir.longitude!=None) & (sevir.distancelimit!=None)):
        lat,long,event_id,filename,idx=searchgeocoordinates(sevir.latitude,sevir.longitude,sevir.distancelimit)
        if(lat!=None):
            filename,idx=searchcataloglatlong(lat,long)
        else:
            raise HTTPException(status_code=404, detail="No events found within specified distance limit. Try increasing limit or removing distancelimit attribute")

    else:
        if((sevir.date!='')&(sevir.time!='')&(sevir.city!='')&(sevir.state!='')):
            filename,idx=searchcatalogdatetime(sevir.date,sevir.time,sevir.city,sevir.state)
            print(filename)
            if(idx==None):
                raise HTTPException(status_code=406, detail="No event found matching the given Date,City,State and Time")

        else:
            raise HTTPException(status_code=405, detail="Date,City,State and Time cannot be empty")


    if(idx):
        result=run(sevir_data,filename[0],idx)

        fig=plot_results(result,output_location+'nowcast_testing.h5',idx)
        client = storage.Client.from_service_account_json('cloud_storage_creds.json')
        bucket = client.bucket('sevir-data')
        blob=bucket.get_blob('result_plot.png')
        img = Image.open(BytesIO(blob.download_as_bytes()))
        #return FileResponse(img)
        data={
            'detail':'SUCCESS'
        }
        #return 'IMAGE RETURNED'
        return data
    else:
        raise HTTPException(status_code=406, detail="No event found matching the criteria")

