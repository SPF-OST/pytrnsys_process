import collections.abc as _abc
import os
import pathlib as _pl
import subprocess

import matplotlib.pyplot as _plt

from pytrnsys_process import settings as sett
from pytrnsys_process.logger import logger


def get_sim_folders(path_to_results: _pl.Path) -> _abc.Sequence[_pl.Path]:
    sim_folders = []
    for item in path_to_results.glob("*"):
        if item.is_dir():
            sim_folders.append(item)
    return sim_folders


def get_files(
        sim_folders: _abc.Sequence[_pl.Path],
        results_folder_name: str = sett.settings.reader.folder_name_for_printer_files,
        get_mfr_and_t: bool = sett.settings.reader.read_step_files,
        read_deck_files: bool = sett.settings.reader.read_deck_files,
) -> _abc.Sequence[_pl.Path]:
    """Get simulation files from folders based on configuration.

    Args:
        sim_folders: Sequence of paths to simulation folders
        results_folder_name: Name of folder containing printer files
        get_mfr_and_t: Whether to include step files (T and Mfr files)
        read_deck_files: Whether to include deck files

    Returns:
        Sequence of paths to simulation files
    """
    sim_files: list[_pl.Path] = []
    for sim_folder in sim_folders:
        if get_mfr_and_t:
            sim_files.extend(sim_folder.glob("*[_T,_Mfr].prt"))
        if read_deck_files:
            sim_files.extend(sim_folder.glob("**/*.dck"))
        results_path = sim_folder / results_folder_name
        if results_path.exists():
            sim_files.extend(results_path.glob("*"))

    return [x for x in sim_files if x.is_file()]


# TODO add docstring #pylint: disable=fixme


def export_plots_in_configured_formats(
        fig: _plt.Figure, path_to_directory: _pl.Path, plot_name: str
) -> None:
    """Save a matplotlib figure in multiple formats and sizes.

    Saves the figure in all configured formats (png, pdf, emf) and sizes (A4, A4_HALF)
    as specified in the plot settings (api.settings.plot).
    For EMF format, the figure is first saved as SVG and then converted using Inkscape.

    Args:
        fig: The matplotlib Figure object to save.
        path_to_directory: Directory path where the plots should be saved.
        plot_name: Base name for the plot file (will be appended with size and format).

    Returns:
        None

    Note:
        - Creates a 'plots' subdirectory if it doesn't exist
        - For EMF files, requires Inkscape to be installed at the configured path
        - File naming format: {plot_name}-{size_name}.{format}

    Example:
    >>> from pytrnsys_process import api
    >>> def processing_of_monthly_data(simulation: api.Simulation):
    >>>     monthly_df = simulation.monthly
    >>>     columns_to_plot = ["QSnk60P", "QSnk60PauxCondSwitch_kW"]
    >>>     fig, ax = api.bar_chart(monthly_df, columns_to_plot)
    >>>
    >>>     # Save the plot in multiple formats
    >>>     api.export_plots_in_configured_formats(fig, simulation.path, "monthly-bar-chart")
    >>>     # Creates files like:
    >>>     #   results/simulation1/plots/monthly-bar-chart-A4.png
    >>>     #   results/simulation1/plots/monthly-bar-chart-A4.pdf
    >>>     #   results/simulation1/plots/monthly-bar-chart-A4.emf
    >>>     #   results/simulation1/plots/monthly-bar-chart-A4_HALF.png
    >>>     #   etc.

    """
    plot_settings = sett.settings.plot
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
                convert_svg_to_emf(file_no_suffix)
                if ".svg" not in plot_settings.file_formats:
                    os.remove(path_to_svg)
            else:
                fig.savefig(file_no_suffix.with_suffix(fmt))


def convert_svg_to_emf(file_no_suffix: _pl.Path) -> None:
    try:
        inkscape_path = sett.settings.plot.inkscape_path
        if not _pl.Path(inkscape_path).exists():
            raise OSError(f"Inkscape executable not found at: {inkscape_path}")
        emf_filepath = file_no_suffix.with_suffix(".emf")
        path_to_svg = file_no_suffix.with_suffix(".svg")

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

    except subprocess.CalledProcessError as e:
        logger.error(
            "Inkscape conversion failed: %s\nOutput: %s",
            e,
            e.output,
            exc_info=True,
        )
    except OSError as e:
        logger.error("System error running Inkscape: %s", e, exc_info=True)


def get_file_content_as_string(
        file_path: _pl.Path, encoding: str = "UTF-8"
) -> str:
    """Read and return the entire content of a file as a string.

    Args:
        file_path (Path): Path to the file to read
        encoding (str, optional): File encoding to use. Defaults to "UTF-8".

    Returns:
        str: Content of the file as a string
    """
    with open(file_path, "r", encoding=encoding) as file:
        return file.read()
