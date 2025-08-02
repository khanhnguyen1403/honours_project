import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from datetime import datetime, timedelta
import os

class ExcelExporter:
    def __init__(self, appliances, right_gui):
        self.appliances = appliances
        self.right_gui = right_gui
        self.export_folder = "exports"
        
        # Create exports folder if it doesn't exist
        if not os.path.exists(self.export_folder):
            os.makedirs(self.export_folder)
    
    def export_data(self):
        """Export all appliance data to Excel"""
        try:
            timestamp = datetime.now()
            filename = f"appliance_data_{timestamp.strftime('%Y%m%d_%H%M')}.xlsx"
            filepath = os.path.join(self.export_folder, filename)
            
            # Create workbook and worksheets
            workbook = openpyxl.Workbook()
            
            # Remove default sheet
            if workbook.worksheets:
                workbook.remove(workbook.active)
            
            # Create summary sheet first
            self.create_summary_sheet(workbook, timestamp)
            
            # Create individual appliance sheets
            for name, appliance in self.appliances.items():
                if name != "All" and appliance is not None:
                    self.create_appliance_sheet(workbook, name, appliance, timestamp)
            
            # Save workbook
            workbook.save(filepath)
            
            # Log success
            if hasattr(self.right_gui, 'log_events'):
                self.right_gui.log_events(f"Data exported to {filename}")
            
            print(f"Excel file exported successfully: {filepath}")
            return True
            
        except Exception as e:
            error_msg = f"Export failed: {str(e)}"
            if hasattr(self.right_gui, 'log_events'):
                self.right_gui.log_events(error_msg)
            print(error_msg)
            return False
    
    def create_summary_sheet(self, workbook, timestamp):
        """Create summary sheet with overview data"""
        try:
            sheet = workbook.create_sheet("Summary", 0)
            
            # Header styling
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            center_align = Alignment(horizontal="center", vertical="center")
            
            # Title
            sheet['A1'] = "Appliance Data Summary"
            sheet['A1'].font = Font(bold=True, size=16)
            sheet['A1'].alignment = center_align
            sheet.merge_cells('A1:G1')
            
            # Export timestamp
            sheet['A2'] = f"Export Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            sheet['A2'].font = Font(bold=True)
            sheet.merge_cells('A2:G2')
            
            # Headers
            headers = ["Appliance", "Type", "Status", "Current Power (W)", "Energy Used (kWh)", "Time Operated (sec)", "Fault"]
            for col, header in enumerate(headers, 1):
                cell = sheet.cell(row=4, column=col, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = center_align
            
            # Data rows
            row = 5
            for name, appliance in self.appliances.items():
                if name == "All":
                    continue
                    
                if appliance is not None:
                    try:
                        # Determine type string
                        type_str = {0: "Load", 1: "Source", 2: "Storage"}.get(appliance.type, "Unknown")
                        
                        # Safely get values with fallbacks
                        current_power = 0
                        energy_used = 0
                        time_operated = 0
                        
                        try:
                            current_power = appliance.get_current_power() if hasattr(appliance, 'get_current_power') else 0
                        except:
                            current_power = 0
                            
                        try:
                            energy_used = appliance.energy_used if hasattr(appliance, 'energy_used') else 0
                        except:
                            energy_used = 0
                            
                        try:
                            time_operated = appliance.time_operated if hasattr(appliance, 'time_operated') else 0
                        except:
                            time_operated = 0
                        
                        # Add data
                        data = [
                            str(name),
                            str(type_str),
                            "ON" if getattr(appliance, 'power_status', False) else "OFF",
                            float(current_power),
                            round(float(energy_used), 3),
                            int(time_operated),
                            "Yes" if getattr(appliance, 'fault', False) else "No"
                        ]
                        
                        for col, value in enumerate(data, 1):
                            cell = sheet.cell(row=row, column=col, value=value)
                            cell.alignment = center_align
                            
                            # Color code status
                            if col == 3:  # Status column
                                if value == "ON":
                                    cell.fill = PatternFill(start_color="90EE90", end_color="90EE90", fill_type="solid")
                                else:
                                    cell.fill = PatternFill(start_color="FFB6C1", end_color="FFB6C1", fill_type="solid")
                        
                        row += 1
                        
                    except Exception as e:
                        print(f"Error processing appliance {name}: {e}")
                        continue
            
            # Summary statistics
            try:
                # Check if "All" appliance exists and has summary data
                if "All" in self.appliances and self.appliances["All"] is not None:
                    summary = self.appliances["All"]
                    
                    sheet[f'A{row + 2}'] = "System Summary"
                    sheet[f'A{row + 2}'].font = Font(bold=True, size=14)
                    sheet.merge_cells(f'A{row + 2}:G{row + 2}')
                    
                    # Safely get summary values
                    total_consumption = getattr(summary, 'total_power_consumption', 0)
                    total_generation = getattr(summary, 'total_power_generation', 0)
                    net_power = 0
                    total_energy_consumption = getattr(summary, 'total_energy_consumption', 0)
                    total_energy_generation = getattr(summary, 'total_energy_generated', 0)
                    
                    try:
                        net_power = summary.get_current_power() if hasattr(summary, 'get_current_power') else 0
                    except:
                        net_power = 0
                    
                    summary_data = [
                        ("Total Power Consumption:", f"{float(total_consumption):.1f} W"),
                        ("Total Power Generation:", f"{float(total_generation):.1f} W"),
                        ("Net Power:", f"{float(net_power):.1f} W"),
                        ("Total Energy Consumption:", f"{float(total_energy_consumption):.3f} kWh"),
                        ("Total Energy Generation:", f"{float(total_energy_generation):.3f} kWh"),
                    ]
                    
                    for i, (label, value) in enumerate(summary_data):
                        sheet[f'A{row + 4 + i}'] = label
                        sheet[f'B{row + 4 + i}'] = value
                        sheet[f'A{row + 4 + i}'].font = Font(bold=True)
            except Exception as e:
                print(f"Error creating summary statistics: {e}")
            
            # Auto-adjust column widths
            try:
                for col in sheet.columns:
                    max_length = 0
                    column = col[0].column_letter
                    for cell in col:
                        try:
                            if cell.value is not None and len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 20) if max_length > 0 else 10
                    sheet.column_dimensions[column].width = adjusted_width
            except Exception as e:
                print(f"Error adjusting column widths: {e}")
                
        except Exception as e:
            print(f"Error creating summary sheet: {e}")
            raise
    
    def create_appliance_sheet(self, workbook, name, appliance, timestamp):
        """Create detailed sheet for individual appliance"""
        try:
            # Clean sheet name (Excel doesn't allow certain characters)
            sheet_name = str(name).replace('/', '_').replace('\\', '_').replace('?', '_').replace('*', '_').replace('[', '_').replace(']', '_').replace(':', '_')
            sheet_name = sheet_name[:31]  # Excel sheet name limit
            
            sheet = workbook.create_sheet(sheet_name)
            
            # Header styling
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            center_align = Alignment(horizontal="center", vertical="center")
            
            # Title
            sheet['A1'] = f"{name}"
            sheet['A1'].font = Font(bold=True, size=16)
            sheet['A1'].alignment = center_align
            sheet.merge_cells('A1:E1')
            
            # Export timestamp
            sheet['A2'] = f"Export Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            sheet['A2'].font = Font(bold=True)
            sheet.merge_cells('A2:E2')
            
            # Current Status Section
            sheet['A4'] = "Current Status"
            sheet['A4'].font = Font(bold=True, size=14)
            sheet.merge_cells('A4:B4')
            
            # Safely get appliance data
            appliance_type = getattr(appliance, 'type', 0)
            power_status = getattr(appliance, 'power_status', False)
            voltage_rating = getattr(appliance, 'voltage_rating', 0)
            power_rating = getattr(appliance, 'power_rating', 0)
            energy_used = getattr(appliance, 'energy_used', 0)
            time_operated = getattr(appliance, 'time_operated', 0)
            fault = getattr(appliance, 'fault', False)
            
            current_power = 0
            try:
                current_power = appliance.get_current_power() if hasattr(appliance, 'get_current_power') else 0
            except:
                current_power = 0
            
            status_data = [
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
            
            for i, (label, value) in enumerate(status_data):
                sheet[f'A{6 + i}'] = label
                sheet[f'B{6 + i}'] = value
                sheet[f'A{6 + i}'].font = Font(bold=True)
            
            # Configuration Section
            config_row = 16
            sheet[f'A{config_row}'] = "Configuration"
            sheet[f'A{config_row}'].font = Font(bold=True, size=14)
            sheet.merge_cells(f'A{config_row}:B{config_row}')
            
            config_data = []
            if appliance_type == 0:  # Load
                config_data = [
                    ("Max Current:", f"{getattr(appliance, 'max_current', 0)} A"),
                    ("Overvoltage Threshold:", f"{getattr(appliance, 'overvoltage_threshold', 0)} V"),
                    ("Undervoltage Threshold:", f"{getattr(appliance, 'undervoltage_threshold', 0)} V"),
                    ("Differential Threshold:", f"{getattr(appliance, 'differential_threshold', 0)} A"),
                ]
            elif appliance_type == 1:  # Source
                config_data = [
                    ("Max Output Power:", f"{getattr(appliance, 'max_output_power', 0)} W"),
                    ("Max Output Current:", f"{getattr(appliance, 'max_output_current', 0)} A"),
                    ("Undervoltage Threshold:", f"{getattr(appliance, 'undervoltage_threshold', 0)} V"),
                ]
            elif appliance_type == 2:  # Storage
                config_data = [
                    ("Capacity:", f"{getattr(appliance, 'capacity', 0)} Wh"),
                    ("Max Charge Current:", f"{getattr(appliance, 'max_charge_current', 0)} A"),
                    ("Max Discharge Current:", f"{getattr(appliance, 'max_discharge_current', 0)} A"),
                ]
            
            for i, (label, value) in enumerate(config_data):
                sheet[f'A{config_row + 2 + i}'] = label
                sheet[f'B{config_row + 2 + i}'] = value
                sheet[f'A{config_row + 2 + i}'].font = Font(bold=True)
            
            # Power History Section
            history_row = config_row + len(config_data) + 4
            sheet[f'A{history_row}'] = "Power History (Last 300 seconds)"
            sheet[f'A{history_row}'].font = Font(bold=True, size=14)
            sheet.merge_cells(f'A{history_row}:C{history_row}')
            
            # Power history headers
            headers = ["Time Index", "Power (W)", "Time Ago (sec)"]
            for col, header in enumerate(headers, 1):
                cell = sheet.cell(row=history_row + 2, column=col, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = center_align
            
            # Power history data
            try:
                power_history = appliance.get_power_history() if hasattr(appliance, 'get_power_history') else [0] * 300
                for i, power_value in enumerate(power_history):
                    row_idx = history_row + 3 + i
                    sheet.cell(row=row_idx, column=1, value=i + 1)
                    sheet.cell(row=row_idx, column=2, value=round(float(power_value), 2))
                    sheet.cell(row=row_idx, column=3, value=299 - i)
            except Exception as e:
                print(f"Error adding power history for {name}: {e}")
            
            # Auto-adjust column widths
            try:
                for col in sheet.columns:
                    max_length = 0
                    column = col[0].column_letter
                    for cell in col:
                        try:
                            if cell.value is not None and len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 20) if max_length > 0 else 10
                    sheet.column_dimensions[column].width = adjusted_width
            except Exception as e:
                print(f"Error adjusting column widths for {name}: {e}")
                
        except Exception as e:
            print(f"Error creating sheet for {name}: {e}")
            raise