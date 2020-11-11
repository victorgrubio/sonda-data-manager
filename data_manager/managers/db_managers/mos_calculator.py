'''
Created on 16 mar. 2020

@author: victor
'''
import json
from db_models import Program, Journey
from helper import global_variables as gv

INIT_MOS_CATEGORIES = {
    "mos_poor": 0,
    "mos_regular": 0,
    "mos_good": 0,
    "mos_excellent": 0
}


class MosCalculator:
    """This class represents the object in charge of performing the MOS (Mean Opinion Score) calculus with different db objects

    :param config_manager: MongoDb handler that manages config
    :type config_manager: data_manager.managers.db_managers.ConfigDbManager
    """
    
    def __init__(self, config_manager):
        """Constructor
        """
        self.config_manager = config_manager
        
    def calculate_average_mos_db_object(self, db_object=None, last_mos=0):
        """Obtains the average program MOS
        
        :param documents: List of measures from VideoQualityProbe
        :type documents: list[dict]
        :return: The average MOS
        :rtype: float
        """
        measures_n_1 = self.get_measures_n_1(db_object)
        measures_n = measures_n_1 + 1 
        if measures_n_1 > 0:
            # TOTALMOS_N = TOTALMOS_N-1 * ( n-1 / n) + MOS_N / n
            average_mos = db_object.mos *( (measures_n_1 ) / measures_n ) + last_mos/measures_n
        else:
            average_mos = last_mos
        return average_mos
    
    def get_measures_n_1(self, db_object):
        measures_n_1 = 0
        if type(db_object) == Program:
            measures_n_1 = len(db_object.data)
        elif type(db_object) == Journey:
            measures_n_1 = db_object.measures
        return measures_n_1
    
    def calculate_mos_categories_db_object(self, db_object=None, last_mos=0):
        """Obtains the MOS percentages for each category 
        from a list of measures
        
        :param documents: List of measures from VideoQualityProbe
        :type documents: list[dict]
        :return: The percentages of each MOS category grouped as a dict
        :rtype: dict
        """
        last_mos_category = self.get_category_mos_value(last_mos)
        measures_n_1 = self.get_measures_n_1(db_object)
        measures_n = measures_n_1 + 1
        if measures_n_1 > 0:
            init_mos_category_percentages = dict(db_object.mos_percentages.to_mongo())
            mos_samples_dict = {}
            final_mos_dict = {}
            for category in init_mos_category_percentages.keys():
                # From percentages to samples
                mos_samples_dict[category] = round( init_mos_category_percentages[category]*(measures_n_1/100)) 
            # Add new samples
            mos_samples_dict[last_mos_category] += 1
            # From samples to percentages
            for category in init_mos_category_percentages.keys():
                # From percentages to samples
                final_mos_dict[category] = min(100.0, (mos_samples_dict[category]*100)/measures_n )
        else:
            final_mos_dict = INIT_MOS_CATEGORIES.copy()
            final_mos_dict[last_mos_category] = 100.0
        return final_mos_dict
    
    def calculate_mos_categories_videoanalysis_queryset(self, videoanalysis_queryset):
        """ """
        length_videoanalysis_queryset = videoanalysis_queryset.count()
        # Mos percentages = mos.count if mos value in range / length of total mos documents
        mos_percentage_dict = {
            
            "mos_poor": videoanalysis_queryset.filter(
                    mosAnalysis__mos__lt=self.config_manager.config.mos_regular
                ).count() / length_videoanalysis_queryset,

            "mos_regular": videoanalysis_queryset.filter(
                    mosAnalysis__mos__lt=self.config_manager.config.mos_good,
                    mosAnalysis__mos__gte=self.config_manager.config.mos_regular
                ).count() / length_videoanalysis_queryset,
            
            "mos_good": videoanalysis_queryset.filter(
                    mosAnalysis__mos__lt=self.config_manager.config.mos_excellent,
                    mosAnalysis__mos__gte=self.config_manager.config.mos_good
                ).count() / length_videoanalysis_queryset,
            
            "mos_excellent": videoanalysis_queryset.filter(
                    mosAnalysis__mos__gte=self.config_manager.config.mos_excellent
                ).count() / length_videoanalysis_queryset
        }
        return mos_percentage_dict
    

    def get_category_mos_value(self, mos_value):
        category = ""
        config = self.config_manager.config
        if mos_value < config.mos_regular:
            category = "mos_poor"
        elif mos_value >= config.mos_regular and mos_value < config.mos_good:
            category = "mos_regular"
        elif mos_value >= config.mos_good and mos_value < config.mos_excellent:
            category = "mos_good"
        elif mos_value >= config.mos_excellent:
            category = "mos_excellent"
        return category
    
    def get_initial_mos_categories(self, videoanalysis_document):
        category = self.get_category_mos_value(videoanalysis_document.mosAnalysis.mos)
        mos_percentage_dict = INIT_MOS_CATEGORIES.copy()
        mos_percentage_dict[category] = 100
        return  mos_percentage_dict
    