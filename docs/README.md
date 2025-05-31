# Scanner Controller Documentation

This directory contains documentation for the Scanner Controller project.

## Contents

- [Directory Structure](directory_structure.md) - Overview of the project organization
- [Setup Instructions](../setup_instructions.md) - How to set up the project

## Scanner Models

### Uniden BC125AT

The BC125AT is a handheld scanner that covers the 25-512 MHz and 758-960 MHz ranges, with features including:

- Close Call RF capture technology
- PC programmable
- Compact size

The protocol documentation is available in [manuals/BC125AT_Remote_Protocol.txt](../manuals/BC125AT_Remote_Protocol.txt).

### Uniden BCD325P2

The BCD325P2 is a handheld scanner with TrunkTracker V technology, covering:

- 25-1300 MHz frequency range
- Location-based scanning
- Digital decoding

The protocol documentation is available in [manuals/BCD325P2_Remote_Protocol_ver_1_02.txt](../manuals/BCD325P2_Remote_Protocol_ver_1_02.txt).

## Using the Application

For detailed usage instructions, see the main [README.md](../README.md) file.

## Development

Documentation for developers:

- Adding a new scanner model requires implementing an adapter in the `adapters/` directory
- Command libraries define how to communicate with each scanner model
- The GUI can be extended with new components in the `scanner_gui/gui/` directory
