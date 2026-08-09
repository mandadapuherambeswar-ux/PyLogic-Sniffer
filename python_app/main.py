import sys
from typing import List, Dict, Any
from PyQt6.QtWidgets import QApplication

from decoders.uart_decoder import UARTDecoder
from decoders.i2c_decoder import I2CDecoder
from decoders.spi_decoder import SPIDecoder
from ui.waveform_viewer import WaveformViewer

def generate_mock_uart_stream():
    """Generates mock microsecond timestamped logic levels for a UART frame."""
    # Represents 8-bit UART character transmission 'A' (0x41 = 0b01000001) at 115200 baud (~8.68 us per bit)
    bit_us = 8.68
    timestamps = [0.0]
    levels = [1]  # Line Idle High

    # Start Bit (LOW)
    timestamps.append(10.0)
    levels.append(0)

    # 8 Data Bits (LSB First for 'A' -> 1, 0, 0, 0, 0, 0, 1, 0)
    data_bits = [1, 0, 0, 0, 0, 0, 1, 0]
    for idx, bit in enumerate(data_bits):
        timestamps.append(10.0 + (1 + idx) * bit_us)
        levels.append(bit)

    # Stop Bit (HIGH)
    timestamps.append(10.0 + 9 * bit_us)
    levels.append(1)

    # Return to Idle
    timestamps.append(10.0 + 12 * bit_us)
    levels.append(1)

    return timestamps, levels

def main():
    app = QApplication(sys.argv)
    viewer = WaveformViewer(channels=4)

    # 1. Generate & Decode Mock UART Data
    uart_timestamps, uart_levels = generate_mock_uart_stream()
    uart_decoder = UARTDecoder(baud_rate=115200)
    decoded_uart = uart_decoder.decode(uart_timestamps, uart_levels)

    print("\n--- [PyLogic-Sniffer] Decoded UART Frames ---")
    for frame in decoded_uart:
        print(f"Time: {frame['start_time_us']:.2f} us | Hex: {frame['hex']} | Char: '{frame['char']}' | Framing Error: {frame['framing_error']}")

    # 2. Render Channels on Waveform Viewer GUI
    viewer.plot_channel_data(0, uart_timestamps, uart_levels)  # CH0: UART RX
    viewer.plot_channel_data(1, [t + 5 for t in uart_timestamps], [1 - l for l in uart_levels])  # CH1: Clock/Trigger
    
    viewer.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
