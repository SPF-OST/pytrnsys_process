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


@dataclass
class Reader:
    folder_name_for_printer_files_loc: str = "temp"


DEFAULT = Settings(plot=Plot(), reader=Reader())

settings = DEFAULT
