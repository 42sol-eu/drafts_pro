# drafts_pro.py
# Usage:
#   python3 drafs_pro.py --help
# source: 
# - v2020.00:   https://gist.github.com/42sol-eu/f4f7cd2ad6ced790fed541aa442e566b
# - v2020.01:  
#    - [x] add typer to improve command line interface
#    - [x] add json config file (drafts_pro.config.json) to manage default values
#    - [x] modify add default values for some draft tags
#    - [ ] alternative config file type (yaml, toml)
#    - [ ] add json5 support for better data handling in config file
#    - [x] modify main command to md2drafs
#    - [ ] modify md2drafs argument input_directory to a file type
#    - [ ] add md2drafs arguments (front matter and back matter)
#    - [x] add command config to show contents of config file
#    - [ ] config file error handling
#    - [ ] config file prompt for data
#    - [x] add command set to change default value for key
#    - [ ] modify position handling (longitute and lattitude)
#    - [x] add command get to show default value for key
#    - [ ] add append to append a item to default value for key
#    - [x] refactor date string generation in helper function
#    - [ ] maybe: use safe_file
#    - [ ] maybe: use colorama


import os, time                   # stdlib
from pathlib import Path          # stdlib
import json                       # stdlib
from enum import Enum             # stdlib
import typer                      # https://typer.tiangolo.com
# import yaml                       # https://pyyaml.org/wiki/PyYAMLDocumentation
# TODO: add a check for Yaml/Json Frontmatters or Backmatters
# from loguru import logger as log  # https://github.com/Delgan/loguru

result = -1
import uuid
import sys

from datetime import datetime, timezone

g_config_file = 'drafts_pro.config.json'
g_left_title_stip_characters = "#=-* "
g_config_data = {}
g_default_data = {
  'flagged': False,
  'folder': 0,
  'languageGrammer': 'Markdown',
  'tags': [],
}

class MetaData(str, Enum):
    none = "none"
    front = "front"
    back = "back"

app = typer.Typer()

def load():
    global g_config_file 
    global g_default_data
    global g_config_data
    with open(g_config_file, "r") as config_file:
      g_config_data = json.load(config_file)

    flagged_key = 'flagged'
    for key, value in g_default_data.items():
      if key not in g_config_data:
        g_config_data[key] = value
        print(f'add {key} with {value}')
                

def save():
    global g_config_file 
    global g_config_data
    with open(g_config_file, "w") as config_file:
      json_data = json.dumps(g_config_data, sort_keys=True, indent=4)
      config_file.write(json_data)

def get_date_string( p_timestamp):
      r_iso8601 = datetime.fromtimestamp(p_timestamp, timezone.utc).isoformat("T", "seconds")
      if r_iso8601[-1] != "Z":
        r_iso8601 = r_iso8601.replace("+00:00", "Z")
      return r_iso8601


@app.command()
def md2drafts(input_directory: str, meta: MetaData = MetaData.none):
    global g_config_data
    global g_left_title_stip_characters
    typer.echo(f"import from {input_directory}")

    load()
    typer.echo(f"- meta: {meta}")
    # typer.echo(f"- back_matter: {back_matter}")
    
    directory = os.fsencode(input_directory)

    export_output = []

    for subdir, dirs, files in os.walk(input_directory):
        for file in files:
            filepath = subdir + os.sep + file
            print(filepath)

            if filepath.endswith(".md"):
                json_export = {}
                json_export['folder'] = g_config_data['folder']
                json_export['languageGrammar'] = g_config_data['languageGrammar']
                json_export['flagged'] = g_config_data['flagged']
                json_export['uuid'] = str(uuid.uuid4())
                json_export['tags'] = g_config_data['tags']
                
                #Replace with your preferred coordinates. Use numbers only, not strings
                longitude = g_config_data['longitude']
                latitude = g_config_data['latitude']

                json_export['modified_longitude'] = longitude
                json_export['modified_latitude'] = latitude
                
                json_export['created_longitude'] = longitude
                json_export['created_latitude'] = latitude

                json_export['modified_at'] = get_date_string(os.path.getmtime(filepath))
                json_export['created_at'] = get_date_string(os.path.getctime(filepath))
                date_string = json_export['created_at'][:10]
                print (date_string)
                json_export['accessed_at'] = get_date_string(os.path.getmtime(filepath))

                file_contents = open(filepath)
                drafts_content = file_contents.read()
                drafts_prefix = ""
                drafts_suffix = ""
                meta_data = ""

                if meta is not MetaData.none:
                  draft_title = drafts_content.split('\n')[0]
                  draft_title = draft_title.lstrip(g_left_title_stip_characters)
                  meta_data += f'title: {draft_title}\n'
                  meta_data += f'autor: {g_config_data["author"]}\n'
                  meta_data += f'date: {g_config_data["meta_affiliation"]}\n'
                  meta_data += f'affiliation: {date_string}\n'
                  meta_data += f'copyright: © {date_string[:4]}, {g_config_data["meta_company"]}\n'
                  meta_data += f'version: {g_config_data["defaultVersion"]}\n'
                  meta_data += f'tags: {g_config_data["tags"]}\n'

                if meta is MetaData.front:
                  drafts_prefix = f'---\n\n{meta_data}\n---\n'
                
                if meta is MetaData.back:
                  drafts_suffix = f'\n\n---\n\n{meta_data}\n---'
                json_export['content'] = f"{drafts_prefix}{drafts_content}{drafts_suffix}"
                export_output.append(json_export)
    with open(f'drafts_import_{date_string}.draftsExport', 'w') as json_file:
      drafts_data = json.dumps(export_output, sort_keys=True, indent=4)
      json_file.write(drafts_data)
      if 0:
        typer.echo(drafts_data)


@app.command()
def set(key: str, value: str):
    global g_config_data
    key = key.lower()
    typer.echo(f'')
    load()
    typer.echo(f'{g_config_file}')
    
    value = value.replace('\'', '"')
    print(value)
    try:
      procesed_value = json.loads(value)
    except:
      procesed_value = value
    #print(value[-3:-1])
    

    typer.echo(f'{key}: {procesed_value}')
    g_config_data[key] = procesed_value

    save()

@app.command()
def get(key: str):
    global g_config_data
    key = key.lower()
    typer.echo(f'')
    load()
    typer.echo(f'{g_config_file}')
    value = g_config_data[key]
    typer.echo(f'{key}: {value}')
    typer.echo(f'')
    save()
    

@app.command()
def config():
    global g_config_data
    typer.echo(f'')
    load()
    typer.echo(f'{g_config_file}')
    for key, value in g_config_data.items():
        typer.echo(f'- {key}: {value}')
    typer.echo(f'')



if __name__ == "__main__":
    app()
    typer.echo(f"completed import status = {result}")



"""
Example output format:
[
  {
    "uuid" : "C13A345F-A2F2-425B-828C-F6585C892239",
    "content" : "Draft Content",
    "folder" : 0,
    "tags" : [

    ],
    "created_latitude" : 46.055316670125848,
    "created_longitude" : -88.705367973270526,
    "modified_latitude" : 46.055530370721598,
    "modified_longitude" : 46.055530370721598,
    "flagged" : false,
    "modified_at" : "2020-09-05T14:38:24Z",
    "accessed_at" : "2020-09-06T02:52:06Z",
    "created_at" : "2020-09-04T01:18:15Z",
    "languageGrammar" : "Markdown"
  }
]
"""
