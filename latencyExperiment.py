
"""
LCRAT scheme latency analysis experiment.
"""

import pandas as pd
import matplotlib.pyplot as plt

from LCRATTransmitter import LCRATTransmitter
from channel import PacketLossChannel
from receiver import AuthenticationReceiver


def generate_adsb_messages(number):
    return ["8D40621D58C382D690C8AC2863A7"] * number


def run_single_experiment(messages, loss_rate, seed=1):

    tx = LCRATTransmitter(
    transmission_interval=1/6,   # 6 Hz
    key_interval=5.0,
)

    packets = tx.transmit(messages)

    channel = PacketLossChannel(
        loss_rate=loss_rate,
        seed=seed,
    )

    received_packets = channel.transmit_all(packets)

    rx = AuthenticationReceiver()

    for packet in received_packets:
        rx.receive_packet(packet)

    results = rx.get_authentication_results()

    delays = [
        result.authentication_delay
        for result in results
    ]

    mean_latency = (
        sum(delays) / len(delays)
        if delays else None
    )

    return {
        "Loss Rate": loss_rate,
        "Mean Authentication Delay (s)": mean_latency,
        "Authenticated Messages": len(results),
        "Authentication Coverage": (
            len(results) / len(messages)
        ),
    }


def plot_latency(df):

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

    df = pd.DataFrame(results)

    df.to_csv(
        "latency_results.csv",
        index=False,
    )

    plot_latency(df)


if __name__ == "__main__":
    run_experiment()
