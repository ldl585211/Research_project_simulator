"""
Simple ADS-B packet loss channel simulator.

Assumption:
    - No propagation delay.
    - No physical layer errors.
    - Packet either arrives immediately or is lost.
"""


import random


class PacketLossChannel:

    def __init__(
        self,
        loss_rate: float = 0.0,
        seed: int | None = None,
    ):
        """
            loss_rate:
                Probability of packet loss.
                Example:
                    0.1 means 10% packet loss.

            seed:
                Random seed for reproducible experiments.
        """

        self.loss_rate = loss_rate

        self.random = random.Random(seed)


        # Statistics
        self.total_packets = 0
        self.lost_packets = 0
        self.received_packets = 0



    def transmit(self, packet):

        """
        Simulate one packet transmission.

        Returns:
            packet:
                received successfully

            None:
                packet lost
        """

        self.total_packets += 1


        # Simulate a packet-loss event.
        # The packet is lost when the generated random value is smaller
        # than the configured packet-loss probability.
        if self.random.random() < self.loss_rate:

            self.lost_packets += 1

            return None


        self.received_packets += 1

        return packet



    def transmit_all(self, packets):

        """
        Transmit a list of packets.

        Lost packets are removed.
        """

        received_packets = []


        for packet in packets:

            result = self.transmit(packet)

            if result is not None:

                received_packets.append(result)


        return received_packets



    def packet_loss_rate(self):

        #Calculate the observed packet-loss rate.
        if self.total_packets == 0:
            return 0


        return (
            self.lost_packets /
            self.total_packets
        )



if __name__ == "__main__":
    """
    Simple standalone test.
    """

    class DummyPacket:
        pass


    packets = [
        DummyPacket()
        for _ in range(10000)
    ]


    channel = PacketLossChannel(
        loss_rate=0.1,
        seed=1
    )


    received = channel.transmit_all(
        packets
    )


    print(
        channel.packet_loss_rate()
    )