from decimal import Decimal
from typing import List
import dash_bootstrap_components as dbc
from dash import dcc
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd

from entity.OutdoorSensor import OutdoorSensor


class Graph(dbc.Container):
    """
    humidity guage class
    https://dash.plotly.com/dash-daq/gauge
    """

    def __init__(self, title: str, dataTitle: str, dataUnits: str, dataKey:str, data: List[OutdoorSensor]):

        super().__init__(children=dcc.Graph(
                    figure=self.buildGraph(title, dataTitle, dataUnits, dataKey, data),
                    animate = False
                    )                         
                )


    def buildGraph(self, title: str, dataTitle: str, dataUnits: str, dataKey:str, data: List[OutdoorSensor]):
    
        val = []
        time = []
   
        min = getattr(data[0], dataKey)
        max = getattr(data[0], dataKey)
        
        r: OutdoorSensor
        for r in data:
            v = getattr(r, dataKey)
            time.append(r.read_time)
            val.append(v)
            if(v < min):
                min = v
            if(v > max):
                max = v
            
        min = min*Decimal(0.9)
        max = max*Decimal(1.10)

        df = pd.DataFrame({
            'x': time,
            'y': val
        })

        fig = go.Figure()

        fig.update_xaxes(title_text="Time")
        fig.update_yaxes(title_text=f"<b>{dataTitle} {dataUnits}</b>", 
                         range = (min,max))

        fig.update_layout(title_text=title, 
                          height=400, 
                          template="plotly_dark"
                          )

        fig.add_trace(go.Scatter(x=time, y=val, mode='lines+markers'))
        
        return fig