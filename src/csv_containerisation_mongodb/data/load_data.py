"""
CSV Data Loader Module

Handles loading and selection of CSV files from specified directories.

Author: Hope Donglo - OpenClassrooms (DataSoluTech)
"""

from pathlib import Path
import glob
import pandas as pd


class LOAD_DATA:
    """Loads CSV files into pandas DataFrames with interactive selection."""
    
    def __init__(self):
        self.data_dict = None
        self.df = None

    def csv_loader(self, data_dir=None, df_name=None):
        """
        Load CSV files from directory and select target DataFrame.
        
        Args:
            data_dir: Path to directory containing CSV files
            df_name: Name of DataFrame to load (without extension)
            
        Returns:
            self: For method chaining
        """
        if data_dir is None:
            print("ERROR: data_dir cannot be None")
            return self
        
        try:
            data_files = list(data_dir.glob('*.csv'))
            if not data_files:
                print("ERROR: No CSV files found in directory")
                return self
            print(f"Files loaded successfully")
        except Exception as e:
            print(f'ERROR: Failed to load files - {e}')
            raise
        
        self.data_dict = {
            file.stem.split('_')[0]: pd.read_csv(file) for file in data_files
        }
        
        if df_name is None:
            self.df = self._interactive_selection()
        else:
            self.df = self._select_dataframe(df_name)
        
        return self
    
    def _select_dataframe(self, df_name):
        """
        Select DataFrame by name with validation.
        
        Args:
            df_name: Name of DataFrame to select
            
        Returns:
            DataFrame: Selected DataFrame
        """
        if df_name in self.data_dict:
            print(f"Loaded dataframe: {df_name}")
            return self.data_dict[df_name]
        
        print(f"ERROR: '{df_name}' not found")
        print(f"Available: {list(self.data_dict.keys())}")
        return self._interactive_selection()
    
    def _interactive_selection(self):
        """
        Prompt user to select DataFrame interactively.
        
        Returns:
            DataFrame: User-selected DataFrame
        """
        print(f'Available dataframes: {list(self.data_dict.keys())}')
        
        while True:
            df_name = input("Enter dataframe name: ").strip()
            
            if df_name in self.data_dict:
                print(f"Loaded dataframe: {df_name}")
                return self.data_dict[df_name]
            
            print(f"ERROR: '{df_name}' not found. Try again.")