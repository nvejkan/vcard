#!/usr/bin/env python3
"""
iPhone-Compatible NFC URL Writer for ACS ACR1252U with NTAG216
"""

import sys
import time
from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.Exceptions import CardConnectionException, NoCardException


class ACR1252U_NTAG216Writer:
    """Handler for ACR1252U reader with NTAG216 cards - iPhone Compatible"""
    
    READER_NAME_PATTERN = "ACR1252"
    NTAG216_USER_START_PAGE = 4
    
    # URI Identifier Codes (NFC Forum)
    URI_IDENTIFIERS = {
        "http://www.": 0x01,
        "https://www.": 0x02,
        "http://": 0x03,
        "https://": 0x04,
        "tel:": 0x05,
        "mailto:": 0x06,
        "ftp://": 0x0D,
    }
    
    def __init__(self):
        self.connection = None
        self.reader = None
    
    def find_reader(self):
        """Find the ACR1252U reader"""
        available_readers = readers()
        
        if not available_readers:
            raise Exception("No readers found. Is ACR1252U connected?")
        
        for reader in available_readers:
            if self.READER_NAME_PATTERN in str(reader):
                self.reader = reader
                print(f"✓ Found reader: {reader}")
                return True
        
        raise Exception(f"ACR1252U not found. Available: {available_readers}")
    
    def connect_card(self):
        """Connect to card"""
        try:
            self.connection = self.reader.createConnection()
            self.connection.connect()
            print("✓ Card connected")
        except NoCardException:
            raise Exception("No card on reader!")
    
    def send_apdu(self, apdu):
        """Send APDU and return response"""
        response, sw1, sw2 = self.connection.transmit(apdu)
        if sw1 != 0x90 or sw2 != 0x00:
            raise Exception(f"APDU failed: SW={sw1:02X}{sw2:02X}")
        return response
    
    def write_page(self, page, data):
        """Write 4 bytes to a page"""
        if len(data) != 4:
            data = list(data) + [0x00] * (4 - len(data))
        apdu = [0xFF, 0xD6, 0x00, page, 0x04] + data[:4]
        self.send_apdu(apdu)
    
    def get_uid(self):
        """Get card UID"""
        uid = self.send_apdu([0xFF, 0xCA, 0x00, 0x00, 0x00])
        return ''.join(f'{b:02X}' for b in uid)
    
    def create_ndef_uri(self, url):
        """
        Create NDEF URI message - iPhone Compatible Format
        
        iPhone requires:
        - Proper NDEF TLV structure
        - Correct capability container
        - Clean terminator
        """
        # Find URI identifier code
        uri_code = 0x00
        uri_data = url
        
        for prefix, code in self.URI_IDENTIFIERS.items():
            if url.lower().startswith(prefix):
                uri_code = code
                uri_data = url[len(prefix):]
                break
        
        # URI payload: identifier + URI string
        uri_bytes = [uri_code] + list(uri_data.encode('utf-8'))
        payload_len = len(uri_bytes)
        
        # NDEF Record
        # Byte 0: Header - MB=1, ME=1, CF=0, SR=1, IL=0, TNF=0x01 = 0xD1
        # Byte 1: Type Length = 1
        # Byte 2: Payload Length
        # Byte 3: Type = 'U' (0x55)
        # Byte 4+: Payload
        
        ndef_record = [
            0xD1,           # Header: MB=1, ME=1, SR=1, TNF=Well-Known
            0x01,           # Type length: 1
            payload_len,    # Payload length
            0x55,           # Type: 'U' for URI
        ] + uri_bytes
        
        ndef_len = len(ndef_record)
        
        # TLV Block
        # Type: 0x03 (NDEF Message)
        # Length: 1 byte if < 255, else 3 bytes
        # Value: NDEF record
        # Terminator: 0xFE
        
        if ndef_len < 0xFF:
            tlv = [0x03, ndef_len] + ndef_record + [0xFE]
        else:
            tlv = [0x03, 0xFF, (ndef_len >> 8) & 0xFF, ndef_len & 0xFF] + ndef_record + [0xFE]
        
        return tlv
    
    def write_url(self, url):
        """Write URL to NTAG216 with iPhone-compatible formatting"""
        
        print(f"\n📝 URL: {url}")
        
        # Ensure HTTPS for iPhone compatibility
        if url.startswith("http://"):
            print("⚠️  Warning: HTTP URLs may not work on iPhone!")
            print("   Consider using HTTPS instead.")
        
        # Get UID
        uid = self.get_uid()
        print(f"📇 Card UID: {uid}")
        
        # Create NDEF message
        ndef_data = self.create_ndef_uri(url)
        print(f"📦 NDEF size: {len(ndef_data)} bytes")
        
        # Pad to 4-byte boundary
        while len(ndef_data) % 4 != 0:
            ndef_data.append(0x00)
        
        # First, write Capability Container (Page 3) for proper NDEF detection
        # CC for NTAG216: E1 10 6D 00
        # E1 = Magic number (NDEF capable)
        # 10 = Version 1.0, read access
        # 6D = Size: 109 * 8 = 872 bytes
        # 00 = Read/Write access
        print("\n📝 Writing Capability Container...")
        self.write_page(3, [0xE1, 0x10, 0x6D, 0x00])
        
        # Write NDEF data starting at page 4
        print("📝 Writing NDEF data...")
        page = self.NTAG216_USER_START_PAGE
        
        for i in range(0, len(ndef_data), 4):
            chunk = ndef_data[i:i+4]
            print(f"   Page {page}: {toHexString(chunk)}")
            self.write_page(page, chunk)
            page += 1
        
        print(f"\n✅ Written {len(ndef_data)} bytes to {page - self.NTAG216_USER_START_PAGE} pages")
        
    def disconnect(self):
        """Disconnect from card"""
        if self.connection:
            try:
                self.connection.disconnect()
            except:
                pass


def main():
    # =====================================================
    # CHANGE YOUR URL HERE - USE HTTPS FOR IPHONE!
    # =====================================================
    URL = "https://www.pwc.com"
    # =====================================================
    
    print("=" * 50)
    print("📱 iPhone-Compatible NFC Writer")
    print("   ACS ACR1252U + NTAG216")
    print("=" * 50)
    
    writer = ACR1252U_NTAG216Writer()
    
    try:
        writer.find_reader()
        
        print("\n⏳ Place NTAG216 card on reader...")
        for _ in range(30):
            try:
                writer.connect_card()
                break
            except:
                print(".", end="", flush=True)
                time.sleep(1)
        else:
            raise Exception("Timeout waiting for card")
        
        writer.write_url(URL)
        
        print("\n" + "=" * 50)
        print("✅ SUCCESS!")
        print("=" * 50)
        print("\n📱 To test on iPhone:")
        print("   1. Wake up iPhone (don't need to unlock)")
        print("   2. Hold TOP of iPhone near the tag")
        print("   3. Wait for notification popup")
        print("\n💡 If it doesn't work:")
        print("   • Open Control Center → tap NFC icon → scan")
        print("   • Make sure URL uses HTTPS")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    finally:
        writer.disconnect()


if __name__ == "__main__":
    main()