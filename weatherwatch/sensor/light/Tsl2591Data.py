from dataclasses import dataclass

__all__ = ["Tsl2591Data"]


@dataclass
class Tsl2591Data:
    lux: float = None
    visible: int = None
    infrared: int = None
    full_spectrum: int = None
    raw_luminosity: tuple[int, int] = None

    def __post_init__(self):
        if self.lux is not None:
            self.lux = round(self.lux, 4)
