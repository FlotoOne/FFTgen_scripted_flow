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
pip3 install requests beautifulsoup4```

## Installation
Ensure you have Python 3 installed on your system. You can download Python from [python.org](https://python.org).

To run the script, clone this repository or download the script file directly. Navigate to the directory containing the script in your terminal or command prompt, and execute the script by running:
