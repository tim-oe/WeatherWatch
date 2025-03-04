from typing import List

import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash import dcc
from entity.OutdoorSensor import OutdoorSensor


class WindCompass(dbc.Container):
    """
    wind compass style graph
    https://plotly.com/python/graph-objects/
    direct CCP from:
    https://github.com/switchdoclabs/SDL_Pi_SkyWeather2/blob/master/dash_app/weather_page.py#L471
    """

    def __init__(self, data: List[OutdoorSensor]):
        """
        ctor
        :param self: this
        :param data: 7 days of outdoor data
        """

        self._data = data
        fig = self.fig_compass_rose()

        # id={"type": "WPRdynamic", "index": "compassrose"},
        super().__init__(fluid=True, children=[dcc.Graph(figure=fig)])

    def fig_compass_rose(self) -> go.Figure:
        """
        generate the wind compass graph
        :param self: this
        """
        df = self.process_wind_data()
        fig = go.Figure()
        fig.add_trace(
            go.Barpolar(
                r=df[5],
                name="> " + self.get_wind_speed_converted(11) + " " + self.get_wind_scale(),
                marker_color="rgb(40,0,163)",
            )
        )
        fig.add_trace(
            go.Barpolar(
                r=df[4],
                name=self.get_wind_speed_converted(8.5) + "-" + self.get_wind_speed_converted(11) + " " + self.get_wind_scale(),
                marker_color="rgb(80,0,163)",
            )
        )

        fig.add_trace(
            go.Barpolar(
                r=df[3],
                name=self.get_wind_speed_converted(4.4)
                + "-"
                + self.get_wind_speed_converted(8.5)
                + " "
                + self.get_wind_scale(),
                marker_color="rgb(120,0,163)",
            )
        )
        fig.add_trace(
            go.Barpolar(
                r=df[2],
                name=self.get_wind_speed_converted(2.2)
                + "-"
                + self.get_wind_speed_converted(4.4)
                + " "
                + self.get_wind_scale(),
                marker_color="rgb(160,0,163)",
            )
        )
        fig.add_trace(
            go.Barpolar(
                r=df[1],
                name=self.get_wind_speed_converted(1.0)
                + "-"
                + self.get_wind_speed_converted(2.3)
                + " "
                + self.get_wind_scale(),
                marker_color="rgb(200,0,163)",
            )
        )
        fig.add_trace(
            go.Barpolar(
                r=df[0],
                name=self.get_wind_speed_converted(0.0) + "-" + self.get_wind_speed_converted(1) + " " + self.get_wind_scale(),
                marker_color="rgb(240,0,163)",
            )
        )

        fig.update_traces(text=["North", "N-E", "East", "S-E", "South", "S-W", "West", "N-W"])
        fig.update_layout(
            title="Wind distribution",
            legend_font_size=16,
            font={"size": 16},
            polar={
                "radialaxis": {"ticksuffix": "%", "angle": 45, "tickfont": {"size": 12}},
                "angularaxis": {"direction": "clockwise", "tickfont": {"size": 14}},
            },
            template="plotly_dark",
        )
        return fig

    def process_wind_data(self):
        """
        calculate wind buckets
        8 cardinal directions 0 - 360
        6 wind buckets
        :param self: this
        """
        total_records = len(self._data)
        df = [[], [], [], [], [], []]
        for i in range(0, 6):
            df[i] = [0, 0, 0, 0, 0, 0, 0, 0]

        os: OutdoorSensor
        for os in self._data:
            wind_speed = os.wind_avg_m_s
            wind_direction = os.wind_dir_deg
            cardinal_bucket = self.get_cardinal_bucket(wind_direction)
            speed_bucket = self.get_speed_bucket(wind_speed)
            # print("SB, CB=", SB, CB)
            df[speed_bucket][cardinal_bucket] = df[speed_bucket][cardinal_bucket] + 1
        # print ("df=", df)
        # print("number of records=", totalRecords)
        # normalize df
        if total_records > 0:
            for single in df:
                for i in range(0, 8):
                    single[i] = round(100.0 * float(single[i]) / float(total_records), 2)

        return df

    def convert_wind_units(self, wind):
        """
        convert wind units based on scaler
        :param self: this
        """

        # TODO add to config
        english_metric = True

        if english_metric is False:  # english units
            wind = wind * 2.23694
        return wind

    def get_wind_scale(self):
        """
        get wind unit scale
        :param self: this
        """

        # TODO add to config
        english_metric = True

        if english_metric is False:  # english units
            units = " mph"
        else:
            units = " m/s"

        return units

    def get_cardinal_bucket(self, wind_direction) -> int:
        """
        get the cardinal bucket
        :param self: this
        :param wind_direction: the wind direction in degrees
        :return: the the cardinal direction bucket
        """
        cardinal_bucket: int = -1

        if wind_direction >= 337.5 or wind_direction < 22.5:
            cardinal_bucket = 0
        if 22.5 <= wind_direction < 67.5:
            cardinal_bucket = 1
        if 67.5 <= wind_direction < 112.5:
            cardinal_bucket = 2
        if 112.5 <= wind_direction < 157.5:
            cardinal_bucket = 3
        if 157.5 <= wind_direction < 202.5:
            cardinal_bucket = 4
        if 202.5 <= wind_direction < 247.5:
            cardinal_bucket = 5
        if 247.5 <= wind_direction < 292.5:
            cardinal_bucket = 6
        if 292.5 <= wind_direction < 337.5:
            cardinal_bucket = 7

        if cardinal_bucket == -1:
            raise ValueError(f"unable to get cardinal from {wind_direction}")

        return cardinal_bucket

    def get_speed_bucket(self, wind_speed):
        """
        get the speed bucket
        :param self: this
        :param wind_speed: the wind speed in meters/second
        :return: the the wind speed bucket
        """
        if wind_speed < 1.0:
            return 0
        if wind_speed < 2.3:
            return 1
        if wind_speed < 4.4:
            return 2
        if wind_speed < 8.5:
            return 3
        if wind_speed < 11.0:
            return 4
        # greater than 11.00
        return 5

    def get_wind_speed_converted(self, speed):
        """
        get the speed converted to proper scale
        :param self: this
        :param speed: the wind speed in meters/second
        :return: the wind speed it k/h
        """
        return str(round(self.convert_wind_units(speed), 1))
