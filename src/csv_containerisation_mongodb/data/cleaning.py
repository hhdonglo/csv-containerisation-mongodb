"""
Data Cleaning Module

Comprehensive data cleaning, standardization, and quality assessment
for healthcare datasets with automated reporting.

Author: Hope Donglo - OpenClassrooms (DataSoluTech)
"""

from pathlib import Path
import glob
import pandas as pd
from IPython.display import display
from datetime import datetime
import sys

from csv_containerisation_mongodb.data.load_data import LOAD_DATA
from csv_containerisation_mongodb.utils.file_manager import FILE_PATH_MANAGER, OUTPUT_MANAGER


class FILE_CLEANING:
    """
    Data cleaning and quality assessment for healthcare datasets.
    
    Provides comprehensive cleaning, standardization, and validation with
    automated output management and reporting through OUTPUT_MANAGER.
    """
    
    def __init__(self, ld_data: LOAD_DATA, file_path: FILE_PATH_MANAGER, file_name=None):
        """
        Initialize FILE_CLEANING with loaded data.
        
        Args:
            ld_data: Initialized LOAD_DATA instance containing the dataframe
            file_path: File path manager instance containing directory paths
            file_name: Name of the file being processed
        """
        self.data_dict = None
        self.df = ld_data.df
        self.file_name = file_name if file_name else 'unnamed'
        
        self.output_manager = OUTPUT_MANAGER(
            output_dir=file_path.processed_data_dir,
            file_name=self.file_name,
            report_title='Data Cleaning Report',
            use_timestamp=False
        )
        
        print(f"FILE_CLEANING initialized for: {file_name}")
        print(f"Initial shape: {self.df.shape}\n")

    def preview(self):
        """Display first few rows of the dataframe."""
        print("\n## Preview\n")
        print("```")
        print(self.df.head().to_string())
        print("```\n")

    def standardising_names(self):
        """Standardize name columns to title case and remove whitespace."""
        print("\n## Name Standardization\n")
        print("Starting name standardization...")
        
        unique_before = self.df['Name'].nunique()
        self.df['Name'] = self.df['Name'].str.title().str.strip()
        unique_after = self.df['Name'].nunique()
        
        print("\n### Results\n")
        print(f"- **Unique names before:** {unique_before}")
        print(f"- **Unique names after:** {unique_after}\n")
        
        print("### Sample of Standardized Names\n")
        print("```")
        print(self.df['Name'][:10].to_string())
        print("```\n")

    def drop_duplicates(self):
        """Remove duplicate rows, keeping first occurrence."""
        print("\n## Duplicate Removal\n")
        
        original_shape = self.df.shape
        duplicates_count = self.df.duplicated().sum()
        
        print("Starting duplicate removal...")
        print(f"- **Shape before:** {self.df.shape}")
        print(f"- **Duplicate rows found:** {duplicates_count}")
        
        self.df = self.df.drop_duplicates(keep='first').reset_index(drop=True)
        
        rows_removed = original_shape[0] - self.df.shape[0]
        reduction_pct = (rows_removed / original_shape[0] * 100) if original_shape[0] > 0 else 0
        
        print("\n### Results\n")
        print(f"- **Shape after:** {self.df.shape}")
        print(f"- **Rows removed:** {rows_removed}")
        print(f"- **Reduction:** {reduction_pct:.2f}%\n")

    def data_type_optimisation(self):
        """Optimize dataframe data types for memory efficiency."""
        print("\n## Data Type Optimization\n")
        print("Starting data type optimization...")
        
        memory_before = self.df.memory_usage(deep=True).sum() / 1024**2
        print(f"- **Memory before:** {memory_before:.2f} MB")
        
        self.df['Date of Admission'] = pd.to_datetime(self.df['Date of Admission'])
        self.df['Discharge Date'] = pd.to_datetime(self.df['Discharge Date'])
        self.df['Hospital'] = self.df['Hospital'].astype('category')
        self.df['Medical Condition'] = self.df['Medical Condition'].astype('category')
        self.df['Billing Amount'] = pd.to_numeric(self.df['Billing Amount'], errors='coerce')
        
        memory_after = self.df.memory_usage(deep=True).sum() / 1024**2
        memory_reduction = ((memory_before - memory_after) / memory_before * 100) if memory_before > 0 else 0
        
        print("\n### Results\n")
        print(f"- **Memory after:** {memory_after:.2f} MB")
        print(f"- **Memory reduction:** {memory_reduction:.2f}%\n")
        
        print("### DataFrame Info\n")
        print("```")
        print(f"Optimizing column names:")
        self.df = self.df.rename(columns={'Date of Admission': 'Admission Date'})

        from io import StringIO
        buffer = StringIO()
        self.df.info(buf=buffer, memory_usage='deep')
        print(buffer.getvalue())
        print("```\n")

    def quality_check(self, export_to_csv=True):
        """
        Generate comprehensive data quality report.
        
        Creates quality metrics including data types, missing values,
        unique values, duplicates, and most common values per column.
        
        Args:
            export_to_csv: If True, exports report to CSV
        
        Returns:
            DataFrame: Quality assessment report
        """
        print("\n## Quality Check\n")
        print("Generating quality check report...")
        
        quality_check = pd.DataFrame({
            'Data Type': self.df.dtypes,
            'Missing Values': self.df.isnull().sum(),
            'Missing %': round((self.df.isnull().sum() / len(self.df)) * 100, 2),
            'Unique Values': self.df.nunique(),
            'Duplicate Count': [self.df[col].duplicated().sum() for col in self.df.columns],
            'Duplicate %': [round((self.df[col].duplicated().sum() / len(self.df)) * 100, 2) for col in self.df.columns],
            'Cardinality': [
                'High' if self.df[col].nunique() / len(self.df) > 0.5
                else 'Medium' if self.df[col].nunique() / len(self.df) > 0.05
                else 'Low'
                for col in self.df.columns
            ],
            'Most Common Value': [self.df[col].mode()[0] if len(self.df[col].mode()) > 0 else None for col in self.df.columns],
            'Most Common Freq': [self.df[col].value_counts().iloc[0] if len(self.df[col]) > 0 else 0 for col in self.df.columns],
            'Most Common %': [round((self.df[col].value_counts().iloc[0] / len(self.df)) * 100, 2) if len(self.df[col]) > 0 else 0 for col in self.df.columns],
        })
        
        print("\n### Summary\n")
        print(f"- **Total columns:** {len(quality_check)}")
        print(f"- **Columns with missing values:** {(quality_check['Missing Values'] > 0).sum()}")
        print(f"- **Total missing values:** {quality_check['Missing Values'].sum()}")
        print(f"- **High cardinality columns:** {(quality_check['Cardinality'] == 'High').sum()}\n")
        
        if export_to_csv:
            csv_path = self.output_manager.get_output_path('quality_csv')
            
            try:
                quality_check.to_csv(csv_path)
                print(f"Quality report CSV saved to: {csv_path.absolute()}")
            except Exception as e:
                print(f"ERROR: Failed to save CSV - {e}")
        
        print("\n### Detailed Metrics\n")
        print(quality_check.to_markdown())
        print("\n```")
        print(quality_check.to_string())
        print("```\n")
        
        return quality_check

    def save_cleaned_csv(self):
        """Save the cleaned dataframe to CSV file."""
        print("\n## Saving Cleaned Data\n")
        
        csv_path = self.output_manager.get_output_path('cleaned_csv')
        print(f"Saving cleaned data to: {csv_path.name}")
        
        try:
            self.df.to_csv(csv_path, index=False)
            file_size = csv_path.stat().st_size / 1024
            print(f"[SUCCESS] Cleaned CSV saved successfully")
            print(f"- **Path:** `{csv_path.absolute()}`")
            print(f"- **Size:** {file_size:.2f} KB")
            print(f"- **Rows:** {len(self.df)}")
            print(f"- **Columns:** {len(self.df.columns)}\n")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to save CSV - {e}\n")
            return False

    def finalize_report(self):
        """Finalize cleaning report with summary statistics and save CSV."""
        self.save_cleaned_csv()
        
        final_memory = self.df.memory_usage(deep=True).sum() / 1024**2
        
        final_stats = {
            'Final shape': f"{self.df.shape}",
            'Final memory usage': f"{final_memory:.2f} MB",
            'Total rows': len(self.df),
            'Total columns': len(self.df.columns)
        }
        
        self.output_manager.finalize_report(final_stats)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            print(f"\n[ERROR] Cleaning operation failed: {exc_val}")
            import traceback
            traceback.print_exception(exc_type, exc_val, exc_tb)
        return False