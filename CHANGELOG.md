# Changelog

All notable changes to this project are documented in this file. The format is
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

* No unreleased changes yet.

## [1.0.0] - 2026-08-31

### Added

* Initial firmware example: Dual IPv4 and IPv6 UDP with NetX Duo on
  NUCLEO-H743 (based on the STMicroelectronics STM32-Hotspot example).
* Azure RTOS ThreadX 6.2 + NetX Duo 6.2 integration generated with
  STM32CubeMX 6.15.0 / X-CUBE-AZRTOS-H7 3.1.0.
* UDP server socket bound to port 6000, listening on IPv4 and IPv6.
* User LED (LD1, PB0) remote control over UDP:
  `LED ON`, `LED_ON`, `LEDON`, `ON` and `LED OFF`, `LED_OFF`, `LEDOFF`, `OFF`
  (case-insensitive matching).
* User button (B1, PC13) polling with software debounce and UDP reporting of
  `BUTTON:0` / `BUTTON:1` to a configurable host (default 192.168.1.160:55100).
* Serial debug console on the ST-Link Virtual COM port (USART3, 115200 8N1):
  prints IPv4 and IPv6 addresses, port binding, sent and received payloads.
* Static IPv4 (192.168.1.111/24) and static global IPv6
  (2600:1702:4eb2:9780::abcd/64) addressing.
* Full documentation in `docs/` with Mermaid flowcharts:
  architecture, building, configuration, protocol, code walkthrough, testing,
  and troubleshooting.
* Contributing guide, issue and pull request templates, changelog, and
  `.gitignore` for build artifacts.

[Unreleased]: https://github.com/ccsalman545/crispy-octo-computing-machine
[1.0.0]: https://github.com/ccsalman545/crispy-octo-computing-machine
