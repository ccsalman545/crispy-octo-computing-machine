# Architecture

This document explains how the firmware is structured: the system diagram, the
software stack, the boot and initialization flow, the thread model, the memory
map, and the interrupt setup. All diagrams use Mermaid flowcharts and render on
GitHub.

---

## 1. System diagram

```mermaid
flowchart LR
    subgraph BOARD["NUCLEO-H743ZI2 board"]
        subgraph MCU["STM32H743ZIT6"]
            CORE["Cortex-M7 core<br/>I-Cache and D-Cache enabled"]
            ETH["Ethernet MAC (ETH)<br/>RMII mode"]
            DMA["DMA descriptors<br/>RAM_D2 at 0x30040000"]
            U3["USART3 115200 8N1"]
            TIM["TIM6 (HAL time base)"]
            GPIO["GPIO PB0 LED, PC13 button"]
        end
        PHY["LAN8742 PHY<br/>RMII interface"]
        LEDP["LD1 green LED"]
        BTNP["B1 user button"]
        VCP["ST-Link Virtual COM Port"]
    end
    SW["Ethernet switch / router"]
    PC["Host PC<br/>Packet Sender, Tera Term"]
    CORE --> ETH --> DMA
    ETH -->|"RMII: MDC, MDIO, TXD, RXD, CRS_DV, REF_CLK"| PHY
    PHY <-->|"10/100BASE-T"| SW
    SW <-->|"UDP 6000 IPv4/IPv6"| PC
    CORE --> U3 --> VCP -->|"USB"| PC
    CORE --> GPIO
    GPIO --> LEDP
    BTNP --> GPIO
    CORE --> TIM
```

Pin mapping for the RMII interface (from the `.ioc` and `MX_GPIO_Init`):

| Signal | Pin | Signal | Pin |
|:-------|:----|:-------|:----|
| RMII_REF_CLK | PA1 | RMII_TXD0 | PG13 |
| RMII_MDIO | PA2 | RMII_TXD1 | PB13 |
| RMII_CRS_DV | PA7 | RMII_TX_EN | PG11 |
| RMII_MDC | PC1 | RMII_RXD0 | PC4 |
| USART3_TX | PD8 | RMII_RXD1 | PC5 |
| USART3_RX | PD9 | HSE clock | PH0 |

---

## 2. Software stack

```mermaid
flowchart TB
    subgraph APP["Application layer"]
        A1["nx_app_thread_entry()<br/>button polling, debounce, UDP RX"]
        A2["send_udp_message()<br/>allocates, appends, sends"]
        A3["printIPv4() / printIPv6()<br/>console helpers"]
    end
    subgraph NX["NetX Duo 6.2"]
        B1["UDP socket API<br/>nx_udp_socket_create / bind / receive / send"]
        B2["IP layer<br/>IPv4 + IPv6, fragmentation, TTL"]
        B3["ARP, ICMP, ICMPv6, TCP, IPv6 ND"]
        B4["Packet pool<br/>(1536 + NX_PACKET) x 10"]
        B5["nx_stm32_eth_driver<br/>Ethernet interface driver"]
    end
    subgraph TX["ThreadX 6.2"]
        C1["Kernel, scheduler, timers"]
        C2["Byte memory pools<br/>tx_app_byte_pool, nx_app_byte_pool"]
        C3["Application thread<br/>priority 10, stack 2 KB"]
    end
    subgraph HAL["STM32 HAL drivers"]
        D1["stm32h7xx_hal_eth.c<br/>MAC + DMA"]
        D2["stm32h7xx_hal_uart.c"]
        D3["GPIO, RCC, PWR, CORTEX, MPU"]
    end
    subgraph HW["Hardware"]
        E1["STM32H743 Cortex-M7 @ up to 480 MHz"]
        E2["LAN8742 PHY"]
        E3["ST-Link VCP (USART3)"]
        E4["LD1 (PB0), B1 (PC13)"]
    end
    A1 --> B1
    A2 --> B1
    B1 --> B2
    B2 --> B3
    B2 --> B4
    B2 --> B5
    B5 --> D1
    A1 --> C1
    C1 --> C2
    C2 --> B4
    C3 --> C1
    D1 --> E1
    D2 --> E3
    D3 --> E1
    D1 --> E2
```

Key include path: `app_netxduo.h` pulls in `nx_api.h` and
`nx_stm32_eth_driver.h`; `app_azure_rtos.h` pulls in `app_threadx.h` and
`app_netxduo.h`, so the application layer sees the whole stack.

---

## 3. Boot and initialization flow

```mermaid
flowchart TD
    PWR["Power on / reset"] --> RST["Reset_Handler<br/>(startup_stm32h743zitx.s)"]
    RST --> SYSI["SystemInit()<br/>(system_stm32h7xx.c)"]
    SYSI --> MAIN["main() in Core/Src/main.c"]
    MAIN --> MPU["MPU_Config()<br/>region 1: 128 KB non-cacheable<br/>at 0x30040000 for DMA descriptors"]
    MPU --> CACHE["SCB_EnableICache()<br/>SCB_EnableDCache()"]
    CACHE --> HALI["HAL_Init()<br/>HAL time base = TIM6"]
    HALI --> CLK["SystemClock_Config()<br/>HSE bypass, PLL, dividers"]
    CLK --> GPIO["MX_GPIO_Init()<br/>LD1 PB0, LD2 PB7, LD3 PB14, B1 PC13"]
    GPIO --> ETHI["MX_ETH_Init()<br/>MAC 00:80:E1:00:00:00, RMII,<br/>RxBuf 1536, TX checksum + CRC pad"]
    ETHI --> UART["MX_USART3_UART_Init()<br/>115200 8N1, TX/RX FIFO"]
    UART --> TXI["MX_ThreadX_Init()"]
    TXI --> KERN["tx_kernel_enter()<br/>(never returns)"]
    KERN --> DEF["tx_application_define()<br/>in app_azure_rtos.c"]
    DEF --> POOL1["tx_byte_pool_create<br/>tx_app_byte_pool (1 KB)"]
    POOL1 --> APP1["App_ThreadX_Init()"]
    APP1 --> POOL2["tx_byte_pool_create<br/>nx_app_byte_pool (30 KB)"]
    POOL2 --> NXINIT["MX_NetXDuo_Init()<br/>in app_netxduo.c"]
    NXINIT --> SCHED["Scheduler starts the<br/>NetX Duo app thread"]
```

### What `MX_NetXDuo_Init()` does, step by step

```mermaid
flowchart TD
    A["MX_NetXDuo_Init(memory_ptr)"] --> B["nx_system_initialize()"]
    B --> C["Allocate NX_APP_PACKET_POOL_SIZE from byte pool"]
    C --> D["nx_packet_pool_create<br/>payload 1536, 10 packets"]
    D --> E["Allocate 2 KB for the IP helper thread"]
    E --> F["nx_ip_create<br/>IP 192.168.1.111, mask 255.255.255.0,<br/>driver nx_stm32_eth_driver, priority 10"]
    F --> G["Allocate 1024 bytes ARP cache"]
    G --> H["nx_arp_enable"]
    H --> I["nx_icmp_enable"]
    I --> J["nx_tcp_enable"]
    J --> K["nx_udp_enable"]
    K --> L["nxd_ipv6_enable"]
    L --> M["nxd_ipv6_address_set<br/>2600:1702:4eb2:9780::abcd/64 on interface 0"]
    M --> N["nxd_icmp_enable"]
    N --> O["Allocate 2 KB thread stack"]
    O --> P["tx_thread_create<br/>nx_app_thread_entry, priority 10, auto start"]
    P --> Q["Return NX_SUCCESS"]
```

---

## 4. Thread model

The application is single-threaded on top of the ThreadX kernel. The kernel
itself runs a helper thread for the IP instance (priority 10) plus the timer
infrastructure.

| Thread | Created by | Priority | Stack | Entry point |
|:-------|:-----------|:---------|:------|:------------|
| IP helper (inside `NX_IP`) | `nx_ip_create` | 10 | 2 KB | internal NetX Duo code |
| Application thread | `tx_thread_create` | 10 | 2 KB | `nx_app_thread_entry` |

```mermaid
flowchart LR
    subgraph TXK["ThreadX kernel"]
        IPT["IP helper thread (prio 10)"]
        APPT["Application thread (prio 10)"]
        TIMR["ThreadX timer tick<br/>100 ticks per second"]
    end
    APPT -->|"nx_udp_socket_receive"| UDP["UDP socket 6000"]
    APPT -->|"nxd_udp_socket_send"| UDP
    IPT -->|"driver callbacks"| ETH["Ethernet driver"]
    TIMR --> IPT
    TIMR --> APPT
```

Both threads share priority 10 and run round-robin in time-slice-free mode;
the application thread yields with `tx_thread_sleep()` and short blocking calls,
so the IP helper always gets CPU time for incoming traffic.

---

## 5. Memory map

The linker script `STM32H743ZITX_FLASH.ld` targets 2 MB flash and 512 KB of
RAM_D1. The Ethernet DMA descriptors and the NetX Duo packet pool are placed in
RAM_D2 via dedicated sections:

| Region | Address | Size | Contents |
|:-------|:--------|:-----|:---------|
| FLASH | `0x08000000` | 2 MB | Vector table, code, constants |
| RAM_D1 | `0x24000000` | 512 KB | `.data`, `.bss`, stacks, heaps |
| RAM_D2 | `0x30000000` | (section) | `.RxDecripSection`, `.TxDecripSection`, `.NetXPoolSection` |
| Rx DMA descriptors | `0x30040000` | 96 bytes | `DMARxDscrTab[ETH_RX_DESC_CNT]` |
| Tx DMA descriptors | `0x30040060` | 96 bytes | `DMATxDscrTab[ETH_TX_DESC_CNT]` |

```mermaid
flowchart TB
    subgraph F["FLASH 0x08000000, 2 MB"]
        F1["Vector table + code + rodata"]
    end
    subgraph D1["RAM_D1 0x24000000, 512 KB"]
        D1A[".data / .bss / stacks"]
    end
    subgraph D2["RAM_D2 0x30000000 (SRAM)"]
        D2A["0x30040000 Rx descriptors<br/>MPU region 1: 128 KB, TEX1,<br/>non-cacheable, non-bufferable"]
        D2B["0x30040060 Tx descriptors"]
        D2C[".NetXPoolSection<br/>packet pool + pools"]
    end
    F --> D1
    F --> D2
```

Why non-cacheable? The DMA engine writes received Ethernet frames into memory.
If the CPU's D-Cache were enabled for that region, the CPU could read stale
cached data. The MPU marks the descriptor region (and the `.NetXPoolSection` is
handled by the `nx_stm32_eth_driver` with cache maintenance) so DMA and CPU see
consistent data.

Static memory pools defined in `app_azure_rtos.c`:

* `tx_byte_pool_buffer[TX_APP_MEM_POOL_SIZE]`, `TX_APP_MEM_POOL_SIZE = 1024` bytes.
* `nx_byte_pool_buffer[NX_APP_MEM_POOL_SIZE]`, `NX_APP_MEM_POOL_SIZE = 30 KB`,
  placed in the `.NetXPoolSection` (RAM_D2).

---

## 6. Interrupts and timing

| Source | Role |
|:-------|:-----|
| ETH IRQ | Ethernet MAC interrupt; the NetX Duo driver defers packet processing to the IP helper thread (`NX_DRIVER_DEFERRED_PROCESSING`) |
| TIM6 | HAL time base: `HAL_TIM_PeriodElapsedCallback` calls `HAL_IncTick()` |
| SysTick | ThreadX timer tick (100 ticks per second) |
| PendSV / SVCall | ThreadX context switching |

Timing constants used by the application thread:

| Constant | Value | Meaning |
|:---------|:------|:--------|
| `NX_IP_PERIODIC_RATE` | 100 ticks/s | one tick = 10 ms |
| `SEND_SLEEP_TICKS` | `NX_IP_PERIODIC_RATE / 5` = 20 ticks | button report every ~200 ms |
| receive timeout | 1 tick | non-blocking-ish UDP receive poll |

---

## 7. Where the code lives

| Concern | File |
|:--------|:-----|
| Hardware init (MPU, clock, ETH, USART3, GPIO) | `Core/Src/main.c` |
| ThreadX kernel entry | `Core/Src/app_threadx.c` |
| Memory pools and application bootstrap | `AZURE_RTOS/App/app_azure_rtos.c` |
| Network stack init and UDP application thread | `NetXDuo/App/app_netxduo.c` |
| Network constants (IP, mask, sizes) | `NetXDuo/App/app_netxduo.h` |
| NetX Duo build options (IPv6 enabled) | `NetXDuo/App/nx_user.h` |
| Pool sizes | `AZURE_RTOS/App/app_azure_rtos_config.h` |
| Linker layout | `STM32H743ZITX_FLASH.ld` |

Continue to [BUILDING.md](BUILDING.md) to compile and flash, or
[CONFIGURATION.md](CONFIGURATION.md) to tune every setting.
