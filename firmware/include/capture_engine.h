/**
 * @file capture_engine.h
 * @brief High-Speed GPIO Sampling and RLE Buffer Interface
 * @project PyLogic-Sniffer
 */

#ifndef CAPTURE_ENGINE_H
#define CAPTURE_ENGINE_H

#include <stdint.h>
#include <stdbool.h>

#define MAX_RLE_SAMPLES 256
#define NUM_CHANNELS    4

/**
 * @brief Run-Length Encoded (RLE) Packet Structure.
 * Packs GPIO pin state bitmask alongside microsecond duration.
 */
typedef struct {
    uint8_t gpio_state;     /**< Bitfield: Bit 0=CH0, Bit 1=CH1, Bit 2=CH2, Bit 3=CH3 */
    uint32_t duration_us;   /**< Pulse width duration in microseconds */
} RLEPacket_t;

/**
 * @brief Ring buffer for queuing compressed RLE samples prior to UART/USB transmit.
 */
typedef struct {
    RLEPacket_t packets[MAX_RLE_SAMPLES];
    volatile uint16_t head;
    volatile uint16_t tail;
    volatile uint16_t count;
} RLEBuffer_t;

/* Function Declarations */
void capture_engine_init(uint32_t sample_rate_hz);
bool capture_engine_push_sample(uint8_t gpio_state, uint32_t duration_us);
bool capture_engine_pop_sample(RLEPacket_t *packet);
void capture_engine_process_gpio_change(uint8_t current_gpio_state, uint32_t current_time_us);

#endif /* CAPTURE_ENGINE_H */
