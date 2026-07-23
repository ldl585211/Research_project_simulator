from dataclasses import dataclass

from packet import OverlayPacket, CABBATypeA, CABBATypeB


@dataclass
class PendingMessage:
    message_id: int
    receive_time: float
    adsb_hex: str
    required_key_id: int


@dataclass
class AuthenticationResult:
    message_id: int
    adsb_hex: str
    receive_time: float
    authentication_time: float
    authentication_delay: float


class AuthenticationReceiver:
    '''
    Unified receiver for:
        - Proposed OverlayPacket
        - CABBATypeA
        - CABBATypeB

    Receiver responsibilities:
        - receive packets
        - store pending messages
        - authenticate when key arrives
        - record authentication results
    '''

    def __init__(self):
        self.pending_messages = {}
        self.authentication_results = []
        self.received_packets = 0


    def receive_packet(self, packet, receive_time=None):

        self.received_packets += 1

        if receive_time is None:
            receive_time = packet.send_time


        if isinstance(packet, OverlayPacket):

            self._receive_message(
                packet.message,
                receive_time
            )

            if packet.disclosed_key is not None:
                self._receive_key(
                    packet.disclosed_key.key_id,
                    key_receive_time=receive_time
                )


        elif isinstance(packet, CABBATypeA):

            self._receive_message(
                packet.message,
                receive_time
            )


        elif isinstance(packet, CABBATypeB):

            self._receive_key(
                packet.disclosed_key.key_id,
                key_receive_time=receive_time
            )


        else:
            raise TypeError(
                f"Unsupported packet type: {type(packet)}"
            )


    def _receive_message(self, message, receive_time):

        pending = PendingMessage(
            message_id=message.message_id,
            receive_time=receive_time,
            adsb_hex=message.adsb_hex,
            required_key_id=message.required_key_id
        )

        if pending.required_key_id not in self.pending_messages:
            self.pending_messages[pending.required_key_id] = []

        self.pending_messages[pending.required_key_id].append(
            pending
        )


    def _receive_key(self, key_id, key_receive_time):

        if key_id not in self.pending_messages:
            return

        messages = self.pending_messages.pop(key_id)

        for message in messages:

            result = AuthenticationResult(
                message_id=message.message_id,
                adsb_hex=message.adsb_hex,
                receive_time=message.receive_time,
                authentication_time=key_receive_time,
                authentication_delay=(
                    key_receive_time -
                    message.receive_time
                )
            )

            self.authentication_results.append(result)


    def get_authentication_results(self):

        return self.authentication_results


if __name__ == "__main__":

    '''
    from transmitter import PhaseOverlayTransmitter

    messages = [
        "8D40621D58C382D690C8AC2863A7"
    ] * 25

    tx = PhaseOverlayTransmitter(
        transmission_interval=0.5,
        key_interval_length=10
    )

    packets = tx.transmit(messages)

    rx = AuthenticationReceiver()

    for packet in packets:
        rx.receive_packet(packet)

    print(
        "Authenticated:",
        len(rx.authentication_results)
    )

    for result in rx.authentication_results:
        print(
            result.message_id,
            result.authentication_delay
        )
    '''

    from CABBATransmitter import CABBATransmitter


    messages = [
        "8D40621D58C382D690C8AC2863A7"
    ] * 45


    tx = CABBATransmitter(
        transmission_interval=0.5,
        type_b_interval=5.0,
    )


    packets = tx.transmit(messages)


    rx = AuthenticationReceiver()


    for packet in packets:

        rx.receive_packet(packet)



    print(
        "Authenticated:",
        len(rx.authentication_results)
    )


    for result in rx.authentication_results:

        print(
            f"Message {result.message_id}: "
            f"delay={result.authentication_delay}s"
        )
