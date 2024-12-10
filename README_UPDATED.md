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

---

Feel free to submit issues and enhancement requests!
