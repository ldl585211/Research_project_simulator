from dataclasses import dataclass


@dataclass(frozen=True)
class AuthMessage:
    message_id: int
    send_time: float
    adsb_hex: str

    # mac: int

    # Key interval ID required for authentication
    required_key_id: int


@dataclass(frozen=True)
class KeyDisclosure:
    """Logical identity of a disclosed key."""

    key_id: int

    # Field length in the phase overlay
    key_length_bits: int = 128


@dataclass(frozen=True)
class LCRATTypeA:
    """
    LCRAT phase-overlay ADS-B packet.

    Overlay fields:
        MAC                         32 bits
        Sequence Number              8 bits
        Previous Key Disclosure     128 bits
        Interval ID & Flags          12 bits
        Reserved / Trust Refresh     24 bits

    Total:
        204 bits
    """
    
    packet_id: int
    send_time: float
    message: AuthMessage
    sequence_number: int
    disclosed_key: KeyDisclosure | None
    mac_length_bits: int = 32
    flags: int = 0
    reserved_trust_refresh: int = 0
    overlay_bit_length: int = 204

    def disclosed_key_id(self):

        if self.disclosed_key is None:
            return None

        return self.disclosed_key.key_id


@dataclass(frozen=True)
class CABBATypeA:
    """
    CABBA Type A packet.

    Sent together with every ADS-B message.

    Fields:
        ADS-B message
        196-bit MAC placeholder
        8-bit sequence number
    """

    packet_id: int
    send_time: float
    message: AuthMessage
    sequence_number: int
    mac_length_bits: int = 196


@dataclass(frozen=True)
class CABBATypeB:
    """
    CABBA Type B packet.

    Sent periodically and contains key disclosure information.

    Contains disclosed authentication key.
    """
    packet_id: int
    send_time: float
    disclosed_key: KeyDisclosure
