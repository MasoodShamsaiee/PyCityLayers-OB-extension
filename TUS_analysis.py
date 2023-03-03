import pandas as pd
class TUS_agents():
    def __init__(self):
        pass
    def occupancy_profiles(self,N_agents, n_rows=11000):

        TUS=pd.read_csv(r"C:\Users\msham\OneDrive - Concordia University - Canada\Datasets\Canadian TUS\2015-\Episodes\gss-89M0034-E-2015-c-29-episode_F2.csv",nrows=n_rows)
        print("Number of unique people available in the dataset:",TUS["PUMFID"].nunique())
        
        if N_agents>TUS["PUMFID"].nunique():
            print("but {} agents requested. Consider increasing the number of rows (n_rows)".format(N_agents))
        
        candidate_agents=TUS["PUMFID"].unique()[:N_agents]
        cols=["TUI_01","STARTMIN","ENDMIN","LOCATION"]
        agents=pd.DataFrame(index=pd.date_range(start="2015-01-01 00:00:00",periods=1441,freq="T"))
        agents_activity=pd.DataFrame([])
        agents_occupancy=pd.DataFrame([])
        for i in candidate_agents:
            raw_TUS=TUS[TUS["PUMFID"]==i]
            # print("i:{},# of records:{}".format(i,len(raw_TUS)))
            selected_raw=raw_TUS[cols].copy()
            
            selected_raw.loc[:,"start"]=selected_raw["STARTMIN"] % 1440
            selected_raw.loc[:,"end"]=selected_raw["ENDMIN"] % 1440
            selected_raw=selected_raw.sort_values("start").reset_index()
            
            # display(selected_raw.head())
            temp=pd.DataFrame(index=range(1441),columns=[0,1])
            for k in range(selected_raw["start"][0]+1):
                temp.iloc[k,0]=selected_raw["LOCATION"].iloc[-1]
                temp.iloc[k,1]=selected_raw["TUI_01"].iloc[-1]
            for j in range(len(selected_raw)):
                for l in range(selected_raw["start"][j],selected_raw["end"][j]+1):
                    temp.iloc[l,0]=selected_raw["LOCATION"][j]
                    temp.iloc[l,1]=selected_raw["TUI_01"][j]
                if selected_raw["start"][j]>selected_raw["end"][j]:
                    for m in range(selected_raw["start"][j],1441):
                        temp.iloc[m,0]=selected_raw["LOCATION"][j]
                        temp.iloc[m,1]=selected_raw["TUI_01"][j]
            temp.index=pd.date_range(start="2015-01-01 00:00:00",periods=1441,freq="T")
            
            occupancy=[]

            for n in range(len(temp)):
                if temp.iloc[n,0]==300:
                    occupancy.append(1)
                else:
                    occupancy.append(0)
            occupancy=pd.DataFrame(occupancy,index=temp.index)
            agents_occupancy=pd.concat([agents_occupancy,occupancy],axis=1)
            activity=[]
            
            for n in range(len(temp)):
                activity.append(temp.iloc[n,1])
            activity=pd.DataFrame(activity,index=temp.index)
            agents_activity=pd.concat([agents_activity,activity],axis=1)

        agents_occupancy.columns,agents_activity.columns=candidate_agents,candidate_agents
            
        # agents.columns=candidate_agents
        return agents_occupancy, agents_activity