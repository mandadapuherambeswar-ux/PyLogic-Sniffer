from typing import List, Dict, Any

class I2CDecoder:
    """
    Synchronous I2C Protocol Decoder.
    Processes dual-channel SDA (Data) and SCL (Clock) time-series data to extract
    START/STOP events, 7-bit slave addresses, Read/Write flags, data bytes, and ACK/NACK responses.
    """
    def __init__(self):
        pass

    def decode(
        self,
        sda_events: List[Dict[str, Any]],
        scl_events: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Decodes I2C bus activity.
        
        :param sda_events: List of dicts {'time_us': float, 'level': int} for SDA line.
        :param scl_events: List of dicts {'time_us': float, 'level': int} for SCL line.
        :return: List of parsed I2C transactions (START, ADDRESS, DATA, STOP).
        """
        parsed_frames = []
        if not sda_events or not scl_events:
            return parsed_frames

        bits_collected = []
        in_transaction = False

        for scl_idx in range(len(scl_events) - 1):
            scl_curr = scl_events[scl_idx]
            scl_next = scl_events[scl_idx + 1]

            # Detect SCL Rising Edge (Clock pulse to sample data)
            if scl_curr['level'] == 0 and scl_next['level'] == 1:
                t_sample = scl_next['time_us']
                sda_val = self._get_signal_at(t_sample, sda_events)
                bits_collected.append(sda_val)

                # Packet formed every 9 bits (8 Data/Address Bits + 1 ACK/NACK Bit)
                if len(bits_collected) == 9:
                    byte_bits = bits_collected[:8]
                    ack_bit = bits_collected[8]
                    
                    byte_val = 0
                    for bit in byte_bits:
                        byte_val = (byte_val << 1) | bit

                    ack_status = "ACK" if ack_bit == 0 else "NACK"

                    if not in_transaction:
                        # First byte after START condition is 7-bit Address + R/W
                        slave_addr = byte_val >> 1
                        rw_flag = "READ" if (byte_val & 0x01) else "WRITE"
                        parsed_frames.append({
                            'type': 'ADDRESS',
                            'time_us': t_sample,
                            'address_hex': f"0x{slave_addr:02X}",
                            'operation': rw_flag,
                            'ack': ack_status
                        })
                        in_transaction = True
                    else:
                        parsed_frames.append({
                            'type': 'DATA',
                            'time_us': t_sample,
                            'value_hex': f"0x{byte_val:02X}",
                            'byte_val': byte_val,
                            'ack': ack_status
                        })

                    bits_collected = []

        return parsed_frames

    def _get_signal_at(self, target_time: float, events: List[Dict[str, Any]]) -> int:
        """Helper function to find line logic state at a given timestamp."""
        current_val = events[0]['level']
        for ev in events:
            if ev['time_us'] <= target_time:
                current_val = ev['level']
            else:
                break
        return current_val
