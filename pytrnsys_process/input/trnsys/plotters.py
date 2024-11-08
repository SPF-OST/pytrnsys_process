from abc import abstractmethod
from typing import Tuple

import matplotlib.pyplot as _plt
import pandas as _pd


class ChartBase:
    X_LABEL = ""
    Y_LABEL = "Energy Flows"
    TITLE = ""
    COLOR_MAP = "viridis"

    def __init__(self, df, x_label=X_LABEL, y_label=Y_LABEL, title=TITLE):
        self.df = df
        self.x_label = x_label
        self.y_label = y_label
        self.title = title
        self.fig, self.ax = _plt.subplots(figsize=(10, 6))

    def configure(self):
        self.ax.set_xlabel(self.x_label)
        self.ax.set_ylabel(self.y_label)
        self.ax.set_title(self.title)
        _plt.tight_layout()

    @abstractmethod
    def plot(self, *args, **kwargs):
        raise NotImplementedError

    # makes no sense
    # def _plot(self, df, columns: list[str]):
    #     # TODO: check if this makes sense.
    #     self.plot(df, columns)
    #     self.configure()


class MonthlyBarChart(ChartBase):

    def plot(
        self, columns: list[str], **kwargs
    ) -> Tuple[_plt.Figure | None, _plt.Axes]:
        self.df[columns].plot(
            kind="bar", stacked=True, ax=self.ax, colormap="viridis"
        )

        self.configure()
        return self.fig, self.ax

class Plotter:

    @staticmethod
    def create_bar_chart_for_hourly(df: _pd.DataFrame, columns: list[str]):
        monthly_data = df.resample("M").sum()
        monthly_data[columns].plot(
            kind="bar", stacked=True, figsize=(10, 6), colormap="viridis"
        )
        _plt.xlabel("Month")
        _plt.ylabel("Energy Values")
        _plt.title("Monthly Energy Consumption by Type")
        _plt.xticks(rotation=45)
        _plt.legend(title="Energy Types")
        _plt.tight_layout()
        _plt.show()

    @staticmethod
    def create_bar_chart_for_monthly(
        df: _pd.DataFrame,
        columns: list[str],
    ) -> Tuple[_plt.Figure, _plt.Axes]:
        ax = df[columns].plot(
            kind="bar", stacked=True, figsize=(10, 6), colormap="tab20"
        )
        _plt.xlabel("Month")
        _plt.ylabel("Energy Values")
        _plt.title("Monthly Energy Consumption by Type")
        _plt.xticks(rotation=45)
        _plt.legend(title="Energy Types")
        _plt.tight_layout()
        _plt.show()
        return ax.get_figure(), ax

    @staticmethod
    def create_energy_balance_monthly(
        df: _pd.DataFrame,
        q_in_columns: list[str],
        q_out_columns: list[str],
        imbalance_column: str,
    ) -> (_plt.Figure, _plt.Axes):
        raise NotImplementedError
