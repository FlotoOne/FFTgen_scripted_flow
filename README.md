# FFTgen_scripted_flow
Scripted SKY130 Flow for PPA With Optimized Performance Using SPIRAL FFT Generator


#### Authors: Shrihari Iyer and Divya Naidu
#### University of Washington

## Overview
This Python script automates the setup and execution of a project to generate Verilog files for Fast Fourier Transform processes, tailored to be used within a SKY130 flow and Hammer CAD environment. The script manages file creation, project directory setup, configuration, and initiates synthesis and place-and-route stages for the designed circuit. This tool simplifies the process of preparing and executing digital design workflows, ensuring all necessary components are correctly configured and executed.

## Prerequisites
To run this script, you need to have the following Python libraries installed:
- `os`: for managing directories and file paths
- `sys`: for accessing system-specific parameters and functions
- `shutil`: for file operations like copying
- `time`: for adding delays in the script execution
- `subprocess`: for running external commands and processes
- `requests`: for making HTTP requests
- `BeautifulSoup` from `bs4`: for parsing HTML and XML documents

These libraries are part of the Python Standard Library, except for `requests` and `BeautifulSoup`, which you can install using pip3:

```bash
pip3 install requests beautifulsoup4
```
If this does not work due to user permissions, you may try:
```bash
pip3 install --user requests beautifulsoup4
```

Also ensure you have the PyYAML library installed:

```bash
pip3 install pyyaml
```

## Installation
Ensure you have Python 3 installed on your system. You can download Python from [python.org](https://python.org).

To run the script, clone this repository or download the script file directly. Navigate to the directory containing the script in your terminal or command prompt, and execute the script by running:

```bash
./fftgen.py
```
or
```bash
python3 fftgen.py
```

Make sure that your working environment does not already contain directories named 'hammer_cad', 'basejump_stl', 'fft_block_design' and make sure there is no preexisting file named 'spiral.v'

## Usage
Upon execution, the script performs the following operations:
1. Requests the user to input their desired FFT block specifications and generates the resulting Verilog file.
2. Sets up the necessary project directory structure.
3. Creates configuration files (`cfg.yml`, `src.yml`, and `tb.yml`).
4. Creates a Makefile and constraint files to run Synthesis and Place-and-Route processes.
5. Executes Synthesis and Place-and-Route processes, adjusting the clock period based on the generated timing reports.
6. Displays relevant PPA information in the terminal while also having all reports readily accessible.

When the script finishes, the user will have a fully functional working directory to run further processes in.

## Troubleshooting
If encountering difficulties or unexpected errors while running the script, please verify your working environment.
- Check if your Python3 is up to date by running this command and verifying your Python3 is installed properly.
```bash
python3 --version
```
- If you have other files in your working directory, try running the script in a fresh and empty directory.
- If you are running this script on a Virtual Machine using an application such as TightVNC or TigerVNC, try switching to VSCode and connecting through ssh. VSCode seems to run consistently without issue.
  - Common errors when running on a VM due to improper Python environment may include a Python3 path lookup error as well as being unable to find "hammer-vlsi" inside the "hammer-cad" directory while running Synthesis.
- If you run into the following error, your area constraints are too low and should be increased within the `create_cfg_file()` function:
```bash
**ERROR: (IMPSE-110):   File '.../fft_block_design/fftgen/build/par-rundir/par.tcl' line 160: 1.
#@ End verbose source .../fft_block_design/fftgen/build/par-rundir/par.tcl
**ERROR: (IMPSYT-6692): Invalid return code while executing '.../fft_block_design/fftgen/build/par-rundir/par.tcl' was returned and script processing was stopped. Review the following error in '.../fft_block_design/fftgen/build/par-rundir/par.tcl' then restart.
**ERROR: (IMPSYT-6693): Error message: .../fft_block_design/fftgen/build/par-rundir/par.tcl: 1.
```
