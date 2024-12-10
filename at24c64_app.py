import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from smartcard.System import readers
from smartcard.util import toHexString, toBytes
import datetime
import logging
import os
import time
from smartcard.scard import SCARD_PROTOCOL_T0, SCARD_PROTOCOL_T1
from smartcard.CardConnection import CardConnection

class AT24C64App:
    def __init__(self, root):
        self.root = root
        self.root.title("AT24C64 EEPROM Reader/Writer")
        
        # Set window size and position
        window_width = 800
        window_height = 600
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Initialize variables
        self.PAGE_SIZE = 32  # AT24C64 has 32-byte page size
        self.TOTAL_SIZE = 8192  # 8KB total memory
        self.PAGES = self.TOTAL_SIZE // self.PAGE_SIZE  # 256 pages
        self.connection = None
        self.reader = None
        self.processing = False
        
        # Setup logging
        logging.basicConfig(level=logging.INFO,
                          format='%(asctime)s - %(levelname)s - %(message)s')
        
        # Create main frames
        self.create_gui()
        
        # Initialize status
        self.update_status("Ready")
        
    def create_gui(self):
        # Create main frames
        left_frame = ttk.Frame(self.root, padding="5")
        left_frame.grid(row=0, column=0, sticky="nsew")
        
        right_frame = ttk.Frame(self.root, padding="5")
        right_frame.grid(row=0, column=1, sticky="nsew")
        
        # Configure grid weights
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create sections
        self.create_control_section(left_frame)
        self.create_read_section(left_frame)
        self.create_write_section(left_frame)
        self.create_console_section(right_frame)
        
    def create_control_section(self, parent):
        control_frame = ttk.LabelFrame(parent, text="Control", padding="5")
        control_frame.pack(fill="x", padx=5, pady=5)
        
        # Connection controls
        ttk.Label(control_frame, text="I²C Address: 0x50").grid(row=0, column=0, padx=5, pady=5)
        
        self.connect_button = ttk.Button(control_frame, text="Connect", command=self.connect_to_card)
        self.connect_button.grid(row=0, column=1, padx=5, pady=5)
        
        self.status_label = ttk.Label(control_frame, text="Status: Ready")
        self.status_label.grid(row=0, column=2, padx=5, pady=5)
        
    def create_read_section(self, parent):
        read_frame = ttk.LabelFrame(parent, text="Read Operations", padding="5")
        read_frame.pack(fill="x", padx=5, pady=5)
        
        # Page selection
        ttk.Label(read_frame, text="Page (0-255):").grid(row=0, column=0, padx=5, pady=5)
        self.page_entry = ttk.Entry(read_frame, width=10)
        self.page_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Read controls
        self.read_button = ttk.Button(read_frame, text="Read Page", command=self.read_page)
        self.read_button.grid(row=0, column=2, padx=5, pady=5)
        
        self.read_all_button = ttk.Button(read_frame, text="Read All", command=self.read_all_memory)
        self.read_all_button.grid(row=0, column=3, padx=5, pady=5)
        
        # View dump button
        self.view_dump_button = ttk.Button(read_frame, text="View Last Dump", command=self.view_last_dump)
        self.view_dump_button.grid(row=0, column=4, padx=5, pady=5)
        
        # Compare dumps button
        self.compare_dumps_button = ttk.Button(read_frame, text="Compare Dumps", command=self.compare_dumps)
        self.compare_dumps_button.grid(row=0, column=5, padx=5, pady=5)
        
        # Read data display with both hex and ASCII view
        frame = ttk.Frame(read_frame)
        frame.grid(row=1, column=0, columnspan=5, padx=5, pady=5)
        
        self.read_data = tk.Text(frame, height=4, width=50)
        self.read_data.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.read_data.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.read_data.configure(yscrollcommand=scrollbar.set)
        
    def create_write_section(self, parent):
        write_frame = ttk.LabelFrame(parent, text="Write Operations", padding="5")
        write_frame.pack(fill="x", padx=5, pady=5)
        
        # Page selection for writing
        ttk.Label(write_frame, text="Page:").grid(row=0, column=0, padx=5, pady=5)
        self.write_page_entry = ttk.Entry(write_frame, width=10)
        self.write_page_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Data input
        ttk.Label(write_frame, text="Data (hex):").grid(row=1, column=0, padx=5, pady=5)
        self.write_data_entry = ttk.Entry(write_frame, width=70)
        self.write_data_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5)
        
        # Write button
        self.write_button = ttk.Button(write_frame, text="Write Page", command=self.write_page)
        self.write_button.grid(row=2, column=1, padx=5, pady=5)
        
        # Separator
        ttk.Separator(write_frame, orient='horizontal').grid(row=3, column=0, columnspan=4, sticky='ew', pady=10)
        
        # Clone card section
        clone_frame = ttk.LabelFrame(write_frame, text="Card Cloning", padding="5")
        clone_frame.grid(row=4, column=0, columnspan=4, sticky='ew', padx=5, pady=5)
        
        # File selection frame
        file_frame = ttk.Frame(clone_frame)
        file_frame.pack(fill='x', padx=5, pady=5)
        
        self.selected_file_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.selected_file_var, width=50)
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.browse_button = ttk.Button(file_frame, text="Browse Dump", command=self.browse_bin_file)
        self.browse_button.pack(side=tk.LEFT)
        
        # Buttons frame
        button_frame = ttk.Frame(clone_frame)
        button_frame.pack(fill='x', padx=5, pady=5)
        
        self.clone_button = ttk.Button(button_frame, text="Clone Card", command=self.clone_card)
        self.clone_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.quick_clone_button = ttk.Button(button_frame, text="Quick Clone Latest Dump", command=self.quick_clone)
        self.quick_clone_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Progress bar
        self.write_progress = ttk.Progressbar(clone_frame, mode='determinate', length=300)
        self.write_progress.pack(fill='x', padx=5, pady=5)
        
        # Binary file write section
        ttk.Label(write_frame, text="Write Binary File:").grid(row=5, column=0, padx=5, pady=5)
        
        # File selection frame
        file_frame = ttk.Frame(write_frame)
        file_frame.grid(row=5, column=1, columnspan=3, sticky='ew', padx=5, pady=5)
        
        self.selected_file_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.selected_file_var, width=50)
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.browse_button = ttk.Button(file_frame, text="Browse", command=self.browse_bin_file)
        self.browse_button.pack(side=tk.LEFT)
        
        # Start address frame
        addr_frame = ttk.Frame(write_frame)
        addr_frame.grid(row=6, column=1, columnspan=3, sticky='w', padx=5, pady=5)
        
        ttk.Label(addr_frame, text="Start Page:").pack(side=tk.LEFT, padx=(0, 5))
        self.start_page_entry = ttk.Entry(addr_frame, width=10)
        self.start_page_entry.pack(side=tk.LEFT)
        self.start_page_entry.insert(0, "0")  # Default to start of memory
        
        # Write binary button and progress bar
        button_frame = ttk.Frame(write_frame)
        button_frame.grid(row=7, column=1, columnspan=3, sticky='ew', padx=5, pady=5)
        
        self.write_bin_button = ttk.Button(button_frame, text="Write Binary to Card", command=self.write_binary_file)
        self.write_bin_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.write_progress = ttk.Progressbar(button_frame, mode='determinate', length=300)
        self.write_progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
    def create_console_section(self, parent):
        console_frame = ttk.LabelFrame(parent, text="Console", padding="5")
        console_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.console = tk.Text(console_frame, height=30, width=50)
        self.console.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(console_frame, orient="vertical", command=self.console.yview)
        scrollbar.pack(side="right", fill="y")
        self.console.configure(yscrollcommand=scrollbar.set)
        
    def connect_to_card(self):
        try:
            # Get list of readers
            reader_list = readers()
            if not reader_list:
                self.log_message("No smart card readers found")
                return
                
            self.reader = reader_list[0]
            self.connection = self.reader.createConnection()
            
            # Connect with T0 protocol since that's what the card supports
            try:
                self.connection.connect(CardConnection.T0_protocol)
                self.log_message("Connected using protocol T0")
            except Exception as e:
                self.log_message(f"Failed to connect: {str(e)}")
                return
            
            # Check if it's an AT24C64
            atr = self.connection.getATR()
            if self.verify_at24c64(atr):
                self.log_message(f"Connected to AT24C64 EEPROM")
                self.log_message(f"ATR: {toHexString(atr)}")
                self.update_status("Connected")
            else:
                self.log_message("Warning: Card may not be AT24C64")
                
        except Exception as e:
            self.log_message(f"Connection error: {str(e)}")
            self.update_status("Connection Failed")

    def verify_at24c64(self, atr):
        # AT24C64 specific verification
        # This would need to be adjusted based on your specific card/reader combination
        return True  # Placeholder - implement actual verification
        
    def read_page(self):
        if not self.connection:
            messagebox.showerror("Error", "Please connect to card first")
            return
            
        try:
            page = int(self.page_entry.get())
            if not 0 <= page < self.PAGES:
                messagebox.showerror("Error", f"Page number must be between 0 and {self.PAGES-1}")
                return
                
            address = page * self.PAGE_SIZE
            # Modified command structure for AT24C64
            # First send the address
            addr_cmd = [0xFF, 0xB0, 0x00, address & 0xFF, self.PAGE_SIZE]
            response, sw1, sw2 = self.connection.transmit(addr_cmd)
            
            if sw1 == 0x90:  # Success
                self.read_data.delete(1.0, tk.END)
                self.read_data.insert(tk.END, toHexString(response))
                self.log_message(f"Successfully read page {page}")
            else:
                self.log_message(f"Read failed: SW1={hex(sw1)}, SW2={hex(sw2)}")
                
        except ValueError:
            messagebox.showerror("Error", "Invalid page number")
        except Exception as e:
            self.log_message(f"Read error: {str(e)}")
            
    def write_page(self):
        if not self.connection:
            messagebox.showerror("Error", "Please connect to card first")
            return
            
        try:
            page = int(self.write_page_entry.get())
            if not 0 <= page < self.PAGES:
                messagebox.showerror("Error", f"Page number must be between 0 and {self.PAGES-1}")
                return
                
            # Convert hex string to bytes
            data = toBytes(self.write_data_entry.get().replace(" ", ""))
            if len(data) > self.PAGE_SIZE:
                messagebox.showerror("Error", f"Data exceeds page size ({self.PAGE_SIZE} bytes)")
                return
                
            address = page * self.PAGE_SIZE
            # Modified command structure for AT24C64
            write_cmd = [0xFF, 0xD6, 0x00, address & 0xFF, len(data)] + list(data)
            response, sw1, sw2 = self.connection.transmit(write_cmd)
            
            if sw1 == 0x90:  # Success
                self.log_message(f"Successfully wrote to page {page}")
            else:
                self.log_message(f"Write failed: SW1={hex(sw1)}, SW2={hex(sw2)}")
                
        except ValueError:
            messagebox.showerror("Error", "Invalid page number or data format")
        except Exception as e:
            self.log_message(f"Write error: {str(e)}")
            
    def read_all_memory(self):
        if not self.connection:
            messagebox.showerror("Error", "Please connect to card first")
            return
            
        try:
            self.log_message("Starting full memory read...")
            data = []
            
            for page in range(self.PAGES):
                address = page * self.PAGE_SIZE
                # Modified command for reading
                read_cmd = [0xFF, 0xB0, 0x00, address & 0xFF, self.PAGE_SIZE]
                response, sw1, sw2 = self.connection.transmit(read_cmd)
                
                if sw1 == 0x90:
                    data.extend(response)
                    if page % 16 == 0:  # Update less frequently to reduce GUI load
                        self.log_message(f"Read page {page}/{self.PAGES-1}")
                else:
                    self.log_message(f"Read failed at page {page}: SW1={hex(sw1)}, SW2={hex(sw2)}")
                    return
                    
            # Save to file
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"at24c64_dump_{timestamp}.bin"
            with open(filename, "wb") as f:
                f.write(bytes(data))
                
            self.log_message(f"Full memory dump saved to {filename}")
            
        except Exception as e:
            self.log_message(f"Read all error: {str(e)}")
            
    def format_hex_dump(self, data, bytes_per_line=16):
        result = []
        ascii_chars = []
        
        for i, byte in enumerate(data):
            if i % bytes_per_line == 0:
                if i != 0:
                    # Add ASCII representation
                    result.append("  " + "".join(ascii_chars))
                    ascii_chars = []
                # Add offset
                result.append(f"\n{i:04X}: ")
            
            result.append(f"{byte:02X} ")
            # Add printable ASCII character or dot
            ascii_chars.append(chr(byte) if 32 <= byte <= 126 else ".")
        
        # Add padding for last line if needed
        if ascii_chars:
            padding = bytes_per_line - len(ascii_chars)
            result.append("   " * padding)
            result.append("  " + "".join(ascii_chars))
        
        return "".join(result)

    def view_last_dump(self):
        try:
            # Find the most recent dump file
            dump_files = [f for f in os.listdir() if f.startswith("at24c64_dump_") and f.endswith(".bin")]
            if not dump_files:
                messagebox.showinfo("Info", "No dump files found")
                return
            
            latest_dump = max(dump_files)
            
            with open(latest_dump, "rb") as f:
                data = f.read()
            
            # Create a new window to display the dump
            dump_window = tk.Toplevel(self.root)
            dump_window.title(f"Memory Dump Viewer - {latest_dump}")
            
            # Add text widget with scrollbars
            frame = ttk.Frame(dump_window, padding="5")
            frame.pack(fill=tk.BOTH, expand=True)
            
            text = tk.Text(frame, wrap=tk.NONE, font=("Courier", 10))
            text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Vertical scrollbar
            yscrollbar = ttk.Scrollbar(frame, orient="vertical", command=text.yview)
            yscrollbar.pack(side=tk.RIGHT, fill="y")
            
            # Horizontal scrollbar
            xscrollbar = ttk.Scrollbar(dump_window, orient="horizontal", command=text.xview)
            xscrollbar.pack(side=tk.BOTTOM, fill="x")
            
            text.configure(yscrollcommand=yscrollbar.set, xscrollcommand=xscrollbar.set)
            
            # Format and display the dump
            formatted_dump = self.format_hex_dump(data)
            text.insert("1.0", formatted_dump)
            text.configure(state="disabled")  # Make read-only
            
            # Set window size
            dump_window.geometry("800x600")
            
            self.log_message(f"Opened dump viewer for {latest_dump}")
            
        except Exception as e:
            self.log_message(f"Error viewing dump: {str(e)}")
            
    def compare_dumps(self):
        try:
            # Find all dump files
            dump_files = [f for f in os.listdir() if f.startswith("at24c64_dump_") and f.endswith(".bin")]
            if len(dump_files) < 2:
                messagebox.showinfo("Info", "Need at least 2 dump files to compare")
                return
            
            # Create file selection window
            select_window = tk.Toplevel(self.root)
            select_window.title("Select Dumps to Compare")
            select_window.geometry("400x200")
            
            # First dump selection
            ttk.Label(select_window, text="First Dump:").pack(pady=5)
            dump1_var = tk.StringVar(value=dump_files[0])
            dump1_combo = ttk.Combobox(select_window, textvariable=dump1_var, values=dump_files)
            dump1_combo.pack(pady=5)
            
            # Second dump selection
            ttk.Label(select_window, text="Second Dump:").pack(pady=5)
            dump2_var = tk.StringVar(value=dump_files[-1])
            dump2_combo = ttk.Combobox(select_window, textvariable=dump2_var, values=dump_files)
            dump2_combo.pack(pady=5)
            
            def start_comparison():
                dump1 = dump1_var.get()
                dump2 = dump2_var.get()
                if dump1 == dump2:
                    messagebox.showwarning("Warning", "Please select different dumps")
                    return
                select_window.destroy()
                self.show_comparison(dump1, dump2)
            
            ttk.Button(select_window, text="Compare", command=start_comparison).pack(pady=20)
            
        except Exception as e:
            self.log_message(f"Error setting up comparison: {str(e)}")
            
    def show_comparison(self, dump1_name, dump2_name):
        try:
            # Read both dumps
            with open(dump1_name, "rb") as f1, open(dump2_name, "rb") as f2:
                data1 = f1.read()
                data2 = f2.read()
            
            # Create comparison window
            comp_window = tk.Toplevel(self.root)
            comp_window.title(f"Dump Comparison")
            comp_window.geometry("1200x800")
            
            # Create main frame with two columns
            main_frame = ttk.Frame(comp_window, padding="5")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Configure grid
            main_frame.grid_columnconfigure(0, weight=1)
            main_frame.grid_columnconfigure(1, weight=1)
            main_frame.grid_rowconfigure(1, weight=1)
            
            # Create control frame for buttons
            control_frame = ttk.Frame(main_frame)
            control_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
            
            # Add labels
            ttk.Label(control_frame, text=f"Dump 1: {dump1_name}").pack(side=tk.LEFT, padx=5)
            ttk.Label(control_frame, text=f"Dump 2: {dump2_name}").pack(side=tk.LEFT, padx=5)
            
            # Add sync scroll toggle button with icon
            self.sync_enabled = tk.BooleanVar(value=True)
            sync_button = ttk.Checkbutton(
                control_frame,
                text="🔗 Sync Scroll",
                variable=self.sync_enabled,
                style='Switch.TCheckbutton'
            )
            sync_button.pack(side=tk.RIGHT, padx=5)
            
            # Create and configure style for the toggle button
            style = ttk.Style()
            style.configure('Switch.TCheckbutton',
                          font=('Segoe UI', 10),
                          padding=2)
            
            # Create text widgets with synchronized scrolling
            frame1 = ttk.Frame(main_frame)
            frame1.grid(row=1, column=0, sticky="nsew", padx=2)
            frame2 = ttk.Frame(main_frame)
            frame2.grid(row=1, column=1, sticky="nsew", padx=2)
            
            text1 = tk.Text(frame1, wrap=tk.NONE, font=("Courier", 10))
            text2 = tk.Text(frame2, wrap=tk.NONE, font=("Courier", 10))
            
            # Configure tags for highlighting
            text1.tag_configure("diff", background="#ffcccc")  # Light red for differences
            text1.tag_configure("same", background="#ccffcc")  # Light green for matches
            text2.tag_configure("diff", background="#ffcccc")
            text2.tag_configure("same", background="#ccffcc")
            
            # Add scrollbars
            yscroll1 = ttk.Scrollbar(frame1, orient="vertical")
            yscroll2 = ttk.Scrollbar(frame2, orient="vertical")
            xscroll = ttk.Scrollbar(main_frame, orient="horizontal")
            
            # Configure scrollbar commands with sync check
            def sync_scroll_y_wrapper(*args):
                if self.sync_enabled.get():
                    self.sync_scroll_y(text1, text2, *args)
                return text1.yview(*args)
                
            def sync_scroll_y_wrapper2(*args):
                if self.sync_enabled.get():
                    self.sync_scroll_y(text2, text1, *args)
                return text2.yview(*args)
                
            def sync_scroll_x_wrapper(*args):
                if self.sync_enabled.get():
                    self.sync_scroll_x(text1, text2, *args)
                return text1.xview(*args)
            
            yscroll1.config(command=sync_scroll_y_wrapper)
            yscroll2.config(command=sync_scroll_y_wrapper2)
            xscroll.config(command=sync_scroll_x_wrapper)
            
            text1.config(yscrollcommand=yscroll1.set, xscrollcommand=xscroll.set)
            text2.config(yscrollcommand=yscroll2.set, xscrollcommand=xscroll.set)
            
            # Pack widgets
            text1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            text2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            yscroll1.pack(side=tk.RIGHT, fill="y")
            yscroll2.pack(side=tk.RIGHT, fill="y")
            xscroll.grid(row=2, column=0, columnspan=2, sticky="ew")
            
            # Format and display dumps with highlighting
            lines1 = self.format_hex_dump(data1).split('\n')
            lines2 = self.format_hex_dump(data2).split('\n')
            
            for i, (line1, line2) in enumerate(zip(lines1, lines2)):
                if line1 == line2:
                    text1.insert(tk.END, line1 + '\n', "same")
                    text2.insert(tk.END, line2 + '\n', "same")
                else:
                    text1.insert(tk.END, line1 + '\n', "diff")
                    text2.insert(tk.END, line2 + '\n', "diff")
            
            # Make text widgets read-only
            text1.config(state="disabled")
            text2.config(state="disabled")
            
            self.log_message(f"Opened comparison view for {dump1_name} and {dump2_name}")
            
        except Exception as e:
            self.log_message(f"Error showing comparison: {str(e)}")
            
    def sync_scroll_y(self, source, target, *args):
        if len(args) > 1:
            source.yview(*args)
            target.yview(*args)
            
    def sync_scroll_x(self, source, target, *args):
        if len(args) > 1:
            source.xview(*args)
            target.xview(*args)
            
    def log_message(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.console.insert(tk.END, f"[{timestamp}] {message}\n")
        self.console.see(tk.END)
        logging.info(message)
        
    def update_status(self, status):
        self.status_label.config(text=f"Status: {status}")
        
    def browse_bin_file(self):
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            title="Select Binary File",
            filetypes=[
                ("Binary files", "*.bin"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.selected_file_var.set(filename)
            
    def write_binary_file(self):
        if not self.connection:
            messagebox.showerror("Error", "Please connect to card first")
            return
            
        filename = self.selected_file_var.get()
        if not filename:
            messagebox.showerror("Error", "Please select a binary file")
            return
            
        try:
            # Read the binary file
            with open(filename, 'rb') as f:
                data = f.read()
                
            # Check file size
            if len(data) > self.TOTAL_SIZE:
                messagebox.showerror("Error", f"File size ({len(data)} bytes) exceeds card capacity ({self.TOTAL_SIZE} bytes)")
                return
                
            # Get start page
            try:
                start_page = int(self.start_page_entry.get())
                if not 0 <= start_page < self.PAGES:
                    messagebox.showerror("Error", f"Start page must be between 0 and {self.PAGES-1}")
                    return
            except ValueError:
                messagebox.showerror("Error", "Invalid start page")
                return
                
            # Calculate required pages
            required_pages = (len(data) + self.PAGE_SIZE - 1) // self.PAGE_SIZE
            if start_page + required_pages > self.PAGES:
                messagebox.showerror("Error", "File too large for selected start page")
                return
                
            # Confirm write
            if not messagebox.askyesno("Confirm Write", 
                f"This will write {len(data)} bytes starting at page {start_page}.\n"
                f"This will affect {required_pages} pages.\n\n"
                "Are you sure you want to continue?"):
                return
                
            # Reset progress bar
            self.write_progress['value'] = 0
            self.write_progress['maximum'] = required_pages
            
            # Write data page by page
            for i in range(required_pages):
                page = start_page + i
                offset = i * self.PAGE_SIZE
                page_data = data[offset:offset + self.PAGE_SIZE]
                
                # Pad last page if needed
                if len(page_data) < self.PAGE_SIZE:
                    page_data = page_data + bytes([0xFF] * (self.PAGE_SIZE - len(page_data)))
                
                # Write the page
                write_cmd = [0xFF, 0xD6, 0x00, page & 0xFF, len(page_data)] + list(page_data)
                response, sw1, sw2 = self.connection.transmit(write_cmd)
                
                if sw1 != 0x90:
                    messagebox.showerror("Error", f"Write failed at page {page}: SW1={hex(sw1)}, SW2={hex(sw2)}")
                    return
                
                # Update progress bar
                self.write_progress['value'] = i + 1
                self.root.update_idletasks()
                
            messagebox.showinfo("Success", f"Successfully wrote {len(data)} bytes to card")
            self.log_message(f"Wrote binary file {filename} to card starting at page {start_page}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Write failed: {str(e)}")
            self.log_message(f"Binary write error: {str(e)}")
            
    def write_page_data(self, page, data, max_retries=3):
        """Write a single page with verification and retry"""
        for attempt in range(max_retries):
            try:
                # Calculate base address for this page
                base_addr = page * self.PAGE_SIZE
                
                # Write data in small chunks (4 bytes at a time)
                chunk_size = 4
                for offset in range(0, len(data), chunk_size):
                    chunk = data[offset:offset + chunk_size]
                    addr = base_addr + offset
                    
                    # Match the working read command structure but for write
                    write_cmd = [
                        0xFF,           # Special CLA for this card
                        0xD0,           # Write command
                        0x00,           # P1
                        addr & 0xFF,    # P2: Address
                        len(chunk)      # Lc: Length of data
                    ] + list(chunk)     # Data bytes
                    
                    response, sw1, sw2 = self.connection.transmit(write_cmd)
                    
                    if sw1 != 0x90:
                        raise Exception(f"Write failed at offset {offset}: SW1={hex(sw1)}, SW2={hex(sw2)}")
                    
                    # AT24C64 write cycle time (5ms typical)
                    time.sleep(0.01)  # 10ms to be safe
                
                # Additional delay after page write
                time.sleep(0.05)  # 50ms between pages
                
                # Verify written data using the known working read command
                verify_cmd = [
                    0xFF,           # Special CLA for this card
                    0xB0,           # Read command
                    0x00,           # P1
                    base_addr & 0xFF,  # P2: Address
                    self.PAGE_SIZE  # Le: Expected length
                ]
                response, sw1, sw2 = self.connection.transmit(verify_cmd)
                
                if sw1 != 0x90:
                    raise Exception(f"Verify read failed: SW1={hex(sw1)}, SW2={hex(sw2)}")
                
                # Compare written data
                if list(response) != list(data):
                    if attempt < max_retries - 1:
                        self.log_message(f"Verification failed on page {page}, attempt {attempt + 1}/{max_retries}")
                        time.sleep(0.1)  # 100ms before retry
                        continue
                    raise Exception("Verification failed: Written data doesn't match")
                
                return True
                
            except Exception as e:
                if attempt < max_retries - 1:
                    self.log_message(f"Retry {attempt + 1}/{max_retries} for page {page}: {str(e)}")
                    time.sleep(0.1)  # 100ms before retry
                    continue
                self.log_message(f"Write error at page {page}: {str(e)}")
                return False
        
        return False

    def clone_card(self):
        """Write the selected dump to card starting from page 0"""
        if not self.connection:
            messagebox.showerror("Error", "Please connect to card first")
            return
            
        filename = self.selected_file_var.get()
        if not filename:
            messagebox.showerror("Error", "Please select a dump file")
            return
            
        try:
            # Read the dump file
            with open(filename, 'rb') as f:
                data = f.read()
                
            # Verify dump size
            if len(data) != self.TOTAL_SIZE:
                messagebox.showerror("Error", 
                    f"Invalid dump size. Expected {self.TOTAL_SIZE} bytes, got {len(data)} bytes.\n"
                    "Please use a complete card dump for cloning.")
                return
                
            # Confirm clone
            if not messagebox.askyesno("Confirm Clone", 
                f"This will completely overwrite the current card with the contents of:\n{filename}\n\n"
                "Are you sure you want to continue?"):
                return
                
            # Reset progress bar
            self.write_progress['value'] = 0
            self.write_progress['maximum'] = self.PAGES
            
            # Write data page by page
            failed_pages = []
            retry_pages = []
            
            for page in range(self.PAGES):
                offset = page * self.PAGE_SIZE
                page_data = data[offset:offset + self.PAGE_SIZE]
                
                # Try to write the page
                if not self.write_page_data(page, page_data):
                    retry_pages.append(page)
                
                # Update progress bar
                self.write_progress['value'] = page + 1
                self.root.update_idletasks()
                
                # Small delay between pages
                time.sleep(0.02)
            
            # Retry failed pages with more retries
            if retry_pages:
                self.log_message(f"Retrying {len(retry_pages)} failed pages...")
                for page in retry_pages:
                    offset = page * self.PAGE_SIZE
                    page_data = data[offset:offset + self.PAGE_SIZE]
                    if not self.write_page_data(page, page_data, max_retries=5):
                        failed_pages.append(page)
                    time.sleep(0.1)  # Longer delay between retries
            
            # Report results
            if not failed_pages:
                messagebox.showinfo("Success", "Card cloned successfully!")
                self.log_message(f"Successfully cloned card from {filename}")
            else:
                failed_str = ", ".join(str(p) for p in failed_pages)
                messagebox.showerror("Error", 
                    f"Clone completed with errors.\nFailed pages: {failed_str}")
                self.log_message(f"Clone completed with errors. Failed pages: {failed_str}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Clone failed: {str(e)}")
            self.log_message(f"Clone error: {str(e)}")
            
    def quick_clone(self):
        """Automatically find the latest dump and clone it"""
        try:
            # Find the most recent dump file
            dump_files = [f for f in os.listdir() if f.startswith("at24c64_dump_") and f.endswith(".bin")]
            if not dump_files:
                messagebox.showinfo("Error", "No dump files found")
                return
                
            latest_dump = max(dump_files)
            self.selected_file_var.set(latest_dump)
            self.clone_card()
            
        except Exception as e:
            messagebox.showerror("Error", f"Quick clone failed: {str(e)}")
            self.log_message(f"Quick clone error: {str(e)}")
            
if __name__ == "__main__":
    root = tk.Tk()
    app = AT24C64App(root)
    root.mainloop()
