from dataclasses import dataclass
from enum import Enum


class PlotSizes(Enum):
    A4 = (7.8, 3.9)
    A4_HALF = (3.8, 3.9)


@dataclass(frozen=True)
class FilePattern:
    patterns: list[str]
    prefix: str


class FileType(Enum):
    MONTHLY = FilePattern(patterns=["_mo_", "_mo", ".mo", "mo_"], prefix="mo_")
    HOURLY = FilePattern(patterns=["_hr_", "_hr", ".hr", "hr_"], prefix="hr_")
    TIMESTEP = FilePattern(patterns=["_step", "step_"], prefix="step_")
