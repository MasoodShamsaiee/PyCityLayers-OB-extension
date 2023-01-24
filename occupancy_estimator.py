import networkx as nx
from shapely.geometry import Polygon, Point
import matplotlib.pyplot as plt


class occupancy_estimator():
    def __init__(self):
        pass
    
    def init_data(self, data_obj):
        self.data = data_obj

    def find_centroids(self):

        centroid=[]
        for i in range(len(self.data)):
            vertex = self.data.iloc[i,:]["geom"]["coordinates"][0]
            polygon1=Polygon(vertex)
            centroid.append(polygon1.centroid)
        self.centroid=centroid
        print("# centroids:",len(centroid))
        print("# polygons:",len(self.data))
        return centroid

    def create_graph(self,show_graph=True,add_outside_node=True):
        self.graph=nx.Graph()
        for i in range(len(self.centroid)):
            self.graph.add_node(i,pos=(self.centroid[i].x,self.centroid[i].y))
        
        # adds a node representing outside and connects all other nodes to it
        if add_outside_node==True:
            self.graph.add_node(len(self.graph),pos=(-73.57,45.53))
            
            for i in range(len(self.graph)-1):
                self.graph.add_edge(i, len(self.graph)-1)

        if show_graph==True:
            nx.draw(self.graph,nx.get_node_attributes(self.graph,'pos'),with_labels=True,node_color="r")
        return self.graph
        
    def visualize_graph(self):
        pos=nx.get_node_attributes(self.graph,'pos')

        xs,ys=[],[]
        for i in range(len(pos)):
            xs.append(pos[i][0])
            ys.append(pos[i][1])
        
        n=list(self.graph.nodes)
        fig, ax = plt.subplots()
        ax.scatter(xs, ys)
        plt.grid()

        for i, txt in enumerate(n):
            ax.annotate(txt, (xs[i], ys[i]))
        plt.show()