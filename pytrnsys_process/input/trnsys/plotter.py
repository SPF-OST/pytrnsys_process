import matplotlib.pyplot as _plt
import pandas as _pd


class Plotter:

    @staticmethod
    def create_bar_chart_for_hourly(df: _pd.DataFrame, columns: list[str]):
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

    @staticmethod
    def create_bar_chart_for_monthly(
        df: _pd.DataFrame,
            columns: list[str],
    ) -> (_plt.Figure, _plt.Axes):
        fig, ax = df[columns].plot(
            kind="bar", stacked=True, figsize=(10, 6), colormap="tab20"
        )
        _plt.xlabel("Month")
        _plt.ylabel("Energy Values")
        _plt.title("Monthly Energy Consumption by Type")
        _plt.xticks(rotation=45)
        _plt.legend(title="Energy Types")
        _plt.tight_layout()

        return fig, ax



    @staticmethod
    def create_energy_balance_monthly(
        df: _pd.DataFrame,
        q_in_columns: list[str],
        q_out_columns: list[str],
        imbalance_column: str,
    ) -> (_plt.Figure, _plt.Axes):
        raise NotImplementedError




