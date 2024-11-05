from typing import List

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import plotly.graph_objs as go
from entity.OutdoorSensor import OutdoorSensor


class WindCompass(dbc.Container):

    def __init__(self, data: List[OutdoorSensor]):
        """
        ctor
        :param self: this
        :param data 7 days of outdoor data
        """
        self._data = data
        fig = self.figCompassRose()

        super().__init__(fluid=True, children=[dcc.Graph(id={"type": "WPRdynamic", "index": "compassrose"}, figure=fig)])

    def figCompassRose(self) -> go.Figure:
        """
        df = [77.5, 72.5, 70.0, 45.0, 22.5, 42.5, 40.0, 62.5]
            fig = px.bar_polar(df, r="frequency", theta="direction",
                color="strength", template="plotly_dark",
                color_discrete_sequence= px.colors.sequential.Plasma_r)
        """
        df = self.processWindData()
        # print("df =", df)
        fig = go.Figure()
        fig.add_trace(
            go.Barpolar(r=df[5], name="> " + self.returnNumberConverted(11) + " " + self.WUnits(), marker_color="rgb(40,0,163)")
        )
        fig.add_trace(
            go.Barpolar(
                r=df[4],
                name=self.returnNumberConverted(8.5) + "-" + self.returnNumberConverted(11) + " " + self.WUnits(),
                marker_color="rgb(80,0,163)",
            )
        )

        fig.add_trace(
            go.Barpolar(
                r=df[3],
                name=self.returnNumberConverted(4.4) + "-" + self.returnNumberConverted(8.5) + " " + self.WUnits(),
                marker_color="rgb(120,0,163)",
            )
        )
        fig.add_trace(
            go.Barpolar(
                r=df[2],
                name=self.returnNumberConverted(2.2) + "-" + self.returnNumberConverted(4.4) + " " + self.WUnits(),
                marker_color="rgb(160,0,163)",
            )
        )
        fig.add_trace(
            go.Barpolar(
                r=df[1],
                name=self.returnNumberConverted(1.0) + "-" + self.returnNumberConverted(2.3) + " " + self.WUnits(),
                marker_color="rgb(200,0,163)",
            )
        )
        fig.add_trace(
            go.Barpolar(
                r=df[0],
                name=self.returnNumberConverted(0.0) + "-" + self.returnNumberConverted(1) + " " + self.WUnits(),
                marker_color="rgb(240,0,163)",
            )
        )

        fig.update_traces(text=["North", "N-E", "East", "S-E", "South", "S-W", "West", "N-W"])
        fig.update_layout(
            #title="Wind Speed Distribution Past Week",
            # font_size=16,
            legend_font_size=16,
            # polar_radialaxis_ticksuffix='%',
            # polar_angularaxis_rotation=90,
            font=dict(size=16),
            polar=dict(
                radialaxis=dict(ticksuffix="%", angle=45, tickfont=dict(size=12)),
                angularaxis=dict(direction="clockwise", tickfont=dict(size=14)),
            ),
            # color_discrete_sequence= go.colors.sequential.Plasma_r,
            template="plotly_dark",
        )
        return fig

    def processWindData(self):
        totalRecords = len(self._data)
        # now calculate buckets
        # 8 cardinal directions 0 - 360
        # 6 wind buckets
        df = [[], [], [], [], [], []]
        for i in range(0, 6):
            df[i] = [0, 0, 0, 0, 0, 0, 0, 0]

        os: OutdoorSensor
        for os in self._data:
            windSpeed = os.wind_avg_m_s
            windDirection = os.wind_dir_deg
            CB = self.returnCardinalBucket(windDirection)
            SB = self.returnSpeedBucket(windSpeed)
            # print("SB, CB=", SB, CB)
            df[SB][CB] = df[SB][CB] + 1
        # print ("df=", df)
        # print("number of records=", totalRecords)
        # normalize df
        if totalRecords > 0:
            for single in df:
                for i in range(0, 8):
                    single[i] = round(100.0 * float(single[i]) / float(totalRecords), 2)

        return df

    def CWUnits(self, wind):

        # TODO add to config
        English_Metric = True

        if English_Metric is False:  # english units
            wind = wind * 2.23694
        return wind

    def WUnits(self):

        # TODO add to config
        English_Metric = True

        if English_Metric is False:  # english units
            units = " mph"
        else:
            units = " m/s"

        return units

    def returnCardinalBucket(self,windDirection):
        if (windDirection >= 337.5) or (windDirection < 22.5):
            return 0
        if (windDirection >= 22.5) and (windDirection < 67.5):
            return 1
        if (windDirection >= 67.5) and (windDirection < 112.5):
            return 2
        if (windDirection >= 112.5) and (windDirection < 157.5):
            return 3
        if (windDirection >= 157.5) and (windDirection < 202.5):
            return 4
        if (windDirection >= 202.5) and (windDirection < 247.5):
            return 5
        if (windDirection >= 247.5) and (windDirection < 292.5):
            return 6
        if (windDirection >= 292.5) and (windDirection < 337.5):
            return 7

        raise ValueError("unable to get cardinal from %s", windDirection)

    def returnSpeedBucket(self, windSpeed):
        # in meters/second
        if windSpeed < 1.0:
            return 0
        if windSpeed < 2.3:
            return 1
        if windSpeed < 4.4:
            return 2
        if windSpeed < 8.5:
            return 3
        if windSpeed < 11.0:
            return 4
        # greater than 11.00
        return 5

    def returnNumberConverted(self, speed):
        speed = self.CWUnits(speed)
        return str(round(speed, 1))
