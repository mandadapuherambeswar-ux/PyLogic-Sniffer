import sys
from typing import List, Dict, Any
from PyQt6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget, QLabel
import pyqtgraph as pg

class WaveformViewer(QMainWindow):
    """
    Interactive Digital Logic Waveform Viewer.
    Renders multi-channel digital signals (0s and 1s) with time-series zoom and pan.
    """
    def __init__(self, channels: int = 4):
        super().__init__()
        self.setWindowTitle("PyLogic-Sniffer — Interactive Logic Analyzer")
        self.setGeometry(100, 100, 1100, 650)
        self.num_channels = channels

        # Main Layout Setup
        main_widget = QWidget()
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

        # Header Info Label
        self.status_label = QLabel("Channels: CH0-CH3 | Mouse Drag: Pan | Scroll Wheel: Zoom")
        self.status_label.setStyleSheet("font-weight: bold; color: #333; padding: 4px;")
        layout.addWidget(self.status_label)

        # PyQtGraph Plot Widget Setup
        pg.setConfigOptions(antialias=True)
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#121212')  # Dark theme for high-contrast waveforms
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel('bottom', 'Time', units='us')
        self.plot_widget.setLabel('left', 'Logic Level / Channel')
        layout.addWidget(self.plot_widget)

    def plot_channel_data(self, channel_id: int, timestamps_us: List[float], logic_levels: List[int]):
        """
        Plots a square-step logic signal for a specific channel.
        Applies a Y-axis offset so channels stack neatly above each other.
        
        :param channel_id: Channel index (0 to N).
        :param timestamps_us: List of timestamps in microseconds.
        :param logic_levels: List of logic states (0 or 1).
        """
        if not timestamps_us or not logic_levels:
            return

        # Y-offset per channel to prevent overlapping waveforms
        y_offset = channel_id * 1.8
        y_data = [lvl + y_offset for lvl in logic_levels]

        # Distinct color palette per logic channel
        colors = ['#00FF7F', '#00E5FF', '#FFD700', '#FF4081', '#AA00FF']
        channel_color = colors[channel_id % len(colors)]

        # Render step plot (square waveforms)
        self.plot_widget.plot(
            timestamps_us,
            y_data,
            stepMode='center',
            pen=pg.mkPen(color=channel_color, width=2),
            name=f"CH{channel_id}"
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = WaveformViewer(channels=4)

    # Mock logic signal for GUI demonstration
    sample_timestamps = [0, 10, 20, 35, 50, 70, 90, 110]
    sample_levels = [0, 1, 0, 1, 1, 0, 1, 0]

    viewer.plot_channel_data(0, sample_timestamps, sample_levels)
    viewer.plot_channel_data(1, sample_timestamps, [1 - lvl for lvl in sample_levels])
    viewer.show()
    sys.exit(app.exec())
