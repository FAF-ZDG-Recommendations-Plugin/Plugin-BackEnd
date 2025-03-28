import os
import re

input_file = "../zdg_db_backup.sql"
output_dir = "D:/xampp/htdocs/zdg/split_tables"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

current_file = None
current_table = None

# Open the input file
with open(input_file, "r", encoding="utf8", errors="ignore") as infile:
    for line_num, line in enumerate(infile, 1):
        # Look for CREATE TABLE lines
        match = re.search(r'CREATE TABLE\s+`([^`]+)`', line)

        if match:
            # Close previous table's file (if any)
            if current_file:
                current_file.close()
                print(f"Closed {current_table}.sql after {line_num} lines.")
            
            # Get current table name
            current_table = match.group(1)
            print(f"Found new table: {current_table} at line {line_num}")
            
            # Create a new file for the current table
            current_file = open(os.path.join(output_dir, f"{current_table}.sql"), "w", encoding="utf8")
            current_file.write(line)  # Write the CREATE TABLE line
        
        # If still writing to a file, write the rest of the lines
        if current_file:
            current_file.write(line)

# Close the last file (if any)
if current_file:
    current_file.close()
    print(f"Closed {current_table}.sql after processing the last lines.")

print("✅ SQL split complete.")