# Debugging

Practical debugging workflows for this firmware with STM32CubeIDE and the
on-board ST-Link: running the debugger, using breakpoints and watches,
analyzing a hard fault, and inspecting the network state.

---

## 1. Debug session basics

```mermaid
flowchart TD
    A["Connect board via USB"] --> B["Project > Debug As ><br/>STM32 ARM C/C++ Application"]
    B --> C["ST-Link flashes the ELF"]
    C --> D["Execution stops at main()<br/>breakpoint"]
    D --> E["Resume (F8)"]
    E --> F["ThreadX starts, app thread runs"]
    F --> G{"Need to break?"}
    G -->|"yes"| H["Suspend (F7) or hit a<br/>breakpoint"]
    G -->|"no"| I["Watch console output in<br/>the built-in terminal"]
```

Tip: while suspended in the debugger, the target is halted and Ethernet RX
stops. Long suspensions can make the PC-side tools time out; keep sessions
short or disable the `main` breakpoint after first entry.

---

## 2. Useful breakpoints

| Breakpoint | File / function | What you learn |
|:-----------|:----------------|:---------------|
| `main()` | `Core/Src/main.c` | firmware entered |
| `nx_app_thread_entry` | `NetXDuo/App/app_netxduo.c` | app thread started |
| `send_udp_message` | `NetXDuo/App/app_netxduo.c` | button report path |
| `nx_udp_socket_receive` return | `NetXDuo/App/app_netxduo.c` line 373 | inbound packet handling |
| `Error_Handler()` | `Core/Src/main.c` | any init failure |
| `HAL_TIM_PeriodElapsedCallback` | `Core/Src/main.c` | HAL time base tick |

```mermaid
flowchart TD
    A["Set breakpoints"] --> B["Resume firmware"]
    B --> C{"Which breakpoint<br/>hit first?"}
    C -->|"main"| D["Peripheral init in progress"]
    C -->|"nx_app_thread_entry"| E["Stack + network up"]
    C -->|"Error_Handler"| F["An init call returned<br/>an error code"]
    D --> G["Step through MX_* init<br/>functions"]
    E --> H["Inspect NxAppPool /<br/>NetXDuoEthIpInstance"]
    F --> I["Check return value of the<br/>last HAL / NetX call"]
```

---

## 3. Watching the network state

While halted, use the Variables or Expressions view to inspect:

| Expression | Type | Meaning |
|:-----------|:-----|:--------|
| `NetXDuoEthIpInstance.nx_ip_interface[0].nx_interface_ip_address` | ULONG | IPv4 in network order |
| `NetXDuoEthIpInstance.nx_ip_interface[0].nx_interface_ip_network_mask` | ULONG | netmask |
| `NetXDuoEthIpInstance.nx_ip_interface[0].nx_interface_ipv6_address[0].nxd_ipv6_address` | NXD_ADDRESS | configured IPv6 |
| `NxAppPool.nx_packet_pool_available` | ULONG | free packets |
| `NxAppPool.nx_packet_pool_total` | ULONG | pool size |
| `UDPSocket.nx_udp_socket_port` | UINT | bound port (6000) |
| `UDPSocket.nx_udp_socket_receive_count` | ULONG | received datagrams |

```mermaid
flowchart TD
    A["Halt at nx_app_thread_entry"] --> B{"pool available =<br/>pool total?"}
    B -->|"yes"| C["Packet pool healthy"]
    B -->|"no"| D["Packet leak or pool<br/>exhaustion"]
    C --> E{"UDPSocket port = 6000?"}
    E -->|"yes"| F["Socket bound correctly"]
    E -->|"no"| G["Check nx_udp_socket_bind<br/>return value"]
    D --> H["Review nx_packet_release<br/>on every path"]
    G --> H
```

---

## 4. Hard fault analysis

When the firmware crashes (e.g. stack overflow, null pointer), the debugger
stops in `HardFault_Handler`. Recovery steps:

```mermaid
flowchart TD
    A["Execution stops in<br/>HardFault_Handler"] --> B["Open the Call Stack view"]
    B --> C{"Which frame is<br/>highlighted?"}
    C -->|"application frame"| D["Step to the faulting<br/>instruction"]
    C -->|"unknown / corrupted"| E["Likely stack overflow:<br/>check 2 KB thread stacks"]
    D --> F["Look at the faulting<br/>address and registers"]
    F --> G{"Address looks like a<br/>bad pointer?"}
    G -->|"yes"| H["Check packet buffer bounds<br/>(data_buffer is 512 B)"]
    G -->|"no"| I["Check buffer overflow in<br/>snprintf / memcpy"]
    E --> J["Increase stack sizes in<br/>app_netxduo.h and<br/>NX_APP_MEM_POOL_SIZE"]
    H --> K["Fix and reflash"]
    I --> K
    J --> K
```

Common hard fault sources in this code:

* `data_buffer[512]` overflow if a received datagram is larger than 512 bytes;
  the code clamps `bytes_read` to the buffer, but keep sends below 512 bytes.
* Stack overflow: both threads use 2 KB; `printf` uses the retargeted UART and
  can consume stack.
* Dereferencing a null `NX_PACKET *` when `nx_udp_socket_receive` failed.

---

## 5. Serial and SWV output

The debug console is the ST-Link Virtual COM port:

```mermaid
flowchart TD
    A["Open terminal in STM32CubeIDE<br/>(or Tera Term / PuTTY)"] --> B{"COM port selected?"}
    B -->|"yes"| C{"115200 8N1 set?"}
    C -->|"yes"| D["Console shows boot banner<br/>and UDP activity"]
    C -->|"no"| E["Set baud 115200,<br/>8 data, no parity, 1 stop"]
    B -->|"no"| F["Find the ST-Link VCP<br/>COM port in the OS"]
```

Note: on the H7 with ST-Link, SWO/ITM trace support is limited; the Virtual
COM port is the primary debug output, and `printf` retargets to USART3.

---

## 6. Measuring timing

| Goal | Method |
|:-----|:-------|
| Button report cadence | set a breakpoint in `send_udp_message`, read the elapsed time between hits |
| Receive latency | breakpoints on packet receive, compare timestamps in the console |
| Pool pressure | watch `NxAppPool.nx_packet_pool_available` while sending traffic |

```mermaid
flowchart LR
    BP["Breakpoint in send_udp_message"] --> T1["Note tick 1"]
    BP --> T2["Note tick 2"]
    T1 --> D["Delta = report interval<br/>should be ~200 ms"]
    T2 --> D
```

Related: [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for behavior fixes,
[TESTING.md](TESTING.md) for the functional test matrix.
