Assignment 4 – Nowcasting WebApp
==============================

https://share.streamlit.io/sairaghav1999/streamlit/main/app.py

Introduction
==============================
As part of the fourth assignment of DAMG 7245 we had to check if the entered longitude and latitude fall within a range of certain miles of the nearest longitude and latitude for a matching event id in our Nowcasting system.  The user can enter any latitude and longitude value as input and the API will search for the nearest event to that latitude and longitude and return the forecast.

Additionally, we have implemented a result caching system for SEVIR. There is an airflow workflow that runs hourly and caches the results for SEVIR nowcasting for 50 events from the Catalog.

The Streamlit frontend now enables the user to choose if they want a fresh nowcasting result or a cache and specify a number of minutes threshold for acceptable cache data. 

Finally, the API endpoints are now secured with JWT tokens and can be accessed only by authenticated users which are tracked in a BigQuery table and all the users have their associated tokens which are used to access the API endpoint to enable nowcasting.

Architecture Diagram
==============================
<img width="606" alt="image" src="https://user-images.githubusercontent.com/91291183/161310438-f01e7b86-429b-4b49-950c-1c0480e5ac06.png">


Nowcasting system
==============================
* [Nowcasts](https://en.wikipedia.org/wiki/Nowcasting_(meteorology)) are short-term forecast of weather variables typically measured by weather radar or satellite.   Nowcasts are different from traditional weather forecasts in that they are based (mostly) on statistical extrapolations of recent data, rather than full physics-based numerical weather prediction (NWP) models.  
* Nowcast are computed in a variety of ways, but one of the most common approaches is to apply optical flow techniques to a sequence of radar images.   These techniques track the motion of storm objects, which is then used to extrapolate the location of storms into the future.  

Heroku
==============================
* Heroku is a container-based cloud Platform as a Service (PaaS). Developers use Heroku to deploy, manage, and scale modern apps. Our platform is elegant, flexible, and easy to use, offering developers the simplest path to getting their apps to market. 
* While Heroku is an easy to host platform there is a limitation of slugsize of 500 MB. Each build cannot exist 500MB. Considering we are using Tensorflow which is a heavy library and storing a bunch of interim data, we faced an issue with Heroku that we were not able to bring our slug size below 800MB when the API is being hit.

GCP App Engine
==============================
* Due to the issues faced with Heroku, we have hosted our uvicorn based FastAPI code on GCP App Engine. The steps for doing the same are detailed in the codelabs document linked below.



Web Application - Location based Nowcasting
=============================================

In this Application, we are generating the predicted images using the nowcast model by calling an API. The application asks the user to input Latitude & Longitude along with the distance based on how far they want to see the storm prediction view the predicted images along with City, State, Date, and Time. The user can mention if they would like fresh data or cached data as well as the acceptable threshold time in minuts. After giving the input we can generate the images using the nowcast model by invoking the API.

Airflow
==============================
* Apache Airflow is an open-source tool programmatically author, schedule, and monitor workflows. When workflows are defined as code, they become more maintainable, versionable, testable, and collaborative. Use Airflow to author workflows as directed acyclic graphs (DAGs) of tasks. The Airflow scheduler executes your tasks on an array of workers while following the specified dependencies.

*Created a DAG with 3 workflows, Selecting the popular 50 locations and hits the nowcast model to generate the images with the help of API and stores them in a Google bucket. This DAG is scheduled to run every hour so that it can store the images in a cache memory. Monitoring of the DAG 

*A Virtual environment was created on Google Cloud Composer to run the Airflow and deployed the DAG in that to schedule task runs and monitor them.

JWT - Authorization
==============================

*JSON Web Token (JWT) is an open standard (RFC 7519) that defines a compact and self-contained way for securely transmitting information between parties as a JSON object. This information can be verified and trusted because it is digitally signed. JWTs can be signed using a secret (with the HMAC algorithm) or a public/private key pair using RSA or ECDSA.

*The process flow on the UI lets a user enter their username and password and the App authenticates them against the list of existing users in a BigQuery table, and if they are an approved user with an associated token, they are allowed to login and use the Nowcasting application.



Requirements
==============================
* Python 3.7
* Jupyter Notebooks
* Google Cloud Account
* Heroku
* Streamlit
* Postman
* GCPAppEngine



Technical Specifications Document
==============================
This is the link to open the CLAAT document:
https://codelabs-preview.appspot.com/?file_id=1pjhtG_WFLeXX97SfbXPW4mzLd9ZyuGAUlCMcyLwVapU#4

User Manual for the WebApp
==============================
https://codelabs-preview.appspot.com/?file_id=1v0RMU7Byf4xneCxlZU65J7qaP7Vrvj13a7cU1FBBCCk#4

Streamlit Repository
==============================
Since Streamlit webhosting requires the repository be a public one, we have created a separate public repository to store our Streamlit webapp code. Below is the link to the repository:

https://github.com/Sairaghav1999/streamlit

Project Organization
------------

```bash
├── LICENSE
├── Makefile
├── NLP_NamedEntityRecognition
│   ├── Dockerfile
│   ├── functions
│   │   └── get_model.py
│   ├── handler.py
│   ├── model
│   ├── requirements.txt
│   └── serverless.yml
├── NLP_Summarization
│   ├── Dockerfile
│   ├── functions
│   │   └── get_model.py
│   ├── handler.py
│   ├── model
│   ├── requirements.txt
│   └── serverless.yml
├── README.md
├── docs
│   ├── Makefile
│   ├── commands.rst
│   ├── conf.py
│   ├── getting-started.rst
│   ├── index.rst
│   └── make.bat
├── models
├── notebooks
├── references
├── reports
│   └── figures
├── requirements.txt
├── runtime.txt
├── setup.py
├── sevir.py
├── src
│   ├── __init__.py
│   ├── airflow_scripts
│   │   ├── HitModel.py
│   │   ├── SaveData.py
│   │   ├── SelectLatLong.py
│   │   └── Sevir_Caching.py
│   ├── data
│   ├── features
│   │   ├── __init__.py
│   │   └── build_features.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── predict_model.py
│   │   └── train_model.py
│   ├── scripts
│   │   ├── CATALOG.csv
│   │   ├── __pycache__
│   │   │   ├── app1.cpython-39.pyc
│   │   │   ├── app2.cpython-39.pyc
│   │   │   ├── auth_bearer.cpython-39.pyc
│   │   │   ├── auth_handler.cpython-39.pyc
│   │   │   ├── catalog_search.cpython-38.pyc
│   │   │   ├── catalog_search.cpython-39.pyc
│   │   │   ├── main.cpython-38.pyc
│   │   │   ├── main.cpython-39.pyc
│   │   │   ├── make_nowcast_dataset.cpython-38.pyc
│   │   │   ├── make_nowcast_dataset.cpython-39.pyc
│   │   │   ├── model.cpython-39.pyc
│   │   │   ├── multiapp.cpython-39.pyc
│   │   │   ├── nowcast.cpython-38.pyc
│   │   │   ├── nowcast.cpython-39.pyc
│   │   │   ├── nowcast_data.cpython-38.pyc
│   │   │   ├── nowcast_data.cpython-39.pyc
│   │   │   ├── nowcast_generator.cpython-38.pyc
│   │   │   ├── nowcast_generator.cpython-39.pyc
│   │   │   ├── utils.cpython-38.pyc
│   │   │   └── utils.cpython-39.pyc
│   │   ├── app.yaml
│   │   ├── auth
│   │   │   ├── __pycache__
│   │   │   │   ├── auth_bearer.cpython-38.pyc
│   │   │   │   ├── auth_bearer.cpython-39.pyc
│   │   │   │   ├── auth_handler.cpython-38.pyc
│   │   │   │   ├── auth_handler.cpython-39.pyc
│   │   │   │   ├── model.cpython-38.pyc
│   │   │   │   └── model.cpython-39.pyc
│   │   │   ├── auth_bearer.py
│   │   │   ├── auth_handler.py
│   │   │   └── model.py
│   │   ├── catalog_search.py
│   │   ├── cloud_storage_creds.json
│   │   ├── main.py
│   │   ├── make_nowcast_dataset.py
│   │   ├── nowcast.py
│   │   ├── nowcast_data.py
│   │   ├── nowcast_generator.py
│   │   ├── nowcast_reader.py
│   │   ├── requirements.txt
│   │   └── utils.py
│   └── visualization
│       ├── __init__.py
│       └── visualize.py
├── structure.json
├── test_environment.py
└── testcases.json


```

--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>

Contributions Statement
==============================
Below are the contributions by the team members to create this App:

1.Shika – 33.33%

* Python Logic – Search by distances function
* Python logic – Caching mechanism
* GCP hosting and debugging of API
* Airflow workflows 

2. Sai – 33.33%

* FastAPI
* JWT Authentication
* Postman testing
* Streamlit

3.Saketh – 33.33%

* Airflow setup
* Hosting airflow on GCP
* Documentation
* Testing

Attestation
==============================

We attest that we have not used any other Student’s work in our code and abide by the policies listed in the Northeastern University Student Handbook regarding plagiarism and intellectual property.


