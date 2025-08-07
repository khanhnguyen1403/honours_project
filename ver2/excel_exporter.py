import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from datetime import datetime, timedelta
import os


class ExcelExporter:
    """
    Excel export utility for appliance data management system.
    Creates comprehensive Excel reports with summary data and individual appliance sheets.
    """
    
    def __init__(self, appliances, right_gui):
        """
        Initialize the Excel exporter with appliance data and GUI reference.
        
        Args:
            appliances: Dictionary of appliance objects keyed by name
            right_gui: Reference to right GUI for logging events
        """
        self.appliances = appliances
        self.right_gui = right_gui
        self.export_folder = "exports"
        
        # Create exports directory if it doesn't exist
        self._ensure_export_folder_exists()
    
    def _ensure_export_folder_exists(self):
        """Create the exports folder if it doesn't already exist."""
        if not os.path.exists(self.export_folder):
            os.makedirs(self.export_folder)
    
    def export_data(self):
        """
        Export all appliance data to a timestamped Excel file.
        Creates a workbook with summary sheet and individual appliance sheets.
        
        Returns:
            bool: True if export successful, False if failed
        """
        try:
            # Generate timestamped filename
            timestamp = datetime.now()
            filename = f"appliance_data_{timestamp.strftime('%Y%m%d_%H%M')}.xlsx"
            filepath = os.path.join(self.export_folder, filename)
            
            # Create new workbook and remove default sheet
            workbook = openpyxl.Workbook()
            if workbook.worksheets:
                workbook.remove(workbook.active)
            
            # Create summary sheet first for overview
            self.create_summary_sheet(workbook, timestamp)
            
            # Create individual sheets for each appliance
            self._create_individual_appliance_sheets(workbook, timestamp)
            
            # Save workbook to file
            workbook.save(filepath)
            
            # Log successful export
            self._log_success(filename)
            print(f"Excel file exported successfully: {filepath}")
            return True
            
        except Exception as e:
            # Handle and log export failures
            self._log_error(e)
            return False

    def _create_individual_appliance_sheets(self, workbook, timestamp):
        """
        Create individual sheets for each appliance (excluding summary).
        
        Args:
            workbook: openpyxl Workbook object
            timestamp: Export timestamp for sheet headers
        """
        for name, appliance in self.appliances.items():
            if name != "All" and appliance is not None:
                self.create_appliance_sheet(workbook, name, appliance, timestamp)

    def _log_success(self, filename):
        """Log successful export operation."""
        if hasattr(self.right_gui, 'log_events'):
            self.right_gui.log_events(f"Data exported to {filename}")

    def _log_error(self, error):
        """Log export error."""
        error_msg = f"Export failed: {str(error)}"
        if hasattr(self.right_gui, 'log_events'):
            self.right_gui.log_events(error_msg)
        print(error_msg)
    
    def create_summary_sheet(self, workbook, timestamp):
        """
        Create a summary sheet with overview of all appliances.
        Includes current status, system totals, and formatted headers.
        
        Args:
            workbook: openpyxl Workbook object
            timestamp: Export timestamp for sheet headers
        """
        try:
            # Create summary sheet as first sheet
            sheet = workbook.create_sheet("Summary", 0)
            
            # Setup styling constants
            header_font, header_fill, center_align = self._get_header_styles()
            
            # Create title and timestamp headers
            self._create_summary_headers(sheet, timestamp, center_align)
            
            # Create data table with headers and appliance data
            self._create_summary_data_table(sheet, header_font, header_fill, center_align)
            
            # Add system summary statistics
            self._create_system_summary_section(sheet)
            
            # Auto-adjust column widths for better presentation
            self._auto_adjust_column_widths(sheet)
                
        except Exception as e:
            print(f"Error creating summary sheet: {e}")
            raise

    def _get_header_styles(self):
        """
        Get consistent styling objects for headers.
        
        Returns:
            tuple: (header_font, header_fill, center_align) style objects
        """
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        center_align = Alignment(horizontal="center", vertical="center")
        return header_font, header_fill, center_align

    def _create_summary_headers(self, sheet, timestamp, center_align):
        """
        Create title and timestamp headers for summary sheet.
        
        Args:
            sheet: openpyxl worksheet object
            timestamp: Export timestamp
            center_align: Alignment style object
        """
        # Main title
        sheet['A1'] = "Appliance Data Summary"
        sheet['A1'].font = Font(bold=True, size=16)
        sheet['A1'].alignment = center_align
        sheet.merge_cells('A1:G1')
        
        # Export timestamp
        sheet['A2'] = f"Export Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        sheet['A2'].font = Font(bold=True)
        sheet.merge_cells('A2:G2')

    def _create_summary_data_table(self, sheet, header_font, header_fill, center_align):
        """
        Create the main data table with appliance information.
        
        Args:
            sheet: openpyxl worksheet object
            header_font: Font style for headers
            header_fill: Fill style for headers
            center_align: Alignment style
        """
        # Create table headers
        headers = [
            "Appliance", "Type", "Status", "Current Power (W)", 
            "Energy Used (kWh)", "Time Operated (sec)", "Fault"
        ]
        
        for col, header in enumerate(headers, 1):
            cell = sheet.cell(row=4, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center_align
        
        # Populate data rows for each appliance
        self._populate_appliance_data_rows(sheet, center_align)

    def _populate_appliance_data_rows(self, sheet, center_align):
        """
        Populate data rows with information from each appliance.
        
        Args:
            sheet: openpyxl worksheet object
            center_align: Alignment style
        """
        row = 5
        for name, appliance in self.appliances.items():
            if name == "All":  # Skip summary appliance
                continue
                
            if appliance is not None:
                try:
                    # Get appliance data safely
                    appliance_data = self._extract_appliance_data(name, appliance)
                    
                    # Add data to cells with formatting
                    for col, value in enumerate(appliance_data, 1):
                        cell = sheet.cell(row=row, column=col, value=value)
                        cell.alignment = center_align
                        
                        # Apply status color coding
                        if col == 3:  # Status column
                            self._apply_status_color_coding(cell, value)
                    
                    row += 1
                    
                except Exception as e:
                    print(f"Error processing appliance {name}: {e}")
                    continue

    def _extract_appliance_data(self, name, appliance):
        """
        Safely extract all relevant data from an appliance object.
        
        Args:
            name: Appliance name
            appliance: Appliance object
            
        Returns:
            list: List of appliance data values
        """
        # Get type string safely
        type_str = {0: "Load", 1: "Source", 2: "Storage"}.get(
            getattr(appliance, 'type', 0), "Unknown"
        )
        
        # Safely extract numeric values with fallbacks
        current_power = self._safe_get_value(appliance, 'get_current_power', 0)
        energy_used = self._safe_get_attribute(appliance, 'energy_used', 0)
        time_operated = self._safe_get_attribute(appliance, 'time_operated', 0)
        
        return [
            str(name),
            str(type_str),
            "ON" if getattr(appliance, 'power_status', False) else "OFF",
            float(current_power),
            round(float(energy_used), 3),
            int(time_operated),
            "Yes" if getattr(appliance, 'fault', False) else "No"
        ]

    def _safe_get_value(self, obj, method_name, default):
        """
        Safely call a method on an object with fallback.
        
        Args:
            obj: Object to call method on
            method_name: Name of method to call
            default: Default value if method fails
            
        Returns:
            Method result or default value
        """
        try:
            if hasattr(obj, method_name):
                return getattr(obj, method_name)()
            return default
        except:
            return default

    def _safe_get_attribute(self, obj, attr_name, default):
        """
        Safely get an attribute from an object with fallback.
        
        Args:
            obj: Object to get attribute from
            attr_name: Name of attribute to get
            default: Default value if attribute doesn't exist
            
        Returns:
            Attribute value or default value
        """
        try:
            return getattr(obj, attr_name, default)
        except:
            return default

    def _apply_status_color_coding(self, cell, value):
        """
        Apply color coding to status cells based on ON/OFF state.
        
        Args:
            cell: openpyxl cell object
            value: Cell value (ON/OFF)
        """
        if value == "ON":
            cell.fill = PatternFill(start_color="90EE90", end_color="90EE90", fill_type="solid")
        else:
            cell.fill = PatternFill(start_color="FFB6C1", end_color="FFB6C1", fill_type="solid")

    def _create_system_summary_section(self, sheet):
        """
        Create system summary statistics section.
        
        Args:
            sheet: openpyxl worksheet object
        """
        try:
            # Calculate current row for summary section
            row = self._find_last_data_row(sheet)
            
            # Check if "All" appliance exists and has summary data
            if "All" in self.appliances and self.appliances["All"] is not None:
                summary = self.appliances["All"]
                
                # Create summary section header
                sheet[f'A{row + 2}'] = "System Summary"
                sheet[f'A{row + 2}'].font = Font(bold=True, size=14)
                sheet.merge_cells(f'A{row + 2}:G{row + 2}')
                
                # Get summary values safely
                summary_data = self._extract_system_summary_data(summary)
                
                # Add summary statistics to sheet
                for i, (label, value) in enumerate(summary_data):
                    sheet[f'A{row + 4 + i}'] = label
                    sheet[f'B{row + 4 + i}'] = value
                    sheet[f'A{row + 4 + i}'].font = Font(bold=True)
        except Exception as e:
            print(f"Error creating summary statistics: {e}")

    def _find_last_data_row(self, sheet):
        """
        Find the last row with data in the sheet.
        
        Args:
            sheet: openpyxl worksheet object
            
        Returns:
            int: Last row number with data
        """
        # Count appliances excluding "All"
        appliance_count = sum(1 for name, appliance in self.appliances.items() 
                            if name != "All" and appliance is not None)
        return 4 + appliance_count  # 4 is the header row + data rows

    def _extract_system_summary_data(self, summary):
        """
        Extract system summary statistics from the summary appliance.
        
        Args:
            summary: Summary appliance object
            
        Returns:
            list: List of (label, value) tuples for summary statistics
        """
        # Safely get summary values with fallbacks
        total_consumption = self._safe_get_attribute(summary, 'total_power_consumption', 0)
        total_generation = self._safe_get_attribute(summary, 'total_power_generation', 0)
        net_power = self._safe_get_value(summary, 'get_current_power', 0)
        total_energy_consumption = self._safe_get_attribute(summary, 'total_energy_consumption', 0)
        total_energy_generation = self._safe_get_attribute(summary, 'total_energy_generated', 0)
        
        return [
            ("Total Power Consumption:", f"{float(total_consumption):.1f} W"),
            ("Total Power Generation:", f"{float(total_generation):.1f} W"),
            ("Net Power:", f"{float(net_power):.1f} W"),
            ("Total Energy Consumption:", f"{float(total_energy_consumption):.3f} kWh"),
            ("Total Energy Generation:", f"{float(total_energy_generation):.3f} kWh"),
        ]

    def _auto_adjust_column_widths(self, sheet):
        """
        Automatically adjust column widths based on content.
        
        Args:
            sheet: openpyxl worksheet object
        """
        try:
            for col in sheet.columns:
                max_length = 0
                column = col[0].column_letter
                
                # Find maximum content length in column
                for cell in col:
                    try:
                        if cell.value is not None and len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                # Set adjusted width with reasonable limits
                adjusted_width = min(max_length + 2, 20) if max_length > 0 else 10
                sheet.column_dimensions[column].width = adjusted_width
        except Exception as e:
            print(f"Error adjusting column widths: {e}")
    
    def create_appliance_sheet(self, workbook, name, appliance, timestamp):
        """
        Create a detailed sheet for an individual appliance with comprehensive data.
        Includes current status, configuration, and power history.
        
        Args:
            workbook: openpyxl Workbook object
            name: Appliance name
            appliance: Appliance object
            timestamp: Export timestamp for sheet headers
        """
        try:
            # Create safe sheet name (Excel has naming restrictions)
            sheet_name = self._create_safe_sheet_name(name)
            sheet = workbook.create_sheet(sheet_name)
            
            # Setup styling
            header_font, header_fill, center_align = self._get_header_styles()
            
            # Create sheet header section
            self._create_appliance_sheet_headers(sheet, name, timestamp, center_align)
            
            # Add current status section
            self._create_current_status_section(sheet, name, appliance)
            
            # Add configuration section
            self._create_configuration_section(sheet, appliance)
            
            # Add power history section
            self._create_power_history_section(sheet, appliance, header_font, header_fill, center_align)
            
            # Auto-adjust column widths
            self._auto_adjust_column_widths(sheet)
                
        except Exception as e:
            print(f"Error creating sheet for {name}: {e}")
            raise

    def _create_safe_sheet_name(self, name):
        """
        Create a safe sheet name that complies with Excel naming restrictions.
        
        Args:
            name: Original appliance name
            
        Returns:
            str: Safe sheet name for Excel
        """
        # Replace invalid characters with underscores
        invalid_chars = ['/', '\\', '?', '*', '[', ']', ':']
        sheet_name = str(name)
        for char in invalid_chars:
            sheet_name = sheet_name.replace(char, '_')
        
        # Excel sheet name limit is 31 characters
        return sheet_name[:31]

    def _create_appliance_sheet_headers(self, sheet, name, timestamp, center_align):
        """
        Create header section for appliance sheet.
        
        Args:
            sheet: openpyxl worksheet object
            name: Appliance name
            timestamp: Export timestamp
            center_align: Alignment style
        """
        # Appliance name title
        sheet['A1'] = f"{name}"
        sheet['A1'].font = Font(bold=True, size=16)
        sheet['A1'].alignment = center_align
        sheet.merge_cells('A1:E1')
        
        # Export timestamp
        sheet['A2'] = f"Export Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        sheet['A2'].font = Font(bold=True)
        sheet.merge_cells('A2:E2')

    def _create_current_status_section(self, sheet, name, appliance):
        """
        Create current status section with appliance metrics.
        
        Args:
            sheet: openpyxl worksheet object
            name: Appliance name
            appliance: Appliance object
        """
        # Section header
        sheet['A4'] = "Current Status"
        sheet['A4'].font = Font(bold=True, size=14)
        sheet.merge_cells('A4:B4')
        
        # Extract appliance data safely
        status_data = self._extract_appliance_status_data(name, appliance)
        
        # Add status data to sheet
        for i, (label, value) in enumerate(status_data):
            sheet[f'A{6 + i}'] = label
            sheet[f'B{6 + i}'] = value
            sheet[f'A{6 + i}'].font = Font(bold=True)

    def _extract_appliance_status_data(self, name, appliance):
        """
        Extract comprehensive status data from appliance object.
        
        Args:
            name: Appliance name
            appliance: Appliance object
            
        Returns:
            list: List of (label, value) tuples for status data
        """
        # Safely extract all appliance attributes
        appliance_type = self._safe_get_attribute(appliance, 'type', 0)
        power_status = self._safe_get_attribute(appliance, 'power_status', False)
        voltage_rating = self._safe_get_attribute(appliance, 'voltage_rating', 0)
        power_rating = self._safe_get_attribute(appliance, 'power_rating', 0)
        energy_used = self._safe_get_attribute(appliance, 'energy_used', 0)
        time_operated = self._safe_get_attribute(appliance, 'time_operated', 0)
        fault = self._safe_get_attribute(appliance, 'fault', False)
        current_power = self._safe_get_value(appliance, 'get_current_power', 0)
        
        return [
            ("Name:", str(name)),
            ("Type:", {0: "Load", 1: "Source", 2: "Storage"}.get(appliance_type, "Unknown")),
            ("Power Status:", "ON" if power_status else "OFF"),
            ("Current Power:", f"{float(current_power):.1f} W"),
            ("Voltage Rating:", f"{float(voltage_rating)} V"),
            ("Power Rating:", f"{float(power_rating)} W"),
            ("Energy Used:", f"{float(energy_used):.3f} kWh"),
            ("Time Operated:", f"{int(time_operated)} seconds"),
            ("Fault Status:", "Yes" if fault else "No"),
        ]

    def _create_configuration_section(self, sheet, appliance):
        """
        Create configuration section with type-specific parameters.
        
        Args:
            sheet: openpyxl worksheet object
            appliance: Appliance object
        """
        config_row = 16
        sheet[f'A{config_row}'] = "Configuration"
        sheet[f'A{config_row}'].font = Font(bold=True, size=14)
        sheet.merge_cells(f'A{config_row}:B{config_row}')
        
        # Get configuration data based on appliance type
        appliance_type = self._safe_get_attribute(appliance, 'type', 0)
        config_data = self._get_configuration_data(appliance, appliance_type)
        
        # Add configuration data to sheet
        for i, (label, value) in enumerate(config_data):
            sheet[f'A{config_row + 2 + i}'] = label
            sheet[f'B{config_row + 2 + i}'] = value
            sheet[f'A{config_row + 2 + i}'].font = Font(bold=True)

    def _get_configuration_data(self, appliance, appliance_type):
        """
        Get type-specific configuration data for appliance.
        
        Args:
            appliance: Appliance object
            appliance_type: Integer type code (0=Load, 1=Source, 2=Storage)
            
        Returns:
            list: List of (label, value) tuples for configuration data
        """
        if appliance_type == 0:  # Load
            return [
                ("Max Current:", f"{self._safe_get_attribute(appliance, 'max_current', 0)} A"),
                ("Overvoltage Threshold:", f"{self._safe_get_attribute(appliance, 'overvoltage_threshold', 0)} V"),
                ("Undervoltage Threshold:", f"{self._safe_get_attribute(appliance, 'undervoltage_threshold', 0)} V"),
                ("Differential Threshold:", f"{self._safe_get_attribute(appliance, 'differential_threshold', 0)} A"),
            ]
        elif appliance_type == 1:  # Source
            return [
                ("Max Output Power:", f"{self._safe_get_attribute(appliance, 'max_output_power', 0)} W"),
                ("Max Output Current:", f"{self._safe_get_attribute(appliance, 'max_output_current', 0)} A"),
                ("Undervoltage Threshold:", f"{self._safe_get_attribute(appliance, 'undervoltage_threshold', 0)} V"),
            ]
        elif appliance_type == 2:  # Storage
            return [
                ("Capacity:", f"{self._safe_get_attribute(appliance, 'capacity', 0)} Wh"),
                ("Max Charge Current:", f"{self._safe_get_attribute(appliance, 'max_charge_current', 0)} A"),
                ("Max Discharge Current:", f"{self._safe_get_attribute(appliance, 'max_discharge_current', 0)} A"),
            ]
        else:
            return []

    def _create_power_history_section(self, sheet, appliance, header_font, header_fill, center_align):
        """
        Create power history section with time series data.
        
        Args:
            sheet: openpyxl worksheet object
            appliance: Appliance object
            header_font: Font style for headers
            header_fill: Fill style for headers
            center_align: Alignment style
        """
        # Calculate starting row for history section
        appliance_type = self._safe_get_attribute(appliance, 'type', 0)
        config_count = len(self._get_configuration_data(appliance, appliance_type))
        history_row = 16 + config_count + 4
        
        # Section header
        sheet[f'A{history_row}'] = "Power History (Last 300 seconds)"
        sheet[f'A{history_row}'].font = Font(bold=True, size=14)
        sheet.merge_cells(f'A{history_row}:C{history_row}')
        
        # Create column headers
        headers = ["Time Index", "Power (W)", "Time Ago (sec)"]
        for col, header in enumerate(headers, 1):
            cell = sheet.cell(row=history_row + 2, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center_align
        
        # Add power history data
        self._populate_power_history_data(sheet, appliance, history_row)

    def _populate_power_history_data(self, sheet, appliance, history_row):
        """
        Populate power history data in the sheet.
        
        Args:
            sheet: openpyxl worksheet object
            appliance: Appliance object
            history_row: Starting row for history section
        """
        try:
            # Get power history data safely
            power_history = self._safe_get_value(appliance, 'get_power_history', [0] * 300)
            if not power_history:
                power_history = [0] * 300
            
            # Populate each data point
            for i, power_value in enumerate(power_history):
                row_idx = history_row + 3 + i
                sheet.cell(row=row_idx, column=1, value=i + 1)  # Time index
                sheet.cell(row=row_idx, column=2, value=round(float(power_value), 2))  # Power value
                sheet.cell(row=row_idx, column=3, value=299 - i)  # Time ago in seconds
        except Exception as e:
            print(f"Error adding power history: {e}")