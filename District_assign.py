import pandas as pd
import geopandas as gpd
from tqdm import tqdm
from shapely.geometry import Polygon, MultiPolygon
import pickle

# Read District Data
data_Koa=gpd.read_file(r"montreal_districts.geojson")
# Read buildings' Data

montreal_dataset=gpd.read_file(r"montreal_dataset_v1.geojson")

Buildings_list=montreal_dataset
tracts_assigned_dict=[]

for i, CODEID in enumerate(data_Koa["CODEID"]):
    
    polya=MultiPolygon(data_Koa[data_Koa['CODEID']==CODEID].iloc[0,:]['geometry'])
    print(f"check for District{CODEID} which is {i+1} / {len(data_Koa)}")
    for j in tqdm(Buildings_list.index, disable=False):
        if "MULTIPOLYGON" in str(Buildings_list[Buildings_list.index==j]["geometry"]):
            continue
        polyb=Polygon(Buildings_list.iloc[j,:]["geometry"])
        if polya.contains(polyb):
            tracts_assigned_dict.append({'Index':j,'ID_UEV':str(Buildings_list.iloc[j,:]["ID_UEV"]),'District':CODEID})

new_df=Buildings_list.copy()
tracts_assigned_df=pd.DataFrame(tracts_assigned_dict)
new_df=pd.merge(new_df,tracts_assigned_df,on="ID_UEV")

with open('Districts2.pickle', 'wb') as handle:
    pickle.dump(new_df, handle, protocol=pickle.HIGHEST_PROTOCOL)
