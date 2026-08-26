"""
LCRAT ADS-B Phase Overlay Transmitter

This module implements the transmitter-side packet generation process for
the proposed Lightweight Compatible Resilient Authentication with TESLA
(LCRAT) scheme.
"""

from packet import AuthMessage, KeyDisclosure, LCRATTypeA


class LCRATTransmitter:
    """
    Generate LCRAT Type A packets from ADS-B messages.
    """

    def __init__(
        self,
        transmission_interval: float = 0.5,
        key_interval: float = 10.0,
    ):

    '''
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
    '''
    
        self.transmission_interval = transmission_interval
        self.key_interval = key_interval

        # Number of ADS-B messages expected within one key interval.
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

        """
        Create one LCRAT Type A packet.
        """

        send_time = packet_id * self.transmission_interval

        sequence_number = packet_id % 256

        current_key_id = self.get_key_id(packet_id)

        # Create the logical ADS-B authentication message.
        message = AuthMessage(
            message_id=packet_id,
            send_time=send_time,
            adsb_hex=adsb_hex,
            required_key_id=current_key_id,
        )

        # LCRAT discloses the TESLA key from the previous interval.
        disclosed_key_id = current_key_id - 1


        if disclosed_key_id >= 0:
            # A previous authentication interval exists
            disclosed_key = KeyDisclosure(
                key_id=disclosed_key_id
            )

            # Flag indicates that a valid previous-key disclosure is present.
            flags = 1

        else:

            # During the first authentication interval, there is no previous TESLA key to disclose.
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
        """
        Convert a list of ADS-B messages into LCRAT Type A packets.

        Args:
            adsb_messages:
                List of ADS-B messages represented as hexadecimal strings.

        Returns:
            list[LCRATTypeA]:
                Generated LCRAT packet sequence in transmission order.
        """
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
    """
    Simple standalone test.
    """

    messages = [
        "8D40621D58C382D690C8AC2863A7"
    ] * 45


    tx = LCRATTransmitter(
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
