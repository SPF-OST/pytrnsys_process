from collections import abc as _abc
from dataclasses import dataclass, field

from pytrnsys_process import constants as const


@dataclass
class Settings:
    plot: "Plot"
    reader: "Reader"


@dataclass
class Plot:
    file_formats: _abc.Sequence[str] = field(
        default_factory=lambda: [".png", ".pdf", ".emf"]
    )

    figure_sizes: dict[str, tuple[float, float]] = field(
        default_factory=lambda: {
            const.PlotSizes.A4.name: const.PlotSizes.A4.value,
            const.PlotSizes.A4_HALF.name: const.PlotSizes.A4_HALF.value,
        }
    )

    inkscape_path: str = "C://Program Files//Inkscape//bin//inkscape.exe"

    x_label: str = ""
    y_label: str = ""
    title: str = ""
    date_format: str = "%b %Y"
    color_map: str = "viridis"
    label_font_size: int = 10
    legend_font_size: int = 8
    title_font_size: int = 12


@dataclass
class Reader:
    folder_name_for_printer_files: str = "temp"
    read_step_files: bool = True


# TODO Provide structure for default settings, so users can easily access the defaults #pylint: disable=fixme


DEFAULT = Settings(plot=Plot(), reader=Reader())

settings = DEFAULT
