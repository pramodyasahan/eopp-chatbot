import pandas as pd
import os

# Define the folder containing Excel files
input_directory = "../data"  # Change this to your folder path
output_file = "merged_data.xlsx"

# Get a list of all Excel files in the directory
excel_files = [f for f in os.listdir(input_directory) if f.endswith(".xlsx")]

# Print detected files
print(f"Detected {len(excel_files)} Excel files: {excel_files}")

# Initialize an empty list to store dataframes
dfs = []
failed_files = []

# Loop through each file and read it
for file in excel_files:
    file_path = os.path.join(input_directory, file)
    try:
        df = pd.read_excel(file_path)
        df["source_file"] = file  # Add a column to track source file names
        dfs.append(df)
        print(f"Successfully read: {file}")
    except Exception as e:
        print(f"Error reading {file}: {e}")
        failed_files.append(file)

# Print failed files
if failed_files:
    print(f"⚠️ The following files could not be read: {failed_files}")

# Merge all dataframes
if dfs:
    merged_df = pd.concat(dfs, ignore_index=True)
    merged_df.to_excel(output_file, index=False)
    print(f"✅ All Excel files merged and saved to {output_file}")
else:
    print("❌ No valid Excel files found.")
