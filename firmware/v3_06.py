"""Stock D878UVII V3.06 (20250123)."""
from .base import Firmware

FIRMWARE = Firmware(
    name="D878UVII_V3.06_20250123",
    version="V3.06",
    sha256="0973126fc33fda1d734dbc064852648710de52f44c2bc7df07bc9fd4272cfef8",
    load_addr=0x08004000,
    spi_length_at=6,
    cdi_length_at=260,
    symbols={
        # ptt-lock
        "STARTED": 0x20001412,
        "SETTINGS": 0x20008470,
        "KEYLOCK_ON": 0x4e,
        "LOCK_OPTIONS": 0xbe,
        "SIDE_KEY_LOCK": 0x08,
        "BUTTONS": 0x2000090e,
        "PTT": 0x01,
        "KEY_LOCKED_SHOWN": 0x10,
        "SHOW_MESSAGE": 0x080100e8,
        "MSG_KEY_LOCKED": 0x18,
        "PTT_HOOK": 0x08029722,
        "PTT_RESUME": 0x08029726,
        "PTT_LOCK_CODE": 0x080e9840,
        # usb-fix
        "USB_START": 0x0807dc50,
        "USB_STOP": 0x08080776,
        "PASSWORD_OK": 0x20000adc,
        "KEY_COMBO_MODE": 0x2000127b,
        "USB_HOOK_MAIN": 0x080047d4,
        "USB_HOOK_COMBO": 0x08004796,
        "USB_FIX_CODE": 0x080e9700,
    },
    known_outputs={
        frozenset({"ptt-lock"}): ("fb9c18bff1d5773cf7c94091f439a455387aedc50dd59301c148c74088df9c16", True),
        frozenset({"usb-fix"}): ("6156829b90aaf60312a479f176f417e3fe0f1ca6001c45bcec88657e390b43be", True),
        frozenset({"ptt-lock", "usb-fix"}): ("d95f47a3d580224977bb8b583656e4831d9f1d1994391c3f0f3c45729080c1a8", True),
    },
)
