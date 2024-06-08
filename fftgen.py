#!/usr/bin/env python3
#
# Shrihari Iyer and Divya Naidu
# EE 478 - VLSI Capstone Project
#
# This project streamlines the process of using the SPIRAL FFT Verilog Generator
# and integrating it into the SKY130 PDK flow for ASIC design. This script
# uses the BaseJump STL and SKY130 Hammer-CAD libraries along with creating
# a working directory to store Verilog files, CFG (.yml and .tcl) files, and
# other needed files. The output files from Synthesis, Place-and-Route, and
# simulations will go into the Build directory.
#
# By using this script, users can automatically obtain PPA metrics from Synthesis
# and Place-and-Route for any FFT Verilog block using the SPIRAL generator.
# note: ask chatgpt to write this portion better

import sys
import subprocess
import os
import shutil
import time
import requests
from bs4 import BeautifulSoup
import os

def get_user_input(descriptive_name):
    return input(f"Enter {descriptive_name}: ")

def fetch_verilog_file_content():
    def fetch_initial_page(params):
        base_url = "https://pmilder.ece.stonybrook.edu/dftgen/gen.php"
        response = requests.get(base_url, params=params)
        return response.text if response.status_code == 200 else None

    def check_iframe_ready(soup):
        iframe = soup.find('iframe', id='resframe')
        if iframe and 'gen2.php' in iframe['src']:
            iframe_src = iframe['src']
            return f"https://pmilder.ece.stonybrook.edu/dftgen/{iframe_src}"
        return None

    def fetch_iframe_content(iframe_url):
        result_response = requests.get(iframe_url)
        return result_response.text if result_response.status_code == 200 else None

    def extract_download_link(iframe_content):
        result_soup = BeautifulSoup(iframe_content, 'html.parser')
        link = result_soup.find('a', string='Download Verilog')
        return link['href'] if link else None

    def download_verilog_file(link):
        base_url = "https://pmilder.ece.stonybrook.edu/dftgen/"
        full_url = f"{base_url}{link}"
        response = requests.get(full_url)
        if response.status_code == 200:
            filename = "spiral.v"  # Always save as spiral.v
            with open(filename, 'wb') as file:
                file.write(response.content)
            return filename
        return None

    def get_user_input(descriptive_name):
        return input(f"Enter {descriptive_name}: ")

    # Inputs from user
    while True:
        idInverse = get_user_input("Forward or Inverse (0 for Forward, 1 for Inverse)")
        if idInverse in ['0', '1']:
            break
        print("Invalid entry. Please enter 0 for Forward or 1 for Inverse.")

    valid_idN_values = ['4', '8', '16', '32', '64', '128', '256', '512', '1024', '2048', '4096', '8192', '16384', '32768']
    while True:
        idN = get_user_input("transform size (Pick a power-of-2 from 4 to 32768)")
        if idN in valid_idN_values:
            break
        print("Invalid entry. Please enter a valid power-of-2 from 4 to 32768.")

    # Data type
    while True:
        idDataType = get_user_input("data type (0 for fixed, 1 for floating)")
        if idDataType in ['0', '1']:
            break
        print("Invalid entry. Please enter 0 for fixed or 1 for floating.")

    if idDataType == '1':
        idWidth = '1'
        idScale = '0'  # Automatically set to unscaled for floating data type
        print("Data type is floating. Scaling set to unscaled.")
    else:
        while True:
            idWidth = get_user_input("bit-width (Data type is fixed point, valid range is 4 to 32 bits)")
            if idWidth.isdigit() and 4 <= int(idWidth) <= 32:
                break
            print("Invalid entry. Please enter a value between 4 and 32.")

        # Determine if scaled or unscaled for fixed point
        while True:
            idScale = get_user_input("scaled (1) or unscaled (0)")
            if idScale in ['0', '1']:
                break
            print("Invalid entry. Please enter 1 for scaled or 0 for unscaled.")

    idTWidth = idWidth

    # Architecture
    while True:
        idArch = get_user_input("architecture (0 for iterative, 1 for fully-streaming)")
        if idArch in ['0', '1']:
            break
        print("Invalid entry. Please enter 0 for iterative or 1 for fully-streaming.")

    # Valid radix algorithms based on size and architecture
    idN = int(idN)
    valid_radices = []

    # Radix options if iterative
    if idArch == '0':
        if idN == 4:
            valid_radices = [2]
        elif idN == 8:
            valid_radices = [2]
        elif idN == 16:
            valid_radices = [2, 4]
        elif idN == 32:
            valid_radices = [2]
        elif idN == 64:
            valid_radices = [2, 4, 8]
        elif idN == 128:
            valid_radices = [2]
        elif idN == 256:
            valid_radices = [2, 4, 16]
        elif idN == 512:
            valid_radices = [2, 8]
        elif idN == 1024:
            valid_radices = [2, 4, 32]
        elif idN == 2048:
            valid_radices = [2]
        elif idN == 4096:
            valid_radices = [2, 4, 8, 16, 64]
        elif idN == 8192:
            valid_radices = [2]
        elif idN == 16384:
            valid_radices = [2, 4]
        elif idN == 32768:
            valid_radices = [2, 8, 32]
        else:
            print("Invalid transform size. Please restart and enter a valid power-of-2 from 4 to 32768.")
            return
    elif idArch == '1':  # If fully-streaming architecture
        if idN == 4:
            valid_radices = [2, 4]
        elif idN == 8:
            valid_radices = [2, 4, 8]
        elif idN == 16:
            valid_radices = [2, 4, 8, 16]
        elif idN == 32:
            valid_radices = [2, 4, 8, 16, 32]
        elif idN >= 64 and idN <= 32768:
            valid_radices = [2, 4, 8, 16, 32, 64]
        else:
            print("Invalid transform size. Please restart and enter a valid power-of-2 from 4 to 32768.")
            return

    valid_radices_str = ", ".join(map(str, valid_radices))
    while True:
        idRadix = get_user_input(f"radix algorithm (Valid options: {valid_radices_str})")
        try:
            if int(idRadix) in valid_radices:
                break
            else:
                print(f"Invalid radix. Please choose from the valid options: {valid_radices_str}")
        except ValueError:
            print(f"Invalid entry. Please enter a valid integer. Valid options: {valid_radices_str}")

    # Valid stream widths based on size and radix
    max_stream_width = min(64, idN)
    min_stream_width = max(2, int(idRadix))

    valid_stream_widths = [i for i in [2, 4, 8, 16, 32, 64] if min_stream_width <= i <= max_stream_width]

    valid_stream_widths_str = ", ".join(map(str, valid_stream_widths))
    while True:
        idStreamWidth = get_user_input(f"stream width (Choose from {valid_stream_widths_str})")
        try:
            if int(idStreamWidth) in valid_stream_widths:
                break
            else:
                print(f"Invalid stream width. Please choose from the valid options: {valid_stream_widths_str}")
        except ValueError:
            print(f"Invalid entry. Please enter a valid integer from {valid_stream_widths_str}")

    # Data order
    print("For all configurations, the data order is set to natural input and natural output. Proceeding...")
    idOrder = '0'

    # BRAM
    while True:
        idBRAM = get_user_input("maximum # of BRAMs (Enter -1 for unlimited)")
        try:
            idBRAM = int(idBRAM)
            if -1 <= idBRAM <= 1000:
                break
            elif idBRAM > 1000:
                print("Please enter -1 for unlimited BRAMs.")
            else:
                print("Invalid entry. Please enter a valid number from -1 to 1000.")
        except ValueError:
            print("Invalid entry. Please enter a valid integer from -1 to 1000.")

    idIP = 1

    params = {
        "idN": idN,
        "idStreamWidth": idStreamWidth,
        "idWidth": idWidth,
        "idTWidth": idTWidth,
        "idOrder": idOrder,
        "idScale": idScale,
        "idBRAM": idBRAM,
        "idRadix": idRadix,
        "idArch": idArch,
        "idDataType": idDataType,
        "idInverse": idInverse,
        "idIP": idIP
    }

    print("Generating Verilog file for FFT block...")

    initial_page_content = fetch_initial_page(params)
    if not initial_page_content:
        return

    soup = BeautifulSoup(initial_page_content, 'html.parser')

    start_time = time.time()
    timeout_seconds = 30

    while True:
        iframe_url = check_iframe_ready(soup)
        if iframe_url:
            iframe_content = fetch_iframe_content(iframe_url)
            if iframe_content:
                download_link = extract_download_link(iframe_content)
                if download_link:
                    filename = download_verilog_file(download_link)
                    if filename:
                        return filename
        elapsed_time = time.time() - start_time
        if elapsed_time > timeout_seconds:
            break
        time.sleep(1)
        initial_page_content = fetch_initial_page(params)
        if not initial_page_content:
            return
        soup = BeautifulSoup(initial_page_content, 'html.parser')

def retry(func, retries=3, delay=1):
    """
    Retries a function or operation multiple times with a delay in between attempts.

    Args:
        func (callable): The function to be retried.
        retries (int, optional): The number of times to retry the function. Default is 3.
        delay (int, optional): The delay (in seconds) between each retry attempt. Default is 1 second.

    Returns:
        Any: The return value of the function if it succeeds within the specified number of retries.

    Raises:
        Exception: If the function fails after the specified number of retries, an exception is raised
                   with a message indicating that the operation failed.
    """
    last_exception = None
    for attempt in range(retries):
        try:
            return func()
        except Exception as e:
            last_exception = e
            print(f"Attempt {attempt+1} failed with error: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
    raise Exception(f"Operation failed after {retries} attempts. Last error: {last_exception}")

def setup_project():
    """
    Sets up the project environment by cloning the Hammer CAD library, running make,
    and creating the necessary project directories.

    Steps:
        1. Clones the Hammer CAD library.
        2. Runs the `make` command in the cloned `hammer_cad` directory.
        3. Creates the main project directory named `fft_block_design`.
        4. Creates a subdirectory named `fftgen` within the main project directory.
        5. Creates a subdirectory named `v` within the `fftgen` directory.

    Returns:
        tuple: A tuple containing:
            - new_dir_name (str): The absolute path of the main project directory.
            - sub_dir_new_name (str): The name of the `fftgen` subdirectory.
            - sub_sub_dir_name (str): The name of the `v` subdirectory.

    Raises:
        Exception: If any of the steps fail, the `retry` function will raise an exception
                   after the specified number of retries.
    """
    hammer_url = "https://github.com/bsg-external/ee477-hammer-cad.git"
    new_dir_name = os.path.abspath("fft_block_design")
    sub_dir_new_name = "fftgen"
    sub_sub_dir_name = "v"

    # Clone Hammer CAD
    print("Cloning Hammer CAD library...")
    retry(lambda: subprocess.run(["git", "clone", hammer_url, "hammer_cad"], check=True))
    print("Successfully cloned Hammer CAD library.")

    # Enter hammer_cad directory and run make
    print("Running make in hammer_cad directory...")
    os.chdir("hammer_cad")
    retry(lambda: subprocess.run(["make"], check=True))
    os.chdir("..")  # Move back to the original directory
    print("Successfully ran make in hammer_cad directory.")

    # Create the new project directory
    print("Creating project directories...")
    os.makedirs(new_dir_name, exist_ok=True)
    fftgen_path = os.path.join(new_dir_name, sub_dir_new_name)
    os.makedirs(fftgen_path, exist_ok=True)
    v_path = os.path.join(fftgen_path, sub_sub_dir_name)
    os.makedirs(v_path, exist_ok=True)
    print("Project directories created.")

    return new_dir_name, sub_dir_new_name, sub_sub_dir_name

def process_verilog_file(filename):
    print(f"Processing Verilog file: {filename}")
    # Placeholder if modifying Verilog file is desired

def create_cfg_file(cfg_file_path):
    """
    Creates and writes a Hammer configuration file at the specified path.

    This function generates a configuration file with predefined synthesis and
    simulation settings, including top module information, preserved modules,
    custom SDC constraints, and placement constraints. The configuration file
    content is written to the specified path.

    Args:
        cfg_file_path (str): The path where the configuration file will be created.

    Content:
        The configuration file contains the following sections:
        - Top levels for synthesis and simulation.
        - Modules to be preserved during synthesis.
        - Custom SDC constraints.
        - Additional SDC files to read.
        - Placement constraints for the top-level module.

    Raises:
        Exception: If there is an error while creating or writing to the file,
                   an exception is raised with the reason for the failure.
    """
    cfg_content = """# Main hammer config file

# Set top levels
synthesis.inputs.top_module: "dft_top"
sim.inputs.tb_name: "dft_testbench"

# Don't synthesize these gate-level netlist modules
synthesis.inputs.preserve_modules: []

# Custom SDC constraints
vlsi.inputs:
  # You can add SDC constraints directly here (list of strings)
  custom_sdc_constraints: []
 
  # Additional SDC files to read
  custom_sdc_files:
    - "constraints.tcl"
  custom_sdc_files_meta: prependlocal # Prepend path of this config file!

# Placement Constraints
vlsi.inputs.placement_constraints:
  - path: "TOP" # (this name isn't actually checked...)
    type: toplevel
    # define chip dimensions
    width:  700
    height: 700
    x: 0
    y: 0
    margins: {left: 0, right: 0, top: 0, bottom: 0}
"""

    try:
        with open(cfg_file_path, 'w') as f:
            f.write(cfg_content)
        print(f"Created and wrote to file: {cfg_file_path}")
    except Exception as e:
        print(f"Failed to create {cfg_file_path}. Reason: {e}")

def create_src_file(src_file_path):
    """
    Creates and writes a source file configuration for Hammer at the specified path.

    This function generates a configuration file that lists all Verilog source files
    to be included in the build. The configuration is used for both synthesis and
    RTL simulation. The content is written to the specified path.

    Args:
        src_file_path (str): The path where the source file configuration will be created.

    Content:
        The source file configuration contains the following sections:
        - List of Verilog source files for synthesis.
        - Meta information for appending and substituting input files.
        - List of Verilog source files for simulation.
        - Meta information for cross-referencing and substituting input files.

    Raises:
        Exception: If there is an error while creating or writing to the file,
                   an exception is raised with the reason for the failure.
    """
    src_content = """# List of all Verilog source files to include in this build.
# Used by both synthesis and RTL simulation.
synthesis.inputs.input_files: [
  "v/spiral.v",
]
synthesis.inputs.input_files_meta: [append, subst]

# Add synthesis input files to simulation inputs
# (Only for RTL sim)
sim.inputs.input_files: synthesis.inputs.input_files
sim.inputs.input_files_meta: [crossref, subst]
"""

    try:
        with open(src_file_path, 'w') as f:
            f.write(src_content)
        print(f"Created and wrote to file: {src_file_path}")
    except Exception as e:
        print(f"Failed to create {src_file_path}. Reason: {e}")

def create_tb_file(tb_file_path):
    """
    Creates and writes a testbench file configuration for Hammer at the specified path.

    This function generates a configuration file that specifies the directories for
    `include` directives, the list of Verilog testbenches, and trace files needed for
    simulation. The content is written to the specified path.

    Args:
        tb_file_path (str): The path where the testbench file configuration will be created.

    Content:
        The testbench file configuration contains the following sections:
        - Directories for `include` directives in simulations.
        - List of Verilog testbenches or other sources needed for simulation.
        - Meta information for appending and substituting testbench input files.
        - List of trace files for the simulation.

    Raises:
        Exception: If there is an error while creating or writing to the file,
                   an exception is raised with the reason for the failure.
    """
    tb_content = """# Search directories for `include directives in simulations
sim.inputs.tb_incdir: [
  "${bsg_root}/bsg_misc"
]
sim.inputs.tb_incdir_meta: [subst]

# List of Verilog testbenches (or other sources) needed for simulation only.
sim.inputs.tb_input_files: [
  # Testbench top
  "v/spiral.v",
  # BSG utilities
  "${bsg_root}/bsg_misc/bsg_defines.v",
  "${bsg_root}/bsg_test/bsg_nonsynth_clock_gen.v",
  "${bsg_root}/bsg_test/bsg_nonsynth_reset_gen.v",
  "${bsg_root}/bsg_fsb/bsg_fsb_node_trace_replay.v",
]
sim.inputs.tb_input_files_meta: [append, subst]

# List of trace files for the simulation
sim.inputs.trace_files: [

]
"""

    try:
        with open(tb_file_path, 'w') as f:
            f.write(tb_content)
        print(f"Created and wrote to file: {tb_file_path}")
    except Exception as e:
        print(f"Failed to create {tb_file_path}. Reason: {e}")

def create_constraints(constraints_file_path, clock_period):
    """
    Creates and writes a timing constraints file for Hammer at the specified path.

    This function generates a constraints file that defines design timing constraints
    for Genus and Innovus. The constraints include clock period, clock uncertainty,
    input and output delays for setup and hold checks. The content is written to the
    specified path.

    Args:
        constraints_file_path (str): The path where the constraints file will be created.
        clock_period (float): The clock period to be set in the constraints.

    Content:
        The constraints file contains the following sections:
        - Creation of the main clock with the specified period.
        - Setting clock uncertainty.
        - Input and output delays for clock setup checks.
        - Input and output delays for clock hold checks.

    Raises:
        Exception: If there is an error while creating or writing to the file,
                   an exception is raised with the reason for the failure.
    """
    constraints_content = f"""# constraints.tcl
#
# This file is where design timing constraints are defined for Genus and Innovus.
# Many constraints can be written directly into the Hammer config files. However,
# you may manually define constraints here as well.
#

create_clock -name clk -period {clock_period} [get_ports clk]
set_clock_uncertainty 0.100 [get_clocks clk]

# Always set the input/output delay as half periods for clock setup checks
set_input_delay  {clock_period / 2} -max -clock [get_clocks clk] [all_inputs]
set_output_delay {clock_period / 2} -max -clock [get_clocks clk] [remove_from_collection [all_outputs] [get_ports clk_o]]

# Always set the input/output delay as 0 for clock hold checks
set_input_delay  0.0 -min -clock [get_clocks clk] [all_inputs]
set_output_delay 0.0 -min -clock [get_clocks clk] [remove_from_collection [all_outputs] [get_ports clk_o]]
"""

    try:
        with open(constraints_file_path, 'w') as f:
            f.write(constraints_content)
        print(f"Created and wrote to file: {constraints_file_path}")
    except Exception as e:
        print(f"Failed to create {constraints_file_path}. Reason: {e}")

def create_makefile(makefile_path):
    """
    Creates and writes a Makefile for a Hammer project at the specified path.

    This function generates a Makefile for a Hammer project, setting up the build
    directory location, input configuration files, and including the main Hammer
    targets from `module_top.mk`. The content is written to the specified path.

    Args:
        makefile_path (str): The path where the Makefile will be created.

    Content:
        The Makefile contains the following sections:
        - Setting the top-level directory containing `module_top.mk`.
        - Defining the build directory location.
        - Specifying input configuration files for synthesis and testbench.
        - Including the main Hammer targets from `module_top.mk`.

    Raises:
        Exception: If there is an error while creating or writing to the file,
                   an exception is raised with the reason for the failure.
    """
    makefile_content = """# Make file for a Hammer project

# Make sure this is set to the top level directory containing module_top.mk
TOP_DIR = $(realpath ../../hammer_cad)

# Build directory location
OBJ_DIR = build

# If you change the names of these files, update them here to reflect.
INPUT_CFGS = cfg/cfg.yml cfg/src.yml
TB_CFGS = cfg/tb.yml

# Main Hammer Targets
include $(TOP_DIR)/module_top.mk
"""

    try:
        with open(makefile_path, 'w') as f:
            f.write(makefile_content)
        print(f"Created and wrote to file: {makefile_path}")
    except Exception as e:
        print(f"Failed to create {makefile_path}. Reason: {e}")

def extract_slack_time(line):
    """Extracts the slack time from a line in the timing report."""
    start_idx = line.find("(") + 1
    end_idx = line.find(")")
    return line[start_idx:end_idx].strip()

def adjust_clock_period(clock_period, slack_value, process_type):
    """
    Adjusts the clock period based on the slack value and process type.

    Args:
        clock_period (float): The current clock period.
        slack_value (float): The slack value from the timing report.
        process_type (str): The type of process ('Synthesis' or 'Place-and-Route').

    Returns:
        float: The adjusted clock period.
    """
    # Define adjustment thresholds for synthesis
    thresholds = {
        'high_positive': 1000,
        'mid_high_positive': 150,
        'low_high_positive': 100,
        'high_negative': -1000,
        'mid_high_negative': -100,
        'low_high_negative': -50
    }

    # Adjust thresholds for place-and-route
    if process_type == 'Place-and-Route':
        thresholds = {key: value / 1000 for key, value in thresholds.items()}

    if slack_value > thresholds['low_high_positive']:
        if slack_value > thresholds['high_positive']:
            adjustment = 2
        elif slack_value <= thresholds['mid_high_positive']:
            adjustment = 0.25
        elif slack_value <= thresholds['mid_high_positive'] + 50:
            adjustment = 0.5
        else:
            adjustment = 1
        clock_period -= adjustment
    elif slack_value < 0:
        if slack_value < thresholds['high_negative']:
            adjustment = 2
        elif slack_value >= thresholds['low_high_negative']:
            adjustment = 0.25
        elif slack_value >= thresholds['mid_high_negative']:
            adjustment = 0.5
        else:
            adjustment = 1
        clock_period += adjustment

    return clock_period

def process_timing_report(report_path, clock_period, process_type, new_dir_name):
    """Processes the timing report to adjust the clock period based on the slack value."""
    try:
        with open(report_path, 'r') as report_file:
            for line in report_file:
                if "Path 1: MET" in line:
                    slack_time = extract_slack_time(line)
                    print("------------------------------------------------------------")
                    print(f"Setup timing MET in {process_type}! Path 1 Slack: {slack_time}")
                    print("------------------------------------------------------------")
                    slack_value = float(slack_time.split()[0])
                    if 0 <= slack_value <= 100:
                        clock_speed_mhz = 1000 / clock_period
                        print(f"Clock Period: {clock_period} ns, Clock Speed: {clock_speed_mhz:.2f} MHz")
                        print("------------------------------------------------------------")
                        time.sleep(10)
                        return clock_period, False  # Stop rerunning if slack is in acceptable range
                    clock_period = adjust_clock_period(clock_period, slack_value, process_type)
                    print(f"Tuning clock constraints. New clock period: {clock_period} ns\nRerunning {process_type} momentarily...")
                    print("------------------------------------------------------------")
                    time.sleep(5)
                    create_constraints(os.path.join(new_dir_name, "cfg", "constraints.tcl"), clock_period)
                    return clock_period, True
                elif "Path 1: VIOLATED" in line:
                    slack_time = extract_slack_time(line)
                    print("------------------------------------------------------------")
                    print(f"Setup timing VIOLATED in {process_type}! Path 1 Slack: {slack_time}")
                    print("------------------------------------------------------------")
                    slack_value = float(slack_time.split()[0])
                    clock_period = adjust_clock_period(clock_period, slack_value, process_type)
                    print(f"Tuning clock constraints. New clock period: {clock_period} ns\nRerunning {process_type} momentarily...")
                    print("------------------------------------------------------------")
                    time.sleep(10)
                    create_constraints(os.path.join(new_dir_name, "cfg", "constraints.tcl"), clock_period)
                    return clock_period, True
            print("--------------------------------------------------")
            print("Timing information not found in the report.")
            print("--------------------------------------------------")
            return clock_period, False
    except Exception as e:
        print(f"Failed to read the report. Reason: {e}")
        return clock_period, False

def rerun_timing(new_dir_name, clock_period, process_type):
    """
    Analyzes the timing reports and adjusts the clock period to meet the timing constraints.

    This function opens the timing reports, reads the slack values, and adjusts the clock period based
    on the slack. If the slack indicates that the timing constraints are not met, it will rerun the
    synthesis or place-and-route process with a new clock period. The process is repeated until the
    slack is within the acceptable range.

    Args:
        new_dir_name (str): The path to the main project directory.
        clock_period (float): The initial clock period for the constraints.
        process_type (str): The type of process ('Synthesis' or 'Place-and-Route') for print statements.

    Returns:
        float: The final tuned clock period.

    Raises:
        Exception: If there is an error while reading the report, an exception is raised with the reason for the failure.
    """
    if process_type == "Place-and-Route":
        setup_paths = [
            os.path.join(new_dir_name, "build", "par-rundir", "timingReports", "dft_top_postRoute_all.tarpt"),
        ]
    else:
        setup_paths = [
            os.path.join(new_dir_name, "build", "syn-rundir", "reports", "final_time_ss_100C_1v60.setup_view.rpt")
        ]

    for report_path in setup_paths:
        clock_period, should_rerun = process_timing_report(report_path, clock_period, process_type, new_dir_name)
        if should_rerun:
            if process_type == 'Synthesis':
                run_synthesis(new_dir_name, clock_period, rerun=True)
            else:
                run_par(new_dir_name, clock_period, rerun=True)
    
    return clock_period

def run_synthesis(new_dir_name, clock_period, rerun=False):
    """
    Runs the synthesis process for the given project directory and clock period.

    This function changes the working directory to the specified project directory,
    runs the synthesis process using the appropriate make command, and then analyzes
    the timing report to adjust the clock period if necessary. If synthesis fails,
    an error message is printed. The working directory is restored at the end.

    Args:
        new_dir_name (str): The path to the main project directory.
        clock_period (float): The clock period for the constraints.
        rerun (bool, optional): Flag indicating whether this is a rerun of the synthesis.
                                Default is False.

    Returns:
        float: The final tuned clock period.

    Raises:
        subprocess.CalledProcessError: If the synthesis process fails, an error message is printed.

    """
    try:
        os.chdir(new_dir_name)
        current_dir = os.getcwd()
        print(f"Running 'make syn' in directory: {current_dir}" if not rerun else f"Running 'make redo-syn' in directory: {current_dir}")  # Debug print statement
        command = ["make", "redo-syn"] if rerun else ["make", "syn"]
        subprocess.run(command, check=True)
        print("Synthesis completed successfully.")
        return rerun_timing(new_dir_name, clock_period, process_type='Synthesis')
    except subprocess.CalledProcessError as e:
        print(f"Synthesis failed. Reason: {e}")
        return clock_period  # Return the last known clock period
    finally:
        os.chdir("..")

def unzip_reports(base_dir):
    """
    Unzips the timing reports in the specified directory.

    Args:
        base_dir (str): The base path to the main project directory.
    """

    timing_reports_dir = os.path.join(base_dir, "build", "par-rundir", "timingReports")

    # Paths to unzipped output files
    setup_report_path = os.path.join(timing_reports_dir, "dft_top_postRoute_all.tarpt")
    hold_report_path = os.path.join(timing_reports_dir, "dft_top_postRoute_all_hold.tarpt")

    try:
        os.chdir(timing_reports_dir)
        
        # Delete existing unzipped files if they exist
        if os.path.exists(setup_report_path):
            os.remove(setup_report_path)
        if os.path.exists(hold_report_path):
            os.remove(hold_report_path)

        # Unzip the timing report files
        subprocess.run(["gunzip", "dft_top_postRoute_all.tarpt.gz"], check=True)
        subprocess.run(["gunzip", "dft_top_postRoute_all_hold.tarpt.gz"], check=True)
        print("Timing reports unzipped successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to unzip timing reports. Reason: {e}")
    finally:
        os.chdir(base_dir)

def display_hold_time_slack(new_dir_name):
    """
    Reads and displays the Path 1 slack from the hold time report after Place-and-Route.

    Args:
        new_dir_name (str): The path to the main project directory.
    """
    hold_report_path = os.path.join(new_dir_name, "build", "par-rundir", "timingReports", "dft_top_postRoute_all_hold.tarpt")
    
    try:
        with open(hold_report_path, 'r') as report_file:
            for line in report_file:
                if "Path 1:" in line:
                    slack_time = extract_slack_time(line)
                    print(f"Hold time Path 1 slack in Place-and-Route: {slack_time}")
                    print("------------------------------------------------------------")
                    return
            print("Hold time Path 1 information not found in the report.")
            print("--------------------------------------------------")
    except Exception as e:
        print(f"Failed to read the hold time report. Reason: {e}")

def display_area_report(new_dir_name):
    """
    Reads and displays the area metrics from the area report after Place-and-Route.

    Args:
        new_dir_name (str): The path to the main project directory.
    """
    area_report_path = os.path.join(new_dir_name, "build", "par-rundir", "dft_top_area.rpt")
    
    try:
        with open(area_report_path, 'r') as report_file:
            for line in report_file:
                if line.strip().startswith("dft_top"):
                    parts = line.split()
                    if len(parts) >= 3:
                        total_area = parts[2].strip()
                        print(f"Total Area for dft_top: {total_area} um^2")
                        print("------------------------------------------------------------")
                        return
            print("Area information not found in the report.")
            print("--------------------------------------------------")
    except Exception as e:
        print(f"Failed to read the area report. Reason: {e}")

def display_power_report(new_dir_name):
    """
    Reads and displays the power metrics from the power report after Place-and-Route.

    Args:
        new_dir_name (str): The path to the main project directory.
    """
    power_report_path = os.path.join(new_dir_name, "build", "par-rundir", "dft_top_power.rpt")
    
    try:
        with open(power_report_path, 'r') as report_file:
            for line in report_file:
                if "Total Internal Power:" in line:
                    internal_power = line.split(':')[1].strip()
                    print(f"Total Internal Power: {internal_power}")
                elif "Total Switching Power:" in line:
                    switching_power = line.split(':')[1].strip()
                    print(f"Total Switching Power: {switching_power}")
                elif "Total Leakage Power:" in line:
                    leakage_power = line.split(':')[1].strip()
                    print(f"Total Leakage Power: {leakage_power}")
                elif "Total Power:" in line:
                    total_power = line.split(':')[1].strip()
                    print(f"Total Power: {total_power} mW")
                    print("------------------------------------------------------------")
                    return
            print("Power information not found in the report.")
            print("--------------------------------------------------")
    except Exception as e:
        print(f"Failed to read the power report. Reason: {e}")

def run_par(new_dir_name, clock_period, rerun=False):
    """
    Runs the place and route (PAR) process for the given project directory and clock period.

    This function changes the working directory to the specified project directory,
    runs the PAR process using the appropriate make command, and then analyzes
    the timing report to adjust the clock period if necessary. If the PAR process fails,
    an error message is printed. The working directory is restored at the end.

    Args:
        new_dir_name (str): The path to the main project directory.
        clock_period (float): The clock period for the constraints.
        rerun (bool, optional): Flag indicating whether this is a rerun of the PAR process.
                                Default is False.

    Raises:
        subprocess.CalledProcessError: If the PAR process fails, an error message is printed.
    """
    try:
        os.chdir(new_dir_name)
        current_dir = os.getcwd()
        
        if rerun:
            print(f"Running 'make clean-build' followed by 'make par' in directory: {current_dir}")
            subprocess.run(["make", "clean-build"], check=True)
            subprocess.run(["make", "par"], check=True)
        else:
            print(f"Running 'make par' in directory: {current_dir}")  # Debug print statement
            subprocess.run(["make", "par"], check=True)

        print("Place-and-Route completed successfully.")
       
        # Unzip the timing reports
        unzip_reports(new_dir_name)
       
        # Display report info and tune
        clock_period = rerun_timing(new_dir_name, clock_period, process_type='Place-and-Route')

        # Hold time slack
        display_hold_time_slack(new_dir_name)

        # Area report
        display_area_report(new_dir_name)

        # Power report
        display_power_report(new_dir_name)

    except subprocess.CalledProcessError as e:
        print(f"Place-and-Route failed. Reason: {e}")
    finally:
        os.chdir("..")

def main():
    # Generate Verilog file
    filename = fetch_verilog_file_content()
    if not filename:
        print("Failed to download Verilog file. Exiting.")
        sys.exit(1)

    print("Verilog file downloaded. Proceeding...")
    time.sleep(5)

    # Set up project directory
    new_dir_name, sub_dir_new_name, sub_sub_dir_name = setup_project()
    process_verilog_file(filename)

    # Copy Verilog file to 'v' subdirectory
    destination_path = os.path.join(new_dir_name, sub_dir_new_name, sub_sub_dir_name, filename)
    shutil.copy(filename, destination_path)

    # Create cfg.yml, src.yml, and tb.yml files
    cfg_dir = os.path.join(new_dir_name, sub_dir_new_name, "cfg")
    os.makedirs(cfg_dir, exist_ok=True)

    cfg_file_path = os.path.join(cfg_dir, "cfg.yml")
    create_cfg_file(cfg_file_path)

    src_file_path = os.path.join(cfg_dir, "src.yml")
    create_src_file(src_file_path)

    tb_file_path = os.path.join(cfg_dir, "tb.yml")
    create_tb_file(tb_file_path)

    # Initial clock period for constraints
    initial_clock_period = 8

    # Create constraints.tcl file
    constraints_file_path = os.path.join(cfg_dir, "constraints.tcl")
    create_constraints(constraints_file_path, initial_clock_period)

    # Create Makefile
    makefile_path = os.path.join(new_dir_name, sub_dir_new_name, "Makefile")
    create_makefile(makefile_path)

    # Run synthesis and get the final clock period
    final_clock_period = run_synthesis(os.path.join(new_dir_name, sub_dir_new_name), initial_clock_period)

    # Run PaR with tuned clock
    run_par(os.path.join(new_dir_name, sub_dir_new_name), final_clock_period)

if __name__ == "__main__":
    main()
