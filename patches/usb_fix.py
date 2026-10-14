"""USB fix: reconnect USB cleanly when start-up restarts it (boot password)."""
from .base import Patch, Placed, hi, lo

# The firmware version file gives these (see firmware/).
NEEDS = (
    "USB_START",         # starts the USB device
    "USB_STOP",          # disconnects from USB, then waits 1 s
    "PASSWORD_OK",       # set once the boot password has been accepted
    "KEY_COMBO_MODE",    # set when started with a key combination that also starts USB
    "USB_HOOK_MAIN",     # USB start in the normal start-up
    "USB_HOOK_COMBO",    # USB start in the key-combination start-up
    "USB_FIX_CODE",      # free space for this patch's code
)


def place(s):
    entry_combo = s.USB_FIX_CODE + 14  # second entry point: after entry_main's 5 instructions
    return Placed(
        code_addr=s.USB_FIX_CODE,
        code=f"""
        push {{r4, lr}}
        movw r0, #{lo(s.KEY_COMBO_MODE)}
        movt r0, #{hi(s.KEY_COMBO_MODE)}
        ldrb r0, [r0]
        b    check_password
    entry_combo:
        push {{r4, lr}}
        movs r0, #0
    check_password:
        movw r1, #{lo(s.PASSWORD_OK)}
        movt r1, #{hi(s.PASSWORD_OK)}
        ldrb r1, [r1]
        orrs r0, r1
        cbz  r0, start
        bl   #{s.USB_STOP}
    start:
        bl   #{s.USB_START}
        pop  {{r4, pc}}
        """,
        hooks=[(s.USB_HOOK_MAIN, f"bl #{s.USB_FIX_CODE}"), (s.USB_HOOK_COMBO, f"bl #{entry_combo}")],
        entries={entry_combo: bytes.fromhex("10b5")},  # push {r4, lr}
    )


PATCH = Patch(
    id="usb-fix",
    title="USB serial port works after the boot password",
    needs=NEEDS,
    place=place,
)
