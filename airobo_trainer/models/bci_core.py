"""
BCI Core Module - BCI Headset Engine and Data Management
Provides BCI headset connectivity and data streaming functionality
"""

import pygds
import numpy as np
import threading
import csv
import os
from datetime import datetime
from scipy import signal


class AttentionCalculator:
    """
    Simplified attention/intention calculator based on motor cortex activity.

    Calculates left/right hand intention from 0-100 based on EEG band power analysis.
    """

    def __init__(self, sampling_rate=500):
        self.fs = sampling_rate
        self.buffer_size = 1000  # 2 seconds at 500Hz
        self.left_buffer = []
        self.right_buffer = []
        self.center_buffer = []

    def add_sample(self, eeg_data):
        """
        Add new EEG sample for attention calculation.

        Args:
            eeg_data: List/array of electrode values in order [C3, CZ, C4]
        """
        if len(eeg_data) >= 3:
            self.left_buffer.append(float(eeg_data[0]))  # C3
            self.center_buffer.append(float(eeg_data[1]))  # CZ
            self.right_buffer.append(float(eeg_data[2]))  # C4

            # Keep buffer size limited
            if len(self.left_buffer) > self.buffer_size:
                self.left_buffer.pop(0)
                self.center_buffer.pop(0)
                self.right_buffer.pop(0)

    def calculate_attention(self):
        """
        Calculate attention/intention levels for left and right hands.

        Returns:
            tuple: (left_attention, right_attention) - values from 0-100
        """
        if len(self.left_buffer) < 100:  # Need minimum data
            return 50, 50  # Neutral

        try:
            # Calculate band power in mu (8-12 Hz) and beta (13-30 Hz) bands
            left_power = self._calculate_motor_power(self.left_buffer)
            right_power = self._calculate_motor_power(self.right_buffer)

            # Calculate laterality index (relative power difference)
            # Positive = right intention, Negative = left intention
            if left_power + right_power > 0:
                laterality = (right_power - left_power) / (left_power + right_power)
            else:
                laterality = 0

            # Convert to 0-100 scale
            # laterality ranges from -1 to 1, convert to 0-100 where:
            # 0 = strong left intention, 50 = neutral, 100 = strong right intention
            left_attention = max(0, min(100, 50 - (laterality * 50)))
            right_attention = max(0, min(100, 50 + (laterality * 50)))

            return int(left_attention), int(right_attention)

        except Exception as e:
            print(f"Attention calculation error: {e}")
            return 50, 50

    def _calculate_motor_power(self, eeg_buffer):
        """
        Calculate motor cortex band power (mu + beta bands).

        Args:
            eeg_buffer: List of EEG samples

        Returns:
            float: Band power value
        """
        if len(eeg_buffer) < 100:
            return 0

        # Convert to numpy array
        data = np.array(eeg_buffer)

        # Design bandpass filter for mu (8-12 Hz) and beta (13-30 Hz) bands
        # Combined as motor-related frequencies
        nyquist = self.fs / 2
        low = 8 / nyquist
        high = 30 / nyquist

        # Apply bandpass filter
        b, a = signal.butter(4, [low, high], btype="band")
        filtered_data = signal.filtfilt(b, a, data)

        # Calculate RMS power
        power = np.sqrt(np.mean(filtered_data**2))

        return float(power)


class BCIEngine:
    """
    BCI Engine for headset connectivity and data streaming.

    Handles connection to BCI headset, data streaming, and recording functionality.
    """

    # Bandpass filter mapping
    BANDPASS_FILTERS = {
        "0.1 – 30 Hz Bandpass": 0,
        "0.1 – 50 Hz Bandpass": 1,
        "0.5 – 30 Hz Bandpass": 2,
        "0.5 – 50 Hz Bandpass": 3,
        "1 – 30 Hz Bandpass": 4,
        "1 – 50 Hz Bandpass": 5,
        "2 – 30 Hz Bandpass": 6,
        "2 – 50 Hz Bandpass": 7,
        "0.1 Hz Highpass": 8,
        "0.5 Hz Highpass": 9,
        "1 Hz Highpass": 10,
        "2 Hz Highpass": 11,
        "20 Hz Lowpass": 12,
        "50 Hz Lowpass": 13,
        "None - No filter applied": -1,
    }

    # Notch filter mapping
    NOTCH_FILTERS = {
        "None": -1,
        "50Hz": 0,
        "60Hz": 1,
        "50Hz + 60Hz": 2,
        "50Hz (Cascading)": 3,
        "60Hz (Cascading)": 4,
    }

    # Electrode mapping: index -> electrode name
    ELECTRODE_NAMES = [
        "FP1",
        "FP2",
        "AF3",
        "AF4",
        "F7",
        "F3",
        "FZ",
        "F4",
        "F8",
        "FC5",
        "FC1",
        "FC2",
        "FC6",
        "T7",
        "C3",
        "CZ",
        "C4",
        "T8",
        "CP5",
        "CP1",
        "CP2",
        "CP6",
        "P7",
        "P3",
        "PZ",
        "P4",
        "P8",
        "PO7",
        "PO3",
        "PO4",
        "PO8",
        "OZ",
    ]

    def __init__(self, serial_number="NP-2025.07.10", config=None):
        """
        Initialize the BCI engine.

        Args:
            serial_number: Serial number of the BCI headset
            config: Dictionary with BCI configuration parameters
        """
        self.SERIAL = serial_number
        self.config = config or {}
        self.FS = int(
            self.config.get("sampling_rate", "250 Hz").split()[0]
        )  # Extract number from "250 Hz"
        self.BLOCK_SIZE = 8
        self.NUMBEROFSCANS = 0
        self.raw_data = []
        self.device = None
        self._running = False
        self._recording = False
        self._csv_writer = None
        self._csv_file = None
        self.data_path = self.config.get("output_path", "airobo_trainer/output")

        # Get selected electrodes (default to C3, CZ, C4 if none selected)
        self.selected_electrodes = self.config.get(
            "selected_electrodes", {14, 15, 16}
        )  # C3, CZ, C4
        if not self.selected_electrodes:
            self.selected_electrodes = {14, 15, 16}  # Default fallback

        # Create electrode name mapping for selected electrodes
        self.selected_electrode_names = [
            self.ELECTRODE_NAMES[i] for i in sorted(self.selected_electrodes)
        ]
        print(f"Selected electrodes: {self.selected_electrode_names}")

    def connect(self):
        """
        Connect to the BCI headset.

        Initializes the GDS library and sets up the device configuration.
        """
        pygds.Uninitialize()
        pygds.Initialize()

        self.device = pygds.GDS(self.SERIAL)
        self.device.NumberOfScans = self.NUMBEROFSCANS
        self.device.SamplingRate = self.FS
        self.device.CommonGround = [1] * 4
        self.device.CommonReference = [1] * 4
        self.device.ShortCutEnabled = 1
        self.device.CounterEnabled = 0
        self.device.TriggerEnabled = 1

        # Get filter settings from config and find appropriate indices for current sampling rate
        bandpass_filter_name = self.config.get("bandpass_filter", "None - No filter applied")
        notch_filter_name = self.config.get("notch_filter", "None")

        # Use exact filter mappings based on device query results
        bandpass_index, notch_index = self._get_exact_filter_indices(
            bandpass_filter_name, notch_filter_name
        )

        print(
            f"BCI Config - Sampling Rate: {self.FS} Hz, Bandpass: {bandpass_filter_name} (index: {bandpass_index}), Notch: {notch_filter_name} (index: {notch_index})"
        )

        for ch in self.device.Channels:
            ch.Acquire = 1
            ch.BandpassFilterIndex = bandpass_index
            ch.NotchFilterIndex = notch_index
            ch.BipolarChannel = 0

        self.device.SetConfiguration()

    def start_streaming(self, raw_callback=None):
        """
        Start data streaming from the headset.

        Args:
            raw_callback: Optional callback function for processing raw data blocks
        """
        self._running = True

        def gds_callback(block):
            if not self._running:
                return False

            # Filter block to only include selected electrodes
            if self.selected_electrodes:
                selected_indices = sorted(self.selected_electrodes)
                filtered_block = block[:, selected_indices]
            else:
                filtered_block = block

            # Append the filtered block to raw_data
            if len(self.raw_data) == 0:
                self.raw_data = np.vstack(filtered_block.copy())
            else:
                self.raw_data = np.vstack((self.raw_data, filtered_block.copy()))

            # Record data if recording is active
            if self._recording and self._csv_writer:
                # Write each sample in the filtered block (no timestamp needed)
                for sample_idx in range(filtered_block.shape[0]):
                    row = filtered_block[sample_idx].tolist()
                    self._csv_writer.writerow(row)

            if raw_callback:
                raw_callback(filtered_block)
            return self._running

        def stream_thread():
            self.device.GetData(self.BLOCK_SIZE, gds_callback)

        self._stream_thread = threading.Thread(target=stream_thread)
        self._stream_thread.start()

    def stop(self):
        """
        Stop data streaming.
        """
        self._running = False
        try:
            self.device.StopStreaming()
        except Exception as e:
            print(f"Error stopping streaming: {e}")
        # Do not join here to avoid blocking the GUI thread

    def start_recording(self, filename=None):
        """
        Start recording data to CSV file.

        Args:
            filename: Optional filename for the CSV file
        """
        if not self._running:
            raise RuntimeError("Cannot start recording: streaming not active")

        # Create output directory if it doesn't exist
        os.makedirs(self.data_path, exist_ok=True)

        # Generate filename with timestamp if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
            filename = f"raw_eeg_{timestamp}.csv"

        filepath = os.path.join(self.data_path, filename)

        # Open CSV file and write header
        self._csv_file = open(filepath, "w", newline="")
        self._csv_writer = csv.writer(self._csv_file)

        # Write header with selected electrode names only
        header = self.selected_electrode_names
        self._csv_writer.writerow(header)

        self._recording = True
        print(f"Started recording to {filepath}")

    def stop_recording(self):
        """
        Stop recording data to CSV file.
        """
        if self._recording:
            self._recording = False
            if self._csv_file:
                self._csv_file.close()
                self._csv_file = None
                self._csv_writer = None
            print("Stopped recording")

    def close(self):
        """
        Close the BCI device connection.
        """
        if self.device:
            self.device.Close()
            del self.device

    def set_data_path(self, path):
        """
        Set the data output path.

        Args:
            path: Directory path for saving data files
        """
        self.data_path = path

    def is_recording(self):
        """
        Check if currently recording.

        Returns:
            bool: True if recording is active
        """
        return self._recording

    def is_streaming(self):
        """
        Check if currently streaming.

        Returns:
            bool: True if streaming is active
        """
        return self._running

    def _get_exact_filter_indices(self, bandpass_filter_name, notch_filter_name):
        """
        Get exact filter indices based on device query results.

        Uses the actual filter mappings discovered from querying the BCI device.
        """
        # Exact mappings based on device query for your specific BCI headset
        if self.FS == 250:
            # 250 Hz sampling rate mappings
            bandpass_mapping = {
                "0.1 – 30 Hz Bandpass": 10,
                "0.1 – 60 Hz Bandpass": 11,
                "0.5 – 30 Hz Bandpass": 13,
                "0.5 – 60 Hz Bandpass": 14,
                "2.0 – 30 Hz Bandpass": 16,
                "2.0 – 60 Hz Bandpass": 17,
                "5.0 – 30 Hz Bandpass": 19,
                "5.0 – 60 Hz Bandpass": 20,
                "0.1 Hz Highpass": 0,
                "1.0 Hz Highpass": 1,
                "2.0 Hz Highpass": 2,
                "5.0 Hz Highpass": 3,
                "30 Hz Lowpass": 4,
                "60 Hz Lowpass": 5,
                "100 Hz Lowpass": 6,
            }
        elif self.FS == 500:
            # 500 Hz sampling rate mappings
            bandpass_mapping = {
                "0.1 – 30 Hz Bandpass": 34,
                "0.1 – 60 Hz Bandpass": 35,
                "0.1 – 100 Hz Bandpass": 36,
                "0.1 – 200 Hz Bandpass": 37,
                "0.5 – 30 Hz Bandpass": 38,
                "0.5 – 60 Hz Bandpass": 39,
                "0.5 – 100 Hz Bandpass": 40,
                "0.5 – 200 Hz Bandpass": 41,
                "2.0 – 30 Hz Bandpass": 42,
                "2.0 – 60 Hz Bandpass": 43,
                "2.0 – 100 Hz Bandpass": 44,
                "2.0 – 200 Hz Bandpass": 45,
                "5.0 – 30 Hz Bandpass": 46,
                "5.0 – 60 Hz Bandpass": 47,
                "5.0 – 100 Hz Bandpass": 48,
                "5.0 – 200 Hz Bandpass": 49,
                "0.1 Hz Highpass": 22,
                "1.0 Hz Highpass": 23,
                "2.0 Hz Highpass": 24,
                "5.0 Hz Highpass": 25,
                "30 Hz Lowpass": 26,
                "60 Hz Lowpass": 27,
                "100 Hz Lowpass": 28,
                "200 Hz Lowpass": 29,
            }
        else:
            bandpass_mapping = {}

        # Notch filter mappings (same for both sampling rates based on device query)
        notch_mapping = {
            "50Hz": 0 if self.FS == 250 else 2,  # Index 0 for 250Hz, 2 for 500Hz
            "60Hz": 1 if self.FS == 250 else 3,  # Index 1 for 250Hz, 3 for 500Hz
        }

        # Get the indices
        bandpass_index = bandpass_mapping.get(bandpass_filter_name, -1)
        notch_index = notch_mapping.get(notch_filter_name, -1)

        return bandpass_index, notch_index

    def _filter_matches_name(self, filter_info, filter_name):
        """
        Check if a filter info matches a filter name from the config.

        Based on the actual device filter data queried from the BCI headset.
        """
        # Get filter properties
        lower_cutoff = filter_info.get("LowerCutoffFrequency", 0)
        upper_cutoff = filter_info.get("UpperCutoffFrequency", 0)

        # Match bandpass filters
        if "Bandpass" in filter_name and " – " in filter_name:
            try:
                parts = filter_name.replace(" Hz Bandpass", "").split(" – ")
                expected_lower = float(parts[0])
                expected_upper = float(parts[1])

                return (
                    abs(lower_cutoff - expected_lower) < 0.1
                    and abs(upper_cutoff - expected_upper) < 0.1
                )
            except (ValueError, IndexError):
                return False

        # Match highpass filters
        elif "Highpass" in filter_name:
            try:
                freq_str = filter_name.replace(" Hz Highpass", "")
                expected_freq = float(freq_str)

                # Highpass has low lower cutoff and high upper cutoff
                return abs(lower_cutoff - expected_freq) < 0.1 and upper_cutoff > 100
            except ValueError:
                return False

        # Match lowpass filters
        elif "Lowpass" in filter_name:
            try:
                freq_str = filter_name.replace(" Hz Lowpass", "")
                expected_freq = float(freq_str)

                # Lowpass has low lower cutoff and specific upper cutoff
                return lower_cutoff < 1 and abs(upper_cutoff - expected_freq) < 0.1
            except ValueError:
                return False

        # Match notch filters
        elif filter_name in ["50Hz", "60Hz"]:
            expected_center = 50.0 if filter_name == "50Hz" else 60.0
            actual_center = (lower_cutoff + upper_cutoff) / 2

            # Check if center frequency is close to expected (within 5 Hz)
            return abs(actual_center - expected_center) < 5

        return False
