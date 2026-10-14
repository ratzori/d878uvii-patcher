# d878uvii-patcher

## Read this first

Whether to use this project is your own decision, and so is the outcome.
If you patch and flash your radio, you accept the risk that it may not work
afterwards. The software comes as is, without any warranty (see
[LICENSE](LICENSE)).

The patches change only the main firmware. The radio's own firmware update
mode (the bootloader) is separate and isn't modified, so you should be able to
flash the official firmware back the same way you flashed the patched one.
Before you flash, keep the official firmware files and make sure you know how
to put the radio into update mode and flash them. Save your codeplug with the
CPS as well.

The patched firmware stays compatible with the official firmware version it
was made from. Read and write the codeplug with the CPS version that matches
that stock firmware version. If your radio already runs that same official
version, you don't need to write your settings back with the CPS after
flashing the patched firmware.

Modified firmware may void your warranty. You are responsible for operating
your radio within your licence and local rules.

## About

Optional fixes for the AnyTone AT-D878UVII firmware. The supported firmware
versions are listed in [FIRMWARE.md](FIRMWARE.md). You pick which patches to
apply; the patcher writes a new firmware set that you flash the same way as an
official update.

This project is not affiliated with or endorsed by AnyTone. It contains no
AnyTone firmware or code: you download the official firmware yourself, and the
patcher modifies your copy locally.

## Patches

### `--ptt-lock`: PTT obeys the key lock

In stock firmware the key lock never blocks PTT. With this patch, when the key
lock is on **and** *Side Key Lock* is ticked in the CPS lock settings, pressing
PTT doesn't transmit. The radio shows "Key Locked" once per press instead.
With Side Key Lock not ticked, or the key lock off, PTT works as in stock.

Notes:
- Only *Side Key Lock* is checked. *Forced Key Lock* on its own doesn't block PTT.
- VOX works as in stock firmware.

Known issues:
- If you press Menu and then PTT while the keys are locked, the radio shows
  "Push * To Unlock Key" instead of "Key Locked", though with the same "!"
  icon as "Key Locked". This is only the message text and is harmless: PTT
  is still blocked.

### `--usb-fix`: USB serial port works after the boot password

In stock firmware, if a boot password is set, the PC loses the radio's USB
serial port after the password is entered. The port is gone or doesn't
respond, so the CPS can't read or write the radio until it's started again
without the password. With this patch the radio briefly disconnects from USB
and reconnects after the password, so the PC detects it again. This adds about
one second to start-up when the password is used. Start-up without a password
is unchanged.

## Supported firmware

[FIRMWARE.md](FIRMWARE.md) lists each supported firmware version with its
stock SHA-256, the patches available for it, the expected output SHA-256s
and which outputs have been tested on a radio.

## Requirements

- Python 3.8 or later
- [Keystone](https://github.com/keystone-engine/keystone)
  (`keystone-engine`), the assembler that turns the patches' assembly code
  into machine code

Install with:

    pip install -r requirements.txt

The patcher has been tested only on Linux, both directly and with Docker.
Being plain Python, it should also work on Windows and macOS, but that hasn't
been tried.

## Usage

Get the official D878UVII firmware of a supported version from AnyTone (see
[FIRMWARE.md](FIRMWARE.md)). You need its three files, `.CDD`, `.spi` and
`.CDI`, in the same folder. The patcher identifies the version by the
`.CDD`'s SHA-256. Anything else is refused with an error that lists the
supported files, including other firmware versions and files that have
already been patched. `--list` shows which versions each patch is available
for.

Then:

    python3 d878uvii_patcher.py --list
    python3 d878uvii_patcher.py path/to/FIRMWARE.CDD --ptt-lock --usb-fix
    python3 d878uvii_patcher.py path/to/FIRMWARE.CDD --all --out mydir

The output goes to `./patched` by default. Its name is the input name with
the patches added, for example `FIRMWARE_PTT-LOCK_USB-FIX.CDD` with its `.spi`
and `.CDI`. The input files are never modified.

### Docker

Run these in the folder that has the stock firmware files:

```bash
# Build the image (in this repository's folder)
docker build -t d878uvii-patcher .

# List the patches
docker run --rm d878uvii-patcher --list

# Patch; the output goes to ./patched in the current folder
docker run --rm --user "$(id -u):$(id -g)" -v "$PWD":/work d878uvii-patcher FIRMWARE.CDD --all
```

## Flashing

This project doesn't flash radios. AnyTone's own tools are for Windows only;
on Linux, [anytone-flash-tools](https://github.com/reald/anytone-flash-tools)
is one example of a tool that can flash the firmware set.

## How it works

Each patch adds a small piece of its own code after the end of the firmware
and redirects one or two instructions in the firmware to it. Patches don't
overlap, so any combination can be applied, and each patch's bytes are the
same whichever other patches are selected.

The patch logic and the firmware details are kept apart:

- `patches/` has one file per patch. Its assembly code uses names, not
  addresses, and it lists the names it needs.
- `firmware/` has one file per supported stock firmware: its SHA-256, the
  values for those names, and the expected output SHA-256s.

A patch is available for a firmware version when that version's file defines
every name the patch needs. Supporting a new version means adding a file in
`firmware/` with values found and tested for that version, and listing it in
[FIRMWARE.md](FIRMWARE.md). A patch whose logic must differ in a version can
choose its code by those values.

## Tests

The tests need the stock firmware, which isn't in this repository:

    D878UVII_STOCK=path/to/FIRMWARE.CDD python3 -m unittest discover tests

`D878UVII_STOCK` can also be a folder; every supported `.CDD` in it is tested.
Without it, only the checks that don't need firmware run.

## Licence

d878uvii-patcher - optional patches for the AnyTone D878UVII firmware.
Copyright (C) 2026 Tommi Tauriainen, OH8DMM.

Released under the MIT License, see [LICENSE](LICENSE).
