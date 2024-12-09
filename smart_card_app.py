import tkinter as tk
from tkinter import ttk, messagebox
from smartcard.System import readers
from smartcard.util import toHexString, toBytes
from smartcard.Exceptions import NoCardException, CardConnectionException
import datetime

class SmartCardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Khanfar Systems Cards Reader")
        
        # Set window size and position
        window_width = 800  
        window_height = 600  
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Initialize variables
        self.TOTAL_SECTORS = 16
        self.BYTES_PER_SECTOR = 16
        self.processing = False
        self.connection = None
        self.reader = None
        
        # Constants
        self.WRITE_COMMANDS = {
            "WRITE (0xD0)": 0xD0,
            "PROGRAM (0xFE)": 0xFE,
            "WRITE PROTECTION (0xD1)": 0xD1,
            "WRITE ALL (0xDE)": 0xDE,
            "UPDATE (0xF0)": 0xF0
        }
        
        # Card type definitions
        self.CARD_TYPES = {
            "3B 67 00 00 4A": "SLE4442",
            "3B 67 00 00 2A": "SLE4428",
            "3B 67 00 00 45": "SLE4432",
            "3B 67 00 00 47": "SLE4436",
            "3B 95 15 40 .. 68": "SLE5542",
            "3B 95 18 40 .. 65": "SLE5528"
        }
        
        # Create main frames
        left_frame = ttk.Frame(root, padding="5")
        left_frame.grid(row=0, column=0, sticky="nsew")
        
        right_frame = ttk.Frame(root, padding="5")
        right_frame.grid(row=0, column=1, sticky="nsew")
        
        # Configure grid weights
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(0, weight=1)
        
        # Create frames for different sections
        control_frame = ttk.LabelFrame(left_frame, text="Control", padding="5")
        control_frame.pack(fill="x", padx=5, pady=5)
        
        read_frame = ttk.LabelFrame(left_frame, text="Read Operations", padding="5")
        read_frame.pack(fill="x", padx=5, pady=5)
        
        write_frame = ttk.LabelFrame(left_frame, text="Write Operations", padding="5")
        write_frame.pack(fill="x", padx=5, pady=5)
        
        # Console frame on the right
        console_frame = ttk.LabelFrame(right_frame, text="Console", padding="5")
        console_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Connection info and button
        connection_info = ttk.Label(control_frame, text="Bitrate: 9600 bps (fixed)")
        connection_info.grid(row=0, column=0, padx=5, pady=5)
        
        self.connect_button = ttk.Button(control_frame, text="Connect", command=self.connect_to_card)
        self.connect_button.grid(row=0, column=1, padx=5, pady=5)
        
        self.connect_canvas = tk.Canvas(control_frame, width=20, height=20)
        self.connect_canvas.grid(row=0, column=2, padx=5, pady=5)
        self.connect_ball = self.connect_canvas.create_oval(5, 5, 15, 15, fill="gray")
        
        # Read section
        ttk.Label(read_frame, text="Sector:").grid(row=0, column=0, padx=5, pady=5)
        self.sector_entry = ttk.Entry(read_frame, width=10)
        self.sector_entry.grid(row=0, column=1, padx=5, pady=5)
        
        self.read_button = ttk.Button(read_frame, text="Read Block", command=self.read_sector)
        self.read_button.grid(row=0, column=2, padx=5, pady=5)
        
        self.read_all_button = ttk.Button(read_frame, text="Read All", command=self.read_all_data)
        self.read_all_button.grid(row=0, column=3, padx=5, pady=5)
        
        self.read_canvas = tk.Canvas(read_frame, width=20, height=20)
        self.read_canvas.grid(row=0, column=4, padx=5, pady=5)
        self.read_ball = self.read_canvas.create_oval(5, 5, 15, 15, fill="gray")
        
        self.read_data = tk.Text(read_frame, height=4, width=40)
        self.read_data.grid(row=1, column=0, columnspan=5, padx=5, pady=5)
        
        # Write section
        ttk.Label(write_frame, text="Sector:").grid(row=0, column=0, padx=5, pady=5)
        self.write_sector_entry = ttk.Entry(write_frame, width=10)
        self.write_sector_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(write_frame, text="Write Command:").grid(row=1, column=0, padx=5, pady=5)
        self.command_type = tk.StringVar(value="WRITE (0xD0)")
        command_combo = ttk.Combobox(write_frame, textvariable=self.command_type, values=list(self.WRITE_COMMANDS.keys()), state="readonly")
        command_combo.grid(row=1, column=1, padx=5, pady=5)
        
        self.command_desc = ttk.Label(write_frame, text="Standard write command", wraplength=200)
        self.command_desc.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        
        # Update command description when selection changes
        def update_command_desc(event):
            cmd = self.command_type.get()
            descriptions = {
                "WRITE (0xD0)": "Standard write command for writing data",
                "PROGRAM (0xFE)": "Program command for writing non-zero values",
                "WRITE PROTECTION (0xD1)": "Write to protection memory",
                "WRITE ALL (0xDE)": "Write same value to multiple addresses",
                "UPDATE (0xF0)": "Update existing data"
            }
            self.command_desc.config(text=descriptions.get(cmd, ""))
        command_combo.bind('<<ComboboxSelected>>', update_command_desc)
        
        ttk.Label(write_frame, text="Data (hex):").grid(row=3, column=0, padx=5, pady=5)
        self.write_data_hex = ttk.Entry(write_frame, width=40)
        self.write_data_hex.grid(row=3, column=1, columnspan=2, padx=5, pady=5)
        
        self.write_button = ttk.Button(write_frame, text="Write Block", command=self.write_sector)
        self.write_button.grid(row=4, column=1, padx=5, pady=5)
        
        self.write_canvas = tk.Canvas(write_frame, width=20, height=20)
        self.write_canvas.grid(row=4, column=2, padx=5, pady=5)
        self.write_ball = self.write_canvas.create_oval(5, 5, 15, 15, fill="gray")
        
        # Console section
        self.console = tk.Text(console_frame, height=20, width=60)
        self.console.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Add scrollbar to console
        scrollbar = ttk.Scrollbar(console_frame, orient="vertical", command=self.console.yview)
        scrollbar.pack(side="right", fill="y")
        self.console.configure(yscrollcommand=scrollbar.set)
        
        # Copy console button
        self.copy_button = ttk.Button(console_frame, text="Copy Console", command=self.copy_console)
        self.copy_button.pack(pady=5)
        
        # Initialize status
        self.update_status_ball_color(self.connect_canvas, self.connect_ball, 'gray')
        self.update_status_ball_color(self.read_canvas, self.read_ball, 'gray')
        self.update_status_ball_color(self.write_canvas, self.write_ball, 'gray')
        
        # Start reader detection
        self.detect_reader()

    def log_to_console(self, message):
        """Log a message to the console with timestamp"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.console.insert(tk.END, f"[{timestamp}] {message}\n")
        self.console.see(tk.END)  # Auto-scroll to the end
        
    def copy_console(self):
        console_text = self.console.get("1.0", tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(console_text)
        messagebox.showinfo("Success", "Console text copied to clipboard!")

    def connect_reader(self):
        """Legacy method - not used anymore"""
        pass

    def connect_to_card(self):
        """Connect to the smart card and get its information"""
        try:
            if not self.reader:
                self.reader = readers()[0]
                self.log_to_console(f"Found reader: {self.reader}")
        
            if self.connection:
                self.connection.disconnect()
                self.connection = None
                self.log_to_console("Disconnected from card")
                self.update_status_ball_color(self.connect_canvas, self.connect_ball, 'gray')
                self.connect_button.config(text="Connect")
            else:
                self.connection = self.reader.createConnection()
                self.connection.connect()
                self.log_to_console("\nConnected to card successfully!")
                self.update_status_ball_color(self.connect_canvas, self.connect_ball, 'green')
                self.connect_button.config(text="Disconnect")
                
                # Print detailed card information
                self.print_card_info()
                
        except Exception as e:
            self.log_to_console(f"Connection error: {str(e)}")
            messagebox.showerror("Error", f"Connection failed: {str(e)}")

    def detect_reader(self):
        try:
            reader_list = readers()
            if reader_list:
                self.reader = reader_list[0]
                self.log_to_console(f"Found reader: {self.reader}")
            else:
                self.log_to_console("No readers found")
        except Exception as e:
            self.log_to_console(f"Error detecting reader: {str(e)}")

    def update_status_ball_color(self, canvas, ball, color):
        canvas.itemconfig(ball, fill=color)

    def read_sector(self):
        try:
            sector = int(self.sector_entry.get())
            if not 0 <= sector < self.TOTAL_SECTORS:
                raise ValueError(f"Sector must be between 0 and {self.TOTAL_SECTORS-1}")
            
            address = sector * self.BYTES_PER_SECTOR
            APDU = [0xFF, 0xB0, 0x00, address, self.BYTES_PER_SECTOR]
            response, sw1, sw2 = self.connection.transmit(APDU)
            
            if sw1 == 0x90 and sw2 == 0x00:
                hex_values = toHexString(response)
                self.read_data.delete(1.0, tk.END)
                self.read_data.insert(tk.END, hex_values)
            else:
                self.read_data.delete(1.0, tk.END)
                self.read_data.insert(tk.END, f"Read Error: SW1={hex(sw1)}, SW2={hex(sw2)}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read sector: {str(e)}")

    def read_all_data(self):
        """Read all sectors and save to file"""
        try:
            self.log_to_console("Starting read all sectors")
            
            # First read protection memory
            command = [0xFF, 0xB2, 0x00, 0x00, 0x04]
            response, sw1, sw2 = self.connection.transmit(command)
            
            protected_sectors = []
            unprotected_sectors = []
            
            if sw1 == 0x90:
                # Process protection bits
                for byte_index in range(len(response)):
                    for bit in range(8):
                        sector = byte_index * 8 + bit
                        if sector < self.TOTAL_SECTORS:
                            if response[byte_index] & (1 << bit):
                                protected_sectors.append(sector)
                            else:
                                unprotected_sectors.append(sector)
            
            # Read all sectors
            all_data = []
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"card_dump_{timestamp}.txt"
            
            with open(filename, 'w') as f:
                for sector in range(self.TOTAL_SECTORS):
                    data = self.read_sector_data(sector)
                    if data:
                        protection_status = "Protected" if sector in protected_sectors else "Unprotected"
                        log_message = f"Read sector {sector:02d}: {data} ({protection_status})"
                        self.log_to_console(log_message)
                        f.write(f"Sector {sector:02d}: {data}\n")
                        all_data.append(data)
                
                # Write protection summary to file
                f.write("\nProtection Status Summary:\n")
                f.write("-" * 50 + "\n")
                f.write(f"Protected Sectors: {', '.join(map(str, protected_sectors))}\n")
                f.write(f"Unprotected Sectors: {', '.join(map(str, unprotected_sectors))}\n")
            
            self.log_to_console(f"Data saved to {filename}")
            
            # Display protection summary
            self.log_to_console("\nProtection Status Summary:")
            self.log_to_console("-" * 50)
            if protected_sectors:
                self.log_to_console(f"Protected Sectors: {', '.join(map(str, protected_sectors))}")
            if unprotected_sectors:
                self.log_to_console(f"Unprotected Sectors: {', '.join(map(str, unprotected_sectors))}")
            self.log_to_console(f"\nFor writing data, use unprotected sectors: {', '.join(map(str, unprotected_sectors))}")
            self.log_to_console("-" * 50)
            
            # Update display
            if all_data:
                self.read_data.delete(1.0, tk.END)
                self.read_data.insert(tk.END, '\n'.join(all_data))
                self.update_status_ball_color(self.read_canvas, self.read_ball, 'green')
            
        except Exception as e:
            self.log_to_console(f"Error reading all sectors: {str(e)}")
            self.update_status_ball_color(self.read_canvas, self.read_ball, 'red')

    def load_pins(self):
        """Load PINs from default_pins.txt file"""
        try:
            pins = []
            with open("default_pins.txt", "r") as f:
                for line in f:
                    # Skip comments and empty lines
                    line = line.strip()
                    if line and not line.startswith("#"):
                        # Extract PIN from line (handle both plain PIN and PIN with comment)
                        pin = line.split("#")[0].strip()
                        if len(pin) == 6:  # Only add valid 6-character PINs
                            pins.append(pin)
            return pins
        except Exception as e:
            self.log_to_console(f"Error loading PINs: {str(e)}")
            return ["FFFFFF"]  # Return default PIN if file can't be read

    def verify_pin(self):
        pins = self.load_pins()
        self.log_to_console("Starting PIN verification...")
        
        for pin in pins:
            try:
                # Present PIN command for SLE4442
                pin_bytes = [int(pin[i:i+2], 16) for i in range(0, 6, 2)]
                APDU = [0xFF, 0x20, 0x00, 0x00, 0x03] + pin_bytes
                response, sw1, sw2 = self.connection.transmit(APDU)
                
                if sw1 == 0x90 and sw2 == 0x00:
                    self.log_to_console(f"PIN verification successful with PIN: {pin}")
                    # Add verified PIN to the list if not already there
                    try:
                        with open("default_pins.txt", "r") as f:
                            content = f.read()
                        if f"{pin}  # Verified on" not in content:
                            with open("default_pins.txt", "a") as f:
                                f.write(f"\n{pin}  # Verified on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    except:
                        pass  # Ignore errors in updating the file
                    return True
                else:
                    self.log_to_console(f"PIN {pin} failed: SW1={hex(sw1)}, SW2={hex(sw2)}")
                    
            except Exception as e:
                self.log_to_console(f"Error trying PIN {pin}: {str(e)}")
                
        self.log_to_console("All PINs failed")
        return False

    def check_protection(self, address):
        """Check if an address is write-protected"""
        try:
            # Read protection memory (32 bytes, each bit protects 4 bytes)
            APDU = [0xFF, 0xB2, 0x00, 0x00, 0x20]
            response, sw1, sw2 = self.connection.transmit(APDU)
            
            if sw1 == 0x90 and sw2 == 0x00:
                # Calculate which protection bit corresponds to this address
                prot_byte = address // 32
                prot_bit = (address % 32) // 4
                
                if prot_byte < len(response):
                    is_protected = bool(response[prot_byte] & (1 << prot_bit))
                    self.log_to_console(f"Protection check for address {hex(address)}: {'Protected' if is_protected else 'Not protected'}")
                    return is_protected
            else:
                self.log_to_console(f"Failed to read protection memory: SW1={hex(sw1)}, SW2={hex(sw2)}")
        
            return True  # Assume protected if we can't read protection memory
        except Exception as e:
            self.log_to_console(f"Error checking protection: {str(e)}")
            return True

    def write_sector(self):
        """Write data to a sector"""
        try:
            # Validate sector input
            sector_text = self.write_sector_entry.get().strip()
            if not sector_text:
                self.log_to_console("Error: Please enter a sector number (0-15)")
                messagebox.showerror("Error", "Please enter a sector number (0-15)")
                return
                
            sector = int(sector_text)
            if not (0 <= sector < self.TOTAL_SECTORS):
                self.log_to_console(f"Error: Sector must be between 0 and {self.TOTAL_SECTORS-1}")
                messagebox.showerror("Error", f"Sector must be between 0 and {self.TOTAL_SECTORS-1}")
                return

            # Validate data input
            data_hex = self.write_data_hex.get().strip()
            if not data_hex:
                self.log_to_console("Error: Please enter data to write (16 bytes in hex)")
                messagebox.showerror("Error", "Please enter data to write (16 bytes in hex)")
                return
            
            # Convert hex string to bytes
            try:
                # Remove spaces and validate length
                data_hex = data_hex.replace(" ", "")
                if len(data_hex) != 32:  # 16 bytes = 32 hex characters
                    self.log_to_console(f"Error: Data must be exactly 16 bytes (32 hex characters). Current length: {len(data_hex)}")
                    messagebox.showerror("Error", f"Data must be exactly 16 bytes (32 hex characters). Current length: {len(data_hex)}")
                    return
                    
                data = bytes.fromhex(data_hex)
            except ValueError:
                self.log_to_console("Error: Invalid hex data format. Use pairs of hex characters (00-FF)")
                messagebox.showerror("Error", "Invalid hex data format. Use pairs of hex characters (00-FF)")
                return

            # Get selected command type
            cmd_type = self.WRITE_COMMANDS[self.command_type.get()]
            self.log_to_console(f"\nStarting write operation:")
            self.log_to_console(f"Sector: {sector}")
            self.log_to_console(f"Data: {' '.join([data_hex[i:i+2] for i in range(0, len(data_hex), 2)])}")
            self.log_to_console(f"Command: {self.command_type.get()}")

            # Check if sector is protected
            command = [0xFF, 0xB2, 0x00, 0x00, 0x04]  # Read protection memory
            response, sw1, sw2 = self.connection.transmit(command)
            
            if sw1 == 0x90:
                byte_index = sector // 8
                bit_index = sector % 8
                is_protected = bool(response[byte_index] & (1 << bit_index))
                self.log_to_console(f"Sector {sector} protection status: {'Protected' if is_protected else 'Unprotected'}")
                
                if not is_protected:
                    # For unprotected sectors, try direct write without PIN
                    self.log_to_console("Sector is unprotected, attempting direct write...")
                    
                    # Try different write commands
                    commands = [
                        (cmd_type, "Selected command"),
                        (0xD0, "WRITE command"),
                        (0xFE, "PROGRAM command"),
                        (0xF0, "UPDATE command")
                    ]
                    
                    for cmd, desc in commands:
                        try:
                            self.log_to_console(f"\nTrying {desc}...")
                            command = [0xFF, cmd, 0x00, sector * self.BYTES_PER_SECTOR, len(data)] + list(data)
                            response, sw1, sw2 = self.connection.transmit(command)
                            
                            if sw1 == 0x90:
                                self.log_to_console(f"Write successful with {desc}")
                                self.update_status_ball_color(self.write_canvas, self.write_ball, 'green')
                                
                                # Verify write
                                self.verify_write(sector, data_hex)
                                return
                            else:
                                self.log_to_console(f"{desc} failed: SW1={hex(sw1)}, SW2={hex(sw2)}")
                        except Exception as e:
                            self.log_to_console(f"Error with {desc}: {str(e)}")
                    
                    self.log_to_console("All write attempts failed")
                    self.update_status_ball_color(self.write_canvas, self.write_ball, 'red')
                else:
                    # For protected sectors, try PIN verification first
                    self.log_to_console("Sector is protected, PIN verification required")
                    self.verify_pin_and_write(sector, data, cmd_type)
            else:
                self.log_to_console("Could not read protection status, attempting write with PIN verification")
                self.verify_pin_and_write(sector, data, cmd_type)
                
        except Exception as e:
            error_msg = str(e)
            self.log_to_console(f"Write error: {error_msg}")
            messagebox.showerror("Error", error_msg)
            self.update_status_ball_color(self.write_canvas, self.write_ball, 'red')

    def verify_pin_and_write(self, sector, data, cmd_type):
        if self.verify_pin():
            self.log_to_console("PIN verification successful, proceeding with write...")
            self.write_sector_with_pin(sector, data, cmd_type)
        else:
            self.log_to_console("PIN verification failed, write operation cancelled")
            self.update_status_ball_color(self.write_canvas, self.write_ball, 'red')

    def write_sector_with_pin(self, sector, data, cmd_type):
        try:
            # Write data byte by byte for SLE4442
            address = sector * self.BYTES_PER_SECTOR
            success = True
            failed_bytes = []
            
            self.log_to_console(f"Writing data to sector {sector}...")
            self.log_to_console("Starting byte-by-byte write operation:")
            
            import time
            
            for i, byte in enumerate(data):
                current_address = address + i
                
                # Check protection before writing
                if self.check_protection(current_address):
                    # Try to update protection memory if protected
                    if byte != 0:  # Only need to unprotect for non-zero values
                        self.log_to_console(f"Attempting to unprotect address {hex(current_address)}")
                        # Write protection bit command
                        prot_APDU = [0xFF, 0xD1, 0x00, current_address // 4, 0x01, 0x00]
                        prot_response, prot_sw1, prot_sw2 = self.connection.transmit(prot_APDU)
                        time.sleep(0.01)  # Wait after protection change
                        
                        if prot_sw1 != 0x90 or prot_sw2 != 0x00:
                            self.log_to_console(f"Failed to unprotect address: SW1={hex(prot_sw1)}, SW2={hex(prot_sw2)}")
                
                if byte != 0 and cmd_type in [0xFE, 0xF0]:  # For non-zero values with PROGRAM or UPDATE
                    self.log_to_console(f"Non-zero value detected at byte {i}: {hex(byte)}, using command {hex(cmd_type)}")
                    # First erase the location if using PROGRAM
                    if cmd_type == 0xFE:
                        erase_APDU = [0xFF, 0xD0, 0x00, current_address, 0x01, 0x00]
                        self.connection.transmit(erase_APDU)
                        time.sleep(0.003)  # Wait after erase
                    
                    # Then program/update the new value
                    APDU = [0xFF, cmd_type, 0x00, current_address, 0x01, byte]
                    self.log_to_console(f"Writing byte {i}: {hex(byte)} to address {hex(current_address)}")
                    response, sw1, sw2 = self.connection.transmit(APDU)
                    time.sleep(0.005)  # 5ms programming time
                    
                    if sw1 != 0x90 and sw2 != 0x00:
                        self.log_to_console(f"Command response: SW1={hex(sw1)}, SW2={hex(sw2)}")
                else:
                    # Use selected command type for other cases
                    APDU = [0xFF, cmd_type, 0x00, current_address, 0x01, byte]
                    self.log_to_console(f"Writing byte {i}: {hex(byte)} to address {hex(current_address)}")
                    response, sw1, sw2 = self.connection.transmit(APDU)
                
                # Rest of your existing verification code...
                
                # Log the response for each byte
                if sw1 == 0x90 and sw2 == 0x00:
                    self.log_to_console(f"✓ Byte {i} written successfully")
                    # Verify immediate read after write
                    verify_APDU = [0xFF, 0xB0, 0x00, current_address, 0x01]
                    verify_response, verify_sw1, verify_sw2 = self.connection.transmit(verify_APDU)
                    
                    if verify_response and verify_response[0] == byte:
                        self.log_to_console(f"✓ Byte {i} verified: wrote {hex(byte)}, read back {hex(verify_response[0])}")
                    else:
                        self.log_to_console(f"✗ Byte {i} verification failed: wrote {hex(byte)}, read back {hex(verify_response[0]) if verify_response else 'none'}")
                        failed_bytes.append(i)
                else:
                    success = False
                    error_msg = f"✗ Write Error at byte {i}: SW1={hex(sw1)}, SW2={hex(sw2)}"
                    self.log_to_console(error_msg)
                    failed_bytes.append(i)
                    messagebox.showerror("Error", error_msg)
                    self.update_status_ball_color(self.write_canvas, self.write_ball, 'red')
                    break
                    
            if success:
                self.log_to_console(f"Sector {sector} write operation completed.")
                if failed_bytes:
                    self.log_to_console(f"Failed bytes at positions: {failed_bytes}")
                
                # Verify the write by reading back
                APDU = [0xFF, 0xB0, 0x00, address, self.BYTES_PER_SECTOR]
                response, sw1, sw2 = self.connection.transmit(APDU)
                
                if sw1 == 0x90 and sw2 == 0x00:
                    read_data = toHexString(response)
                    self.log_to_console(f"Final verification read of sector {sector}: {read_data}")
                    
                    # Compare written data with read data
                    if read_data.replace(" ", "").upper() == data_hex.upper():
                        self.log_to_console("Verification successful - written data matches read data")
                        self.update_status_ball_color(self.write_canvas, self.write_ball, 'green')
                        messagebox.showinfo("Success", f"Sector {sector} written and verified successfully!")
                    else:
                        self.log_to_console("Warning: Read data doesn't match written data!")
                        self.log_to_console(f"Attempted to write: {data_hex}")
                        self.log_to_console(f"Actually written: {read_data}")
                        self.log_to_console("Byte-by-byte comparison:")
                        for i in range(16):
                            written = int(data_hex[i*2:(i+1)*2], 16)
                            read = response[i]
                            if written != read:
                                self.log_to_console(f"Mismatch at byte {i}: Wrote {hex(written)}, Read {hex(read)}")
                        self.update_status_ball_color(self.write_canvas, self.write_ball, 'red')
                        messagebox.showwarning("Warning", "Written data doesn't match intended data!")
                else:
                    self.log_to_console(f"Verification read failed: SW1={hex(sw1)}, SW2={hex(sw2)}")
                    self.update_status_ball_color(self.write_canvas, self.write_ball, 'red')

        except Exception as e:
            error_msg = f"Failed to write sector: {str(e)}"
            self.log_to_console(error_msg)
            messagebox.showerror("Error", error_msg)
            self.update_status_ball_color(self.write_canvas, self.write_ball, 'red')

    def get_card_type(self):
        """Get the card type by reading its ATR"""
        try:
            if not self.connection:
                return "No card connected"
            
            atr = toHexString(self.connection.getATR())
            
            # Try to match ATR with known card types
            for atr_pattern, card_type in self.CARD_TYPES.items():
                # Replace dots with wildcard for pattern matching
                pattern = atr_pattern.replace(".", r"\d")
                if atr.startswith(pattern.split()[0]):
                    return f"{card_type} (ATR: {atr})"
            
            return f"Unknown card type (ATR: {atr})"
        except Exception as e:
            return f"Error reading card type: {str(e)}"

    def get_card_uid(self):
        """Get the card's UID if available"""
        try:
            if not self.connection:
                return "No card connected"
            
            # Try to read UID using different commands for different card types
            # GET DATA command for ISO cards
            COMMANDS = [
                [0xFF, 0xCA, 0x00, 0x00, 0x00],  # Standard GET DATA
                [0xFF, 0xB0, 0x00, 0x00, 0x08],  # Read first 8 bytes
                [0xFF, 0x36, 0x00, 0x00, 0x08]   # Alternative command
            ]
            
            for cmd in COMMANDS:
                try:
                    response, sw1, sw2 = self.connection.transmit(cmd)
                    if sw1 == 0x90 and len(response) > 0:
                        return f"Card UID: {toHexString(response)}"
                except:
                    continue
            
            return "UID not available for this card type"
        except Exception as e:
            return f"Error reading UID: {str(e)}"

    def read_protection_memory(self):
        """Read the protection memory of the card"""
        try:
            # Command to read protection memory
            command = [0xFF, 0xB2, 0x00, 0x00, 0x04]
            response, sw1, sw2 = self.connection.transmit(command)
            
            if sw1 == 0x90:
                self.log_to_console("\nProtection Memory:")
                self.log_to_console("-" * 40)
                self.log_to_console(f"Raw data: {toHexString(response)}")
                
                # Analyze protection bits
                for i, byte in enumerate(response):
                    protected_sectors = []
                    for bit in range(8):
                        if byte & (1 << bit):
                            sector = (i * 8) + bit
                            if sector < self.TOTAL_SECTORS:
                                protected_sectors.append(sector)
                    
                    if protected_sectors:
                        self.log_to_console(f"Protected sectors in byte {i}: {protected_sectors}")
                    else:
                        self.log_to_console(f"No protected sectors in byte {i}")
            else:
                self.log_to_console(f"Failed to read protection memory: SW1={hex(sw1)}, SW2={hex(sw2)}")
                
        except Exception as e:
            self.log_to_console(f"Error reading protection memory: {str(e)}")

    def read_security_memory(self):
        """Read the security memory of the card"""
        try:
            # Command to read security memory
            command = [0xFF, 0xB1, 0x00, 0x00, 0x04]
            response, sw1, sw2 = self.connection.transmit(command)
            
            if sw1 == 0x90:
                self.log_to_console("\nSecurity Memory:")
                self.log_to_console("-" * 40)
                self.log_to_console(f"Raw data: {toHexString(response)}")
                
                # Error counter is typically in first byte
                error_counter = response[0] if response else 0
                self.log_to_console(f"PIN error counter: {error_counter}")
                
                if len(response) > 1:
                    self.log_to_console(f"Additional security data: {toHexString(response[1:])}")
            else:
                self.log_to_console(f"Failed to read security memory: SW1={hex(sw1)}, SW2={hex(sw2)}")
                
        except Exception as e:
            self.log_to_console(f"Error reading security memory: {str(e)}")

    def print_card_info(self):
        """Print detailed card information to console"""
        try:
            self.log_to_console("\n" + "="*50)
            self.log_to_console("CARD INFORMATION:")
            self.log_to_console("-"*50)
            
            # Get and display card type
            card_type = self.get_card_type()
            self.log_to_console(f"Card Type: {card_type}")
            
            # Get and display UID
            card_uid = self.get_card_uid()
            self.log_to_console(f"Card ID: {card_uid}")
            
            # Get additional card info
            if self.connection:
                atr = toHexString(self.connection.getATR())
                self.log_to_console(f"Raw ATR: {atr}")
                self.log_to_console(f"Protocol: T=0 (Memory Card)")
                self.log_to_console(f"Memory Size: 256 bytes (16 sectors × 16 bytes)")
                self.log_to_console(f"Protection Memory: 32 bytes")
                self.log_to_console(f"Security Memory: 4 bytes")
                
                # Read protection and security memory
                self.read_protection_memory()
                self.read_security_memory()
            
            self.log_to_console("="*50 + "\n")
            
        except Exception as e:
            self.log_to_console(f"Error getting card info: {str(e)}")

    def verify_write(self, sector, data_hex):
        # Verify the write by reading back
        APDU = [0xFF, 0xB0, 0x00, sector * self.BYTES_PER_SECTOR, self.BYTES_PER_SECTOR]
        response, sw1, sw2 = self.connection.transmit(APDU)
        
        if sw1 == 0x90 and sw2 == 0x00:
            read_data = toHexString(response)
            self.log_to_console(f"Final verification read of sector {sector}: {read_data}")
            
            # Compare written data with read data
            if read_data.replace(" ", "").upper() == data_hex.upper():
                self.log_to_console("Verification successful - written data matches read data")
                self.update_status_ball_color(self.write_canvas, self.write_ball, 'green')
                messagebox.showinfo("Success", f"Sector {sector} written and verified successfully!")
            else:
                self.log_to_console("Warning: Read data doesn't match written data!")
                self.log_to_console(f"Attempted to write: {data_hex}")
                self.log_to_console(f"Actually written: {read_data}")
                self.log_to_console("Byte-by-byte comparison:")
                for i in range(16):
                    written = int(data_hex[i*2:(i+1)*2], 16)
                    read = response[i]
                    if written != read:
                        self.log_to_console(f"Mismatch at byte {i}: Wrote {hex(written)}, Read {hex(read)}")
                self.update_status_ball_color(self.write_canvas, self.write_ball, 'red')
                messagebox.showwarning("Warning", "Written data doesn't match intended data!")
        else:
            self.log_to_console(f"Verification read failed: SW1={hex(sw1)}, SW2={hex(sw2)}")
            self.update_status_ball_color(self.write_canvas, self.write_ball, 'red')

    def read_sector_data(self, sector):
        try:
            address = sector * self.BYTES_PER_SECTOR
            APDU = [0xFF, 0xB0, 0x00, address, self.BYTES_PER_SECTOR]
            response, sw1, sw2 = self.connection.transmit(APDU)
            
            if sw1 == 0x90 and sw2 == 0x00:
                return toHexString(response)
            else:
                return f"Read Error: SW1={hex(sw1)}, SW2={hex(sw2)}"
        except Exception as e:
            return f"Error reading sector: {str(e)}"

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Khanfar Systems Cards Reader")
    app = SmartCardApp(root)
    root.mainloop()
