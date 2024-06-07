# FFTgen_scripted_flow
Scripted SKY130 Flow for PPA With Optimized Performance Using SPIRAL FFT Generator

## Overview
This Python script automates the setup and execution of a project to generate Verilog files for FFT (Fast Fourier Transform) processes, tailored to be used within a Hammer CAD environment. The script manages file creation, project directory setup, configuration, and initiates synthesis and place-and-route stages for the designed circuit. This tool simplifies the intricate process of preparing and executing digital design workflows, ensuring all necessary components are correctly configured and executed.

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
pip install --user requests beautifulsoup4
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
1. Fetches and generates the initial Verilog file content.
2. Sets up the necessary project directory structure.
3. Creates configuration files (`cfg.yml`, `src.yml`, and `tb.yml`).
4. Prepares a synthesis environment by creating a Makefile and constraint files.
5. Executes synthesis and place-and-route processes, adjusting the clock period based on the synthesis results.

The user is required to ensure that the directory paths and environment variables are correctly set to match their specific setup.

## Troubleshooting
If encountering difficulties or unexpected errors while running the script, please verify your working environment.
- Check if your Python3 is up to date by running this command and verifying your Python3 is installed properly.
```bash
python3 --version
```
- If you have other files in your working directory, try running the script in a fresh and empty directory.
- If you are running this script on a Virtual Machine using an application such as TightVNC or TigerVNC, try switching to VSCode and connecting through ssh.

## Contributing
Contributions to this script are welcome. Please ensure that any pull requests or changes maintain compatibility with Hammer CAD tools and adhere to Python 3 standards.
