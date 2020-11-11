import pymongo
from mongoengine import connect
import traceback

from helper import global_variables as gv
from helper import config as cfg

class DbConnection:
    """This class represent a MongoDB connection handler.   

    :param db: MongoDB database, defaults to None
    :type db: pymongo.database.Database, optional
    :param db_client: Pymongo client, defaults to None
    :type db_client: pymongo.MongoClient, optional
    :param dblist: List of databases in database, defaults to None
    :type dblist: List, optional
    :param collection: Collection of the handler, defaults to None
    :type collection: pymongo.collection.Collection, optional
    :param collection_name: Name of collection used, defaults to None
    :type collection_name: str, optional
    """
    
    def __init__(self, db=None, db_client=None, dblist=None,
                  collection=None, collection_name=None):
        """Constructor
        
        """
        self.db_client = db_client
        self.db = db
        self.dblist = dblist
        self.collection = collection
        self.collection_name = collection_name
        self.set_up_db()
    
    def set_up_db(self):
        """Starts db connection
        """
        try:
            gv.logger.info("Setting up DB connection... ")
            # Establish connection
            if self.db_client is None:
                self.establish_client_connection()
                # Create new collection
                if self.collection_name is None:
                    self.collection_name = cfg.collection_name
                self.create_new_collection_instance(collection_name=self.collection_name)
                gv.logger.info("DB connection has been set up properly")
            else:
                gv.logger.info("DB connection already available")
        except Exception as e:
            gv.logger.error(e)
            gv.logger.error(traceback.print_exc())
            
    
    def establish_client_connection(self):
        """Connects the client with the MongoDB database
        """
        try:
            self.db_client = pymongo.MongoClient(cfg.db_host, int(cfg.db_port))
            connect(cfg.db_name, host=cfg.host, port=int(cfg.db_port))
            self.db = self.db_client[cfg.db_name]
            if not self.check_database_exists():
                gv.logger.info("The new db created!")
        except Exception as e:
            gv.logger.error(e)
            gv.logger.error(traceback.print_exc())


    def create_new_collection_instance(self, collection_name):
        """Creates a new instance for the specific collection
        
        :param collection_name: Name of new collection
        :type collection_name: str
        """
        try:
            # If no exists
            if self.db is not None:
                self.collection = self.db[collection_name]
            else:
                gv.logger.warning("The connection to the db is not established!")
        except Exception as e:
            gv.logger.error(e)
            gv.logger.error(traceback.print_exc())  


    def check_db(self):
        """Checks if dbManager has started. If not, initialize dbManager.
        """
        try:
            if self.db_client is None:
                gv.logger.info("DB CLIENT IS NONE")
                self.establish_client_connection()
        except Exception as e:
            gv.logger.error(e)
            gv.logger.error(traceback.print_exc())

    def check_database_exists(self):
        """Checks if configuration database is in MongoDB database
        
        :return: True if config database is in MongoDB, else False
        :rtype: boolean
        """
        try:
            response = True
            dblist = self.db_client.list_database_names()
            if cfg.db_name not in dblist:
                response = False
        except Exception as e:
            gv.logger.error(e)
            gv.logger.error(traceback.print_exc())
            response = None
        return response