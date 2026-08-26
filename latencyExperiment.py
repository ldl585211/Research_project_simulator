
"""
LCRAT authentication latency experiment.

This module evaluates the mean authentication latency of the LCRAT scheme
under different packet-loss conditions.

The experiment also records the number of authenticated messages and the
overall authentication coverage.

Results are saved to a CSV file and plotted as a latency curve.
"""

import pandas as pd
import matplotlib.pyplot as plt

from LCRATTransmitter import LCRATTransmitter
from channel import PacketLossChannel
from receiver import AuthenticationReceiver


def generate_adsb_messages(number):
    """
    Generate a list of example ADS-B messages.
    """
    return ["8D40621D58C382D690C8AC2863A7"] * number


def run_single_experiment(messages, loss_rate, seed=1):
    """
    Run one LCRAT latency experiment for a given packet-loss rate.
    """

    # Configure the LCRAT transmitter.
    tx = LCRATTransmitter(
    transmission_interval=1/6,   # 6 Hz
    key_interval=5.0,            # 5.0 s
    )

    # Generate LCRAT packets from the ADS-B message sequence.
    packets = tx.transmit(messages)

    # Configure the packet-loss channel.
    channel = PacketLossChannel(
        loss_rate=loss_rate,
        seed=seed,
    )

    # Simulate packet transmission over the lossy channel and remove lost packets.
    received_packets = channel.transmit_all(packets)

    # Initialize the authentication receiver.
    rx = AuthenticationReceiver()

    # Process all successfully received packets.
    for packet in received_packets:
        rx.receive_packet(packet)

    # Retrieve successfully authenticated message results.
    results = rx.get_authentication_results()

    # Extract authentication delay from each authenticated message.
    delays = [
        result.authentication_delay
        for result in results
    ]

    # Calculate the mean authentication latency.
    mean_latency = (
        sum(delays) / len(delays)
        if delays else None
    )

    # Return the performance metrics for this packet-loss rate.
    return {
        "Loss Rate": loss_rate,
        "Mean Authentication Delay (s)": mean_latency,
        "Authenticated Messages": len(results),
        "Authentication Coverage": (
            len(results) / len(messages)
        ),
    }


def plot_latency(df):
    """
    Plot mean authentication latency against packet-loss rate.
    """

    plt.figure(figsize=(7, 5))

    plt.plot(
        df["Loss Rate"],
        df["Mean Authentication Delay (s)"],
        marker="o",
    )

    plt.xlabel("Packet Loss Rate")
    plt.ylabel("Mean Authentication Delay (s)")

    plt.xticks(
        df["Loss Rate"],
        [f"{x:.0%}" for x in df["Loss Rate"]],
        rotation=45
    )

    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        "mean_authentication_latency.png",
        dpi=300,
    )

    plt.close()


def run_experiment():
    """
    Run the complete LCRAT authentication latency experiment.
    """
    # Generate the ADS-B message dataset used for all packet-loss rates.
    # Each key interval contains 30 packets, so 100020 is chosen as a multiple of 30.
    # One additional packet is added to disclose the key for the final interval,
    # resulting in a total of 100021 packets.
    messages = generate_adsb_messages(100021)

    loss_rates = [
        0.00,
        0.05,
        0.10,
        0.15,
        0.20,
        0.25,
        0.30,
        0.35,
        0.40,
        0.45,
        0.50,
        0.55,
        0.60,
        0.65,
        0.70,
        0.75,
        0.80,
        0.85,
        0.90,
        0.95,
    ]

    results = []

    # Run one experiment for each configured packet-loss rate.
    for loss_rate in loss_rates:

        print(
            f"Running loss rate {loss_rate:.0%}"
        )

        results.append(
            run_single_experiment(
                messages,
                loss_rate,
            )
        )

    # Save numerical results to CSV.
    df = pd.DataFrame(results)

    df.to_csv(
        "latency_results.csv",
        index=False,
    )

    # Generate the authentication latency figure.
    plot_latency(df)


if __name__ == "__main__":
    run_experiment()
