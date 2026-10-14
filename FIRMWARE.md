# Supported firmware

The patcher accepts only the unmodified official firmware listed here. It
identifies the version by the `.CDD`'s SHA-256 and refuses anything else,
including other versions and files that have already been patched.

Read and write the codeplug with the CPS version that matches the stock
firmware version you patch.

"Tested" means that exact output image was flashed and used on a D878UVII.
The patcher prints the output's SHA-256 and tells you whether it's one of the
tested images.

## V3.06 (20250123)

Stock files: `D878UVII_V3.06_20250123.CDD`, `.spi` and `.CDI`.
The `.CDD` SHA-256 is:

    0973126fc33fda1d734dbc064852648710de52f44c2bc7df07bc9fd4272cfef8

| Patches | Output `.CDD` SHA-256 | Tested on a radio |
|---|---|---|
| `--ptt-lock` | `bc2b34657ebb111ed9ead81fa821ff3193fb0fd59d57c0e88bf7f5713898cab1` | yes |
| `--usb-fix` | `6156829b90aaf60312a479f176f417e3fe0f1ca6001c45bcec88657e390b43be` | yes |
| `--ptt-lock --usb-fix` | `64223c63d1829135ec92d5ce8c2fba425fb52a915d6742899885629d1adc0316` | yes |
