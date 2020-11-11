import traceback
import managers.db_managers as db_managers
from managers.epg_manager import EpgManager
from helper import global_variables as gv
from helper import config as cfg

class MongoDbManager(db_managers.BaseDbManager):
    """
    A class that contains the different DbManagers for handling 
    the multiple collections required in MongoDB

    :param db_connection:  DbConnection object to handle MongoDb
    :type db_connection: managers.DbConnection object, optional
    """
    def __init__(self, db_connection):
        """Constructor
        """
        try:
            db_managers.BaseDbManager.__init__(self, db_connection)
            self.historic_manager = db_managers.HistoricDbManager(db_connection)
            self.config_manager = db_managers.ConfigDbManager(db_connection)
            self.journey_manager = db_managers.JourneyDbManager(db_connection, self.config_manager)
            self.epg_manager = EpgManager(db_connection, self.config_manager,
                                          self.journey_manager, cfg.guide_file)
            self.program_manager = db_managers.ProgramDbManager(db_connection, self.config_manager,
                                                                 self.journey_manager, self.epg_manager)
            self.alert_manager = db_managers.AlertDbManager(db_connection, self.config_manager,
                                                            self.journey_manager, self.program_manager)
            gv.logger.info("Alert DB manager set up")
            self.document_manager = db_managers.DocumentDbManager(db_connection, self.config_manager,
                                                                  self.journey_manager, self.program_manager,
                                                                  self.alert_manager)
            self.mos_calculator = db_managers.MosCalculator(self.config_manager)
            gv.logger.info("DB managers have been set up")
        except Exception as e:
            gv.logger.error(e)
            gv.logger.error(traceback.print_exc())