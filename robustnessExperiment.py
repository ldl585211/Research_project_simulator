'''
Authentication robustness experiment for LCRAT and CABBA.

This module compares the authentication robustness of LCRAT and CABBA
under different packet-loss conditions.

Two metrics are evaluated:
Authentication Success Rate (ASR)
success_rate = authenticated/received(in CABBA, type A only)

    
Overall Authentication Coverage
overall_coverage = authenticated/transmitted(in CABBA, type A only)

It stores the numerical results in a CSV file, and generates comparison plots.
'''

from packet import CABBATypeA
from LCRATTransmitter import LCRATTransmitter
from CABBATransmitter import CABBATransmitter
from channel import PacketLossChannel
from receiver import AuthenticationReceiver
import csv
import matplotlib.pyplot as plt


def generate_adsb_messages(number):
    """
    Generate a list of example ADS-B messages.
    """
    return ["8D40621D58C382D690C8AC2863A7"] * number


def run_lcrat_experiment(adsb_messages, loss_rate, seed=1):
    """
    Run one LCRAT robustness experiment for a given packet-loss rate.
    """

    # Configure the LCRAT transmitter.
    tx = LCRATTransmitter(
        transmission_interval=1/6,   # 6 Hz
        key_interval=5.0,            # 5.0 s
    )

    # Generate LCRAT packets from the ADS-B message sequence.
    packets = tx.transmit(adsb_messages)

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

    #Calculate the Authentication Success Rate and Overall Authentication Coverage:
    received_messages = len(received_packets)
    authenticated = len(rx.authentication_results)

    success_rate = (
        authenticated / received_messages
        if received_messages > 0 else 0
    )

    overall_coverage = (
        authenticated / len(adsb_messages)
        if len(adsb_messages) > 0 else 0
    )

    return {
        "authenticated": authenticated,
        "total_received": received_messages,
        "success_rate": success_rate,
        "overall_coverage": overall_coverage,
    }


def run_cabba_experiment(adsb_messages, loss_rate, seed=1):

    # Configure the CABBA transmitter.
    tx = CABBATransmitter(
        transmission_interval=1/6,   # 6 Hz
        type_b_interval=5.0,
    )

    # Generate CABBA packets from the ADS-B message sequence.
    packets = tx.transmit(adsb_messages)

    # Configure the packet-loss channel.
    channel = PacketLossChannel(
        loss_rate=loss_rate,
        seed=seed,
    )

    # Simulate packet transmission over the lossy channel and remove lost packets.
    received_packets = channel.transmit_all(packets)

    # Initialize the authentication receiver.
    rx = AuthenticationReceiver()

    # Process all successfully received CABBA packets.
    # Count only received CABBA Type A packets because they correspond
    # directly to ADS-B message transmissions.
    received_type_a = 0

    for packet in received_packets:

        if isinstance(packet, CABBATypeA):
            received_type_a += 1

        rx.receive_packet(packet)

    #Calculate the Authentication Success Rate and Overall Authentication Coverage:
    authenticated = len(rx.authentication_results)

    success_rate = (
        authenticated / received_type_a
        if received_type_a > 0 else 0
    )

    overall_coverage = (
        authenticated / len(adsb_messages)
        if len(adsb_messages) > 0 else 0
    )

    return {
        "authenticated": authenticated,
        "total_received_type_a": received_type_a,
        "success_rate": success_rate,
        "overall_coverage": overall_coverage,
    }


def run_robustness_experiment():
    """
    Run the complete robustness comparison experiment.
    """
    # Generate the ADS-B message dataset used for all packet-loss rates.
    # Each key interval contains 30 packets, so 100020 is chosen as a multiple of 30.
    # One additional packet is added to disclose the key for the final interval,
    # resulting in a total of 100021 packets.

    adsb_messages = generate_adsb_messages(100021)

    loss_rates = [
        0.0,
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

    print(
        "Loss Rate | "
        "LCRAT ASR | CABBA ASR |"
        " LCRAT Coverage | CABBA Coverage"
    )
    print("-" * 90)

    # Run LCRAT and CABBA experiments for each packet-loss rate.
    for loss_rate in loss_rates:

        lcrat = run_lcrat_experiment(
            adsb_messages,
            loss_rate,
            seed=1,
        )

        cabba = run_cabba_experiment(
            adsb_messages,
            loss_rate,
            seed=1,
        )

        row = {
            "Loss Rate": loss_rate,
            "LCRAT ASR": lcrat["success_rate"],
            "CABBA ASR": cabba["success_rate"],
            "LCRAT Coverage": lcrat["overall_coverage"],
            "CABBA Coverage": cabba["overall_coverage"],
        }

        results.append(row)

        print(
            f"{loss_rate:8.0%} | "
            f"{lcrat['success_rate']:.4f} | "
            f"{cabba['success_rate']:.4f} | "
            f"{lcrat['overall_coverage']:.4f} | "
            f"{cabba['overall_coverage']:.4f}"
        )

    # Save CSV result
    csv_file = "robustness_results.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"\\nCSV saved: {csv_file}")

    loss = [r["Loss Rate"] for r in results]

    # Figure 1: Authentication Success Rate comparison
    plt.figure(figsize=(8, 5))

    plt.plot(
        loss,
        [r["LCRAT ASR"] for r in results],
        marker="o",
        label="LCRAT ASR"
    )

    plt.plot(
        loss,
        [r["CABBA ASR"] for r in results],
        marker="s",
        label="CABBA ASR"
    )

    plt.xlabel("Loss Rate")
    plt.ylabel("Authentication Success Rate (ASR)")
    plt.title("ASR vs Packet Loss Rate")

    # Axis settings
    plt.xlim(-0.02, 0.97)
    plt.ylim(0, 1.05)

    plt.xticks(
        loss,
        [f"{x:.0%}" for x in loss],
        rotation=45,
        )

    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        "ASR_comparison.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    # Figure 2: Overall Authentication Coverage comparison
    plt.figure(figsize=(8, 5))

    plt.plot(
        loss,
        [r["LCRAT Coverage"] for r in results],
        marker="o",
        label="LCRAT Coverage"
    )

    plt.plot(
        loss,
        [r["CABBA Coverage"] for r in results],
        marker="s",
        label="CABBA Coverage"
    )

    plt.xlabel("Loss Rate")
    plt.ylabel("Authentication Coverage")
    plt.title("Coverage vs Packet Loss Rate")

    # Axis settings
    plt.xlim(-0.02, 0.97)
    plt.ylim(0, 1.05)

    plt.xticks(
        loss,
        [f"{x:.0%}" for x in loss],
        rotation=45,
    )

    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig(
        "Coverage_comparison.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print("Figures saved:")
    print(" - ASR_comparison.png")
    print(" - Coverage_comparison.png")


if __name__ == "__main__":
    run_robustness_experiment()
