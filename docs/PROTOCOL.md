# UDP protocol reference

The board is a UDP endpoint on the local network. It exposes one server socket
(listening on both IPv4 and IPv6) and one client socket for button reports.

---

## 1. Port summary

| Socket | Role | Port | Payload direction |
|:-------|:-----|:-----|:------------------|
| `UDPSocket` | server, bound in `nx_app_thread_entry` | **6000** | PC to board (commands), board echoes to console |
| `UDPSocket` | client, used by `send_udp_message` | **55100** (destination) | board to PC (button state) |

Both roles share the single `UDPSocket` instance created at
`app_netxduo.c` line 318.

```mermaid
flowchart LR
    PC["Host PC"] -->|"UDP packet to 192.168.1.111:6000<br/>or 2600:1702:4eb2:9780::abcd:6000"| BOARD["NUCLEO-H743 board"]
    BOARD -->|"BUTTON:0 / BUTTON:1<br/>to 192.168.1.160:55100"| PC
```

---

## 2. Outbound messages: button state

The application thread polls the user button B1 (PC13, active low) every loop
iteration and reports its state roughly every 200 ms.

| Payload | Meaning |
|:--------|:--------|
| `BUTTON:1` | button released (PC13 reads high) |
| `BUTTON:0` | button pressed (PC13 reads low) |

### Outbound flow

```mermaid
flowchart TD
    START["Loop iteration"] --> READ["HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_13)"]
    READ --> CMP{"current == last_button_state?"}
    CMP -->|"yes"| RESET["stable_count = 0"]
    CMP -->|"no"| INC["stable_count++"]
    INC --> CHK{"stable_count >= 2?"}
    CHK -->|"no"| SEND1["Report current last_button_state"]
    CHK -->|"yes"| ACC["last_button_state = current<br/>stable_count = 0"]
    ACC --> SEND1
    RESET --> SEND1
    SEND1["snprintf BUTTON:%d<br/>0 = pressed, 1 = released"]
    SEND1 --> ALLOC["nx_packet_allocate(NX_UDP_PACKET)"]
    ALLOC --> APPEND["nx_packet_data_append(message)"]
    APPEND --> SEND2["nxd_udp_socket_send to<br/>192.168.1.160:55100"]
    SEND2 --> FAIL{"send failed?"}
    FAIL -->|"yes"| REL["nx_packet_release + return"]
    FAIL -->|"no"| CON["Console: Sent: BUTTON:x"]
    REL --> SLEEP["tx_thread_sleep(20 ticks = 200 ms)"]
    CON --> SLEEP
    SLEEP --> RX["Continue to UDP receive poll"]
```

The `BUTTON:0` / `BUTTON:1` framing is plain ASCII text with no terminator;
receivers may treat the whole datagram as the message. A netcat listener:

```bash
nc -u -l 55100
```

Or in Packet Sender: switch to **Server** mode, bind UDP port 55100, and watch
the incoming pane.

---

## 3. Inbound messages: LED commands

Every received datagram on port 6000 is printed to the serial console. Then the
parser tries to classify it:

| Payload pattern | LED LD1 (PB0) |
|:----------------|:--------------|
| contains `LED` (any case) and contains `ON`, `on`, or `On` | SET (on) |
| contains `LED` (any case) and contains `OFF`, `off`, or `Off` (but no ON variant) | RESET (off) |
| contains `LED` but neither ON nor OFF variant | unchanged, console message |
| exactly `ON` or `on` | SET (on) |
| exactly `OFF` or `off` | RESET (off) |
| anything else | unchanged, payload echoed to console |

### Inbound decision flowchart

```mermaid
flowchart TD
    RX["Packet received on port 6000"] --> RETR["nx_packet_data_retrieve into buffer"]
    RETR --> NUL["Null-terminate, strip trailing CR/LF"]
    NUL --> PRINT["Console: echo raw payload"]
    PRINT --> HASLED{"strstr(data, LED)<br/>or strstr(data, led)?"}
    HASLED -->|"yes"| ONCHK{"strstr ON, on, or On?"}
    ONCHK -->|"yes"| LON["HAL_GPIO_WritePin PB0 SET<br/>led_state = 1"]
    ONCHK -->|"no"| OFFCHK{"strstr OFF, off, or Off?"}
    OFFCHK -->|"yes"| LOFF["HAL_GPIO_WritePin PB0 RESET<br/>led_state = 0"]
    OFFCHK -->|"no"| UNK["Console: LED command not recognized"]
    HASLED -->|"no"| BARE{"strcmp ON / on?"}
    BARE -->|"yes"| LON
    BARE -->|"no"| BARE2{"strcmp OFF / off?"}
    BARE2 -->|"yes"| LOFF
    BARE2 -->|"no"| IGN["Ignore (already echoed)"]
    LON --> DONE["nx_packet_release"]
    LOFF --> DONE
    UNK --> DONE
    IGN --> DONE
    DONE --> LOOP["Back to loop: button poll + receive"]
```

Examples that work:

```
LED ON
led on
LED_ON
LEDON
ON
on

LED OFF
led off
LED_OFF
LEDOFF
OFF
off
```

The parser is intentionally lenient (substring matching). `LED ON` and
`LED_ON` and `LEDON` all contain the substrings `LED` and `ON`, so all of them
work. Note that `LED_OFF` contains `OFF` but not `ON`, so it correctly turns
the LED off.

---

## 4. Packet Sender quick setup

| Field | IPv4 test | IPv6 test |
|:------|:----------|:----------|
| Protocol | UDP | UDP |
| IP / Hostname | `192.168.1.111` | `2600:1702:4eb2:9780::abcd` |
| Port | `6000` | `6000` |
| Payload | `LED ON` | `LED OFF` |

Screenshots in the README (`images/ipv4_packetsender.jpg` and
`images/ipv6_packetsender.jpg`) show both cases.

```mermaid
flowchart LR
    PS["Packet Sender<br/>send LED ON to 6000"] --> SW["Router"]
    SW -->|"IPv4 192.168.1.111"| B4["ETH driver receives frame"]
    SW -->|"IPv6 global address"| B6["ETH driver receives frame"]
    B4 --> RX1["NetX Duo demuxes to UDP socket 6000"]
    B6 --> RX1
    RX1 --> APP["nx_app_thread_entry parses command"]
    APP --> LED["LED LD1 toggles"]
    APP --> CON["Console echoes payload"]
```

---

## 5. End-to-end data flow for a received packet

```mermaid
sequenceDiagram
    participant PC as Host PC (Packet Sender)
    participant PHY as LAN8742 PHY
    participant DMA as ETH DMA (RAM_D2)
    participant DRV as nx_stm32_eth_driver
    participant NX as NetX Duo UDP socket
    participant APP as nx_app_thread_entry
    participant UART as USART3 console
    PC->>PHY: UDP datagram (IPv4 or IPv6)
    PHY->>DMA: frame received into RX descriptor
    DMA->>DRV: ETH IRQ, deferred processing
    DRV->>NX: packet handed to IP/UDP layer
    NX->>APP: nx_udp_socket_receive returns packet
    APP->>UART: print raw payload
    alt LED command
        APP->>APP: parse LED ON / LED OFF
        APP->>GPIO: drive PB0
    end
    APP->>NX: nx_packet_release
```
