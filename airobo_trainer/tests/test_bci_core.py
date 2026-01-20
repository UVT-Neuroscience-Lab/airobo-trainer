"""
Unit tests for BCI Core Module
"""

import pytest
from unittest.mock import Mock, patch, mock_open
from airobo_trainer.models.bci_core import BCIEngine


class TestBCIEngine:
    """Test suite for the BCIEngine class."""

    def test_init_default_config(self):
        """Test BCIEngine initialization with default config."""
        engine = BCIEngine()

        assert engine.SERIAL == "NP-2025.07.10"
        assert engine.FS == 250  # Default sampling rate
        assert engine.BLOCK_SIZE == 8
        assert engine.NUMBEROFSCANS == 0
        assert engine.raw_data == []
        assert engine.device is None
        assert engine._running is False
        assert engine._recording is False
        assert engine._csv_writer is None
        assert engine._csv_file is None
        assert engine.data_path == "airobo_trainer/output"
        assert engine.selected_electrodes == {14, 15, 16}  # C3, CZ, C4
        assert engine.selected_electrode_names == ["C3", "CZ", "C4"]

    def test_init_custom_config(self):
        """Test BCIEngine initialization with custom config."""
        config = {
            "sampling_rate": "500 Hz",
            "selected_electrodes": {0, 1, 2},
            "output_path": "custom/path",
        }
        engine = BCIEngine("CUSTOM-123", config)

        assert engine.SERIAL == "CUSTOM-123"
        assert engine.FS == 500
        assert engine.selected_electrodes == {0, 1, 2}
        assert engine.selected_electrode_names == ["FP1", "FP2", "AF3"]
        assert engine.data_path == "custom/path"

    def test_init_empty_electrodes_fallback(self):
        """Test that empty electrodes fall back to default."""
        config = {"selected_electrodes": set()}
        engine = BCIEngine(config=config)

        assert engine.selected_electrodes == {14, 15, 16}  # Default fallback

    @patch("airobo_trainer.models.bci_core.pygds")
    def test_connect(self, mock_pygds):
        """Test device connection."""
        mock_device = Mock()
        mock_pygds.GDS.return_value = mock_device
        mock_device.Channels = [Mock() for _ in range(32)]

        config = {
            "sampling_rate": "500 Hz",
            "bandpass_filter": "0.1 – 60 Hz Bandpass",
            "notch_filter": "50Hz",
        }
        engine = BCIEngine(config=config)
        engine.connect()

        mock_pygds.Initialize.assert_called_once()
        mock_pygds.GDS.assert_called_once_with("NP-2025.07.10")
        assert engine.device == mock_device
        assert mock_device.SamplingRate == 500
        mock_device.SetConfiguration.assert_called_once()

    def test_get_exact_filter_indices_250hz(self):
        """Test filter index lookup for 250 Hz."""
        config = {"sampling_rate": "250 Hz"}
        engine = BCIEngine(config=config)

        bandpass_idx, notch_idx = engine._get_exact_filter_indices("0.1 – 60 Hz Bandpass", "50Hz")

        assert bandpass_idx == 11
        assert notch_idx == 0

    def test_get_exact_filter_indices_500hz(self):
        """Test filter index lookup for 500 Hz."""
        config = {"sampling_rate": "500 Hz"}
        engine = BCIEngine(config=config)

        bandpass_idx, notch_idx = engine._get_exact_filter_indices("0.1 – 60 Hz Bandpass", "50Hz")

        assert bandpass_idx == 35
        assert notch_idx == 2

    def test_get_exact_filter_indices_unknown(self):
        """Test filter index lookup for unknown filters."""
        engine = BCIEngine()

        bandpass_idx, notch_idx = engine._get_exact_filter_indices(
            "Unknown Filter", "Unknown Notch"
        )

        assert bandpass_idx == -1
        assert notch_idx == -1

    def test_filter_matches_name_bandpass(self):
        """Test bandpass filter name matching."""
        engine = BCIEngine()

        filter_info = {"LowerCutoffFrequency": 0.1, "UpperCutoffFrequency": 60.0}

        assert engine._filter_matches_name(filter_info, "0.1 – 60 Hz Bandpass")
        assert not engine._filter_matches_name(filter_info, "0.1 – 50 Hz Bandpass")

    def test_filter_matches_name_highpass(self):
        """Test highpass filter name matching."""
        engine = BCIEngine()

        filter_info = {"LowerCutoffFrequency": 0.1, "UpperCutoffFrequency": 200.0}

        assert engine._filter_matches_name(filter_info, "0.1 Hz Highpass")
        assert not engine._filter_matches_name(filter_info, "0.5 Hz Highpass")

    def test_filter_matches_name_lowpass(self):
        """Test lowpass filter name matching."""
        engine = BCIEngine()

        filter_info = {"LowerCutoffFrequency": 0.1, "UpperCutoffFrequency": 60.0}

        assert engine._filter_matches_name(filter_info, "60 Hz Lowpass")
        assert not engine._filter_matches_name(filter_info, "50 Hz Lowpass")

    def test_filter_matches_name_notch(self):
        """Test notch filter name matching."""
        engine = BCIEngine()

        filter_info = {"LowerCutoffFrequency": 45.0, "UpperCutoffFrequency": 55.0}

        assert engine._filter_matches_name(filter_info, "50Hz")
        assert not engine._filter_matches_name(filter_info, "60Hz")

    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    @patch("csv.writer")
    def test_start_recording(self, mock_csv_writer, mock_file, mock_makedirs):
        """Test starting recording."""
        engine = BCIEngine()
        engine._running = True  # Simulate streaming active

        engine.start_recording("test.csv")

        mock_makedirs.assert_called_once_with("airobo_trainer/output", exist_ok=True)
        mock_file.assert_called_once()
        mock_csv_writer.assert_called_once()
        assert engine._recording is True
        assert engine._csv_writer is not None

    def test_start_recording_not_streaming(self):
        """Test starting recording when not streaming raises error."""
        engine = BCIEngine()

        with pytest.raises(RuntimeError, match="Cannot start recording: streaming not active"):
            engine.start_recording()

    @patch("builtins.open")
    def test_stop_recording(self, mock_file):
        """Test stopping recording."""
        mock_csv_file = Mock()
        mock_file.return_value = mock_csv_file

        engine = BCIEngine()
        engine._recording = True
        engine._csv_file = mock_csv_file
        engine._csv_writer = Mock()

        engine.stop_recording()

        assert engine._recording is False
        assert engine._csv_file is None
        assert engine._csv_writer is None
        mock_csv_file.close.assert_called_once()

    def test_set_data_path(self):
        """Test setting data path."""
        engine = BCIEngine()
        engine.set_data_path("new/path")

        assert engine.data_path == "new/path"

    def test_is_recording(self):
        """Test recording status check."""
        engine = BCIEngine()

        assert engine.is_recording() is False

        engine._recording = True
        assert engine.is_recording() is True

    def test_is_streaming(self):
        """Test streaming status check."""
        engine = BCIEngine()

        assert engine.is_streaming() is False

        engine._running = True
        assert engine.is_streaming() is True

    @patch("threading.Thread")
    @patch("numpy.vstack")
    def test_start_streaming_with_callback(self, mock_vstack, mock_thread):
        """Test starting streaming with callback."""
        mock_callback = Mock()
        engine = BCIEngine()

        # Mock the device
        engine.device = Mock()

        engine.start_streaming(mock_callback)

        assert engine._running is True
        mock_thread.assert_called_once()

    def test_stop_streaming(self):
        """Test stopping streaming."""
        engine = BCIEngine()
        engine._running = True
        engine.device = Mock()

        engine.stop()

        assert engine._running is False
        engine.device.StopStreaming.assert_called_once()

    def test_close_device(self):
        """Test closing device connection."""
        engine = BCIEngine()
        mock_device = Mock()
        engine.device = mock_device

        engine.close()

        mock_device.Close.assert_called_once()
        assert not hasattr(engine, "device")
