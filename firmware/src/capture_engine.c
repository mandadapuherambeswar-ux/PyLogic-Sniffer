/**
 * @file capture_engine.c
 * @brief High-Speed GPIO Sampling and RLE Compression Implementation
 * @project PyLogic-Sniffer
 */

#include "capture_engine.h"

static RLEBuffer_t rle_ring_buffer;
static uint32_t last_timestamp_us = 0;
static uint8_t last_gpio_state = 0xFF;

/**
 * @brief Initializes the capture engine and clears the RLE ring buffer pointers.
 */
void capture_engine_init(uint32_t sample_rate_hz) {
    (void)sample_rate_hz; // Used for timer prescaler configuration in target HW
    rle_ring_buffer.head = 0;
    rle_ring_buffer.tail = 0;
    rle_ring_buffer.count = 0;
    last_timestamp_us = 0;
    last_gpio_state = 0;
}

/**
 * @brief Pushes an RLE packet into the volatile ring buffer.
 */
bool capture_engine_push_sample(uint8_t gpio_state, uint32_t duration_us) {
    if (rle_ring_buffer.count >= MAX_RLE_SAMPLES) {
        return false; // Buffer overflow
    }

    rle_ring_buffer.packets[rle_ring_buffer.head].gpio_state = gpio_state;
    rle_ring_buffer.packets[rle_ring_buffer.head].duration_us = duration_us;

    rle_ring_buffer.head = (rle_ring_buffer.head + 1) % MAX_RLE_SAMPLES;
    rle_ring_buffer.count++;
    return true;
}

/**
 * @brief Pops an RLE packet from the ring buffer for UART / USB transmission.
 */
bool capture_engine_pop_sample(RLEPacket_t *packet) {
    if (rle_ring_buffer.count == 0 || packet == NULL) {
        return false; // Buffer empty
    }

    *packet = rle_ring_buffer.packets[rle_ring_buffer.tail];
    rle_ring_buffer.tail = (rle_ring_buffer.tail + 1) % MAX_RLE_SAMPLES;
    rle_ring_buffer.count--;
    return true;
}

/**
 * @brief Interrupt Service Routine (ISR) handler for GPIO edge transitions.
 * Calculates pulse duration delta and pushes state change into RLE queue.
 */
void capture_engine_process_gpio_change(uint8_t current_gpio_state, uint32_t current_time_us) {
    if (current_gpio_state != last_gpio_state) {
        uint32_t duration = current_time_us - last_timestamp_us;
        
        if (duration > 0 && last_timestamp_us != 0) {
            capture_engine_push_sample(last_gpio_state, duration);
        }

        last_gpio_state = current_gpio_state;
        last_timestamp_us = current_time_us;
    }
}
