import requests
import json
from pprint import pprint
import numpy as np
import os
import pandas as pd
# import wget
from .datasets import CKANDataset, GQLDataset


class Collection:
    def __init__(self, source, schema, rooturl):
        self._datasets = []
        self._source = source
        self.rooturl = rooturl
        self.schema = schema

    def __len__(self):
        return len(self._datasets)
    
    def __getitem__(self, index):
        return self._datasets[index]
    
    @property
    def metadata(self):
        """
            returns the metadata dict loaded previously into the class.
            :return: dict, metadata dict of data collection loaded.
        """
        self.is_data_loaded()
        return self._metadata
    
    @property
    def tags(self):
        return self._tags
    
    @property
    def names(self):
        return self._names
    
    def is_data_loaded(self):
        """
            checks if any data has been loaded to work with.
                throws a ValueError in the absence of a data 
                collection and stops the flow of the code.
                
            :raises: ValueError, when there is no data loaded.
        """
        try:
            self._datasets[0]
        except:
            raise ValueError("no dataset loaded to work with!")
        
    @property
    def datasets(self):
        return self._datasets
    
    def __repr__(self):
        """repr method showing most important attributes of the class"""
        return f"{10*'-'} Data Collection {10*'-'}\nSource:\t\t{self._source} \nDatasets Count:\t{len(self)}"

        

    
class GQLCollection(Collection):
    def __init__(self, source, schema, rooturl):
        super().__init__(source, schema, rooturl)
        # init metadata ingestion
        self.load_from(schema)
    
    def load_from(self, schema):
        self._metadata = schema.to_json()
        items = self._metadata['data']['__schema']['queryType']['fields']
        self._datasets = []
        self._names = []
        # remove aggregate alias tables autogenerated by server
        items = [item for item in items if not '_aggregate' in item['name']]
        for ix, item in enumerate(items):
             d = GQLDataset(url=self.rooturl)
             d.load_from({
                 'resources':[{
                      **item, 
                     'position': 0, 
                     'format':'CSV',
                     'description':'',
                     }], 
                 'name':item['name'],
                 'position': ix
                 })
             self._datasets.append(d)
             self._names.append(item['name'])     
             
    # def search(self, by_tag=None, by_name=None, return_indices=False):
    #     self._names
    #     datasets = self._datasets
    #     indices = list(range(len(self._datasets)))
        
    #     if not (by_name is None):
    #         indices = [ix for ix, ds in zip(indices, datasets) if by_name in ds._name ]
    #         datasets = [self._datasets[ix] for ix in indices]

    def search(self, by_tag=None, by_name=None, return_indices=False):
        """
            searches the collection of datasets to return 
                datasets that satisfy the specified criteria.
            
            :param by_name: string, search by name if a dataset name attribute contains the given string
                default: None, which doesn't use this search criterion
            :param by_tag: string, search by tag string if any of dataset tags contains the given string
                default: None, which doesn't use this search criterion
            :param return_indices: bool, flag for returning the indices of found datasets as well.
                default: False, which doesn't return indices of found datasets
            :return: list|tuple, list of Dataset instances matching the search condition OR a tuple 
                containing the return indices if return_indices flag is True.

        """
        self.is_data_loaded()
        datasets = self._datasets
        indices = list(range(len(self._datasets)))
        
        if not (by_name is None):
            indices = [ix for ix, ds in zip(indices, datasets) if by_name in ds._name ]
            datasets = [self._datasets[ix] for ix in indices]
        if not (by_tag is None):
            indices = [ix for ix, ds in zip(indices, datasets) if by_tag in " ".join(ds._tags) ]
            datasets = [self._datasets[ix] for ix in indices]            
        if return_indices:
            return (datasets, indices)
        else:
            return datasets
    




class CKANCollection(Collection):
    """
        class representing info and methods available for interacting
            with a collection of datasets
    """
    def __init__(self, source, schema, rooturl):
        super().__init__(source, schema, rooturl)
        # init metadata ingestion
        self.load_from(schema)
        
    
    def load_from(self, collection_dict):
        """
            imports a dictionary object representing the data collection metadata.
            
            :param collection_dict: dict, dictionary of data collection metadata
            :return: None
        """
        self._metadata = collection_dict
        self._datasets = []
        for dataset_dict in collection_dict:
            d = CKANDataset(url=self.rooturl)
            d.load_from(dataset_dict)
            self._datasets.append(d)
        # assign tags list 
        tags = [ds._tags for ix, ds in enumerate(self._datasets) ]
        tags_flat_list = [item for sublist in tags for item in sublist]
        self._tags = list(np.unique(tags_flat_list))
        # assign names list
        names_flat_list = [ds._name for ix, ds in enumerate(self._datasets) ]
        self._names = list(np.unique(names_flat_list))

    
    def search(self, by_tag=None, by_name=None, return_indices=False):
        """
            searches the collection of datasets to return 
                datasets that satisfy the specified criteria.
            
            :param by_name: string, search by name if a dataset name attribute contains the given string
                default: None, which doesn't use this search criterion
            :param by_tag: string, search by tag string if any of dataset tags contains the given string
                default: None, which doesn't use this search criterion
            :param return_indices: bool, flag for returning the indices of found datasets as well.
                default: False, which doesn't return indices of found datasets
            :return: list|tuple, list of Dataset instances matching the search condition OR a tuple 
                containing the return indices if return_indices flag is True.

        """
        self.is_data_loaded()
        datasets = self._datasets
        indices = list(range(len(self._datasets)))
        
        if not (by_name is None):
            indices = [ix for ix, ds in zip(indices, datasets) if by_name in ds._name ]
            datasets = [self._datasets[ix] for ix in indices]
        if not (by_tag is None):
            indices = [ix for ix, ds in zip(indices, datasets) if by_tag in " ".join(ds._tags) ]
            datasets = [self._datasets[ix] for ix in indices]            
        if return_indices:
            return (datasets, indices)
        else:
            return datasets
        