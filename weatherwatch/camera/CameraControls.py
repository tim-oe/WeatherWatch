import math
from dataclasses import asdict, dataclass

import libcamera

__all__ = ["CameraControls"]


@dataclass(init=False)
class CameraControls:
    """
    typed camera controls for picamera2
    https://libcamera.org/api-html/namespacelibcamera_1_1controls.html

    Maps lux to (ExposureTime us, AnalogueGain) for OV5647.

    Approximate lux zones:
    > 10,000     : bright daylight
    1,000-10,000 : overcast / indoor bright
    100-1,000    : indoor ambient
    10-100       : dim indoor / dusk
    1-10         : twilight
    < 1          : night
    """

    AeEnable: bool
    ExposureTime: int
    AnalogueGain: float
    NoiseReductionMode: libcamera.controls.draft.NoiseReductionModeEnum
    AwbEnable: bool
    AwbMode: libcamera.controls.AwbModeEnum

    def __init__(self, lux: float):
        """
        ctor
        :param lux: the ambient light level to contol exposure/iso settings
        """
        self.AeEnable = False
        self.AwbEnable = True
        self.AwbMode = libcamera.controls.AwbModeEnum.Auto
        self.NoiseReductionMode = libcamera.controls.draft.NoiseReductionModeEnum.HighQuality

        self.lux_to_gain(lux)
        self.lux_to_exposure(lux)

    def lux_to_gain(self, lux: float):
        """
        Map lux to gain
        :param lux: the ambient light level to contol exposure/iso settings
        :returns gain
        """
        # Prefer longer exposure over high gain to minimize noise
        if lux >= 5.0:
            self.AnalogueGain = 1.0
        elif lux >= 1.0:
            self.AnalogueGain = 2.0
        elif lux >= 0.5:
            self.AnalogueGain = 4.0
        else:
            self.AnalogueGain = 8.0

    def lux_to_exposure(self, lux: float):
        """
        Map lux to exposure time
        Anchor points based on real-world targets:

        10,000 lux (bright sun)  →  500µs   (1/2000s)
        1,000  lux (overcast)    →  2,000µs  (1/500s)
        100    lux (indoor bright)→ 20,000µs (1/50s)
        10     lux (dim indoor)  →  80,000µs (1/12s)
        5      lux (dusk)        →  400,000µs (0.4s)
        1    lux (twilight)    →  1,000,000µs (1s)
        0.5   lux (night)       →  3,000,000µs (3s)

        :param lux: the ambient light level to contol exposure/iso settings
        :returns exposure time
        """
        # Anchor points: (lux, exposure_us)
        # tweakking setting for sensor in use
        anchors = [
            (10000, 500),
            (1000, 2_000),
            (100, 20_000),
            (10, 80_000),
            (5, 400_000),
            (1, 1_000_000),
            (0.5, 3_000_000)
        ]

        lux = max(lux, 0.001)

        # Find bracketing anchors and interpolate in log space
        if lux >= anchors[0][0]:
            exposure = anchors[0][1]
        elif lux <= anchors[-1][0]:
            exposure = anchors[-1][1]
        else:
            for i in range(len(anchors) - 1):
                lux_hi, exp_hi = anchors[i]
                lux_lo, exp_lo = anchors[i + 1]
                if lux_lo <= lux <= lux_hi:
                    # Log-linear interpolation between anchors
                    t = (math.log10(lux) - math.log10(lux_lo)) / (math.log10(lux_hi) - math.log10(lux_lo))
                    exposure = int(exp_lo + t * (exp_hi - exp_lo))
                    break

        self.ExposureTime = exposure

    # def lux_to_image_controls(self, lux: float):
    #     """
    #     Map lux to image controls
    #     TODO need to see if tweaks are needed  but only after sampling lux
    #     :param lux: the ambient light level to contol exposure/iso settings
    #     :returns image controls
    #     """
    #     if lux > 1000:  # bright daylight
    #         brightness = 0.05
    #         contrast = 1.2
    #         saturation = 1.1
    #         sharpness = 1.5
    #     elif lux > 100:  # indoor bright / overcast
    #         brightness = 0.02
    #         contrast = 1.1
    #         saturation = 1.05
    #         sharpness = 1.2
    #     elif lux > 10:  # dim indoor (~where you are now at 28 lux)
    #         brightness = 0.0
    #         contrast = 1.0
    #         saturation = 1.0
    #         sharpness = 1.0
    #     elif lux > 1:  # dusk / twilight
    #         brightness = 0.0
    #         contrast = 0.95
    #         saturation = 0.9
    #         sharpness = 0.8
    #     else:  # night
    #         brightness = 0.0
    #         contrast = 0.9
    #         saturation = 0.8
    #         sharpness = 0.7

    def to_dict(self) -> dict:
        """
        convert to dict
        :param self: this
        :returns dict
        """
        return asdict(self)
