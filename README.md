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
- Authentication latency visualization

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
│   └── CABBA Type A and Type B packet transmitter
│
├── channel.py
│   └── Packet loss channel simulator
│
├── latencyExperiment.py
│   └── Authentication latency evaluation experiment
│
└── receiver.py
    └── Authentication receiver
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

The proposed LCRAT packet integrates message authentication and TESLA key disclosure into the same phase-overlay packet.

The simulated fields are:

```
MAC                         32 bits
Sequence Number              8 bits
Previous Key Disclosure     128 bits
Interval ID & Flags          12 bits
Reserved / Trust Refresh     24 bits

Total                       204 bits
```

The corresponding data structure is:

```python
LCRATTypeA
```

It contains:

- ADS-B message
- Sequence number
- Previous TESLA key disclosure
- Authentication flags

---

## CABBA Packet Structures

CABBA uses two packet types.

### CABBA Type A

A Type A packet is transmitted together with every ADS-B message.

It contains:

- ADS-B message
- Sequence number
- MAC placeholder

The corresponding structure is:

```python
CABBATypeA
```

---

### CABBA Type B

A Type B packet is periodically transmitted for TESLA key disclosure.

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

Interval for transmitting CABBA Type B key disclosure packets.

---

The transmitter generates:

- Type A packets for every ADS-B message
- Type B packets periodically

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

which corresponds to:

```
6 ADS-B messages per second
```

The TESLA key interval is configured as:

```python
key_interval = 5.0
```

---

The evaluated packet loss rates are:

```
0%
5%
10%
15%
...
95%
```

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

# Installation

## Requirements

Python >= 3.10


Install required packages:

```bash
pip install pandas matplotlib
```

---

# Running the Experiment

Run:

```bash
python latencyExperiment.py
```

The simulator will:

1. Generate ADS-B messages
2. Create LCRAT authentication packets
3. Apply packet loss
4. Perform authentication processing
5. Calculate authentication latency
6. Export results

---

# Simulation Assumptions

The simulator focuses on packet-loss effects and therefore does not model:

- Physical-layer modulation errors
- Channel fading
- Propagation delay
- Doppler effects
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
