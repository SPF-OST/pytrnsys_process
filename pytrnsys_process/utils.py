import pathlib as _pl

RESULTS_FOLDER_NAME = "temp"


def get_sim_folders(path_to_results: _pl.Path) -> list[_pl.Path]:
    sim_folders = []
    for item in path_to_results.glob("*"):
        if item.is_dir():
            sim_folders.append(item)
    return sim_folders


def get_files(
        sim_folders: list[_pl.Path], results_folder_name: str = RESULTS_FOLDER_NAME
) -> list[_pl.Path]:
    sim_files = []
    for sim_folder in sim_folders:
        for sim_file in (sim_folder / results_folder_name).glob("**/*"):
            sim_files.append(sim_file)
    return sim_files
