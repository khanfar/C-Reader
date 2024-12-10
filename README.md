# Smart Card Reader and AT24C64 EEPROM Reader/Writer

## Project Overview
This project consists of two applications developed by Khanfar Systems:  
1. **AT24C64 EEPROM Reader/Writer**  
2. **Smart Card Reader**  

These applications are designed to interact with smart cards and AT24C64 EEPROMs, providing functionalities for reading, writing, and managing data.

## Features

### AT24C64 EEPROM Reader/Writer

- **Read and Write Operations**: Read individual pages or the entire memory of the AT24C64 EEPROM. Write data to specific pages with verification.
- **Card Cloning**: Clone data from one EEPROM to another.
- **Data Comparison**: Compare memory dumps to identify differences.
- **Real-Time Logging**: Detailed logging of operations and status updates.
- **User-Friendly GUI**: Built using `tkinter` for easy interaction.

### Smart Card Reader

- **Read and Write Operations**: Read data from specific sectors or write data with various command types.
- **Card Type Detection**: Automatically detects card types based on ATR.
- **Protection Management**: Checks and manages write protection for sectors.
- **User-Friendly GUI**: Built using `tkinter` for easy interaction.

## How it Works

### AT24C64 EEPROM Reader/Writer

The application communicates with the AT24C64 EEPROM via I²C protocol. It provides a graphical interface for users to perform read and write operations, view logs, and manage data dumps.

### Smart Card Reader

This application communicates with smart cards using the ISO/IEC 7816 protocol. It allows users to read and write data, manage protection, and view detailed card information.

## Technical Details

### AT24C64 EEPROM Reader/Writer

- **Dependencies**: `tkinter`, `smartcard`, `datetime`, `logging`, `os`.
- **Memory Management**: Supports 8KB total memory with 32-byte page size.

### Smart Card Reader

- **Dependencies**: `tkinter`, `smartcard`, `datetime`, `logging`.
- **Supported Cards**: Compatible with various SLE card types.

## Functions Overview

### AT24C64 EEPROM Reader/Writer

- `create_gui()`: Initializes the graphical user interface.
- `connect_to_card()`: Establishes a connection with the EEPROM.
- `read_page()`: Reads data from a specified page.
- `write_page()`: Writes data to a specified page.
- `read_all_memory()`: Reads the entire memory and saves it to a file.
- `compare_dumps()`: Compares two memory dumps.

### Smart Card Reader

- `connect_to_card()`: Connects to the smart card reader and retrieves card information.
- `read_sector()`: Reads data from a specified sector.
- `write_sector()`: Writes data to a specified sector with the selected command type.
- `get_card_type()`: Retrieves the type of the connected card.

## Detailed Function Overview

### AT24C64 EEPROM Reader/Writer Functions

- **`create_gui(self)`**: Initializes the graphical user interface, setting up the main frames and sections for controls, reading, writing, and console output. This function is responsible for creating the visual components of the application, including buttons, text fields, and display areas.

- **`connect_to_card(self)`**: Establishes a connection to the AT24C64 EEPROM card, verifying the connection and checking the card type. This function handles the low-level communication with the EEPROM, ensuring that the application can read and write data correctly.

- **`read_page(self)`**: Reads data from a specified page in the EEPROM and displays it in the GUI. This function takes a page number as input, reads the corresponding data from the EEPROM, and updates the GUI to show the retrieved data.

- **`write_page(self)`**: Writes data to a specified page in the EEPROM, verifying the data format and handling errors if the page is protected. This function checks the input data for correctness, writes it to the specified page, and handles any errors that may occur during the write operation.

- **`read_all_memory(self)`**: Reads all memory pages from the EEPROM and saves the data to a binary file. This function reads the entire contents of the EEPROM, page by page, and saves the data to a file for later use.

- **`compare_dumps(self)`**: Compares two memory dump files and displays the differences in the GUI. This function takes two file paths as input, reads the corresponding memory dumps, and displays any differences between the two files in the GUI.

### Smart Card Reader Functions

- **`connect_to_card(self)`**: Connects to the smart card reader and retrieves detailed information about the card. This function establishes a connection to the smart card reader, retrieves the card's ATR, and displays the card's information in the GUI.

- **`read_sector(self)`**: Reads data from a specified sector of the smart card and displays it in the GUI. This function takes a sector number as input, reads the corresponding data from the smart card, and updates the GUI to show the retrieved data.

- **`write_sector(self)`**: Writes data to a specified sector of the smart card, checking for protection and handling PIN verification if necessary. This function checks the input data for correctness, writes it to the specified sector, and handles any errors that may occur during the write operation.

- **`get_card_type(self)`**: Retrieves the card type by reading its ATR and matching it with known card types. This function reads the card's ATR, matches it against a database of known card types, and returns the card type.

## AT24C64 EEPROM Card Overview

### Pinout Diagram
The AT24C64 EEPROM card has the following pin configuration:


          ______________________
         |                      |
         |      AT24C64        |
         |                      |
         |   +--------------+   |
         |   |              |   |
         |   |   Chip      |   |
         |   |              |   |
         |   +--------------+   |
         |                      |
         |   Pin 1 (VCC)      |  <--- Connect to C1 (VCC)
         |   Pin 2 (SDA)      |  <--- Connect to C7 (SDA)
         |   Pin 3 (SCL)      |  <--- Connect to C3 (CLK)
         |   Pin 4 (GND)      |  <--- Connect to C5 (GND)
         |   Pin 5 (WP)       |  <--- Connect to C8 (WP)
         |______________________|

## AT24C64 Pinout Diagram
```
   +--------------------+
   |    AT24C64        |
   |                    |
   |   Pin 1 (VCC)     |  <--- Connect to C1 (VCC)
   |   Pin 2 (SDA)     |  <--- Connect to C7 (SDA)
   |   Pin 3 (SCL)     |  <--- Connect to C3 (CLK)
   |   Pin 4 (GND)     |  <--- Connect to C5 (GND)
   |   Pin 5 (WP)      |  <--- Connect to C8 (WP)
   +--------------------+
```

### Commands for Reading and Writing
The AT24C64 EEPROM supports the following commands for reading and writing data:

- **Read Command**: 
  - Command Format: `[0xFF, 0xB0, 0x00, Address, Length]`
  - Description: Reads data from the specified address for the given length.

- **Write Command**: 
  - Command Format: `[0xFF, 0xD6, 0x00, Address, Length, Data...]`
  - Description: Writes data to the specified address with the given length.

### Supported Protocols
The AT24C64 EEPROM communicates using the I²C (Inter-Integrated Circuit) protocol. This allows multiple devices to communicate over the same bus.

### Write Protection Commands
The AT24C64 EEPROM includes a write protection feature that can be controlled via the WP pin:

- **WP Command**: 
  - When the WP pin is connected to VCC, write operations are disabled, protecting the data from being overwritten.
  - When the WP pin is connected to GND, write operations are enabled.

### Connection Types
The AT24C64 EEPROM can be connected using the following methods:

- **I²C Connection**: 
  - Connect the SDA and SCL pins to the corresponding pins on the microcontroller or card reader.
  - Ensure that pull-up resistors are used on the SDA and SCL lines for proper operation.

### Using AT24C64 with ACR38U-R4
The ACR38U-R4 is a smart card reader that can be used to interface with the AT24C64 EEPROM. To connect:

1. **Connect the Card**: Insert the AT24C64 EEPROM into the ACR38U-R4 reader.
2. **Power Supply**: Ensure the reader is powered on and properly configured.
3. **Communication**: Use the provided software to send I²C commands to read from or write to the EEPROM.

**Note**: Ensure that the ACR38U-R4 supports I²C communication mode for compatibility with the AT24C64 EEPROM.

## ACR38U-R4 Card Reader Pinout and Connections

The ACR38U-R4 card reader features several pins that connect to the AT24C64 EEPROM card. Below is the corrected pin configuration for the ACR38U-R4:

- **C1**: VCC (Power Supply) - Connects to Pin 1 (VCC) of the AT24C64.
- **C2**: RST (Reset) - Not directly connected to the AT24C64.
- **C3**: CLK (Clock) - Connects to Pin 3 (SCL) of the AT24C64.
- **C4**: NA (Not Applicable) - Not used.
- **C5**: GND (Ground) - Connects to Pin 4 (GND) of the AT24C64.
- **C6**: NC (Not Connected) - Not used.
- **C7**: SDA (Data Input/Output) - Connects to Pin 2 (SDA) of the AT24C64.
- **C8**: WP (Write Protect) - Connects to Pin 5 (WP) of the AT24C64.

## ACR38U-R4 Pinout Diagram
```
   +--------------------+
   |    ACR38U-R4      |
   |                    |
   |   C1 (VCC)        |  <--- Connect to Pin 1 (VCC)
   |   C2 (RST)        |  <--- Not Connected
   |   C3 (CLK)        |  <--- Connect to Pin 3 (SCL)
   |   C4 (NA)         |  <--- Not Used
   |   C5 (GND)        |  <--- Connect to Pin 4 (GND)
   |   C6 (NC)         |  <--- Not Used
   |   C7 (SDA)        |  <--- Connect to Pin 2 (SDA)
   |   C8 (WP)         |  <--- Connect to Pin 5 (WP)
   +--------------------+
```

### AT24C64 Pin Connections to ACR38U-R4

| ACR38U-R4 Pin | AT24C64 Pin | Description                     |
|----------------|--------------|---------------------------------|
| C1             | Pin 1       | VCC (Power Supply)             |
| C2             | Not Connected| RST (Reset)                    |
| C3             | Pin 3       | CLK (Clock) - Connects to SCL  |
| C4             | Not Used    | NA (Not Applicable)            |
| C5             | Pin 4       | GND (Ground)                   |
| C6             | Not Used    | NC (Not Connected)             |
| C7             | Pin 2       | SDA (Data Input/Output)        |
| C8             | Pin 5       | WP (Write Protect)             |

### Summary of Connections
- **C1 (VCC)** connects to **Pin 1 (VCC)** of the AT24C64.
- **C2 (RST)** is not connected to the AT24C64.
- **C3 (CLK)** connects to **Pin 3 (SCL)** of the AT24C64.
- **C5 (GND)** connects to **Pin 4 (GND)** of the AT24C64.
- **C7 (SDA)** connects to **Pin 2 (SDA)** of the AT24C64.
- **C8 (WP)** connects to **Pin 5 (WP)** of the AT24C64.

This configuration ensures that the AT24C64 EEPROM can communicate effectively with the ACR38U-R4 card reader using the I²C protocol.

### Connection Diagram
Below is a simple representation of how the ACR38U-R4 connects to the AT24C64 EEPROM card:

```
ACR38U-R4 Pin  | AT24C64 EEPROM Pin
---------------|--------------------
C1 (VCC)       | Pin 1 (VCC)
C2 (RST)       | Not Connected
C3 (CLK)       | Pin 3 (SCL)
C4 (NA)        | Not Used
C5 (GND)       | Pin 4 (GND)
C6 (NC)        | Not Used
C7 (SDA)       | Pin 2 (SDA)
C8 (WP)        | Pin 5 (WP)
```

### Commands for Communication
When communicating with the AT24C64 via the ACR38U-R4, use the following commands:
- **Read Command**: 
  - Format: `[0xFF, 0xB0, 0x00, Address, Length]`
- **Write Command**: 
  - Format: `[0xFF, 0xD6, 0x00, Address, Length, Data...]`

### Supported Protocols
The ACR38U-R4 supports the I²C protocol, allowing seamless communication with the AT24C64 EEPROM.

### Write Protection
To enable write protection on the AT24C64, connect the WP pin to VCC. To disable it, connect the WP pin to GND.

## Tutorials

### AT24C64 EEPROM Reader/Writer

1. Launch the application.
2. Connect to the AT24C64 EEPROM using the "Connect" button.
3. Use the "Read Page" button to read a specific page or "Read All" to dump the entire memory.
4. To write data, enter the page number and hexadecimal data, then click "Write Page".
5. Use the "Compare Dumps" feature to compare two memory dumps.

### Smart Card Reader

1. Launch the application.
2. Click the "Connect" button to establish a connection with the smart card.
3. Enter the sector number and click "Read Block" to read data.
4. To write data, enter the sector number, select the command type, and input the data in hexadecimal format, then click "Write Block".

## Safety Precautions

1. Always verify PIN before writing.
2. Back up card data before modifications.
3. Use write protection when possible.
4. Test operations on non-critical sectors first.
5. Keep logs for troubleshooting.

## Known Limitations

- Some commands may not work with all readers.
- Protection bits are permanent once set.
- PIN lock is irreversible.
- Limited to 16 sectors of 16 bytes each.

## Recommendations

- Ensure that the correct card type is selected before performing operations.
- Regularly check for software updates to improve functionality and security.

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License.

## Table of Contents
1. [Project Overview](#project-overview)
2. [Features](#features)
3. [How it Works](#how-it-works)
4. [Technical Details](#technical-details)
5. [Functions Overview](#functions-overview)
6. [Detailed Function Overview](#detailed-function-overview)
7. [Tutorials](#tutorials)
8. [Safety Precautions](#safety-precautions)
9. [Known Limitations](#known-limitations)
10. [Recommendations](#recommendations)
11. [Contributing](#contributing)
12. [License](#license)
13. [Installation Instructions](#installation-instructions)
14. [Usage Examples](#usage-examples)
15. [FAQs](#faqs)
16. [Changelog](#changelog)
17. [Contact Information](#contact-information)
18. [Acknowledgments](#acknowledgments)
19. [Future Enhancements](#future-enhancements)
20. [Testing Instructions](#testing-instructions)
21. [Deployment Instructions](#deployment-instructions)
22. [System Architecture Diagram](#system-architecture-diagram)
23. [Flowcharts](#flowcharts)
24. [Pinout Diagrams](#pinout-diagrams)
25. [Common Issues and Solutions](#common-issues-and-solutions)
26. [Best Practices](#best-practices)

## Installation Instructions
1. Ensure you have Python 3.x installed.
2. Install required packages:
   ```bash
   pip install pyscard tkinter
   ```

## Usage Examples
### AT24C64 EEPROM Reader/Writer
- To read a page from the EEPROM, click on the "Read Page" button after connecting.
- To write data, enter the page number and hexadecimal data, then click "Write Page".

### Smart Card Reader
- Insert the card into the reader and click "Connect" to read the card details.

## FAQs
**Q: What should I do if the card is not detected?**  
A: Ensure the card is properly inserted and that the reader is functioning correctly.

**Q: Can I use this application on Linux?**  
A: Yes, but ensure that the necessary dependencies are installed for your distribution.

## Changelog
- **Version 1.0**: Initial release with basic functionalities.
- **Version 1.1**: Added support for additional card types and improved logging.

## Contact Information
For questions or support, please contact:  
**Email**: support@khanfarsystems.com

## Acknowledgments
- Thanks to the contributors and libraries that made this project possible.

## Future Enhancements
- Support for additional EEPROM types.
- Enhanced user interface with more features.

## Testing Instructions
To run tests, ensure you have the `unittest` framework installed and execute:
```bash
python -m unittest discover
```

## Deployment Instructions
To deploy the application:
1. Package the application using a tool like `PyInstaller`.
2. Follow the instructions for your target operating system to install the package.

## System Architecture Diagram
A system architecture diagram illustrates the overall structure of the application, showing how the different components interact. You can create this diagram using tools like Lucidchart, Draw.io, or Microsoft Visio. The diagram should include:
- GUI components
- Communication with the AT24C64 EEPROM
- Interaction with the Smart Card Reader
- Libraries and dependencies used

## Flowcharts
Flowcharts help visualize the logic flow for key processes in the application. You can create flowcharts for:
- Connecting to a card
- Reading and writing data
- Handling errors
Use the same tools mentioned above to create these flowcharts.

## Pinout Diagrams
Pinout diagrams provide information on the pin configurations for supported smart cards. Below is an example of how to format this section:
- **SLE4442 Memory Card**
  - Pin 1: VCC (Power)
  - Pin 2: GND (Ground)
  - Pin 3: I/O (Data Input/Output)
  - Pin 4: CLK (Clock)

You can find pinout diagrams online or create your own using graphical tools.

## Common Issues and Solutions
Here are some common issues that developers may encounter while using the applications, along with their solutions:
- **Issue**: Card not detected
  - **Solution**: Ensure the card is properly inserted and that the reader is functioning correctly.
- **Issue**: Write operation fails
  - **Solution**: Check if the sector is protected or if the data format is correct.

## Best Practices
To maintain code quality and ensure smooth collaboration, consider the following best practices:
- Follow consistent coding standards across the codebase.
- Document your code thoroughly, explaining the purpose of complex functions.
- Use version control effectively, including meaningful commit messages and branching strategies.
