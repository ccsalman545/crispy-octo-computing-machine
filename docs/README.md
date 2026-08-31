# Documentation index

All documentation for the Dual IPv4 and IPv6 UDP with NetX Duo on NUCLEO-H743
project. Every guide uses Mermaid flowcharts that render on GitHub.

| Guide | Purpose |
|:------|:--------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System diagram, software stack, boot flow, thread model, memory map, interrupts |
| [BUILDING.md](BUILDING.md) | Import into STM32CubeIDE, build, flash, debug, CLI build, CubeMX regeneration |
| [CONFIGURATION.md](CONFIGURATION.md) | Every configurable parameter with exact file and line references |
| [PROTOCOL.md](PROTOCOL.md) | UDP ports, message grammar, decision flowcharts, Packet Sender setup |
| [CODE_WALKTHROUGH.md](CODE_WALKTHROUGH.md) | Annotated tour of main.c, app_azure_rtos.c, app_netxduo.c |
| [TESTING.md](TESTING.md) | Repeatable test matrix with expected results |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Common problems, root causes, and fixes |

Suggested reading order for new contributors:

```mermaid
flowchart LR
    A["README.md"] --> B["ARCHITECTURE.md"]
    B --> C["CODE_WALKTHROUGH.md"]
    C --> D["CONFIGURATION.md"]
    D --> E["BUILDING.md"]
    E --> F["TESTING.md"]
    F --> G["PROTOCOL.md"]
    G --> H["TROUBLESHOOTING.md"]
```

Start with the README for the one-screen overview, then go deep in the order
above.
