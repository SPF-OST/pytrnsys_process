from collections import abc as _abc
from dataclasses import dataclass, field
from enum import Enum

from pytrnsys_process.config import constants as const


@dataclass
class Plot:  # pylint: disable=too-many-instance-attributes
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
    markers: _abc.Sequence[str] = field(
        default_factory=lambda: [
            "x",
            "o",
            "^",
            "D",
            "v",
            "<",
            ">",
            "p",
            "*",
            "s",
        ]
    )


@dataclass
class Reader:
    folder_name_for_printer_files: str = "temp"
    read_step_files: bool = False
    read_deck_files: bool = True
    force_reread_prt: bool = False
    starting_year = 2024


@dataclass
class Settings:
    plot: Plot

    reader: Reader


class Defaults(Enum):
    "Default settings for different use cases"

    DEFAULT = Settings(plot=Plot(), reader=Reader())


global_settings = Defaults.DEFAULT.value
