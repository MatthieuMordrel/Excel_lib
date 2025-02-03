import win32com.client
import json
import os

# doesn't work well if references are complex

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the full path to location.json
location_path = os.path.join(script_dir, 'location.json')

# Launch Excel via COM
excel = win32com.client.Dispatch("Excel.Application")
excel.Visible = True

# Open the workbook using the full path from location.json
with open(location_path) as f:
    location_data = json.load(f)
    workbook = excel.Workbooks.Open(location_data['file_path'])
    worksheet = workbook.Worksheets(location_data['sheet_name'])
    target_cell = worksheet.Range(location_data['cell_address'])

# Rest of the code remains the same...
if target_cell.HasFormula:
    try:
        direct_precedents = target_cell.DirectPrecedents
    except Exception as e:
        print("No direct precedents found or an error occurred:", e)
        direct_precedents = None

    if direct_precedents:
        for area in direct_precedents.Areas:
            print("Precedent area:", area.Address)
            for cell in area:
                print("Cell:", cell.Address, "Value:", cell.Value)
else:
    print("Target cell does not contain a formula; hence, no precedents.")

workbook.Close(SaveChanges=False)
excel.Quit()
