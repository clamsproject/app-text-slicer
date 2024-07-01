# Text Slicer

## Description
The app named `app-text-slicer` is used to "slice" (or extract) snippets of text from
given single `TextDocument` based on single or multiple `TimeFrame` annotations within the `Mmif` object.

## User instruction
_**Important**_: 
Users need to read [CLAMS Apps User Manual](https://apps.clams.ai/clamsapp) before using this app.

### Run the app on local server
To run the app in a containerized environment: 

`curl -X ... localhost:<port>?containLabel=<label_X>&containLabel=<label_Y>?<other_params>`

### Run the app in CLI
First, to seek for help from the app, type `python cli.py -h` under the app source directory

Then, similar to other CLAMS apps, to run the app via CLI, do

```
python cli.py \
    --containLabel=<label_X> \
    --containLabel=<label_Y> \
    --other_params \
    <input_mmif_file_path> \
    <output_mmif_file_path> 
```

### Configurable runtime parameter

`--containLabel`: the parameter to slice texts within `TimeFrame`s having label(s) user provides


For the full list of parameters, please refer to the app metadata from the [CLAMS App Directory](https://apps.clams.ai) or the [`metadata.py`](metadata.py) file in this repository.

## System requirements

_**Until 7/1/2024**_:
```
clams-python=1.2.5
```


