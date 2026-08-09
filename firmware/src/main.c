/**
 * @file main.c
 * @brief Firmware Main Super-Loop & Virtual Serial Streaming
 * @project PyLogic-Sniffer
 */

#include <stdio.h>
#include "capture_engine.h"

/**
 * @brief Main application entry point for MCU target.
 */
int main(void) {
    // 1. Initialize hardware capture engine at 1MHz sampling rate base
    capture_engine_init(1000000);

    // 2. Simulate incoming GPIO edge interrupts for UART 'A' pulse
    capture_engine_process_gpio_change(0x01, 0);     // Line Idle High
    capture_engine_process_gpio_change(0x00, 10);    // Start Bit (LOW)
    capture_engine_process_gpio_change(0x01, 19);    // Data Bit 0 (HIGH)
    capture_engine_process_gpio_change(0x00, 27);    // Data Bits 1-5 (LOW)
    capture_engine_process_gpio_change(0x01, 71);    // Data Bit 6 (HIGH)
    capture_engine_process_gpio_change(0x00, 79);    // Data Bit 7 (LOW)
    capture_engine_process_gpio_change(0x01, 88);    // Stop Bit (HIGH)

    // 3. Process queued RLE packets and stream over USB-CDC / UART
    RLEPacket_t packet;
    printf("--- [Firmware Stream] Transmitting RLE Packets ---\n");
    while (capture_engine_pop_sample(&packet)) {
        printf("GPIO State: 0x%02X | Duration: %lu us\n", packet.gpio_state, (unsigned long)packet.duration_us);
    }

    return 0;
}
