import collections.abc as _abc
import os
import pathlib as _pl
import subprocess

import matplotlib.pyplot as _plt

from pytrnsys_process import settings as _set
from pytrnsys_process.logger import logger


def get_sim_folders(path_to_results: _pl.Path) -> _abc.Sequence[_pl.Path]:
    sim_folders = []
    for item in path_to_results.glob("*"):
        if item.is_dir():
            sim_folders.append(item)
    return sim_folders


def get_files(
        sim_folders: _abc.Sequence[_pl.Path],
        results_folder_name: str = _set.settings.reader.folder_name_for_printer_files_loc,
        get_mfr_and_t: bool = _set.settings.reader.read_step_files,
) -> _abc.Sequence[_pl.Path]:
    sim_files: list[_pl.Path] = []
    for sim_folder in sim_folders:
        if get_mfr_and_t:
            sim_files.extend(sim_folder.glob("*[_T,_Mfr].prt"))
        for sim_file in (sim_folder / results_folder_name).glob("**/*"):
            sim_files.append(sim_file)

    return [x for x in sim_files if x.is_file()]


# TODO add docstring #pylint: disable=fixme

def save_plot(
        fig: _plt.Figure, path_to_directory: _pl.Path, plot_name: str
) -> None:
    plot_settings = _set.settings.plot
    plots_folder = path_to_directory / "plots"
    plots_folder.mkdir(exist_ok=True)

    for size_name, size in plot_settings.figure_sizes.items():
        file_no_suffix = plots_folder / f"{plot_name}-{size_name}"
        fig.set_size_inches(size)
        _plt.tight_layout()
        for fmt in plot_settings.file_formats:
            if fmt == ".emf":
                path_to_svg = file_no_suffix.with_suffix(".svg")
                fig.savefig(path_to_svg)
                convert_svg_to_emf(path_to_svg)
            else:
                fig.savefig(file_no_suffix.with_suffix(fmt))


def convert_svg_to_emf(path_to_svg: _pl.Path) -> None:
    try:
        inkscape_path = _set.settings.plot.inkscape_path
        if not _pl.Path(inkscape_path).exists():
            raise OSError(f"Inkscape executable not found at: {inkscape_path}")
        emf_filepath = path_to_svg.parent / f"{path_to_svg.stem}.emf"

        subprocess.run(
            [
                inkscape_path,
                "--export-filename=" + str(emf_filepath),
                "--export-type=emf",
                str(path_to_svg),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        os.remove(path_to_svg)
    except subprocess.CalledProcessError as e:
        logger.error(
            "Inkscape conversion failed: %s\nOutput: %s",
            e,
            e.output,
            exc_info=True,
        )
    except OSError as e:
        logger.error("System error running Inkscape: %s", e, exc_info=True)
