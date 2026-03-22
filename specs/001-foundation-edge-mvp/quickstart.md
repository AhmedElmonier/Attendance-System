# Quickstart: Foundation & Edge MVP (Phase 1)

## Local Environment (Laptop/WSL2)

### 1. Python Virtual Environment
```bash
# In your WSL2 or Windows terminal
python -m venv venv
source venv/bin/activate  # Or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Required Core Dependencies
- `opencv-python`: For camera access and frame processing.
- `mediapipe`: For Euler angle detection.
- `sqlcipher-lib`: For encrypted local persistence.
- `hnswlib`: For sub-200ms vector matching.

### 3. Running the Foundation MVP (Simulation)
```bash
# Run the enrollment simulator (uses webcam)
python edge/src/main.py --mode enroll --user "Ahmed"

# Run the attendance simulator
python edge/src/main.py --mode clock-in
```

## Hardware Abstraction Layer (HAL) Note
The code will automatically detect if it is running on a standard laptop (using DirectShow/V4L2) or a Raspberry Pi (using CSI/USB). You can manually override this in `config.yaml`:
```yaml
hal:
  input: "webcam" # Options: webcam, rpi_cam, jetson_csi
  io: "simulated" # Options: simulated, gpio
```
