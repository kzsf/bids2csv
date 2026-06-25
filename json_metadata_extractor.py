import json
import yaml
import pandas as pd
from pathlib import Path

#load paths from paths.yaml
with open('paths.yaml', 'r') as file:
    paths = yaml.safe_load(file)['paths']

#assign variables from paths.yaml
id_csv = paths.get('id_csv')
bids_dir = paths.get('bids_dir')
output_dir = paths.get('output_dir')

print(f"id_csv={id_csv}\nbids_dir={bids_dir}\noutput_dir={output_dir}")

#read bids id csv
if not id_csv:
    raise ValueError('`id_csv` not found in paths.yaml')

df = pd.read_csv(id_csv)

#fields to extract from json
fields_to_extract = ['Modality', 'SeriesDescription']

results = []

for index, row in df.iterrows():
    bids_id = row['bids_id']
    session_id = row['session']

    #bids session directory path
    session_dir = Path(bids_dir).expanduser() / f"{bids_id}" / f"ses-{session_id}"

    if not session_dir.exists():
        print(f"session directory does not exist: {session_dir}")
        continue

    #recursively find json files in the session directory
    for json_file in session_dir.rglob('*.json'):
        try:
            metadata = json.loads(json_file.read_text())
        except Exception as e:
            print(f"failed to load {json_file}: {e}")
            continue

        row_data = {
            'bids_id': bids_id,
            'session': session_id,
            'json_file': str(json_file.relative_to(session_dir))
        }

        for field in fields_to_extract:
            row_data[field] = metadata.get(field)

        results.append(row_data)

#save results to csv
out_df = pd.DataFrame(results)
if output_dir:
    Path(output_dir).expanduser().mkdir(parents=True, exist_ok=True)
    out_csv = Path(output_dir).expanduser() / 'extracted_metadata.csv'
    out_df.to_csv(out_csv, index=False)
    print(f"saved extracted metadata to: {out_csv}")
else:
    display(out_df.head())
