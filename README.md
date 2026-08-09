# PyLogic-Sniffer: MCU-Based Protocol Analyzer & Logic Waveform GUI

`PyLogic-Sniffer` turns microcontrollers into high-speed digital signal acquisition devices paired with a custom Python desktop application for real-time protocol decoding (UART, I2C, SPI) and digital logic waveform visualization.

---

## 🏗️ System Architecture

```text
  [ Target Hardware ]
 (SPI / I2C / UART Bus)
          │
          ▼
 [ MCU GPIO Pins ] ──► [ High-Speed Timer / DMA Capture ] ──► [ USB-CDC / UART ]
                                                                     │
                                                                     ▼
 [ Waveform UI ] ◄── [ Protocol Decoders ] ◄── [ Packet Reconstructor ]
