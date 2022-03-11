from sre_constants import ANY
from numpy import double, empty
from geopy.geocoders import Nominatim
import geopy
#import nowcast
from sqlite3 import Date
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import Any, Optional, List
from make_nowcast_dataset import generate_data
from nowcast import plot_results
#import nowcast_generator as ng
from catalog_search import searchcataloglatlong,searchcatalogdatetime

app = FastAPI()

class Sevir(BaseModel):
    latitude: Optional[float] = None
    longitude:Optional[float] = None
    date: str
    time: str
    city: str
    state: str
   
@app.get("/")
def read_root():
    return {"message": "Welcome from the nowcast API"}

@app.post('/input/')
async def create_sevir_view(sevir: Sevir):
    sevir_data='/Users/sairaghavendraviravalli/Desktop/Projects/neurips-2020-sevir-master-3/data/' 
    # Save sevir data with name as original file.
    sevir_catalog='/Users/sairaghavendraviravalli/Desktop/Projects/neurips-2020-sevir-master-3/data/CATALOG.csv'
    # filter catalog.csv to have only one event id.
    output_location='/Users/sairaghavendraviravalli/Desktop/Projects/neurips-2020-sevir-master-3/data/interim/'
    if((sevir.latitude!=None) & (sevir.longitude!=None)):
        filename,idx=searchcataloglatlong(sevir.latitude,sevir.longitude)
    else:
        if((sevir.date!='')&(sevir.time!='')&(sevir.city!='')&(sevir.state!='')):
            filename,idx=searchcatalogdatetime(sevir.date,sevir.time,sevir.city,sevir.state)
        else:
            return {
              "status" : "FAIL",
              "reason": "date,city,state,time cannot be empty",
              }

    if(idx):
        generate_data(sevir_data,sevir_catalog,output_location)
    #Pass file index instead of random number
        plot_results(output_location+'nowcast_testing.h5',idx)
        return {
              "status" : "SUCCESS",
              "data" : sevir,
               "output image location": "/Users/sairaghavendraviravalli/Desktop/Projects/neurips-2020-sevir-master-3/src/data/sample.png"
              }
    else:
         return {
              "status" : "FAIL",
              "reason": "matching event not found",
              }

@app.post('/create/')
async def make_nowcast_dataset(sevir: Sevir):
    return {
        "status" : "SUCCESS",
        "data" : sevir,
    }
