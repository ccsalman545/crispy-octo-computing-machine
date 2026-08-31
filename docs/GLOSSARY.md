# Glossary

Terms used throughout the repository, explained in the context of this
firmware.

| Term | Meaning |
|:-----|:--------|
| ARP | Address Resolution Protocol; maps IPv4 addresses to MAC addresses on a LAN. Enabled via `nx_arp_enable` |
| Azure RTOS | Microsoft's RTOS family; ThreadX (kernel) + NetX Duo (network) used here |
| B1 | the user button on the Nucleo boards, connected to PC13 |
| BSP | Board Support Package; the HAL driver layer plus board components (e.g. LAN8742 driver) |
| byte pool | ThreadX memory pool that allocates variable-size blocks (`tx_byte_allocate`) |
| CRS_DV | RMII signal "Carrier Sense / Data Valid", input to the MAC |
| D-Cache | data cache on the Cortex-M7; disabled for the Ethernet descriptor region via MPU |
| DAD | Duplicate Address Detection; IPv6 check for address conflicts; disabled in `nx_user.h` |
| DHCP | Dynamic Host Configuration Protocol; not used (static IP), see EXTENDING.md |
| DMA | Direct Memory Access; the ETH uses dedicated descriptors for RX/TX frames |
| dual stack | running IPv4 and IPv6 simultaneously on one interface |
| EEMBC / CMSIS | not used here; see license file for included components |
| ETH | the Ethernet peripheral (MAC + DMA) of the STM32H743 |
| HAL | Hardware Abstraction Layer, ST's driver layer (`stm32h7xx_hal_*.c`) |
| HSE | High Speed External clock; 8 MHz bypass source on PH0 in this project |
| ICMP | Internet Control Message Protocol (IPv4 ping); enabled via `nx_icmp_enable` |
| ICMPv6 | ICMP for IPv6, also carries neighbor discovery; enabled via `nxd_icmp_enable` |
| IP helper thread | internal NetX Duo thread that processes received packets (deferred processing) |
| IPv4 | Internet Protocol version 4; static 192.168.1.111/24 here |
| IPv6 | Internet Protocol version 6; static 2600:1702:4eb2:9780::abcd/64 here |
| LAN8742 | the Ethernet PHY chip on the Nucleo-144 boards (RMII) |
| LD1 / LD2 / LD3 | user LEDs on the Nucleo: green PB0, blue PB7, red PB14 |
| link-local | IPv6 address valid only on the local link (FE80::/10), auto-generated |
| MAC | Media Access Control address of the Ethernet interface (00:80:E1:00:00:00) |
| MDC / MDIO | management interface between MAC and PHY |
| MPU | Memory Protection Unit; configures cacheability/access for memory regions |
| ND | Neighbor Discovery; IPv6 equivalent of ARP |
| NetX Duo | Microsoft's dual-stack TCP/IP stack that runs on ThreadX |
| Nucleo-144 | the 144-pin Arduino-compatible STM32 evaluation board family |
| NXD_ADDRESS | NetX Duo structure holding either an IPv4 or an IPv6 address |
| NX_PACKET | NetX Duo packet structure; payload follows the header |
| Packet Sender | free UDP/TCP test tool used in the README screenshots |
| packet pool | NetX Duo pool of preallocated packet buffers (10 x 1536 here) |
| PHY | physical layer transceiver (LAN8742) converting MAC frames to line signals |
| priority | ThreadX scheduling level; lower number = higher priority |
| printf retarget | `__io_putchar` redirects `printf` to USART3 |
| RAM_D1 / RAM_D2 | STM32H743 RAM regions; D1 is cached AXI SRAM, D2 is DMA-friendly SRAM |
| RMII | Reduced Media Independent Interface; 2-bit data path, 50 MHz reference clock |
| RTOS | Real-Time Operating System; ThreadX here |
| RX / TX | receive / transmit |
| socket | UDP endpoint abstraction (NX_UDP_SOCKET) |
| ST-Link | on-board debugger/programmer and Virtual COM port bridge |
| STM32CubeMX | ST's code generator that produced the `.ioc` project |
| SYSCLK | system clock, 400 MHz in this configuration (see SYSTEM_CLOCK.md) |
| TCP | Transmission Control Protocol; enabled but no socket used |
| ThreadX | Azure RTOS kernel; priorities, threads, byte pools, timers |
| tick | ThreadX time unit; 100 ticks per second here (10 ms) |
| TTL | Time To Live; IP hop limit (`NX_IP_TIME_TO_LIVE`) |
| UART | Universal Asynchronous Receiver/Transmitter; USART3 is the console |
| UDP | User Datagram Protocol; the application protocol (port 6000/55100) |
| VCP | Virtual COM Port (ST-Link); the serial console interface |
