# Research Project Simulator

A discrete packet-level simulator for evaluating TESLA-based ADS-B authentication schemes under packet-loss conditions.

This simulator is developed to analyze the authentication performance of the proposed **Lightweight Compatible Resilient Authentication with TESLA (LCRAT)** architecture and compare it with the existing **Compatible Authenticated Bandwidth-efficient Broadcast for ADS-B (CABBA)** scheme.

The simulator focuses on the impact of packet loss on authentication robustness and latency. Physical-layer effects, propagation delay, and cryptographic computation overhead are abstracted away.

---

# Features

- Packet-level simulation of ADS-B authentication schemes
- Simulation of LCRAT and CABBA authentication architectures
- Configurable ADS-B transmission interval
- Configurable TESLA key disclosure interval
- Configurable packet loss probability
- Reproducible experiments using random seeds
- Authentication latency evaluation under different packet-loss conditions
- Automatic CSV result generation
- Authentication visualization

---

# Project Structure

```
Research_project_simulator/

│
├── packet.py
│   └── Definition of authentication packet structures
│
├── LCRATTransmitter.py
│   └── LCRAT Type A packet transmitter
│
├── CABBATransmitter.py
│   └── CABBA Type A and Type B1 packet transmitter
│
├── receiver.py
│   └── Authentication receiver
│
├── channel.py
│   └── Packet loss channel simulator
│
├── latencyExperiment.py
│   └── Authentication latency evaluation experiment
│
└── robustnessExperiment.py
    └── Authentication robustness evalutaion experiment
```

---

# Simulator Architecture

The simulator contains three main stages:

```
ADS-B Transmitter
        |
        v
Packet Loss Channel
        |
        v
Authentication Receiver
        |
        v
Performance Evaluation
```

The transmitter generates authentication packets according to the selected scheme. The packet loss channel randomly removes packets according to the configured loss probability. The receiver processes successfully received packets and determines authentication completion time.

---

# Packet Definition

The packet structures are implemented in:

```
packet.py
```

The file defines the logical packet formats used by both LCRAT and CABBA.

## LCRAT Type A Packet

The proposed LCRAT packet integrates message authentication code (MAC) and TESLA key disclosure into the same phase-overlay packet.

The corresponding data structure is:

```python
LCRATTypeA
```

It contains:

- ADS-B message
- Authentication information including MAC and Previous TESLA key disclosure

The simulated Authentication information fields are:

```
MAC                         32 bits
Sequence Number              8 bits
Previous Key Disclosure     128 bits
Interval ID & Flags          12 bits
Reserved / Trust Refresh     24 bits

Total                       204 bits
```
---

## CABBA Packet Structures

CABBA uses two packet types.

### CABBA Type A

A Type A packet is transmitted together with every ADS-B message.

The corresponding structure is:

```python
CABBATypeA
```

It contains:

- ADS-B message
- MAC

---

### CABBA Type B1

A Type B1 packet is periodically transmitted for TESLA key disclosure.

The corresponding structure is:

```python
CABBATypeB
```

It contains the disclosed authentication key.

---

# LCRAT Transmitter

File:

```
LCRATTransmitter.py
```

The `LCRATTransmitter` generates LCRAT Type A packets.

The transmitter is initialized using:

```python
LCRATTransmitter(
    transmission_interval,
    key_interval
)
```

Parameters:

## transmission_interval

ADS-B message transmission period.

Example:

```python
transmission_interval = 0.5
```

means one ADS-B packet is generated every 0.5 seconds.

---

## key_interval

TESLA authentication key interval duration.

Example:

```python
key_interval = 10.0
```

means one TESLA key is associated with a 10-second interval.

---

The transmitter automatically determines:

- Required authentication key ID
- Previous key disclosure
- Sequence number

The main transmission function is:

```python
transmit()
```

which converts ADS-B messages into LCRAT authentication packets.

---

# CABBA Transmitter

File:

```
CABBATransmitter.py
```

The `CABBATransmitter` implements the packet generation process of CABBA.

Initialization:

```python
CABBATransmitter(
    transmission_interval,
    type_b_interval
)
```

Parameters:

## transmission_interval

ADS-B message transmission period.

## type_b_interval

Interval for transmitting CABBA Type B1 key disclosure packets.

---

The transmitter generates:

- Type A packets for every ADS-B message
- Type B1 packets periodically

The generated packets are sorted according to transmission time.

Main function:

```python
transmit()
```

---

# Packet Loss Channel

File:

```
channel.py
```

The `PacketLossChannel` simulates a simplified lossy communication environment.

The model assumes:

- No propagation delay
- No physical-layer errors
- Packet reception is binary

A packet either:

- arrives successfully
- is completely lost

---

The channel is configured by:

```python
PacketLossChannel(
    loss_rate,
    seed
)
```

Parameters:

## loss_rate

Packet loss probability.

Example:

```python
loss_rate = 0.1
```

represents a 10% packet loss rate.

---

## seed

Random seed used for reproducible experiments.

Example:

```python
seed = 1
```

---

The main transmission functions are:

```python
transmit()
```

Simulates transmission of a single packet.

```python
transmit_all()
```

Simulates transmission of a packet list and removes lost packets.

---

# Authentication Latency Experiment

File:

```
latencyExperiment.py
```

This script evaluates authentication latency under different packet-loss conditions.

The experiment workflow is:

```
Generate ADS-B Messages

        |
        v

LCRATTransmitter

        |
        v

PacketLossChannel

        |
        v

AuthenticationReceiver

        |
        v

Latency Calculation
```

---

# Experiment Configuration

The experiment generates ADS-B messages using:

```python
generate_adsb_messages()
```

The default experiment uses:

```python
transmission_interval = 1/6
```

which corresponds to 6 ADS-B messages per second

The TESLA key interval is configured as:

```python
key_interval = 5.0
```

The evaluated packet loss rates are 0% to 95% with an increment of 5%.

All the above parameters can be modified by users according to their experimental requirements.

---

# Experiment Output

The experiment produces:

## CSV Result

```
latency_results.csv
```

Containing:

| Parameter | Description |
|-|-|
| Loss Rate | Packet loss probability |
| Mean Authentication Delay (s) | Average authentication completion delay |
| Authenticated Messages | Number of authenticated messages |
| Authentication Coverage | Ratio of successfully authenticated messages |

---

## Latency Figure

The experiment generates:

```
mean_authentication_latency.png
```

which shows the relationship between packet loss rate and authentication latency.

---

# Authentication Robustness Experiment

File:

```
robustnessExperiment.py
```

This script evaluates authentication robustness of LCRAT and CABBA under different packet-loss conditions.

Unlike the latency experiment, which focuses on authentication delay, this experiment evaluates whether ADS-B messages can still be successfully authenticated when packets are lost.

The experiment measures:

- Authentication Success Rate (ASR)
- Overall Authentication Coverage

---

# Robustness Experiment Workflow

```
Generate ADS-B Messages

        |
        v

LCRAT & CABBA Transmitter

        |
        v

PacketLossChannel

        |
        v

AuthenticationReceiver

        |
        v

Robustness Evaluation
```

For each packet loss rate, LCRAT and CABBA are evaluated under identical channel conditions.

---

# Evaluation Metrics

## Authentication Success Rate (ASR)

The Authentication Success Rate represents the percentage of received packets that are successfully authenticated.

For LCRAT:

```
ASR = authenticated messages / received packets
```

For CABBA:

```
ASR = authenticated messages / received Type A packets
```

Only Type A packets are considered for CABBA because they correspond directly to ADS-B message transmissions.

---

## Overall Authentication Coverage

Overall Authentication Coverage represents the percentage of transmitted ADS-B messages that are successfully authenticated.

```
Overall Coverage = authenticated messages / transmitted ADS-B messages
```

This metric reflects the availability of authenticated surveillance information under packet-loss conditions.

---

# Robustness Experiment Configuration

The robustness experiment uses the same configurable parameters as the latency experiment.

Default ADS-B transmission rate:

```python
transmission_interval = 1/6
```

TESLA key interval:

For LCRAT:

```python
key_interval = 5.0
```

For CABBA:

```python
type_b_interval = 5.0
```

The evaluated packet loss rates are 0% to 95% with an increment of 5%.

All the above parameters can be modified by users according to their experimental requirements.

---

# Robustness Experiment Output

The experiment generates:

CSV result:

```
robustness_results.csv
```

The file contains:

| Parameter | Description |
|-|-|
| Loss Rate | Packet loss probability |
| LCRAT ASR | LCRAT authentication success rate |
| CABBA ASR | CABBA authentication success rate |
| LCRAT Coverage | LCRAT authentication coverage |
| CABBA Coverage | CABBA authentication coverage |

---

Generated figures:

## ASR Comparison

Output:

```
ASR_comparison.png
```

This figure compares authentication success rate between LCRAT and CABBA.

---

## Coverage Comparison

Output:

```
Coverage_comparison.png
```

This figure compares authentication coverage between LCRAT and CABBA.

---

# Running the Simulator

## Run Latency Experiment

```bash
py latencyExperiment.py
```

---

## Run Robustness Experiment

```bash
py robustnessExperiment.py
```

---

The simulator will:

1. Generate ADS-B messages
2. Create authentication packets
3. Apply packet loss
4. Perform authentication processing
5. Calculate performance metrics
6. Save numerical results and figures

---



# Installation

## Requirements

Install required packages:

```bash
pip install pandas matplotlib
```

---

# Simulation Assumptions

The simulator focuses on packet-loss effects and therefore does not model:

- Physical-layer modulation errors
- Propagation delay
- Cryptographic computation time

Instead, authentication completion is determined by the arrival time of the required TESLA key disclosure.

---

# Research Purpose

This simulator is designed for research on lightweight ADS-B authentication mechanisms.

The main objectives are:

- Evaluate authentication robustness under packet-loss conditions
- Compare LCRAT and CABBA authentication performance
- Analyze authentication latency degradation
- Investigate communication-efficient TESLA-based authentication designs

---

# License

This project is intended for academic research and evaluation purposes.
