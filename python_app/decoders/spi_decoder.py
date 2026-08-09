from typing import List, Dict, Any

class SPIDecoder:
    """
    Synchronous SPI (Serial Peripheral Interface) Protocol Decoder.
    Samples MOSI and MISO data lines on SCLK clock transitions while CS (Chip Select) is active (Low).
    """
    def __init__(self, cpol: int = 0, cpha: int = 0):
        self.cpol = cpol  # Clock Polarity (0: Idle Low, 1: Idle High)
        self.cpha = cpha  # Clock Phase (0: Sample on 1st Edge, 1: Sample on 2nd Edge)

    def decode(
        self,
        sclk_events: List[Dict[str, Any]],
        mosi_events: List[Dict[str, Any]],
        miso_events: List[Dict[str, Any]],
        cs_events: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Decodes full-duplex SPI bus transfers.
        
        :param sclk_events: Time-series event list for SCLK (Clock).
        :param mosi_events: Time-series event list for MOSI (Master Out).
        :param miso_events: Time-series event list for MISO (Master In).
        :param cs_events: Time-series event list for CS (Chip Select).
        :return: List of decoded full-duplex SPI frames containing MOSI and MISO hex values.
        """
        parsed_frames = []
        if not sclk_events or not cs_events:
            return parsed_frames

        mosi_bits = []
        miso_bits = []
        frame_start_time = None

        for i in range(len(sclk_events) - 1):
            clk_curr = sclk_events[i]
            clk_next = sclk_events[i + 1]
            t_sample = clk_next['time_us']

            # Check if Chip Select line is active (Low)
            cs_level = self._get_signal_at(t_sample, cs_events)
            if cs_level == 0:
                # Sample on SCLK rising edge
                if clk_curr['level'] == 0 and clk_next['level'] == 1:
                    if frame_start_time is None:
                        frame_start_time = t_sample

                    mosi_val = self._get_signal_at(t_sample, mosi_events) if mosi_events else 0
                    miso_val = self._get_signal_at(t_sample, miso_events) if miso_events else 0

                    mosi_bits.append(mosi_val)
                    miso_bits.append(miso_val)

                    # Assemble 8-bit bytes (MSB first)
                    if len(mosi_bits) == 8:
                        mosi_byte = 0
                        miso_byte = 0
                        for bit in mosi_bits:
                            mosi_byte = (mosi_byte << 1) | bit
                        for bit in miso_bits:
                            miso_byte = (miso_byte << 1) | bit

                        parsed_frames.append({
                            'time_us': frame_start_time,
                            'mosi_hex': f"0x{mosi_byte:02X}",
                            'miso_hex': f"0x{miso_byte:02X}",
                            'mosi_val': mosi_byte,
                            'miso_val': miso_byte
                        })

                        mosi_bits = []
                        miso_bits = []
                        frame_start_time = None
            else:
                # Reset bit buffers when CS goes inactive (High)
                mosi_bits = []
                miso_bits = []
                frame_start_time = None

        return parsed_frames

    def _get_signal_at(self, target_time: float, events: List[Dict[str, Any]]) -> int:
        """Helper to extract logic state at a given microsecond timestamp."""
        if not events:
            return 0
        current_val = events[0]['level']
        for ev in events:
            if ev['time_us'] <= target_time:
                current_val = ev['level']
            else:
                break
        return current_val
