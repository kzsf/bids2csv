import json
import yaml
import pandas as pd
from pathlib import Path

# Load paths from YAML
with open('paths.yaml', 'r') as file:
    paths = yaml.safe_load(file)['paths']

# Assign variables from paths (use values, not keys)
id_csv = paths.get('id_csv')
bids_dir = paths.get('bids_dir')
output_dir = paths.get('output_dir')

print(f"id_csv={id_csv}\nbids_dir={bids_dir}\noutput_dir={output_dir}")

# Read the CSV of BIDS IDs
if not id_csv:
    raise ValueError('`id_csv` not found in paths.yaml')

df = pd.read_csv(id_csv)

# Fields to extract from JSON files - modify this list as needed
fields_to_extract = ['Modality', 'SeriesDescription']

results = []

for index, row in df.iterrows():
    bids_id = row['bids_id']
    session_id = row['session']

    # Bids session directory path
    session_dir = Path(bids_dir).expanduser() / f"{bids_id}" / f"ses-{session_id}"

    if not session_dir.exists():
        print(f"Session directory does not exist: {session_dir}")
        continue

    # Recursively find JSON files in the session directory
    for json_file in session_dir.rglob('*.json'):
        try:
            metadata = json.loads(json_file.read_text())
        except Exception as e:
            print(f"Failed to load {json_file}: {e}")
            continue

        row_data = {
            'bids_id': bids_id,
            'session': session_id,
            'json_file': str(json_file.relative_to(session_dir))
        }

        for field in fields_to_extract:
            row_data[field] = metadata.get(field)

        results.append(row_data)

# Save results to csv
out_df = pd.DataFrame(results)
if output_dir:
    Path(output_dir).expanduser().mkdir(parents=True, exist_ok=True)
    out_csv = Path(output_dir).expanduser() / 'extracted_metadata.csv'
    out_df.to_csv(out_csv, index=False)
    print(f"Saved extracted metadata to: {out_csv}")
else:
    display(out_df.head())
