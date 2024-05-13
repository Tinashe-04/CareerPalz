""" 
This script is used to create a single file for the LCA 2023 data.
The required data is in 4 different files, one for each quarter of the year.
I will use this script to combine the data from each of those four quarters into a single file.
"""

# import the libraries for data analysis
import pandas as pd
import os

# Set the path to the data files
q1 = '/Users/tinashem/LCA Data/FY2023/LCA_Disclosure_Data_FY2023_Q1.xlsx'
q2 = '/Users/tinashem/LCA Data/FY2023/LCA_Disclosure_Data_FY2023_Q2.xlsx'
q3 = '/Users/tinashem/LCA Data/FY2023/LCA_Disclosure_Data_FY2023_Q3.xlsx'
q4 = '/Users/tinashem/LCA Data/FY2023/LCA_Disclosure_Data_FY2023_Q4.xlsx'

# Read the data and create a list of the dataframes
data_q1 = pd.read_excel(q1)
data_q2 = pd.read_excel(q2)
data_q3 = pd.read_excel(q3)
data_q4 = pd.read_excel(q4)

df_list = [data_q1, data_q2, data_q3, data_q4]

# find out how many rows and columns are in each of the dataframes
print(df.shape for df in df_list)

# Combine the data
combined_data = pd.concat(df_list, ignore_index=True, verify_integrity=True)
