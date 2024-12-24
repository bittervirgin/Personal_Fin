import pdfplumber
import pandas as pd
import json
import re
import os
import sys

class pdfReader():
    def __init__(self, pdf_path, path_column_schema=None):
        self.__pdf_path = pdf_path
        self.__path_col_schema  = path_column_schema

    @property
    def path_col_schema(self):
        return self.__path_col_schema
    @path_col_schema.setter
    def path_col_schema(self, path_col_schema):
        if os.path.exists(path_col_schema):
            self.__path_col_schema = path_col_schema
        else:
            raise FileNotFoundError(f"File not found: {path_col_schema}")
        
    def extract_tables(self):
        """Extract tables from the PDF file."""
        with pdfplumber.open(self.__pdf_path) as pdf:
            tables = []
            for page in pdf.pages:
                page_tables = page.extract_tables()
                for table in page_tables:
                    if table:
                        tables.append(pd.DataFrame(table))
        return tables

    def clean_headers(self, headers):
        """Clean column headers by removing Vietnamese words stand before slash and replacing spaces with underscores."""
        cleaned = []
        for header in headers:
            # Remove Vietnamese words (containing diacritics) and keep only English words

            for char in ("/", "\n"):
                try:
                    english_only = header.split(char)[1]
                except IndexError as e:
                    continue
                else:
                    english_only = header

            cleaned.append(english_only.strip().replace(' ', '_'))  # Replace spaces with underscores
        return cleaned
    
    def exportColName(self):
        """"Export list col names from dataframe to json file to prepare for mapping"""
        tables = self.extract_tables()
        for table in tables:
            # Assuming target headers are column's names
            headers = table.columns.tolist()

            # Create a dict with column's names as keys and empty string as values
            col_dict = {header: "" for header in headers}

            # Export the dict to  a JSON file
            with open(self.__path_col_schema, "w") as f:
                json.dump(col_dict, f, indent=4)
        



class payslipReader(pdfReader):
    def __init__(self, pdf_path, path_column_schema=r"D:\\Hungtv7\\Personal_Fin\\config\\VNG_payslip.json"):
        super().__init__(pdf_path, path_column_schema)

    def special_case_for_header(header):
        if header == 'Công ty':
            return "Company"
        # elif header == "Tổng số ngày nghỉ hưởng lương BHXH (tỷ lệ 75%)":
        #     return "Leave days subject to 75% Social Insurance"
        # elif header == "Tổng số ngày nghỉ hưởng lương BHXH (tỷ lệ 100%)":
        #     return "Leave days subject to 100% Social Insurance"
        elif header == "Lương doanh số Commission":
            return "Comission"
        else:
            return header
    
    def clean_headers(self, headers):
        """Clean column headers by removing Vietnamese words stand before slash and replacing spaces with underscores."""
        cleaned = []
        for header in headers:
            # Remove Vietnamese words (containing diacritics) and keep only English words
            
            for char in ("/", "\n"):
                try:
                    print(header.split(f"{char}")[1])
                    english_only = payslipReader.special_case_for_header(header.split(f"{char}")[1])
                except IndexError as e:
                    continue
                    
            # print(english_only.strip().replace(' ', '_'))
            cleaned.append(english_only.strip().replace(' ', '_'))  # Replace spaces with underscores
        return cleaned
        
    def extract_tables(self):
        """Extract tables from the PDF file."""
        with pdfplumber.open(self._pdfReader__pdf_path) as pdf:
            tables = []
            for page in pdf.pages:
                page_tables = page.extract_tables()
                for table in page_tables:
                    if table:
                        df = pd.DataFrame(table[1:], columns=table[0]).transpose()
                        df.reset_index(inplace=True)
                        df.columns = self.clean_headers(df.iloc[0])  # Clean headers
                        df = df.drop(df.index[0])  # Drop the row used for column names
                        tables.append(df)
        return tables


vng_payslip_reader = payslipReader(r"D:\Hungtv7\Personal_Fin\VNG_payslip\payslip_VG-15316_2021_04.pdf")

transposed_tables = vng_payslip_reader.extract_tables()

# Display the first few rows of each extracted table for illustration
for i, table in enumerate(transposed_tables):
    if table.shape[0] < 3:
        table.drop([1])   
    elif table.shape[0] >= 3:
        table.drop([1])
    print(f"Transposed Table {i+1}:\n", table)
