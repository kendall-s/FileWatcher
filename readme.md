# File Watcher

![Testing Suite](https://github.com/kendall-s/FileWatcher/actions/workflows/run_tests.yml/badge.svg)


#### Terminal application for pinging locations and copying matched files if they're not in already in the destination folder 📂

## Usage

Edit the parameters.json file (lives in same directory as file_watcher.py) with the required fields, run the file_watcher.py and watch the terminal for status updates.
```
python file_watcher.py
```

## Parameters

The fields required for file watcher are as follows:
- voyage: wildcard replacement for ?voyage in parameter strings (i.e. paths and name)
<br>

- id: integer to represent the watched file job
- frequency: integer to represent file checking frequency in seconds
- source_host: path to the source host directory
- source: folder path to check for matched files
- dest_host: path to the destination host directory
- dest: folder path to copy matched files
- file_type: required file type to match
- name_contains: string that will be in file name
- source_auth: auth fields for source directory
  - domain: 
  - username:
  - password
- dest_auth: authentication fields for destination directory
  - domain:
  - username
  - password:

### Example parameters.json
```json
{
    "voyage": "in2021_v04", 
    "watching": [
        {
            "id": 1,
            "frequency": "10",
            "source_host": "\\\\processing-pc\\oxygen-data",
            "source": "?voyage/oxygen/",
            "dest_host": "\\\\files.data",
            "dest": "?voyage/processed-data/Oxygen/",
            "file_type": ".lst",
            "name_contains": "?voyageoxy",
            "source_auth": {
                "domain": "internal",
                "username": "procesing",
                "password": "processing_pwd"
            },
            "dest_auth": {
                "domain": "internal",
                "username": "general",
                "password": "general_pwd"
            }
        },
        {
            "id": 2,
            "frequency": "5",
            "source_host": "\\\\acquisition-pc\\nutrient-data",
            "source": "?voyage/nutrient/",
            "dest_host": "\\\\files.data",
            "dest": "?voyage/raw-data/Nutrient/",
            "file_type": ".csv",
            "name_contains": "?voyagenut",
            "source_auth": {
                "domain": "internal",
                "username": "acqnut",
                "password": "acqnut_pwd"
            },
            "dest_auth": {
                "domain": "internal",
                "username": "general",
                "password": "general_pwd"
            }
        }
    ]
}
```

## Context

This app is incredibly simplistic, mainly so less-tech-savy individuals can hopefully use the application. Parameterisation of copying files is kept at the absolute minimum for the sake of keeping it simple.

There is certainly the possibility to add a keywords or regex type search to the file finding, perhaps even by size or by time. For now, the file watcher serves its purpose. ✌

📊 Used the rich library to make the terminal a little bit nicer. Might build on this feature in the future if necessary.