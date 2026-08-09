from typing import List, Dict, Any

class UARTDecoder:
    """
    Asynchronous UART Protocol Decoder.
    Parses raw time-series digital logic signals into decoded bytes.
    """
    def __init__(self, baud_rate: int = 115200, data_bits: int = 8, stop_bits: int = 1):
        self.baud_rate = baud_rate
        # Bit period duration in microseconds: T_bit = 1 / Baud Rate
        self.bit_period_us = (1.0 / baud_rate) * 1e6
        self.data_bits = data_bits
        self.stop_bits = stop_bits

    def decode(self, timestamps_us: List[float], logic_levels: List[int]) -> List[Dict[str, Any]]:
        """
        Decodes a digital waveform into UART frames.
        
        :param timestamps_us: List of timestamps in microseconds for state changes.
        :param logic_levels: List of logic levels (0 or 1) at each timestamp.
        :return: List of decoded UART packet dictionaries containing value, hex, and framing errors.
        """
        decoded_bytes = []
        if len(timestamps_us) < 2:
            return decoded_bytes

        idx = 0
        num_samples = len(timestamps_us)

        while idx < num_samples - 1:
            # Detect falling edge (High -> Low transition) indicating a START bit
            if logic_levels[idx] == 1 and logic_levels[idx + 1] == 0:
                start_time = timestamps_us[idx + 1]
                byte_val = 0
                framing_error = False

                # Sample 8 data bits LSB first at mid-bit intervals (1.5*T_bit, 2.5*T_bit, etc.)
                for bit_idx in range(self.data_bits):
                    sample_time = start_time + (1.5 + bit_idx) * self.bit_period_us
                    bit_val = self._sample_signal_at(sample_time, timestamps_us, logic_levels)
                    
                    if bit_val == 1:
                        byte_val |= (1 << bit_idx)

                # Verify STOP bit at (Start + 9.5 * T_bit)
                stop_time = start_time + (1.5 + self.data_bits) * self.bit_period_us
                stop_bit_val = self._sample_signal_at(stop_time, timestamps_us, logic_levels)
                if stop_bit_val != 1:
                    framing_error = True

                decoded_bytes.append({
                    'start_time_us': start_time,
                    'byte_val': byte_val,
                    'char': chr(byte_val) if 32 <= byte_val <= 126 else '.',
                    'hex': f"0x{byte_val:02X}",
                    'framing_error': framing_error
                })

                # Advance index past current frame timestamp range
                idx += 1
            else:
                idx += 1

        return decoded_bytes

    def _sample_signal_at(self, target_time: float, timestamps: List[float], levels: List[int]) -> int:
        """Helper to sample the logic level present at a specific microsecond timestamp."""
        current_level = levels[0]
        for t, lvl in zip(timestamps, levels):
            if t <= target_time:
                current_level = lvl
            else:
                break
        return current_level
