from typing import List, Optional, Literal, Set
import os
import win32com.client
import pythoncom
from typing_extensions import TypedDict

# Default path and table configurations
DEFAULT_PATH = r"C:\Users\matth\OneDrive - Matthieu Mordrel\Work\Projects\Kovera\Project 2\Analysis of Files"
DEFAULT_FILE_NAME = "12. Grouped Data.xlsx"
DEFAULT_FULL_PATH = os.path.join(DEFAULT_PATH, DEFAULT_FILE_NAME)
DEFAULT_SHEET = "Sheet1"  # Assuming the default sheet name

# Type definitions for table configurations
class TableConfig(TypedDict):
    sheet_name: str
    table_name: str
    column_name: str

# Table configurations
TABLE_CONFIGS: dict[str, TableConfig] = {
    "P_P": {
        "sheet_name": "P_P",
        "table_name": "P_P_Table",
        "column_name": "Product_Code_Parent"
    },
    "P_E": {
        "sheet_name": "P_E",
        "table_name": "P_E_Table",
        "column_name": "Product_Code"
    },
    "P_LADE": {
        "sheet_name": "P_LADE",
        "table_name": "P_LADE_Table",
        "column_name": "Product_Code"
    }
}

def delete_rows_by_values(
    values_to_delete: List[str],
    excel_path: Optional[str] = None,
    sheet_name: Optional[str] = None,
    table_name: Optional[str] = None,
    column_name: Optional[str] = None,
    save_changes: bool = True,
    table_type: Optional[Literal["P_P", "P_E", "P_LADE"]] = None,
    visible: bool = False
) -> int:
    """
    Deletes rows from an Excel table where values in a specified column match any value in the provided list.
    Uses pywin32 to interact directly with Excel, preserving array formulas.
    
    Args:
        values_to_delete (List[str]): List of values to search for and delete matching rows
        excel_path (str, optional): Path to the Excel file. Defaults to the standard analysis file.
        sheet_name (str, optional): Name of the worksheet containing the table. Defaults to "Sheet1".
        table_name (str, optional): Name of the table to search in. If table_type is provided, this is determined automatically.
        column_name (str, optional): Name of the column to search in. If table_type is provided, this is determined automatically.
        save_changes (bool, optional): Whether to save changes to the file. Defaults to True.
        table_type (str, optional): Shortcut to specify a predefined table configuration. Options: "P_P", "P_E", "P_LADE".
        visible (bool, optional): Whether to make Excel visible during processing. Defaults to False.
        
    Returns:
        int: Number of rows deleted
        
    Example:
        # Delete rows where Product Code is "P001" or "P002" in the P_E table
        delete_rows_by_values(
            ["P001", "P002"], 
            table_type="P_E"
        )
        
        # Delete rows with full custom parameters
        delete_rows_by_values(
            ["P001", "P002"], 
            "C:/path/to/file.xlsx", 
            "Products", 
            "ProductTable", 
            "ProductID"
        )
    """
    # Apply default configurations if table_type is provided
    if table_type and table_type in TABLE_CONFIGS:
        config = TABLE_CONFIGS[table_type]
        sheet_name = config["sheet_name"]
        table_name = config["table_name"]
        column_name = config["column_name"]
    
    # Apply other defaults
    if excel_path is None:
        excel_path = DEFAULT_FULL_PATH
    
    if sheet_name is None:
        sheet_name = DEFAULT_SHEET
    
    # Ensure all required parameters are provided
    if table_name is None:
        raise ValueError("Table name must be provided either directly or via table_type")
    
    if column_name is None:
        raise ValueError("Column name must be provided either directly or via table_type")
    
    # Ensure the file exists
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Excel file not found: {excel_path}")
    
    # Convert values_to_delete to a set for faster lookups (case-insensitive)
    values_set: Set[str] = {str(v).lower() for v in values_to_delete}
    
    # Initialize COM
    pythoncom.CoInitialize()
    
    # Define Excel as None initially to handle the case where it's not created
    excel = None
    
    try:
        # Create Excel application
        excel = win32com.client.Dispatch("Excel.Application")
        excel.DisplayAlerts = False  # Suppress alerts
        excel.Visible = visible  # Set visibility
        
        # Open the workbook
        workbook = excel.Workbooks.Open(excel_path)
        
        try:
            # Check if the sheet exists
            try:
                worksheet = workbook.Worksheets(sheet_name)
            except Exception:
                raise ValueError(f"Sheet '{sheet_name}' not found in workbook")
            
            # Find the table
            table_found = False
            list_object = None
            
            for list_obj in worksheet.ListObjects:
                if list_obj.Name == table_name or list_obj.DisplayName == table_name:
                    table_found = True
                    list_object = list_obj
                    break
            
            if not table_found or list_object is None:
                raise ValueError(f"Table '{table_name}' not found in sheet '{sheet_name}'")
            
            # Get the header row and find the column index
            # Access COM object properties directly
            header_range = list_object.HeaderRowRange
            column_index = None
            
            for i in range(1, header_range.Columns.Count + 1):
                if header_range.Cells(1, i).Value == column_name:
                    column_index = i
                    break
            
            if column_index is None:
                raise ValueError(f"Column '{column_name}' not found in table '{table_name}'")
            
            # Get the data range
            data_range = list_object.DataBodyRange
            
            if data_range is None or data_range.Rows.Count == 0:
                # No data in the table
                return 0
            
            # Find rows to delete (in reverse order to avoid index shifting issues)
            rows_to_delete: List[int] = []
            
            for row in range(data_range.Rows.Count, 0, -1):
                cell_value = data_range.Cells(row, column_index).Value
                
                # Skip None values
                if cell_value is None:
                    continue
                
                # Convert to string and compare case-insensitively
                if str(cell_value).lower() in values_set:
                    rows_to_delete.append(row)
            
            # Delete the identified rows
            deleted_count = 0
            
            for row_index in rows_to_delete:
                data_range.Rows(row_index).Delete()
                deleted_count += 1
            
            # Save if requested
            if save_changes:
                workbook.Save()
            
            return deleted_count
            
        finally:
            # Close the workbook
            workbook.Close(SaveChanges=False)  # We've already saved if needed
            
    except Exception as e:
        raise e
    
    finally:
        # Quit Excel and clean up
        if excel is not None:
            excel.Quit()
            del excel
        
        # Uninitialize COM
        pythoncom.CoUninitialize()

def delete_from_pp_table(values_to_delete: List[str], excel_path: Optional[str] = None) -> int:
    """
    Deletes rows from the P_P_Table where Product_Code_Parent matches any value in the provided list.
    
    Args:
        values_to_delete (List[str]): List of Product_Code_Parent values to delete
        excel_path (str, optional): Path to the Excel file. Defaults to the standard analysis path.
        
    Returns:
        int: Number of rows deleted
    """
    return delete_rows_by_values(values_to_delete, excel_path=excel_path, table_type="P_P")

def delete_from_pe_table(values_to_delete: List[str], excel_path: Optional[str] = None) -> int:
    """
    Deletes rows from the P_E_Table where Product_Code matches any value in the provided list.
    
    Args:
        values_to_delete (List[str]): List of Product_Code values to delete
        excel_path (str, optional): Path to the Excel file. Defaults to the standard analysis path.
        
    Returns:
        int: Number of rows deleted
    """
    return delete_rows_by_values(values_to_delete, excel_path=excel_path, table_type="P_E")

def delete_from_plade_table(values_to_delete: List[str], excel_path: Optional[str] = None) -> int:
    """
    Deletes rows from the P_LADE_Table where Product_Code matches any value in the provided list.
    
    Args:
        values_to_delete (List[str]): List of Product_Code values to delete
        excel_path (str, optional): Path to the Excel file. Defaults to the standard analysis path.
        
    Returns:
        int: Number of rows deleted
    """
    return delete_rows_by_values(values_to_delete, excel_path=excel_path, table_type="P_LADE")

# =============================================================================
# CONFIGURATION SECTION - MODIFY THIS PART TO RUN THE SCRIPT
# =============================================================================

# Set this to True to run the script when this file is executed
RUN_SCRIPT = True

# Choose which operation to perform by setting exactly ONE of these to True
DELETE_FROM_PP_TABLE = False
DELETE_FROM_PE_TABLE = False
DELETE_FROM_PLADE_TABLE = False
DELETE_FROM_CUSTOM_TABLE = True

# Values to delete - MODIFY THIS LIST with your values
VALUES_TO_DELETE = [
    "fezaf",
    "Riette",
    "Jambon",
    "Saucisson",
    "1",
    "3",
    "5",
    "7",
    "zaef",
    "_9",
    "fef",
    "esf"
]

# -------------------------------------------------------------------------
# FILE PATH CONFIGURATION
# -------------------------------------------------------------------------
# By default, the script uses this file for all operations:
# C:\Users\matth\OneDrive - Matthieu Mordrel\Work\Projects\Kovera\Project 2\Analysis of Files\12. Grouped Data.xlsx
#
# To use a different file, set USE_DEFAULT_FILE to False and specify the full path below
USE_DEFAULT_FILE = False
CUSTOM_FILE_PATH = r"C:\Users\matth\OneDrive - Matthieu Mordrel\Work\Projects\Kovera\Project 2\Analysis of Files\Test_Delete.xlsx"

# Custom table parameters (only used if DELETE_FROM_CUSTOM_TABLE is True)
CUSTOM_SHEET_NAME = "Sheet1"
CUSTOM_TABLE_NAME = "Table1"
CUSTOM_COLUMN_NAME = "id"

# Set to True to make Excel visible during processing (useful for debugging)
MAKE_EXCEL_VISIBLE = False

# =============================================================================
# END OF CONFIGURATION SECTION
# =============================================================================

if __name__ == "__main__":
    if RUN_SCRIPT:
        try:
            # Determine which file path to use
            file_path = DEFAULT_FULL_PATH if USE_DEFAULT_FILE else CUSTOM_FILE_PATH
            
            if DELETE_FROM_PP_TABLE:
                # Delete from P_P_Table
                deleted = delete_from_pp_table(VALUES_TO_DELETE, excel_path=file_path)
                print(f"Successfully deleted {deleted} rows from P_P_Table where Product_Code_Parent matched any of: {', '.join(VALUES_TO_DELETE)}")
                
            elif DELETE_FROM_PE_TABLE:
                # Delete from P_E_Table
                deleted = delete_from_pe_table(VALUES_TO_DELETE, excel_path=file_path)
                print(f"Successfully deleted {deleted} rows from P_E_Table where Product_Code matched any of: {', '.join(VALUES_TO_DELETE)}")
                
            elif DELETE_FROM_PLADE_TABLE:
                # Delete from P_LADE_Table
                deleted = delete_from_plade_table(VALUES_TO_DELETE, excel_path=file_path)
                print(f"Successfully deleted {deleted} rows from P_LADE_Table where Product_Code matched any of: {', '.join(VALUES_TO_DELETE)}")
                
            elif DELETE_FROM_CUSTOM_TABLE:
                # Delete from custom table
                deleted = delete_rows_by_values(
                    values_to_delete=VALUES_TO_DELETE,
                    excel_path=file_path,
                    sheet_name=CUSTOM_SHEET_NAME,
                    table_name=CUSTOM_TABLE_NAME,
                    column_name=CUSTOM_COLUMN_NAME,
                    visible=MAKE_EXCEL_VISIBLE
                )
                print(f"Successfully deleted {deleted} rows from {CUSTOM_TABLE_NAME} where {CUSTOM_COLUMN_NAME} matched any of: {', '.join(VALUES_TO_DELETE)}")
            
            else:
                print("No operation selected. Please set one of the DELETE_* variables to True.")
                
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Script is disabled. Set RUN_SCRIPT to True to enable it.") 