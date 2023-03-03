import networkx as nx
from shapely.geometry import Polygon, Point
import matplotlib.pyplot as plt
import pandas as pd

class semantic_graph():
    def __init__(self):
        pass
    
    def init_data(self, data_obj):
        self.data = data_obj
        print("{} buildings imported".format(len(self.data)))

    def find_centroids(self):

        centroid=[]
        uid=[]
        dwelling_number=[]
        landuse_code=[]


        for i in range(len(self.data)):
            vertex = self.data.iloc[i,:]["geom"]["coordinates"][0]
            polygon1=Polygon(vertex)
            centroid.append(polygon1.centroid)
            uid.append(self.data.iloc[i,:]["uid"])
            dwelling_number.append(self.data.iloc[i,:]
            ["dwelling_number"])
            landuse_code.append(self.data.iloc[i,:]["landuse_code"])

            plt.plot(*polygon1.exterior.xy)
        self.centroid=pd.concat([pd.DataFrame(centroid),pd.DataFrame(uid)
        ,pd.DataFrame(dwelling_number),pd.DataFrame(landuse_code)],axis=1)
        self.centroid.columns=["centroid","uid","dwelling_number","landuse_code"]
        self.centroid=self.centroid.set_index("uid")

        plt.show()
        print("# centroids:",len(self.centroid))
        print("# polygons:",len(self.data))
        return self.centroid

    def create_graph(self,show_graph=True,show_edges=False,add_outside_node=False):
        
        self.find_centroids()

        self.graph=nx.Graph()
        
        for i in range(len(self.centroid)):
            self.graph.add_node(list(self.centroid.index)[i],pos=(list(self.centroid["centroid"])[i].x,list(self.centroid["centroid"])[i].y),
                dwelling_number=list(self.centroid["dwelling_number"])[i],landuse_code=list(self.centroid["landuse_code"])[i])
        print("Number of nodes:",self.graph.number_of_nodes())
        self.color=pd.Series([],dtype=str)
        for i in range(len(self.graph)):
            if list(self.graph.nodes(data=True))[i][1]['landuse_code']!=1000:
                self.color[i]="r"
                for j in range(len(self.graph)):
                    self.graph.add_edge(list(self.graph.nodes())[j],list(self.graph.nodes())[i])
            else:
                self.color[i]="g"
                self.graph.add_edge(list(self.graph.nodes())[i],list(self.graph.nodes())[i])

        # adds a node representing outside and connects all other nodes to it
        if add_outside_node==True:
            self.graph.add_node(len(self.graph),pos=(-73.57,45.53))
            
            for i in range(len(self.graph)-1):
                self.graph.add_edge(i, len(self.graph)-1)
        
        if show_graph==True:
            if show_edges==True:
                self.plot_graph()
            else:
                self.plot_nodes()
        
        return self.graph
        
    def plot_graph(self,show_labels=False):
        nx.draw_networkx(self.graph,nx.get_node_attributes(self.graph,'pos'),with_labels=show_labels,node_color=self.color,node_size=50)

    def plot_nodes(self):
        nx.draw_networkx_nodes(self.graph,nx.get_node_attributes(self.graph,'pos'),node_color=self.color,node_size=50)