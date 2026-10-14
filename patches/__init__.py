from .ptt_lock import PATCH as PTT_LOCK
from .usb_fix import PATCH as USB_FIX

ALL = {p.id: p for p in (PTT_LOCK, USB_FIX)}
