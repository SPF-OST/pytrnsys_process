import datetime as _dt
import pathlib as _pl
import pandas as _pd
import matplotlib.pyplot as _plt


class Plotter:

    @staticmethod
    def create_bar_chart_for_hourly(df: _pd.DataFrame):
        monthly_data = df.resample("M").sum()
        monthly_data.plot(
            kind="bar", stacked=True, figsize=(10, 6), colormap="viridis"
        )
        _plt.xlabel("Month")
        _plt.ylabel("Energy Values")
        _plt.title("Monthly Energy Consumption by Type")
        _plt.xticks(rotation=45)
        _plt.legend(title="Energy Types")
        _plt.tight_layout()
        _plt.show()
