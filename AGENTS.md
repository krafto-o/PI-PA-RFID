# AGENTS.md

## Project overview

RFID door lock controller for Arduino Uno using MFRC522 reader. Reads card UIDs and triggers a relay on match.

## Build & commands

- **Build:** `pio run`
- **Upload to board:** `pio run --target upload`
- **Serial monitor:** `pio device monitor`
- **Clean:** `pio run --target clean`
- **Install deps:** `pio pkg install` (runs automatically on build)

## Architecture

- **Entry point:** `src/rfid_code.cpp`
- **Config:** `platformio.ini` — single env `uno`, atmelavr platform, Arduino framework
- **Library dep:** `miguelbalboa/MFRC522@^1.4.12` (managed by PlatformIO, stored in `.pio/`)
- **`archivos/`** — reference/legacy code only, not part of the build. Contains an older multi-user version (`Arduino P40 Home_123124.cpp`) and an unrelated Python tkinter app

## Hardware pin mapping

| Pin | Function |
|-----|----------|
| 9   | MFRC522 RST |
| 10  | MFRC522 SS (SPI) |
| 8   | Relay output (active-HIGH logic) |

## Key details

- Authorized UID is hardcoded as a byte array in `src/rfdi_code.cpp`; update `tarjetaAutorizada[4]` to change access
- The reference version in `archivos/` supports multiple users and adds buzzer feedback on pin 8 — the main source does not
- Relay logic in `src/rfdi_code.cpp` has inverted comments vs. code: `digitalWrite(RELAY_PIN, HIGH)` in setup is commented as "apagado" (off), but the access-grant path also writes HIGH — review intended relay active state before modifying
- No unit tests; `test/` is default PlatformIO placeholder

