
"""
Proposed ADS-B Phase Overlay Transmitter

Key interval is defined in absolute time (seconds).

Parameters:
    transmission_interval:
        ADS-B message transmission period.

    key_interval:
        Authentication key interval duration.

Example:
    transmission_interval = 0.5 s
    key_interval = 10 s

Result:
    Message 0-19  -> Key 0
    Message 20-39 -> Key 1
"""

from packet import AuthMessage, KeyDisclosure, LCRATTypeA


class PhaseOverlayTransmitter:

    def __init__(
        self,
        transmission_interval: float = 0.5,
        key_interval: float = 10.0,
    ):

        self.transmission_interval = transmission_interval
        self.key_interval = key_interval

        self.messages_per_key = int(
            key_interval / transmission_interval
        )


    def get_key_id(self, packet_id: int) -> int:
        """
        Return authentication key ID for an ADS-B packet.
        """

        send_time = packet_id * self.transmission_interval

        return int(
            send_time // self.key_interval
        )


    def create_packet(
        self,
        adsb_hex: str,
        packet_id: int,
    ) -> LCRATTypeA:

        send_time = packet_id * self.transmission_interval

        sequence_number = packet_id % 256

        current_key_id = self.get_key_id(packet_id)


        message = AuthMessage(
            message_id=packet_id,
            send_time=send_time,
            adsb_hex=adsb_hex,
            mac=packet_id,
            required_key_id=current_key_id,
        )


        disclosed_key_id = current_key_id - 1


        if disclosed_key_id >= 0:

            disclosed_key = KeyDisclosure(
                key_id=disclosed_key_id
            )

            flags = 1

        else:

            disclosed_key = None
            flags = 0


        return LCRATTypeA(
            packet_id=packet_id,
            send_time=send_time,
            message=message,
            sequence_number=sequence_number,
            disclosed_key=disclosed_key,
            flags=flags,
            reserved_trust_refresh=0,
        )


    def transmit(
        self,
        adsb_messages: list[str],
    ) -> list[LCRATTypeA]:

        packets = []

        for packet_id, adsb_hex in enumerate(adsb_messages):

            packets.append(
                self.create_packet(
                    adsb_hex,
                    packet_id,
                )
            )

        return packets



if __name__ == "__main__":

    messages = [
        "8D40621D58C382D690C8AC2863A7"
    ] * 45


    tx = PhaseOverlayTransmitter(
        transmission_interval=0.5,
        key_interval=10.0,
    )


    packets = tx.transmit(messages)


    for packet in packets:

        print(
            f"Packet {packet.packet_id}: "
            f"requires K{packet.message.required_key_id}, "
            f"discloses {packet.disclosed_key_id()}"
        )
