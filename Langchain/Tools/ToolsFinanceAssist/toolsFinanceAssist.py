## README ##
# # # # # # # # # # # # # # # # # # # # # # # # 
#    ____  _____    _    ____  __  __ _____    #
#   |  _ \| ____|  / \  |  _ \|  \/  | ____|   #
#   | |_) |  _|   / _ \ | | | | |\/| |  _|     #
#   |  _ <| |___ / ___ \| |_| | |  | | |___    #
#   |_| \_\_____/_/   \_\____/|_|  |_|_____|   #
#                                              #
#                                              #
# # # # # # # # # # # # # # # # # # # # # # # # 

# # Original Data
# 9,FD,2200,2400,200              
# # Added row by the Tool, The amt should be in INT
# 10,FD,"6,400.00 Rs","7,200.00 Rs",800.00 Rs

## drop row is not working

"""
LangChain Tools for Personal Finance Tracking
Handles reading and writing finance data from/to CSV file
"""

## IMPORT ##
# # # # # # # # # # # # # # # # # # # # # 
#    ___ __  __ ____   ___  ____ ___:_    #
#   |_ _|  \/  |  _ \ / _ \|  _ \_   _|   #
#    | || |\/| | |_) | | | | |_) || |     #
#    | || |  | |  __/| |_| |  _ < | |     #
#   |___|_|  |_|_|    \___/|_| \_\|_|     #
#                                         #
#                                         #
# # # # # # # # # # # # # # # # # # # # # 


import csv
import os
from typing import Dict, List, Any
from pathlib import Path
from pydantic import BaseModel, Field
from langchain.tools import tool



## VARIABLES ##
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#   __     ___    ____  ___    _    ____  _     _____ ____     #
#   \ \   / / \  |  _ \|_ _|  / \  | __ )| |   | ____/ ___|    #
#    \ \ / / _ \ | |_) || |  / _ \ |  _ \| |   |  _| \___ \    #
#     \ V / ___ \|  _ < | | / ___ \| |_) | |___| |___ ___) |   #
#      \_/_/   \_\_| \_\___/_/   \_\____/|_____|_____|____/    #
#                                                              #
#                                                              #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 


FINANCE_CSV_PATH = "/root/ProjectRpi/Rpi/PersonalAssistant/Langchain/Tools/ToolsFinanceAssist/Data/finance.csv"
CSV_COLUMNS = ["SrNo", "Name", "InvestedAmount", "CurrentAmount", "Profit"]



## FUNCTIONS ##
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#    _____ _   _ _   _  ____ _____ ___ ___  _   _ ____     #
#   |  ___| | | | \ | |/ ___|_   _|_ _/ _ \| \ | / ___|    #
#   | |_  | | | |  \| | |     | |  | | | | |  \| \___ \    #
#   |  _| | |_| | |\  | |___  | |  | | |_| | |\  |___) |   #
#   |_|    \___/|_| \_|\____| |_| |___\___/|_| \_|____/    #
#                                                          #
#                                                          #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# ============================================================================
# PYDANTIC SCHEMAS FOR TOOL INPUTS
# ============================================================================

class ReadFinanceInput(BaseModel):
    """Schema for reading finance data"""
    filterBy: str = Field(
        default="all",
        description="Filter by: 'all', 'investment_name', or specific row number"
    )
    filterValue: str = Field(
        default="",
        description="Value to filter by (e.g., 'Stocks' or '2')"
    )


class WriteFinanceInput(BaseModel):
    """Schema for writing finance data"""
    operation: str = Field(
        description="Operation type: 'add', 'update', or 'delete'"
    )
    rowNumber: int = Field(
        default=None,
        description="Row number (SrNo) for update/delete operations"
    )
    investmentName: str = Field(
        default="",
        description="Name of the investment (required for 'add' operation)"
    )
    investedAmount: float = Field(
        default=0.0,
        description="Amount invested (required for 'add' operation)"
    )
    currentAmount: float = Field(
        default=0.0,
        description="Current amount (required for 'add' operation)"
    )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def InitializeFinanceCSV() -> None:
    """Initialize finance.csv with headers if it doesn't exist"""
    if not os.path.exists(FINANCE_CSV_PATH):
        print(f"The finance file do not exist:: FINANCE_CSV_PATH: {FINANCE_CSV_PATH}")
        # with open(FINANCE_CSV_PATH, 'w', newline='', encoding='utf-8') as csvFile:
        #     writer = csv.DictWriter(csvFile, fieldnames=CSV_COLUMNS)
        #     writer.writeheader()


def CalculateProfit(investedAmount: float, currentAmount: float) -> float:
    """Calculate profit from invested and current amounts"""
    return round(currentAmount - investedAmount, 2)


def FormatCurrency(amount: float) -> str:
    """Format amount as currency (Rs)"""
    return f"{amount:,.2f} Rs"


def ReadAllFinanceData() -> list[dict]:
    """Read all data from finance.csv"""
    InitializeFinanceCSV()
    
    financeData = []
    try:
        with open(FINANCE_CSV_PATH, 'r', encoding='utf-8') as csvFile:
            reader = csv.DictReader(csvFile)
            for row in reader:
                if row and any(row.values()):  # Skip empty rows
                    financeData.append(row)
    except Exception as e:
        raise Exception(f"Error reading CSV: {str(e)}")
    
    return financeData


def WriteFinanceData(financeData: list[dict]) -> None:
    """Write data to finance.csv"""
    try:
        # backup the current finance.csv file as <timestamp>_finance.csv.bak
        # TODO
        input("WriteFinanceData")

        with open(FINANCE_CSV_PATH, 'w', newline='', encoding='utf-8') as csvFile:
            writer = csv.DictWriter(csvFile, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            writer.writerows(financeData)
    except Exception as e:
        raise Exception(f"Error writing to CSV: {str(e)}")


def GetNextRowNumber() -> int:
    """Get the next available row number (SrNo)"""
    financeData = ReadAllFinanceData()
    if not financeData:
        return 1
    
    maxRowNumber = max(int(row.get("SrNo", 0)) for row in financeData)
    print(f"GetNextRowNumber() maxRowNumber: {maxRowNumber}")
    return maxRowNumber + 1


# ============================================================================
# LANGCHAIN TOOLS
# ============================================================================

@tool(args_schema=ReadFinanceInput)
def ToolReadFinanceData(
    filterBy: str = "all",
    filterValue: str = ""
) -> str:
    """
    Read personal finance data from CSV file.
    
    Args:
        filterBy: Filter type ('all', 'investment_name', 'row_number')
        filterValue: Value to filter by
    
    Returns:
        Formatted finance data as string
    """
    try:
        allFinanceData = ReadAllFinanceData()
        print(f"allFinanceData: {allFinanceData}")
        input("Human01")
        
        if not allFinanceData:
            return "No finance data found. CSV is empty."
        
        # Filter data based on user request
        filteredData = allFinanceData
        print(f"filteredData: {filteredData}")
        input("Human02")
        
        if filterBy == "investment_name" and filterValue:
            filteredData = [
                row for row in allFinanceData 
                if filterValue.lower() in row.get("Name", "").lower()
            ]
        elif filterBy == "row_number" and filterValue:
            filteredData = [
                row for row in allFinanceData 
                if row.get("SrNo") == filterValue
            ]
        
        if not filteredData:
            return f"No data found for filter: {filterBy}={filterValue}"
        
        print(f"filteredData: {filteredData}")
        input("Human03")

        # Format output
        output = "📊 Personal Finance Data:\n"
        output += "=" * 80 + "\n"
        
        totalInvested = 0.0
        totalCurrent = 0.0
        totalProfit = 0.0
        
        for row in filteredData:
            srNo = row.get("SrNo", "N/A")
            name = row.get("Name", "N/A")
            investedStr = row.get("InvestedAmount", "0")
            currentStr = row.get("CurrentAmount", "0")
            profitStr = row.get("Profit", "0")
            
            # Convert to float for calculations
            invested = float(investedStr.replace(",", "").replace(" Rs", ""))
            current = float(currentStr.replace(",", "").replace(" Rs", ""))
            profit = float(profitStr.replace(",", "").replace(" Rs", ""))
            
            totalInvested += invested
            totalCurrent += current
            totalProfit += profit
            
            output += f"\n📌 Sr No: {srNo}\n"
            output += f"   Name: {name}\n"
            output += f"   Invested: {FormatCurrency(invested)}\n"
            output += f"   Current: {FormatCurrency(current)}\n"
            output += f"   Profit: {FormatCurrency(profit)}\n"
        
        output += "\n" + "=" * 80 + "\n"
        output += "📈 Summary:\n"
        output += f"   Total Invested: {FormatCurrency(totalInvested)}\n"
        output += f"   Total Current: {FormatCurrency(totalCurrent)}\n"
        output += f"   Total Profit: {FormatCurrency(totalProfit)}\n"
        
        if totalInvested > 0:
            profitPercentage = (totalProfit / totalInvested) * 100
            output += f"   ROI: {profitPercentage:.2f}%\n"
        
        print(f"output: {output}")
        input("Human04")
        return output
        
    except Exception as e:
        return f"Error reading finance data: {str(e)}"


@tool(args_schema=WriteFinanceInput)
def ToolWriteFinanceData(
    operation: str,
    rowNumber: int = None,
    investmentName: str = "",
    investedAmount: float = 0.0,
    currentAmount: float = 0.0
) -> str:
    """
    Write/update personal finance data to CSV file.
    
    Args:
        operation: 'add', 'update', or 'delete'
        rowNumber: Row number (SrNo) for update/delete
        investmentName: Name of investment
        investedAmount: Amount invested
        currentAmount: Current amount
    
    Returns:
        Success/error message
    """
    try:
        financeData = ReadAllFinanceData()
        print(f"financeData: {financeData}")
        input("Human01")

        if operation.lower() == "add":
            if not investmentName:
                return "Error: investmentName is required for 'add' operation"
            
            nextRowNumber = GetNextRowNumber()
            profitValue = CalculateProfit(investedAmount, currentAmount)
            
            newRow = {
                "SrNo": str(nextRowNumber),
                "Name": investmentName,
                "InvestedAmount": FormatCurrency(investedAmount),
                "CurrentAmount": FormatCurrency(currentAmount),
                "Profit": FormatCurrency(profitValue)
            }
            
            financeData.append(newRow)
            WriteFinanceData(financeData)
            
            return (
                f"✅ Successfully added new investment:\n"
                f"   Sr No: {nextRowNumber}\n"
                f"   Name: {investmentName}\n"
                f"   Invested: {FormatCurrency(investedAmount)}\n"
                f"   Current: {FormatCurrency(currentAmount)}\n"
                f"   Profit: {FormatCurrency(profitValue)}"
            )
        
        elif operation.lower() == "update":
            if not rowNumber:
                return "Error: rowNumber is required for 'update' operation"
            
            foundIndex = None
            for idx, row in enumerate(financeData):
                if row.get("SrNo") == str(rowNumber):
                    foundIndex = idx
                    break
            
            if foundIndex is None:
                return f"Error: No investment found with Sr No {rowNumber}"
            
            oldRow = financeData[foundIndex]
            profitValue = CalculateProfit(investedAmount, currentAmount)
            
            financeData[foundIndex] = {
                "SrNo": str(rowNumber),
                "Name": investmentName or oldRow.get("Name"),
                "InvestedAmount": FormatCurrency(investedAmount) if investedAmount > 0 else oldRow.get("InvestedAmount"),
                "CurrentAmount": FormatCurrency(currentAmount) if currentAmount > 0 else oldRow.get("CurrentAmount"),
                "Profit": FormatCurrency(profitValue)
            }
            
            WriteFinanceData(financeData)
            
            return (
                f"✅ Successfully updated investment Sr No {rowNumber}:\n"
                f"   Name: {financeData[foundIndex].get('Name')}\n"
                f"   Invested: {financeData[foundIndex].get('InvestedAmount')}\n"
                f"   Current: {financeData[foundIndex].get('CurrentAmount')}\n"
                f"   Profit: {financeData[foundIndex].get('Profit')}"
            )
        
        elif operation.lower() == "delete":
            if not rowNumber:
                return "Error: rowNumber is required for 'delete' operation"
            
            foundIndex = None
            for idx, row in enumerate(financeData):
                if row.get("SrNo") == str(rowNumber):
                    foundIndex = idx
                    break
            
            if foundIndex is None:
                return f"Error: No investment found with Sr No {rowNumber}"
            
            deletedRow = financeData.pop(foundIndex)
            WriteFinanceData(financeData)
            
            return (
                f"✅ Successfully deleted investment:\n"
                f"   Sr No: {rowNumber}\n"
                f"   Name: {deletedRow.get('Name')}"
            )
        
        else:
            return f"Error: Unknown operation '{operation}'. Use 'add', 'update', or 'delete'"
    
    except Exception as e:
        return f"Error writing finance data: {str(e)}"



# ============================================================================
# RETURN
# ============================================================================

toolsAdvance =  []             	# Need for human in loop
toolsIntermediate = [ToolReadFinanceData, ToolWriteFinanceData]
toolsBasic = []                  # No need for human in loop

tools = toolsAdvance + toolsIntermediate + toolsBasic

def ToolsList():
    global tools
    return tools

## TEMP ##
# # # # # # # # # # # # # # # # # 
#    _____ _____ __  __ ____     #
#   |_   _| ____|  \/  |  _ \    #
#     | | |  _| | |\/| | |_) |   #
#     | | | |___| |  | |  __/    #
#     |_| |_____|_|  |_|_|       #
#                                #
#                                #
# # # # # # # # # # # # # # # # # 

# get add the FD rows, create a single FD row with all the investment and current value combined, drop the old FD rows
