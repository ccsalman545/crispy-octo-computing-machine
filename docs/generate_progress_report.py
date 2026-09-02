#!/usr/bin/env python3
"""Generate a two-page firmware progress report PDF."""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont("DejaVu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuBold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuMono", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"))

NAVY = HexColor("#1B365D")
BODY = HexColor("#1E293B")
MUTED = HexColor("#475569")
RULE = HexColor("#CBD5E1")
ROW_ALT = HexColor("#F1F5F9")
HEAD_BG = HexColor("#1B365D")
ACCENT = HexColor("#0F766E")
PALE = HexColor("#F8FAFC")
STATUS_OK = HexColor("#065F46")
STATUS_WARN = HexColor("#92400E")
NAVY_MID = HexColor("#1D4ED8")
LINE = HexColor("#E2E8F0")
GRID = HexColor("#94A3B8")

PAGE_W, PAGE_H = letter
LEFT = 0.70 * inch
RIGHT = 0.70 * inch
TOP = 0.58 * inch
BOTTOM = 0.58 * inch
CONTENT_W = PAGE_W - LEFT - RIGHT

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Progress_Report.pdf")


def styles():
    s = {}
    s["title"] = ParagraphStyle(
        "title", fontName="DejaVuBold", fontSize=14.2, leading=18,
        textColor=NAVY, alignment=TA_LEFT,
    )
    s["subtitle"] = ParagraphStyle(
        "subtitle", fontName="DejaVu", fontSize=8.7, leading=12.2,
        textColor=MUTED, alignment=TA_LEFT,
    )
    s["meta"] = ParagraphStyle(
        "meta", fontName="DejaVu", fontSize=8, leading=10.8,
        textColor=BODY, alignment=TA_LEFT,
    )
    s["meta_b"] = ParagraphStyle(
        "meta_b", fontName="DejaVuBold", fontSize=8, leading=10.8,
        textColor=NAVY, alignment=TA_LEFT,
    )
    s["h"] = ParagraphStyle(
        "h", fontName="DejaVuBold", fontSize=10, leading=13,
        textColor=NAVY,
    )
    s["body"] = ParagraphStyle(
        "body", fontName="DejaVu", fontSize=8.5, leading=12.0,
        textColor=BODY, alignment=TA_JUSTIFY, spaceAfter=0,
    )
    s["small"] = ParagraphStyle(
        "small", fontName="DejaVu", fontSize=7.8, leading=10.8,
        textColor=BODY, alignment=TA_LEFT,
    )
    s["th"] = ParagraphStyle(
        "th", fontName="DejaVuBold", fontSize=7.3, leading=9.6,
        textColor=white, alignment=TA_LEFT,
    )
    s["td"] = ParagraphStyle(
        "td", fontName="DejaVu", fontSize=7.4, leading=10.0,
        textColor=BODY, alignment=TA_LEFT,
    )
    s["td_b"] = ParagraphStyle(
        "td_b", fontName="DejaVuBold", fontSize=7.4, leading=10.0,
        textColor=NAVY, alignment=TA_LEFT,
    )
    s["td_m"] = ParagraphStyle(
        "td_m", fontName="DejaVuMono", fontSize=7.0, leading=10.0,
        textColor=BODY, alignment=TA_LEFT,
    )
    s["bullet"] = ParagraphStyle(
        "bullet", fontName="DejaVu", fontSize=8.3, leading=11.6,
        textColor=BODY, leftIndent=12, firstLineIndent=-10, spaceAfter=2.2,
    )
    s["cap"] = ParagraphStyle(
        "cap", fontName="DejaVu", fontSize=7.3, leading=10.0,
        textColor=MUTED, alignment=TA_LEFT, spaceBefore=3, spaceAfter=0,
    )
    s["pill_l"] = ParagraphStyle(
        "pill_l", fontName="DejaVuBold", fontSize=7.5, leading=10,
        textColor=BODY, alignment=TA_LEFT,
    )
    s["pill_t"] = ParagraphStyle(
        "pill_t", fontName="DejaVu", fontSize=7.3, leading=10.0,
        textColor=BODY, alignment=TA_LEFT,
    )
    return s


S = styles()


def P(text, style="body"):
    return Paragraph(text, S[style])


def header_footer(c, doc):
    c.saveState()
    c.setFillColor(NAVY)
    c.rect(0, PAGE_H - 26, PAGE_W, 26, fill=1, stroke=0)
    c.setFillColor(ACCENT)
    c.rect(0, PAGE_H - 29, PAGE_W, 3, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("DejaVuBold", 7.8)
    c.drawString(LEFT, PAGE_H - 16.5, "FIRMWARE PROGRESS REPORT")
    c.setFont("DejaVu", 7.8)
    c.drawRightString(PAGE_W - RIGHT, PAGE_H - 16.5, "NUCLEO-H743  |  NetX Duo UDP  |  2 September 2026")

    c.setFillColor(NAVY)
    c.rect(0, 0, PAGE_W, 24, fill=1, stroke=0)
    c.setFillColor(ACCENT)
    c.rect(0, 24, PAGE_W, 2.4, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("DejaVu", 7.2)
    c.drawString(LEFT, 9, "ccsalman545 / crispy-octo-computing-machine    |    Project baseline 1.0.0")
    c.setFont("DejaVuBold", 7.2)
    c.drawRightString(PAGE_W - RIGHT, 9, f"Page {doc.page} of 2")
    c.restoreState()


def section_head(title, first=False):
    data = [[P(title, "h")]]
    t = Table(data, colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 2 if first else 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, -1), 1.15, NAVY),
    ]))
    return t


def styled_table(headers, rows, col_widths, mono_cols=None, bold_col0=True, compact=False):
    mono_cols = mono_cols or set()
    head = [P(h, "th") for h in headers]
    body = []
    for r in rows:
        cells = []
        for i, val in enumerate(r):
            if i in mono_cols:
                cells.append(P(val, "td_m"))
            elif i == 0 and bold_col0:
                cells.append(P(val, "td_b"))
            else:
                cells.append(P(val, "td"))
        body.append(cells)
    data = [head] + body
    t = Table(data, colWidths=col_widths, repeatRows=1)
    pad_h, pad_b = (5.0, 4.0) if not compact else (4.4, 3.4)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), HEAD_BG),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, 0), pad_h),
        ("BOTTOMPADDING", (0, 0), (-1, 0), pad_h),
        ("TOPPADDING", (0, 1), (-1, -1), pad_b),
        ("BOTTOMPADDING", (0, 1), (-1, -1), pad_b),
        ("GRID", (0, 0), (-1, -1), 0.3, GRID),
        ("LINEBELOW", (0, 0), (-1, 0), 1.3, ACCENT),
    ]
    for i in range(1, len(data)):
        style.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT if i % 2 == 0 else white))
    t.setStyle(TableStyle(style))
    return t


def meta_block():
    # Two columns, four rows. Labels stay on one line.
    pairs = [
        ("Date", "2 September 2026", "Release", "1.0.0 (31 August 2026)"),
        ("Period", "31 August 2026 to 2 September 2026", "Status", "Baseline complete. Lab bind pending."),
        ("Board", "NUCLEO-H743ZI2, STM32H743ZIT6, Cortex-M7", "Stack", "ThreadX 6.2 + NetX Duo 6.2"),
        ("Tools", "CubeMX 6.15.0, X-CUBE-AZRTOS-H7 3.1.0", "Repo", "ccsalman545/crispy-octo-computing-machine"),
    ]
    rows = []
    for a, av, b, bv in pairs:
        rows.append([P(a, "meta_b"), P(av, "meta"), P(b, "meta_b"), P(bv, "meta")])
    t = Table(rows, colWidths=[0.72*inch, 2.88*inch, 0.72*inch, 2.74*inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE),
        ("BOX", (0, 0), (-1, -1), 0.6, RULE),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5.2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5.2),
    ]))
    return t


def status_pills():
    items = [
        ("Complete", STATUS_OK, HexColor("#D1FAE5"),
         "Firmware 1.0.0: dual-stack UDP, LED and button paths, full docs set."),
        ("In lab", STATUS_WARN, HexColor("#FEF3C7"),
         "Static IPv4 and IPv6 must match the local subnet before tests."),
        ("Open", NAVY_MID, HexColor("#DBEAFE"),
         "DHCP, IPv6 button reports, and TCP sockets are out of scope."),
    ]
    cells = []
    for label, fg, bg, text in items:
        inner = Table(
            [[P(f'<font color="{fg.hexval()}"><b>{label}</b></font>', "pill_l")],
             [P(text, "pill_t")]],
            colWidths=[2.28*inch],
        )
        inner.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), bg),
            ("BOX", (0, 0), (-1, -1), 0.45, fg),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (0, 0), 6),
            ("BOTTOMPADDING", (0, 0), (0, 0), 1),
            ("TOPPADDING", (0, 1), (0, 1), 1),
            ("BOTTOMPADDING", (0, 1), (0, 1), 7),
        ]))
        cells.append(inner)
    t = Table([cells], colWidths=[2.355*inch, 2.355*inch, 2.355*inch])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (0, 0), 6),
        ("RIGHTPADDING", (1, 0), (1, 0), 6),
        ("RIGHTPADDING", (2, 0), (2, 0), 0),
        ("LEFTPADDING", (1, 0), (1, 0), 0),
        ("LEFTPADDING", (2, 0), (2, 0), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return t


def build():
    doc = SimpleDocTemplate(
        OUT,
        pagesize=letter,
        leftMargin=LEFT,
        rightMargin=RIGHT,
        topMargin=TOP + 8,
        bottomMargin=BOTTOM + 6,
        title="Progress Report: Dual IPv4 and IPv6 UDP with NetX Duo on NUCLEO-H743",
        author="Project team",
        subject="Two-page firmware progress report",
    )
    story = []

    story.append(Spacer(1, 4))
    story.append(P("Dual IPv4 and IPv6 UDP with NetX Duo on NUCLEO-H743", "title"))
    story.append(Spacer(1, 5))
    story.append(P(
        "Status of the STM32CubeIDE firmware example as of 2 September 2026. "
        "UDP server on port 6000, LED remote control, button reporting, serial console, documentation.",
        "subtitle",
    ))
    story.append(Spacer(1, 8))
    story.append(meta_block())
    story.append(Spacer(1, 8))
    story.append(status_pills())

    story.append(section_head("1.  Purpose"))
    story.append(Spacer(1, 6))
    story.append(P(
        "Record the 1.0.0 baseline on NUCLEO-H743ZI2. ThreadX 6.2 and NetX Duo 6.2 run one UDP "
        "socket on port 6000 for IPv4 and IPv6. Text commands drive LD1 (PB0). Button B1 (PC13) is "
        "polled with a two-read debounce and reported to a host PC. USART3 (115200 8N1, ST-Link VCP) "
        "prints addresses, the bind line, and every payload. CubeMX generates HAL, linker scripts, "
        "and startup. IPv6 is enabled by hand in app_netxduo.c because CubeMX does not emit it."
    ))

    story.append(section_head("2.  Work completed"))
    story.append(Spacer(1, 5))
    bullets = [
        "UDP server bound to port 6000. Dual-stack receive path is live.",
        "LED parser: LED ON, LED_ON, LEDON, ON and the matching OFF forms, including case variants.",
        "Button stream: BUTTON:0 pressed, BUTTON:1 released, to 192.168.1.160:55100 every 20 ticks (~200 ms).",
        "Addressing: IPv4 192.168.1.111/24, IPv6 2600:1702:4eb2:9780::abcd/64. Link-local from the MAC.",
        "Ethernet: LAN8742 RMII, MAC 00:80:E1:00:00:00, DMA descriptors at 0x30040000, 128 KB non-cacheable MPU region.",
        "Pools: 10 x 1536 B packets, ARP 1024 B, 30 KB NetX pool in RAM_D2. Two priority-10 threads, 2 KB stacks, 100 ticks/s. Docs and PR #1 merged 31 August 2026.",
    ]
    for b in bullets:
        story.append(Paragraph(f"-  {b}", S["bullet"]))

    story.append(section_head("3.  Runtime path"))
    story.append(Spacer(1, 6))
    story.append(P(
        "Reset_Handler, SystemInit, main(): MPU_Config, I/D-cache, HAL_Init (TIM6), SystemClock_Config "
        "(HSE bypass + PLL), MX_GPIO_Init, MX_ETH_Init, MX_USART3_UART_Init, MX_ThreadX_Init. "
        "tx_kernel_enter does not return. tx_application_define creates the 1 KB ThreadX pool and the "
        "30 KB NetX pool, then MX_NetXDuo_Init: nx_system_initialize, nx_packet_pool_create, nx_ip_create "
        "(192.168.1.111 / 255.255.255.0, nx_stm32_eth_driver), ARP/ICMP/TCP/UDP enable, nxd_ipv6_enable, "
        "nxd_ipv6_address_set (/64, interface 0), nxd_icmp_enable, tx_thread_create(nx_app_thread_entry). "
        "The thread prints addresses, binds UDP 6000, then loops: read PC13, debounce, send BUTTON:n, "
        "sleep 20 ticks, receive with a 1-tick timeout, parse LED commands, release the packet."
    ))

    story.append(section_head("4.  UDP protocol and endpoints"))
    story.append(Spacer(1, 5))
    story.append(styled_table(
        ["Direction", "Address / port", "Payload", "Effect"],
        [
            ["PC to board", "192.168.1.111 port 6000", "LED ON, LED_ON, LEDON, ON", "LD1 (PB0) high"],
            ["PC to board", "[2600:1702:4eb2:9780::abcd] port 6000", "LED OFF, LED_OFF, LEDOFF, OFF", "LD1 (PB0) low"],
            ["PC to board", "Same socket, IPv4 or IPv6", "Any other text", "Echo on USART3"],
            ["Board to PC", "192.168.1.160 port 55100", "BUTTON:0", "B1 pressed"],
            ["Board to PC", "192.168.1.160 port 55100", "BUTTON:1", "B1 released"],
        ],
        [1.10*inch, 2.52*inch, 2.18*inch, 1.26*inch],
        mono_cols={1, 2},
        compact=True,
    ))

    story.append(PageBreak())

    story.append(section_head("5.  Configuration snapshot", first=True))
    story.append(Spacer(1, 5))
    story.append(styled_table(
        ["Item", "Value", "Where"],
        [
            ["IPv4 / mask", "192.168.1.111 / 255.255.255.0", "app_netxduo.h lines 87, 89"],
            ["IPv6 global / prefix", "2600:1702:4eb2:9780::abcd / 64", "app_netxduo.c lines 265 to 268"],
            ["UDP listen / report", "6000 listen, 55100 report", "app_netxduo.c lines 323, 365"],
            ["MAC / console", "00:80:E1:00:00:00, USART3 115200 8N1", "main.c lines 229 to 234, 276"],
            ["Packet pool / stacks", "10 x 1536 B, 2 KB stacks, priority 10", "app_netxduo.h lines 47, 73, 77 to 83"],
            ["NetX byte pool", "30 KB in .NetXPoolSection (RAM_D2)", "app_azure_rtos_config.h"],
            ["Debounce / PHY", "2 reads, 20 ticks; LAN8742 RMII", "nx_app_thread_entry; .ioc"],
        ],
        [1.55*inch, 2.95*inch, 2.56*inch],
        mono_cols={1, 2},
        compact=True,
    ))

    story.append(section_head("6.  Verification status"))
    story.append(Spacer(1, 5))
    story.append(styled_table(
        ["ID", "Check", "Pass when", "State"],
        [
            ["T1", "Console bring-up", "Prints IPv4, IPv6, and UDP Server listening on PORT 6000..", "Ready to run"],
            ["T2", "IPv4 LED on/off", "LED ON / LED OFF (and ON / OFF) drive LD1; console confirms", "Ready to run"],
            ["T3", "IPv6 LED on/off", "LED_ON / LED_OFF to the /64 address drive LD1", "Network dependent"],
            ["T4", "Unknown payload", "hello is echoed on USART3; LED unchanged", "Ready to run"],
            ["T5", "Button stream", "BUTTON:1 idle, BUTTON:0 while B1 held, ~200 ms period", "Ready to run"],
            ["T6", "ICMPv4 / ICMPv6", "ping 192.168.1.111 replies; ping6 to ::abcd if the LAN routes it", "IPv4 ready; IPv6 LAN"],
        ],
        [0.40*inch, 1.38*inch, 3.95*inch, 1.33*inch],
        compact=True,
    ))
    story.append(P(
        "Ready to run means the code path and the matrix in docs/TESTING.md exist. "
        "Pass or fail is recorded on the target LAN after static addresses match that LAN. "
        "IPv6 unicast through consumer routers is not guaranteed. Use the same /64, or test link-local.",
        "cap",
    ))

    story.append(section_head("7.  Open items and risks"))
    story.append(Spacer(1, 5))
    story.append(styled_table(
        ["Item", "Impact", "Action"],
        [
            ["IPv6 address is lab-specific", "Unreachable on another /64.", "Edit the four v6 words in app_netxduo.c."],
            ["IPv4 is static only", "Wrong subnet or duplicate 192.168.1.111.", "Align NX_APP_DEFAULT_IP_ADDRESS."],
            ["Button reports IPv4 only", "IPv6-only hosts never see BUTTON:n.", "Add an NXD_ADDRESS v6 target if required."],
            ["TCP enabled, unused", "Uses RAM with no application socket.", "Leave as-is, or drop nx_tcp_enable."],
            ["Error_Handler is silent", "Bind or IPv6 failure looks like a hang.", "Use USART3 and docs/DEBUGGING.md."],
        ],
        [1.85*inch, 2.50*inch, 2.71*inch],
        compact=True,
    ))

    story.append(section_head("8.  Next steps (in order)"))
    story.append(Spacer(1, 5))
    nexts = [
        "Set IPv4, IPv6, MAC, and the PC report address to the lab network. Rebuild and flash via ST-Link.",
        "Run T1 to T6. Keep the USART3 transcript and Packet Sender captures for IPv4 and IPv6.",
        "Confirm B1 reporting on UDP 55100. Change SEND_SLEEP_TICKS only if the host cannot keep up.",
        "Do not add DHCP, TCP sockets, or extra threads until dual-stack UDP is signed off on hardware.",
    ]
    for i, n in enumerate(nexts, 1):
        story.append(Paragraph(f"{i}.  {n}", S["bullet"]))

    story.append(Spacer(1, 8))
    close = Table(
        [[P(
            "Prepared 2 September 2026 from repository 1.0.0 (changelog 31 August 2026). "
            "Sources: NetXDuo/App/app_netxduo.c, app_netxduo.h, Core/Src/main.c, "
            "AZURE_RTOS/App/app_azure_rtos.c, docs/ARCHITECTURE.md, docs/TESTING.md, "
            "docs/CONFIGURATION.md. No scope change is proposed in this report.",
            "small",
        )]],
        colWidths=[CONTENT_W],
    )
    close.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE),
        ("BOX", (0, 0), (-1, -1), 0.6, RULE),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(close)

    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    return OUT


if __name__ == "__main__":
    print(build())
