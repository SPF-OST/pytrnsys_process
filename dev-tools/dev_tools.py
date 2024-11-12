#!/usr/bin/python3.12

"""Helper script for developers for running unit tests, static checkers and much more."""

# Run from top-level directory

import argparse as ap
import pathlib as pl
import shutil as sh
import subprocess as sp
import sys
import sysconfig as sc
import time
import typing as tp

_SCRIPTS_DIR = pl.Path(sc.get_path("scripts"))

_REPO_ROOT_PATH = pl.Path(__file__).parents[1]

_DOC_DIR_PATH = _REPO_ROOT_PATH / "doc"

_SOURCE_DIR_NAMES = ["pytrnsys_process", "tests", "dev-tools"]


def main():
    """Run the tool"""

    arguments = _parse_arguments()

    test_results_dir_path = pl.Path("test-results")
    _prepare_test_results_directory(
        test_results_dir_path, arguments.shallKeepResults
    )

    _maybe_run_mypy(arguments)

    _maybe_run_pylint(arguments)

    _maybe_run_black(arguments)

    _maybe_create_diagrams(arguments)

    _maybe_run_pytest(arguments, test_results_dir_path)

    _maybe_create_documentation(arguments)


def _parse_arguments() -> ap.Namespace:
    parser = ap.ArgumentParser()

    parser.add_argument(
        "-k",
        "--keep-results",
        help="Don't clean test results",
        action="store_true",
        dest="shallKeepResults",
    )
    parser.add_argument(
        "-s",
        "--static-checks",
        help="Perform linting and type checking",
        action="store_true",
        dest="shallPerformStaticChecks",
    )
    parser.add_argument(
        "-l",
        "--lint",
        help="Perform linting",
        type=str,
        default=None,
        const="",
        nargs="?",
        dest="lintArguments",
    )
    parser.add_argument(
        "-b",
        "--black",
        help="Check formatting",
        type=str,
        default=None,
        const="--check",
        nargs="?",
        dest="blackArguments",
    )
    parser.add_argument(
        "-t",
        "--type",
        help="Perform type checking",
        type=str,
        default=None,
        const="",
        nargs="?",
        dest="mypyArguments",
    )
    parser.add_argument(
        "-u",
        "--unit",
        help="Perform unit tests",
        type=str,
        default=None,
        const="",
        nargs="?",
        dest="pytestMarkersExpression",
    )
    parser.add_argument(
        "-d",
        "--diagram",
        help="Create package and class diagrams",
        nargs="?",
        default=None,
        const="pdf",
        choices=["pdf", "dot"],
        dest="diagramsFormat",
    )
    parser.add_argument(
        "-c",
        "--doc",
        help="Create documentation using Sphinx",
        action="store_true",
        dest="shallCreateDocumentation",
    )
    parser.add_argument(
        "-a",
        "--all",
        help="Perform all checks",
        action="store_true",
        dest="shallRunAll",
    )
    arguments = parser.parse_args()
    return arguments


def _prepare_test_results_directory(
    test_results_dir_path: pl.Path, shall_keep_results: bool
) -> None:
    if test_results_dir_path.exists() and not test_results_dir_path.is_dir():
        print(
            "ERROR: `test-results` exists but is not a directory",
            file=sys.stderr,
        )
        sys.exit(2)

    if not shall_keep_results and test_results_dir_path.is_dir():
        sh.rmtree(test_results_dir_path)

    # Sometimes we need to give Windows a bit of time so that it can realize that
    # the directory is gone and it allows us to create it again.
    time.sleep(1)

    if not test_results_dir_path.is_dir():
        test_results_dir_path.mkdir()


def _maybe_run_mypy(arguments):
    if (
        arguments.shallRunAll
        or arguments.shallPerformStaticChecks
        or arguments.mypyArguments is not None
    ):
        cmd = _create_static_checker_command("mypy", "--show-error-codes")
        additional_args = arguments.mypyArguments or ""
        _print_and_run([*cmd, *additional_args.split()])


def _maybe_run_pylint(arguments):
    if (
        arguments.shallRunAll
        or arguments.shallPerformStaticChecks
        or arguments.lintArguments is not None
    ):
        cmd = _create_static_checker_command("pylint")
        additional_args = arguments.lintArguments or ""

        _print_and_run([*cmd, *additional_args.split()])


def _maybe_run_black(arguments):
    if (
        arguments.shallRunAll
        or arguments.shallPerformStaticChecks
        or arguments.blackArguments is not None
    ):
        cmd = _create_static_checker_command("black", "-l 79")
        additional_args = (
            "--check"
            if arguments.blackArguments is None
            else arguments.blackArguments
        )

        _print_and_run([*cmd, *additional_args.split()])


def _create_static_checker_command(
    static_checker_name: str, *args: str
) -> tp.Sequence[str]:
    cmd = [
        f"{_SCRIPTS_DIR / static_checker_name}",
        *args,
        *_SOURCE_DIR_NAMES,
    ]
    return cmd


def _maybe_create_diagrams(arguments):
    if arguments.shallRunAll or arguments.diagramsFormat:
        diagrams_format = (
            arguments.diagramsFormat if arguments.diagramsFormat else "pdf"
        )
        cmd = (
            f"{_SCRIPTS_DIR / 'pyreverse'} -k -o {diagrams_format}"
            " -p pytrnsys_process -d test-results pytrnsys_process"
        )
        _print_and_run(cmd.split())


def _maybe_run_pytest(arguments, test_results_dir_path):
    was_called_without_arguments = (
        not arguments.shallPerformStaticChecks
        and arguments.mypyArguments is None
        and arguments.lintArguments is None
        and arguments.blackArguments is None
        and arguments.diagramsFormat is None
        and not arguments.shallCreateDocumentation
    )
    if (
        arguments.shallRunAll
        or arguments.pytestMarkersExpression is not None
        or was_called_without_arguments
    ):
        _run_unit_tests_with_pytest(arguments, test_results_dir_path)
        _run_doctests_with_pytest()


def _run_unit_tests_with_pytest(arguments, test_results_dir_path):
    marker_expressions = _get_marker_expressions(
        arguments.pytestMarkersExpression
    )
    additional_args = ["-m", marker_expressions]
    cmd = [
        _SCRIPTS_DIR / "pytest",
        "-v",
        "--benchmark-skip",
        "--cov=pytrnsys_process",
        f"--cov-report=html:{test_results_dir_path / 'coverage-html'}",
        f"--cov-report=lcov:{test_results_dir_path / 'coverage.lcov'}",
        "--cov-report=term",
        f"--html={test_results_dir_path / 'report' / 'report.html'}",
    ]
    args = [*cmd, *additional_args, "tests"]
    _print_and_run(args)


def _run_doctests_with_pytest():
    cmd = [_SCRIPTS_DIR / "pytest", "--doctest-modules", "pytrnsys_process"]
    _print_and_run(cmd)


def _get_marker_expressions(user_supplied_marker_expressions: str) -> str:
    hard_coded_marker_expressions = "not tool"
    marker_expressions = (
        f"({hard_coded_marker_expressions}) and ({user_supplied_marker_expressions})"
        if user_supplied_marker_expressions
        else hard_coded_marker_expressions
    )
    return marker_expressions


def _maybe_create_documentation(arguments):
    if arguments.shallRunAll or arguments.shallCreateDocumentation:
        _run_apidoc()
        _run_sphinx_build()


def _run_apidoc():
    apidoc_output_dir_path = _DOC_DIR_PATH / "_apidoc"

    _ensure_empty_dir_exists(apidoc_output_dir_path)

    cmd = [
        f"{_SCRIPTS_DIR / 'sphinx-apidoc'}",
        "-o",
        apidoc_output_dir_path,
        "pytrnsys_process",
    ]

    _print_and_run(cmd)


def _run_sphinx_build():
    build_dir_path = _DOC_DIR_PATH / "_build"

    _ensure_empty_dir_exists(build_dir_path)

    cmd = [
        f"{_SCRIPTS_DIR / 'sphinx-build'}",
        "-E",
        _DOC_DIR_PATH,
        build_dir_path,
    ]

    _print_and_run(cmd)


def _ensure_empty_dir_exists(dir_path):
    if dir_path.exists():
        if not dir_path.is_dir():
            raise ValueError("Not a directory", dir_path)

        sh.rmtree(dir_path)
        time.sleep(1)

    dir_path.mkdir()


def _print_and_run(args: tp.Sequence[str]) -> None:
    formatted_args = " ".join(str(arg) for arg in args)
    print(f"Running '{formatted_args}'...", flush=True)
    sp.run(args, check=True)
    print("...DONE.", flush=True)


if __name__ == "__main__":
    main()
