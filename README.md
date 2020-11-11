# Data-Manager

An intermediate module which connects both Frame-Processing (VideoQualityProbe) component and Artificial Intelligence component (VideoQualityAnalysis) for Video Quality Assesment.

**Table of contents**

- [Requirements](#requirements)
- [Scripts](#scripts)
- [Code Structure](#code-structure)


## Requirements

To install the python dependencies, a requirements.txt file has been provided and the following command is needed to install such dependecies:
```bash
pip3 install -r requirements.txt
```
## Scripts
```bash
./build_docs.sh  # Creates the documentation from the code comments
./build_swagger.sh # Build Swagger documentation for the API
```

## Code structure

The code is structured in the following groups:

- [Db Models](#db-models)
- [Helper](#helper)
- [Managers](#managers)
    - [Db Managers](#db-managers)
- [Routers](#routers)
- [Schemas](#schemas)
- [Static](#static)
- [Views](#views)

### Db Models
Models for MongoDB collections. The fields of each model are self explanatory. There is one model per collection in the Db. This is imported in the code to handle objects instead of dictionaries for managing DB issues.
### Helper
This has been modified with the structure inherited by David's code. I have added some config values inside the config script. There has been also a modification in the custom log to use environment variables.
### Views
In this folder, all the blueprints of Flask are saved [(more info about blueprints)](https://flask.palletsprojects.com/en/1.1.x/tutorial/views/). As I have explained in a video tutorial before, these blueprints contain the requests for a specific group: probe, journeys, db ...

These would be the api endpoints stored in the app.py but splited in different files for the sake of organization.
Each of these views contain a call to a [routers](#routers) function that will manage the response.

### Routers
As the structure of the Data Manager started to get complex, I built intermediate functions to handle each of the blueprints defined above. These routers have an specific DB Manager (described in the next section) and their objective is to do the logic for each endpoint together with the Db interaction. To do so, each of the routers have, in its constructor, a DB Manager. I think the code in api_manager.py illustrates it better than my words.

Therefore, the routers just do a brief handling of the request and call the function of the correspondent DB Manager. 

### Managers
Here are the main backend elements. This folder contains the APIManager, which is the global element declared in the helper file that handles everything globally. There is a list of different managers, each one with an specific functionality:

- DbConnection: Is the singleton object to have a unique client connection to the DB. Inherited by all the Db Managers.
- Epg Manager: In charge of handling operations related to EPGs.
- File Manager: In charge of handling operation relateds to files.
- Memory Emergency Manager: Handles the behaviour of the API when memory issues appear (killing and restarting the probe). 
- Probe healthchecker: Thread to check if the API and the probe are working properly via the status,
- Thread Playlist: This object handles the management of playlists using threads.
- VideoQualityPred Manager: This, as explained before in the video, just handles the requests with the AI module from David.

The API Manager have the dbConnection declared for all elements. Then we have the main db manager. This db manager groups all the db manager for the specific collection. This way, they can be easily accessed by the different routers in the declaration. 

Then, we have all the different routers declared inside this API Manager. This is for accessing the from the global variable at the views.

#### Db Managers
As mentioned in previous sections, these managers handle most of the logic as the interaction with the mongodb is fundamental for the correct performance of the backend. There is one manager for each collection. I think the best way to undestand them is to read the code as they should be deeply documented.

### Schemas
These are Marshmallow schemas [(docs)](https://marshmallow.readthedocs.io/en/stable/install.html) to create the swagger documentation. Using the marshmallow-mongoengine library [(docs)](https://marshmallow-mongoengine.readthedocs.io/en/latest/apireference.html), we create a model from the DB Models defined above. They fulfill a similar function, to be managed as object.

The only functionality of this is to create the objects for the [APISpec](https://apispec.readthedocs.io/en/latest/) parsing that builds the swagger docs from code documentation.
### Static
This just stores the swagger.json file and the folders where all the static resources (CSVs, JSONs, imgs, etc) produced/need by the API.
