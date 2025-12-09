# README.md
# The tool is able to create a output.csv file on given user input
# - userInput: create a sample csv file of customers table with 3 fields and 3 rows
# Tool is able to get analysis on the DataInput/*.csv files

from langchain_core.tools import tool

import os
import subprocess
# import tempfile
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field
from langchain.tools import tool
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
# from langchain_anthropic import ChatAnthropic

from datetime import datetime
import os

# Configuration
# DEFAULT_WORKING_DIR = "/tmp/pyspark_jobs"  # Change this to your desired path
# /home/ssbrpi/ProjectRpi/Python/PySpark/Sandbox
# /root/ProjectRpi/Python/PySpark/Sandbox
# defaultWorkingDirDocker = "/root/ProjectRpi/Python/PySpark/Sandbox"  # Change this to your desired path
# OUTPUT_FILE = "output.csv"

# date_str = datetime.now().strftime("%Y-%m-%d")   # yyyy-mm-dd [web:6][web:12]
# OUTPUT_FILE = f"{date_str}_output.csv"
# Create a custom logger
# Configuration
# DEFAULT_DATA_DIR = "/tmp/pyspark_data"  # Location of input CSV files
# DEFAULT_WORKING_DIR = "/tmp/pyspark_jobs"  # Location for output
# OUTPUT_FILE = "output.csv"

# DEFAULT_DATA_DIR = "/root/ProjectRpi/Python/PySpark/Sandbox/DataInput/"  # Location of input CSV files
# DEFAULT_WORKING_DIR = "/root/ProjectRpi/Python/PySpark/Sandbox/DataOutput/"  # Location for output
# dirDockerDataInput
dirDockerDataInput = "/root/ProjectRpi/Python/PySpark/Sandbox/DataInput/"  # Location of input CSV files
# dirDockerDataOutput
dirDockerDataOutput = "/root/ProjectRpi/Python/PySpark/Sandbox/DataOutput/"  # Location for output
# OUTPUT_FILE = "output.csv"

# date_str = datetime.now().strftime("%Y-%m-%d")   # yyyy-mm-dd [web:6][web:12]
timeStamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
OUTPUT_FILE = f"{timeStamp}_output.csv"



####################### V02 vvv ######################
class CSVAnalysisInput(BaseModel):
    """Input schema for CSV data analysis."""
    
    user_query: str = Field(
        description="Natural language query about the CSV data (e.g., 'List customers in xyz project')"
    )
    dirDockerDataInput: Optional[str] = Field(
        default=dirDockerDataInput,
        description="Directory path where CSV files are located"
    )
    dirDockerDataOutput: Optional[str] = Field(
        default=dirDockerDataOutput,
        description="Directory path where output files will be saved"
    )



@tool(args_schema=CSVAnalysisInput)
def analyze_csv_data(
    user_query: str,
    dirDockerDataInput: str = dirDockerDataInput,
    dirDockerDataOutput: str = dirDockerDataOutput
) -> str:
    """
    Analyze existing CSV files using natural language queries.
    
    This tool:
    1. Discovers available CSV files in dirDockerDataInput
    2. Analyzes CSV schema and metadata
    3. Converts user query to PySpark analysis code
    4. Executes the analysis in dirDockerDataOutput
    5. Saves results to output.csv
    
    Args:
        user_query: Natural language question about the CSV data
        dirDockerDataInput: Directory containing CSV files to analyze
        dirDockerDataOutput: Directory where analysis results are saved
    
    Returns:
        Status message with execution result or error details
    
    Example:
        result = analyze_csv_data(
        )
    """
    
    try:
        # Step 1: Verify data directory exists
        if not Path(dirDockerDataInput).exists():
            return f"✗ Data directory not found: {dirDockerDataInput}"
        print(f"dirDockerDataInput: {dirDockerDataInput}")
        input("HumanInterupt01")

        # Step 2: Discover CSV files
        csv_files = _discover_csv_files(dirDockerDataInput)
        if not csv_files:
            return f"✗ No CSV files found in: {dirDockerDataInput}"
        print(f"csv_files: {csv_files}")
        input("HumanInterupt02")
        
        # Step 3: Build metadata for Claude
        csv_metadata = _build_csv_metadata(dirDockerDataInput)
        print(f"csv_metadata: {csv_metadata}")
        input("HumanInterupt03")

        # Step 4: Generate analysis code
        # scriptFileRpiPath = scriptFileDockerPath.replace("/root", "/home/ssbrpi")
        dirRpiDataInput = dirDockerDataInput.replace("/root", "/home/ssbrpi")
        pyspark_code = _generate_analysis_code(
            user_query=user_query,
            dirRpiDataInput=dirRpiDataInput,
            csv_metadata=csv_metadata
        )
        print(f"pyspark_code: {pyspark_code}")
        input("HumanInterupt04")
        
        # Step 5: Create working directory
        Path(dirDockerDataOutput).mkdir(parents=True, exist_ok=True)
        print(f"dirDockerDataOutput: {dirDockerDataOutput}")
        input("HumanInterupt05")
        
        # Step 6: Write analysis script
        script_file = os.path.join(dirDockerDataOutput, "analysis_script.py")
        with open(script_file, 'w') as f:
            f.write(pyspark_code)
        print(f"script_file: {script_file}")
        input("HumanInterupt06")
        
        # Step 7: Execute analysis
        # dirDockerDataInput = data_directory
        dirRpiDataInput = dirDockerDataInput.replace("/root", "/home/ssbrpi")
        dirRpiDataOutput = dirDockerDataOutput.replace("/root", "/home/ssbrpi")
        scriptRpiFilePath = script_file.replace("/root", "/home/ssbrpi")

        # result = _execute_analysis_script(scriptRpiFilePath, dirRpiDataOutput, dirRpiDataInput, dirDockerDataInput)
        result = _execute_analysis_script(scriptRpiFilePath, dirRpiDataOutput)
        print(f"result: {result}")
        input("HumanInterupt07")
        
        if result['success']:
            output_path = os.path.join(dirDockerDataOutput, OUTPUT_FILE)
            return f"""✓ Analysis completed successfully!

Query: {user_query}

Available CSV files: {', '.join(csv_files)}
Output saved to: {output_path}

Execution details:
{result['message']}"""
        else:
            return f"""✗ Analysis failed:
Query: {user_query}

Error details:
{result['message']}"""
    
    except Exception as e:
        return f"✗ Error during analysis setup: {str(e)}"


# def _discover_csv_files(data_directory: str) -> List[str]:
def _discover_csv_files(dirDockerDataInput: str) -> list[str]:
    """
    Discover all CSV files in the data directory.
    
    Args:
        dirDockerDataInput: Path to search for CSV files
    
    Returns:
        List of CSV file names (without path)
    
    Example:
        ['customers.csv', 'company.csv', 'project.csv']
    """
    try:
        data_path = Path(dirDockerDataInput)
        if not data_path.exists():
            return []
        
        csv_files = [f.name for f in data_path.glob("*.csv")]
        return sorted(csv_files)
    except Exception as e:
        print(f"Warning: Error discovering CSV files: {e}")
        return []



def _build_csv_metadata(dirDockerDataInput: str) -> str:
    """
    Build metadata about all CSV files for the prompt.
    
    Args:
        dirDockerDataInput: Directory containing CSV files
    
    Returns:
        Formatted metadata string for Claude
    """
    csv_files = _discover_csv_files(dirDockerDataInput)
    
    if not csv_files:
        return "No CSV files found in the data directory."
    
    metadata = f"Available CSV files ({len(csv_files)}):\n"
    metadata += "=" * 50 + "\n"
    
    for csv_file in csv_files:
        schema = _get_csv_schema(dirDockerDataInput, csv_file)
        if schema:
            metadata += f"\nFile: {schema['filename']}\n"
            metadata += f"Columns: {', '.join(schema['columns'])}\n"
            metadata += f"Sample: {dict(zip(schema['columns'], schema['sample_row']))}\n"
    
    return metadata


def _get_csv_schema(dirDockerDataInput: str, csv_filename: str) -> Optional[dict]:
    """
    Get schema information for a CSV file.
    
    Args:
        dirDockerDataInput: Directory containing CSV files
        csv_filename: Name of the CSV file
    
    Returns:
        Dictionary with column names and sample data
    """
    try:
        csv_path = os.path.join(dirDockerDataInput, csv_filename)
        
        with open(csv_path, 'r') as f:
            # Read header
            header = f.readline().strip().split(',')
            # Read first data row as sample
            first_row = f.readline().strip().split(',')
        
        return {
            'filename': csv_filename,
            'columns': header,
            'sample_row': first_row
        }
    except Exception as e:
        print(f"Warning: Error reading schema from {csv_filename}: {e}")
        return None


def _generate_analysis_code(
    user_query: str,
    dirRpiDataInput: str,
    csv_metadata: str
) -> str:
    """
    Generate PySpark analysis code from user query.
    
    Args:
        user_query: Natural language query about the data
        dirRpiDataInput: Directory containing CSV files
        csv_metadata: Metadata about available CSV files
    
    Returns:
        Generated PySpark Python code as string
    """
    
    prompt = f"""You are a PySpark data analysis expert. Generate production-ready PySpark code to answer this query:

User Query: {user_query}

Available Data:
{csv_metadata}

Requirements:
1. Read CSV files from: {dirRpiDataInput}
2. Use PySpark DataFrame API (NOT SQL)
3. Write code to load CSV files:
   - Use: spark.read.option("header", "true").csv("{dirRpiDataInput}/filename.csv")
   
4. Perform joins/filters/transformations as needed for the query
5. Show intermediate results if helpful (optional)
6. Save final result to CSV:
   - Path: "{OUTPUT_FILE}" (relative to execution directory)
   - Use: df_result.write.mode("overwrite").option("header", "true").csv("{OUTPUT_FILE}")

7. Include error handling with try/except/finally
8. Stop SparkSession in finally block
9. Add comments explaining each step

Code Requirements:
- Must be standalone and executable
- Initialize: spark = SparkSession.builder.master("local[*]").appName("DataAnalyzer").getOrCreate()
- Import necessary modules from pyspark.sql
- Handle missing files gracefully
- Optimize joins (use broadcast for small DataFrames)
- Do NOT use SQL, use DataFrame API only

Generate ONLY the Python code, no explanations or markdown."""
    
    try:
        model = ChatOpenAI(model="gpt-3.5-turbo", streaming=True, max_tokens=500, temperature=0, max_retries=1)
        # model = ChatAnthropic(model="claude-opus-4-1-20250805")
        print(f"prompt: {prompt}")
        input("HumanStop00")
        response = model.invoke(prompt)
        
        # Extract code from response
        code = response.content
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0].strip()
        elif "```" in code:
            code = code.split("```")[1].split("```")[0].strip()
        
        return code
    
    except Exception as e:
        print(f"Warning: Code generation failed ({str(e)}).")
        # return _get_fallback_analysis_template(dirRpiDataInput, csv_metadata)
        return f"Warning: Code generation failed ({str(e)})."

def _execute_analysis_script(
    scriptRpiFilePath: str,
    dirRpiDataOutput: str,
    # dirRpiDataInput: str,
    # dirDockerDataInput: str
) -> dict:
# def _execute_analysis_script(
#     script_path: str,
#     working_directory: str,
#     dirDockerDataInput: str
# ) -> dict:
    """
    Execute analysis script with data directory accessible.
    
    Args:
        script_path: Path to the analysis Python script
        dirRpiDataOutput: Directory to execute from
        dirDockerDataInput: Directory containing CSV files (passed via env)
    
    Returns:
        Dictionary with keys: 'success' (bool) and 'message' (str)
    """
    
    try:
        # Prepare environment
        # env = os.environ.copy()
        # env['DATA_DIR'] = data_directory
        # env['PYSPARK_PYTHON'] = 'python'
        
        # Create shell command
        # scriptRpiFilePath: str,
        # dirRpiDataOutput: str,
        # dirRpiDataInput: str,
        # dirDockerDataInput: str
        # shell_command = f"cd {working_directory} && python {script_path}"
        print(f"in ShellCmd, dirRpiDataOutput: {dirRpiDataOutput}, scriptRpiFilePath: {scriptRpiFilePath}")
        shell_command = f'ssh ssbrpi@172.17.0.1 "cd {dirRpiDataOutput}; python {scriptRpiFilePath}"'
        # Execute with timeout
        # result = subprocess.run(
        #     shell_command,
        #     shell=True,
        #     capture_output=True,
        #     text=True,
        #     timeout=300  # 5 minute timeout
        #     # cwd=working_directory,
        #     # env=env
        # )

        process = subprocess.Popen(
            shell_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Merge stderr into stdout
            text=True,
            bufsize=1  # Line buffering
        )

        output_lines = []
        try:
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    print(line, end='', flush=True)  # Live print
                    output_lines.append(line)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        finally:
            process.stdout.close()

        # result_output = ''.join(output_lines)
        result = ''.join(output_lines)
        returncode = process.returncode
        
        # if result.returncode == 0:
        if returncode == 0:
            return {
                'success': True,
                'message': f"""Script executed in: {dirRpiDataOutput}"""
            }
        else:
            return {
                'success': False,
                'message': f"""Return code: {returncode}"""
            }
    
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'message': "Script execution timeout (exceeded 300 seconds)"
        }
    except Exception as e:
        return {
            'success': False,
            'message': f"Execution error: {str(e)}"
        }




# toolsAdvance =  [toolShell]             	# Need for human in loop
# toolsIntermediate = [execute_pyspark_code] analyze_csv_data
toolsIntermediate = [analyze_csv_data]
# toolsBasic = [toolMyName, toolMyPetsName]                  # No need for human in loop
# toolsBasic = [toolMyName]                  # No need for human in loop
# toolsBasic = [toolMyName, toolMyPetsName]                  # No need for human in loop

tools = toolsIntermediate

# ~ humanBreak = input("humanBreak:")

def ToolsList():
    global tools
    return tools

# create a sample csv file of customers
# Give me Top 10 Expensive Projects by Department
