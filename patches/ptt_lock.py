"""PTT lock: ignore PTT while the key lock is on and Side Key Lock is enabled."""
from .base import Patch, Placed, hi, lo

# The firmware version file gives these (see firmware/).
NEEDS = (
    "STARTED",           # 1 once start-up has finished
    "SETTINGS",          # general settings from the codeplug
    "KEYLOCK_ON",        #   offset: key lock currently engaged
    "LANGUAGE",          #   offset: display language
    "LOCK_OPTIONS",      #   offset: lock options
    "SIDE_KEY_LOCK",     #   lock options bit: Side Key Lock
    "BUTTONS",           # button-state byte
    "PTT",               #   bit: PTT
    "KEY_LOCKED_SHOWN",  #   bit unused by stock: message already shown for this press
    "SHOW_MESSAGE",      # shows a status message
    "MESSAGE_TEXT",      #   text it shows, set by the caller
    "MSG_KEY_LOCKED",    #   message: "Key Locked"
    "KEY_LOCKED_TEXT",   #   its text, one 8-byte entry per language
    "PTT_HOOK",          # where the button-state byte is stored
    "PTT_RESUME",        # the instruction after it
    "PTT_LOCK_CODE",     # free space for this patch's code
)


def place(s):
    return Placed(
        code_addr=s.PTT_LOCK_CODE,
        code=f"""
        movw r3, #{lo(s.STARTED)}
        movt r3, #{hi(s.STARTED)}
        ldrb r3, [r3]
        cmp  r3, #1
        bne  store
        movw r3, #{lo(s.SETTINGS)}
        movt r3, #{hi(s.SETTINGS)}
        ldrb.w r3, [r3, #{s.KEYLOCK_ON}]
        cbz  r3, store
        movw r3, #{lo(s.SETTINGS)}
        movt r3, #{hi(s.SETTINGS)}
        ldrb.w r3, [r3, #{s.LOCK_OPTIONS}]
        and  r3, r3, #{s.SIDE_KEY_LOCK}
        cbz  r3, store
        mov  r2, r0
        and  r2, r2, #{s.PTT}
        bic  r0, r0, #{s.PTT}
        cbz  r2, store
        movw r1, #{lo(s.BUTTONS)}
        movt r1, #{hi(s.BUTTONS)}
        ldrb r3, [r1]
        and  r3, r3, #{s.KEY_LOCKED_SHOWN}
        cbnz r3, relatch
        push {{r0, r4, lr}}
        movw r3, #{lo(s.SETTINGS)}
        movt r3, #{hi(s.SETTINGS)}
        ldrb r3, [r3, #{s.LANGUAGE}]
        movw r2, #{lo(s.KEY_LOCKED_TEXT)}
        movt r2, #{hi(s.KEY_LOCKED_TEXT)}
        ldr.w r2, [r2, r3, lsl #3]
        movw r3, #{lo(s.MESSAGE_TEXT)}
        movt r3, #{hi(s.MESSAGE_TEXT)}
        str  r2, [r3]
        movs r0, #{s.MSG_KEY_LOCKED}
        bl   {s.SHOW_MESSAGE}
        pop  {{r0, r4, lr}}
    relatch:
        orr  r0, r0, #{s.KEY_LOCKED_SHOWN}
    store:
        movw r1, #{lo(s.BUTTONS)}
        movt r1, #{hi(s.BUTTONS)}
        strb r0, [r1]
        b.w  #{s.PTT_RESUME}
        """,
        hooks=[(s.PTT_HOOK, f"b.w #{s.PTT_LOCK_CODE}")],
    )


PATCH = Patch(
    id="ptt-lock",
    title="PTT is ignored while the key lock is on (Side Key Lock)",
    needs=NEEDS,
    place=place,
)
