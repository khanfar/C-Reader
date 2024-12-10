# Smart Card Reader and AT24C64 EEPROM Reader/Writer

## Project Overview
This project consists of two applications developed by Khanfar Systems:  
1. **AT24C64 EEPROM Reader/Writer**  
2. **Smart Card Reader**  

These applications are designed to interact with smart cards and AT24C64 EEPROMs, providing functionalities for reading, writing, and managing data.

## Applications

### 1. AT24C64 EEPROM Reader/Writer (`at24c64_app.py`)

#### Features
- **Read and Write Operations**: Read individual pages or the entire memory of the AT24C64 EEPROM. Write data to specific pages with verification.
- **Card Cloning**: Clone data from one EEPROM to another.
- **Data Comparison**: Compare memory dumps to identify differences.
- **Real-Time Logging**: Detailed logging of operations and status updates.
- **User-Friendly GUI**: Built using `tkinter` for easy interaction.

#### How it Works
The application communicates with the AT24C64 EEPROM via I²C protocol. It provides a graphical interface for users to perform read and write operations, view logs, and manage data dumps.

#### Technical Details
- **Dependencies**: `tkinter`, `smartcard`, `datetime`, `logging`, `os`.
- **Memory Management**: Supports 8KB total memory with 32-byte page size.

#### Functions Overview
- `create_gui()`: Initializes the graphical user interface.
- `connect_to_card()`: Establishes a connection with the EEPROM.
- `read_page()`: Reads data from a specified page.
- `write_page()`: Writes data to a specified page.
- `read_all_memory()`: Reads the entire memory and saves it to a file.
- `compare_dumps()`: Compares two memory dumps.

#### Tutorial
1. Launch the application.
2. Connect to the AT24C64 EEPROM using the "Connect" button.
3. Use the "Read Page" button to read a specific page or "Read All" to dump the entire memory.
4. To write data, enter the page number and data in hexadecimal format, then click "Write Page".
5. Use the "Compare Dumps" feature to compare two memory dumps.

### 2. Smart Card Reader (`smart_card_app.py`)

#### Features
- **Read and Write Operations**: Read data from specific sectors or write data with various command types.
- **Card Type Detection**: Automatically detects card types based on ATR.
- **Protection Management**: Checks and manages write protection for sectors.
- **User-Friendly GUI**: Built using `tkinter` for easy interaction.

#### How it Works
This application communicates with smart cards using the ISO/IEC 7816 protocol. It allows users to read and write data, manage protection, and view detailed card information.

#### Technical Details
- **Dependencies**: `tkinter`, `smartcard`, `datetime`, `logging`.
- **Supported Cards**: Compatible with various SLE card types.

#### Functions Overview
- `connect_to_card()`: Connects to the smart card reader and retrieves card information.
- `read_sector()`: Reads data from a specified sector.
- `write_sector()`: Writes data to a specified sector with the selected command type.
- `get_card_type()`: Retrieves the type of the connected card.

#### Tutorial
1. Launch the application.
2. Click the "Connect" button to establish a connection with the smart card.
3. Enter the sector number and click "Read Block" to read data.
4. To write data, enter the sector number, select the command type, and input the data in hexadecimal format, then click "Write Block".

## Recommendations
- Ensure that the correct card type is selected before performing operations.
- Regularly check for software updates to improve functionality and security.

## Developed By
Khanfar Systems

## Features

- Automatic card type detection and ATR reading
- UID reading for supported cards
- Read and display card contents by sector
- Write data to specific sectors
- Multiple write command support
- PIN verification
- Protection bit management
- Real-time operation status indicators
- Detailed logging console
- Reads and displays protection memory status
- Shows security memory contents
- Automatic detection of protected and unprotected sectors
- Smart write handling:
  - Unprotected sectors: Direct write without PIN
  - Protected sectors: Requires PIN verification

## Supported Hardware

### Card Readers
- ACS CCID USB Reader
- Other PC/SC compliant readers (may have limited functionality)

### Smart Card Types
Primary Support:
- SLE4442 Memory Cards
- SLE4428 Memory Cards
- SLE4432 Memory Cards
- SLE4436 Memory Cards
- SLE5542 Memory Cards
- SLE5528 Memory Cards

Other memory cards may work with limited functionality

## Card Type Detection

The application automatically detects the card type when connecting by:
1. Reading the card's Answer To Reset (ATR)
2. Matching the ATR against known card patterns
3. Displaying the card type and full ATR in the console
4. Attempting to read the card's UID (if available)

Example console output:
```
Connected successfully
SLE4442 (ATR: 3B 67 00 00 4A)
Card UID: A1 B2 C3 D4
```

## Installation

1. Install Python 3.x
2. Install required packages:
```bash
pip install pyscard tkinter
```

## Usage

### Basic Operations

1. **Connect to Card**
   - Insert card into reader
   - Click "Connect" button
   - Status indicator will turn green when connected

2. **Read Card**
   - Click "Read All" to view all sectors
   - Data is displayed in hexadecimal format
   - Automatically saved to a dump file with timestamp

3. **Write to Card**
   - Enter sector number (0-15)
   - Enter 16 bytes of hex data
   - Select write command type
   - Click "Write Block"
   - Green indicator shows success

### Write Commands

The application supports multiple write commands for different purposes:

1. **WRITE (0xD0)**
   - Standard write command
   - Best for writing zero values
   - Fastest operation
   - No special timing requirements

2. **PROGRAM (0xFE)**
   - Specialized for writing non-zero values
   - Includes automatic erase before write
   - Uses longer programming time (5ms)
   - Required for changing bits from 0 to 1

3. **WRITE PROTECTION (0xD1)**
   - Modifies protection bits
   - Controls which memory areas can be written
   - Requires PIN verification
   - Permanent operation - use with caution

4. **WRITE ALL (0xDE)**
   - Writes same value to multiple addresses
   - Useful for initialization
   - More efficient than multiple single writes
   - Not supported by all cards

5. **UPDATE (0xF0)**
   - Updates existing data
   - No erase cycle
   - Faster than PROGRAM
   - May not work with all values

### PIN Verification

- Default PIN: FFFFFF (hex)
- Required for write operations
- Three attempts before card lock
- PIN verification status shown in console

### Protection Bits

- Each memory block can be write-protected
- Protection status checked before writing
- Automatic unprotect attempt for non-zero writes
- Protection status displayed in console

## Error Handling

The application provides detailed error feedback:

- Write operation status indicator
- Detailed console logging
- Verification after each write
- Protection bit status
- Command response codes

## Troubleshooting

1. **Can't Write Non-Zero Values**
   - Try PROGRAM command instead of WRITE
   - Check protection bits
   - Verify PIN is correct
   - Ensure proper timing (use delays)

2. **Card Not Detected**
   - Check reader connection
   - Ensure card is properly inserted
   - Verify reader is supported
   - Check system drivers

3. **Write Verification Fails**
   - Try different command type
   - Check for write protection
   - Increase programming time
   - Verify card supports operation

## Technical Details

### Memory Layout (SLE4442)

- 256 bytes main memory (16 sectors × 16 bytes)
- 32 bytes protection memory
- 4 bytes security memory
- Each protection bit controls 4 bytes

### Command Structure

All commands use the following APDU format:
```
[0xFF, Command, 0x00, Address, Length, Data]
```

### Timing Requirements

- PIN verification: immediate
- WRITE command: 1ms
- PROGRAM command: 2.5-5ms
- Protection bit: 10ms

## Safety Precautions

1. Always verify PIN before writing
2. Back up card data before modifications
3. Use write protection when possible
4. Test operations on non-critical sectors first
5. Keep logs for troubleshooting

## Known Limitations

- Some commands may not work with all readers
- Protection bits are permanent once set
- PIN lock is irreversible
- Limited to 16 sectors of 16 bytes each

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License.
