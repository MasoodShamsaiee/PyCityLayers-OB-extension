from pycitylayers.client import Client
from pycitylayers.utils import PointGQL, PolygonGQL
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point, MultiPolygon
import numpy as np
import geopandas as gpd
import contextily as cx
from shapely.geometry import Polygon, Point, MultiPolygon



def tract_extract(x=-73.57055894277187,y=45.530384608361125,r=0.03):
    client = Client().create(source='cerc')
    coll = client.collection
    tb=coll[9][0]
    print("Tracts collection acquired")

    query_geometry = PointGQL().point(str(x),str(y))
    query_options = {
    # 'columns': ['index', 'built_area', 'geom', 'year_built'], 
    'nrows': 10000, 
    'skiprows': 0,
    'geometry_operation': 'distance_from_point',
    'geom_distance': r,
    'geometry': query_geometry,
    'crs_epsg': 4326,
    }
    data_tracts = tb.query_simple( **query_options )
    print("selecting {} tracts in {} m radius of point {},{}".format(len(data_tracts),round(r*111100),x,y))

    return data_tracts

def building_extract(x=-73.57055894277187,y=45.530384608361125,r=0.03):

    client = Client().create(source='cerc')
    coll = client.collection
    tb=coll[6][0]
    print("building lots collection acquired")
    query_geometry = PointGQL().point(str(x),str(y))
    query_options = {
    # 'columns': ['index', 'built_area', 'geom', 'year_built'], 
    'nrows': 50000, 
    'skiprows': 0,
    'geometry_operation': 'distance_from_point',
    'geom_distance': r,
    'geometry': query_geometry,
    'crs_epsg': 4326,
    }

    data_building_lots = tb.query_simple( **query_options )
    print("selecting {} buildings in {} m radius of point {},{}".format(len(data_building_lots),round(r*111100),x,y))
    return(data_building_lots)

def building_footprint_extract(x=-73.57055894277187,y=45.530384608361125,r=0.03):
    client = Client().create(source='cerc')
    coll = client.collection
    tb=coll[5][0]
    print("building lots collection acquired")
    query_geometry = PointGQL().point(str(x),str(y))
    query_options = {
    # 'columns': ['index', 'built_area', 'geom', 'year_built'], 
    'nrows': 50000, 
    'skiprows': 0,
    'geometry_operation': 'distance_from_point',
    'geom_distance': r,
    'geometry': query_geometry,
    'crs_epsg': 4326,
    }

    data_building_lots = tb.query_simple( **query_options )
    print("selecting {} buildings in {} m radius of point {},{}".format(len(data_building_lots),round(r*111100),x,y))
    return(data_building_lots)    


def tract_assign(Buildings_list,x=-73.57055894277187,y=45.530384608361125,r=0.03):
    
    data_tracts=tract_extract(x,y,r)
    tracts_assigned_dict=dict([])
    for i, CTname in enumerate(data_tracts["CTNAME"]):
        polya=Polygon(data_tracts[data_tracts.loc[:,"CTNAME"]==CTname]["geom"][i]["coordinates"][0][0])
        for j in Buildings_list.index:
            polyb=Polygon(Buildings_list.iloc[j,:]["geom"]["coordinates"][0])
            if polya.contains(polyb):
                tracts_assigned_dict[j]=CTname

    new_df=Buildings_list.copy()
    new_df["Tract"]=np.nan
    for j in tracts_assigned_dict:
        new_df["Tract"][j]=tracts_assigned_dict[j]
    return new_df

def buildings_in_tracts(x=-73.57055894277187,y=45.530384608361125,r=0.03):
    buildings=building_extract(x,y,r)
    full_df=tract_assign(Buildings_list=buildings,x=x,y=y,r=r)
    print("assignment done")
    tracts_bldg_count_dic=dict([])
    for tract in full_df["Tract"].unique():
        tracts_bldg_count_dic[tract]=len(full_df[full_df["Tract"]==tract])
    return(tracts_bldg_count_dic)


### --- PLOTTING FUNCTIONS --- ###
def geometry_generator(bldgs,multipolygon=False):
    polygon_list=[]
    for i in range(len(bldgs)):
        if multipolygon:
            vertex = bldgs.iloc[i,:]["geom"]["coordinates"][0][0]
        else:    
            vertex = bldgs.iloc[i,:]["geom"]["coordinates"][0]
        polygon1=Polygon(vertex)
        polygon_list.append(polygon1)
    return polygon_list

def plot_it(buildings_list,column=None,legend=False,basemap=True,multipolygon=False,alpha=1):
    if type(buildings_list)!=gpd.geodataframe.GeoDataFrame:
        dataset=gpd.GeoDataFrame(buildings_list)
        dataset=dataset.set_geometry(geometry_generator(buildings_list,multipolygon=multipolygon))
        dataset=dataset.set_crs(epsg=4326)
    if multipolygon:
        ax=dataset.plot(column=column,legend=legend, edgecolor="black", alpha=alpha)
    else:
        ax=dataset.plot(column=column,legend=legend,alpha=alpha)
    if basemap:
        cx.add_basemap(ax, crs=dataset.crs.to_string(),source=cx.providers.OpenStreetMap.Mapnik)
    
    return