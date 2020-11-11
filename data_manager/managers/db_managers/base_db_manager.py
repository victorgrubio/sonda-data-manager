'''
Created on 16 mar. 2020

@author: victor
'''
    
class BaseDbManager:
    """DbManager base class to handle db connections

    :param db_connection:  DbConnection object to handle MongoDb
    :type db_connection: managers.DbConnection object, optional
    """
    
    def __init__(self, db_connection):
        """Constructor
        
        """
        self.db_connection = db_connection 
    
    def set_up_db(self):
        """Starts the db connection
        """
        self.db_connection.set_up_db()

    def create_new_collection_instance(self, collection_name):
        """Creates a new collection with a given name
        
        :param collection_name: Name of collection to create
        :type collection_name: str
        """
        self.db_connection.create_new_collection_instance(collection_name) 

    def check_db(self):
        """Checks db status
        """
        self.db_connection.check_db()

    def check_database_exists(self):
        """Checks if db exists and returns the boolean result
        
        :return: True if db exists, False if it does not.
        :rtype: boolean
        """
        return self.db_connection.check_database_exists()