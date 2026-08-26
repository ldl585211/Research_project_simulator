"""
Unified authentication receiver for both LCRAT and CABBA.

The receiver stores pending ADS-B messages and authenticates them when
the required TESLA key is received. Authentication results and latency
are recorded for performance evaluation.
"""

from dataclasses import dataclass

from packet import LCRATTypeA, CABBATypeA, CABBATypeB


@dataclass
class PendingMessage:
    """
    Represents a received ADS-B message waiting for authentication.
    """
    message_id: int
    receive_time: float
    adsb_hex: str
    required_key_id: int


@dataclass
class AuthenticationResult:
    """
    Stores the authentication result of one ADS-B message.
    """
    message_id: int
    adsb_hex: str
    receive_time: float
    authentication_time: float
    authentication_delay: float


class AuthenticationReceiver:
    '''
    Unified receiver for ADS-B messages including:
        - LCRATTypeA
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
        """
        Process one received authentication packet.
        """

        self.received_packets += 1

        # In the current channel model, there is no propagation delay.
        # Therefore, reception time is assumed to equal transmission time
        # unless another value is explicitly provided.
        if receive_time is None:
            receive_time = packet.send_time


        if isinstance(packet, LCRATTypeA):

            self._receive_message(
                packet.message,
                receive_time
            )

            # LCRAT carries the previous interval key directly in
            # the Type A phase-overlay packet.
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
            # CABBA Type B provides the TESLA key required to authenticate
            # messages from the previous authentication interval.
            self._receive_key(
                packet.disclosed_key.key_id,
                key_receive_time=receive_time
            )


        else:
            raise TypeError(
                f"Unsupported packet type: {type(packet)}"
            )


    def _receive_message(self, message, receive_time):
        """
        Store a received ADS-B message as pending authentication.
        """
        # Convert the received AuthMessage into a receiver-side pending-message representation.
        pending = PendingMessage(
            message_id=message.message_id,
            receive_time=receive_time,
            adsb_hex=message.adsb_hex,
            required_key_id=message.required_key_id
        )

        # Create a new pending-message list when this required key ID has not previously been observed.
        if pending.required_key_id not in self.pending_messages:
            self.pending_messages[pending.required_key_id] = []

        # Store the message until its required TESLA key is received.
        self.pending_messages[pending.required_key_id].append(
            pending
        )


    def _receive_key(self, key_id, key_receive_time):
        """
        Process a disclosed TESLA key.

        If pending messages require this key, all of those messages are
        considered successfully authenticated at the key reception time.
        """

        # If no pending message requires this key, there is currently nothing to authenticate.
        if key_id not in self.pending_messages:
            return
            
        # Retrieve and remove all messages waiting for this key.
        messages = self.pending_messages.pop(key_id)

        # Authenticate every message associated with the disclosed key.
        for message in messages:

            result = AuthenticationResult(
                message_id=message.message_id,
                adsb_hex=message.adsb_hex,
                receive_time=message.receive_time,

                #Authentication is considered complete when the required TESLA key is received.
                authentication_time=key_receive_time,

                # Authentication latency is measured from message reception to key reception.
                authentication_delay=(
                    key_receive_time - message.receive_time
                )
            )

            # Store the completed authentication result.
            self.authentication_results.append(result)


    def get_authentication_results(self):
        """
        Return all successfully authenticated messages.
        """

        return self.authentication_results


if __name__ == "__main__":
    """
    2 versions of simple standalone receiver test.
    """

    '''
    from transmitter import LCRATTransmitter

    messages = [
        "8D40621D58C382D690C8AC2863A7"
    ] * 25

    tx = LCRATTransmitter(
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
