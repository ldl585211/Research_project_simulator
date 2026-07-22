'''
Authentication Success Rate (ASR)
success_rate = authenticated/received

    
Overall Authentication Coverage
overall_coverage = authenticated/transmitted
'''

from packet import CABBATypeA
from ProposedTransmitter import PhaseOverlayTransmitter
from CABBATransmitter import CABBATransmitter
from channel import PacketLossChannel
from receiver import AuthenticationReceiver


def generate_adsb_messages(number):
    return ["8D40621D58C382D690C8AC2863A7"] * number


def run_proposed_experiment(adsb_messages, loss_rate, seed=1):
    tx = PhaseOverlayTransmitter(
        transmission_interval=0.5,
        key_interval=10,
    )

    packets = tx.transmit(adsb_messages)

    channel = PacketLossChannel(
        loss_rate=loss_rate,
        seed=seed,
    )

    received_packets = channel.transmit_all(packets)

    rx = AuthenticationReceiver()

    for packet in received_packets:
        rx.receive_packet(packet)

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
    tx = CABBATransmitter(
        transmission_interval=0.5,
        type_b_interval=10.0,
    )

    packets = tx.transmit(adsb_messages)

    channel = PacketLossChannel(
        loss_rate=loss_rate,
        seed=seed,
    )

    received_packets = channel.transmit_all(packets)

    rx = AuthenticationReceiver()

    received_type_a = 0

    for packet in received_packets:

        if isinstance(packet, CABBATypeA):
            received_type_a += 1

        rx.receive_packet(packet)

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

    adsb_messages = generate_adsb_messages(100001)

    loss_rates = [
        0.0,
        0.05,
        0.10,
        0.20,
        0.30,
        0.40,
        0.50,
        0.60,
        0.70,
        0.80,
        0.90,
        0.95,

    ]

    print(
        "Loss Rate | "
        "Proposed ASR | CABBA ASR |"
        "Proposed Coverage |  CABBA Coverage"
    )
    print("-" * 85)

    for loss_rate in loss_rates:

        proposed = run_proposed_experiment(
            adsb_messages,
            loss_rate,
            seed=1,
        )

        cabba = run_cabba_experiment(
            adsb_messages,
            loss_rate,
            seed=1,
        )

        print(
            f"{loss_rate:8.0%} | "
            f"{proposed['success_rate']:.4f} | "
            f"{cabba['success_rate']:.4f} | "
            f"{proposed['overall_coverage']:.4f} | "
            f"{cabba['overall_coverage']:.4f}"
        )


if __name__ == "__main__":
    run_robustness_experiment()
