
"""
CABBA transmitter simulator.

This transmitter follows the packet structures defined in packet.py:

    Type A:
        - One packet for every ADS-B message
        - Contains AuthMessage
        - Contains 8-bit sequence number
        - Uses a 196-bit MAC placeholder

    Type B:
        - Sent periodically
        - Contains key disclosure information
"""

from packet import (
    AuthMessage,
    KeyDisclosure,
    CABBATypeA,
    CABBATypeB,
)


class CABBATransmitter:
    """
    CABBA transmitter.

    Parameters:

        transmission_interval:
            ADS-B message transmission interval (seconds)

        type_b_interval:
            Type B key disclosure interval (seconds)

    Example:

        transmission_interval = 0.5 s
        type_b_interval = 10 s


        Type A:
            t=0.0
            t=0.5
            t=1.0
            ...


        Type B:
            t=10
            t=20
            t=30
            ...
    """

    def __init__(
        self,
        transmission_interval: float = 0.5,
        type_b_interval: float = 10.0,
    ):

        self.transmission_interval = transmission_interval
        self.type_b_interval = type_b_interval



    def get_key_id(
        self,
        packet_id: int,
    ) -> int:

        send_time = (
            packet_id *
            self.transmission_interval
        )

        return int(
            send_time //
            self.type_b_interval
        )



    def create_type_a(
        self,
        adsb_hex: str,
        packet_id: int,
    ) -> CABBATypeA:
        """
        Create one CABBA Type A packet.
        """

        send_time = (
            packet_id *
            self.transmission_interval
        )

        required_key_id = self.get_key_id(
            packet_id
        )


        message = AuthMessage(

            message_id=packet_id,

            send_time=send_time,

            adsb_hex=adsb_hex,

            # 196-bit MAC placeholder
        #    mac=packet_id,

            required_key_id=required_key_id,
        )


        return CABBATypeA(

            packet_id=packet_id,

            send_time=send_time,

            message=message,

            sequence_number=packet_id % 256,
        )



    def create_type_b(
        self,
        disclosure_id: int,
    ) -> CABBATypeB:
        
        """
        Create one CABBA Type B packet.

        Type B discloses the key required for messages
        from the previous authentication interval.
        """

        send_time = (
            disclosure_id *
            self.type_b_interval
        )

        disclosed_key_id = (
            disclosure_id - 1
        )

        return CABBATypeB(

            packet_id=disclosure_id,

            send_time=send_time,

            disclosed_key=KeyDisclosure(
                key_id=disclosed_key_id
            )
        )



    def transmit(
        self,
        adsb_messages: list[str],
    ):
        """
        Generate all CABBA Type A and Type B packets.

        The returned packets are sorted by transmission time.
        """

        packets = []


        # Generate Type A packets
        for packet_id, adsb_hex in enumerate(adsb_messages):

            packets.append(
                self.create_type_a(
                    adsb_hex,
                    packet_id,
                )
            )


        # Generate enough Type B packets to cover the dataset
        total_time = (
            len(adsb_messages)
            *
            self.transmission_interval
        )


        number_of_type_b = int(
            total_time / self.type_b_interval
        )


        for disclosure_id in range(
            1,
            number_of_type_b + 1
        ):

            packets.append(
                self.create_type_b(
                    disclosure_id
                )
            )


        packets.sort(
            key=lambda packet: packet.send_time
        )


        return packets



if __name__ == "__main__":

    messages = [
        "8D40621D58C382D690C8AC2863A7"
    ] * 45


    tx = CABBATransmitter(
        transmission_interval=0.5,
        type_b_interval=10.0,
    )


    packets = tx.transmit(messages)


    for packet in packets:

        if isinstance(packet, CABBATypeA):

            print(
                f"Type A | "
                f"Packet {packet.packet_id} | "
                f"t={packet.send_time:.1f}s | "
                f"Message={packet.message.message_id} | "
                f"requires K{packet.message.required_key_id}"
            )

        else:

            print(
                f"Type B | "
                f"t={packet.send_time:.1f}s | "
                f"discloses K{packet.key_id}"
            )
