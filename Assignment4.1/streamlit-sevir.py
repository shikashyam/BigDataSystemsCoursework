import requests
import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image

st.title('Location based Nowcasting')

st.header('Please Enter the Latitude and Longitude')

form = st.form(key="Form1")
lat, long, distance = st.columns(3)
with lat:
    LatitudeInput = form.text_input('Latitude:')
with long:
    LongitudeInput = form.text_input('Longitude:')
with distance:
    SliderInput = form.select_slider('Select the Distance (miles)', options=[0, 200, 400, 600, 800, 1000])
data ={
    'latitude':LatitudeInput,
    'longitude':LongitudeInput,
    'distancelimit':SliderInput,
    "date":0,
    "time": 0,
    "city": 0,
    "state": ""
}

#submitButton = form.form_submit_button(label='Predict')


st.header('Please enter the Location and Timestamp')

form2 = st.form(key="Form2")
city, state, date, time = st.columns(4)
with city:
    CityInput = form2.text_input('City:')
with state:
    # StateInput = form2.text_input('State:')
    option = form2.selectbox(
        'State:',
        ("Alaska", "Alabama", "Arkansas", "American Samoa", "Arizona", "California", "Colorado", "Connecticut", "District of Columbia", "Delaware", "Florida", "Georgia", "Guam", "Hawaii", "Iowa", "Idaho", "Illinois", "Indiana", "Kansas", "Kentucky", "Louisiana", "Massachusetts", "Maryland", "Maine", "Michigan", "Minnesota", "Missouri", "Mississippi", "Montana", "North Carolina", "North Dakota", "Nebraska", "New Hampshire", "New Jersey", "New Mexico", "Nevada", "New York", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Puerto Rico", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Virginia", "Virgin Islands", "Vermont", "Washington", "Wisconsin", "West Virginia", "Wyoming"
        ))
with date:
    DateInput = form2.text_input('Date input')
with time:
    TimeInput = form2.text_input('Time entry')
data={
     'latitude':0,
    'longitude':0,
    'distancelimit':0,
    "date":date,
    "time": time,
    "city": city,
    "state": state
}

if st.button("predict"):
    response=requests.post("http://127.0.0.1:8000/input/", json=data)
    image = Image.open(response)
    st.success("Forecasting for the next hour")

#submitButton1 = form2.form_submit_button(label='Predict')

# st.text_input('City:')
# st.text_input('State:')
# st.date_input('Date input')
# st.time_input('Time entry')
# if st.button('Predict'):
#     res = requests.post(
#         headers={"Connection": "close"})

# with open("flower.png", "rb") as file:
#     btn = st.download_button(
#         label="Download image",
#         data=file,
#         file_name="flower.png",
#         mime="image/png"
#     )
# , data, file_name=None, mime=None, key=None, help=None, on_click=None, args=None, kwargs=None , disabled=False)

st.write('You selected:', option)

df = pd.DataFrame(
    np.random.randn(1000, 2) / [30, 30] + [39.76, -97.2],
    columns=['lat', 'lon'])

st.map(df)

#htp7 = "https://upload.wikimedia.org/wikipedia/en/thumb/7/7a/Manchester_United_FC_crest.svg/1200px-Manchester_United_FC_crest.svg.png"
#image = Image.open(htp7)
#st.image(htp7, caption='Sunrise over the mountains', width=800)




# image = Image.open('sunrise.jpg')
# st.image(image, caption='Sunrise by the mountains')


# res = requests.post(
#                 f"https://us-central1-hardy-portal-318606.cloudfunctions.net/get_nowcast?modelName={model}&pklname={pklRes}&idx={idx}",
#                 headers={"Connection": "close"})

# [theme]
#
# primaryColor="#6eb52f"
# backgroundColor="#f0f0f5"
# secondaryBackgroundColor="#e0e0ef"
# textColor="#262730"
# font="sans serif"