"""
Healthcare Data Processing Pipeline

Main pipeline class orchestrating the complete ETL process:
1. CSV data loading
2. Data cleaning and standardization
3. Quality reporting
4. MongoDB migration
5. Data integrity verification

Author: Hope Donglo - OpenClassrooms (DataSoluTech)
"""

from pathlib import Path
import logging
from typing import Optional
from dataclasses import dataclass
import os

from csv_containerisation_mongodb.utils.file_manager import FILE_PATH_MANAGER
from csv_containerisation_mongodb.data.load_data import LOAD_DATA
from csv_containerisation_mongodb.data.cleaning import FILE_CLEANING
from csv_containerisation_mongodb.migration.migration import Connect, LoadDb
from csv_containerisation_mongodb.test.test import DataIntegrityChecker


@dataclass
class PipelineConfig:
    """Configuration for the data pipeline."""
    raw_file_name: str = 'healthcare'
    cleaned_file_name: str = 'cleaned_healthcare'
    db_name: str = os.getenv('MONGO_DATABASE', 'medical_records')
    collection_name: str = 'healthcare_data'
    mongodb_uri: str = os.getenv('MONGO_URI', 'mongodb://localhost:27017')


class HealthcarePipeline:
    """
    Main healthcare data processing pipeline.
    
    Orchestrates the complete ETL process from CSV to MongoDB with
    quality checks and integrity verification.
    """
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        """
        Initialize the pipeline.
        
        Args:
            config: Pipeline configuration. Uses defaults if None.
        """
        self.config = config or PipelineConfig()
        self.data_path = FILE_PATH_MANAGER()
        self.loader = LOAD_DATA()

    def run(self) -> bool:
        """
        Execute the complete pipeline.
        
        Returns:
            bool: True if pipeline completed successfully, False otherwise
        """
        try:
            self._print_header()
            
            if not self._load_raw_data():
                return False
            
            if not self._clean_data():
                return False
            
            conn = self._connect_mongodb()
            if not conn:
                return False
            
            if not self._load_cleaned_data():
                return False
            
            if not self._migrate_to_mongodb(conn):
                return False
            
            if not self._verify_integrity(conn):
                return False
            
            self._print_footer()
            return True
            
        except Exception as e:
            print(f"Pipeline failed: {e}")
            return False

    def _print_header(self) -> None:
        """Print pipeline header."""
        print("=" * 80)
        print("HEALTHCARE DATA PROCESSING PIPELINE")
        print("=" * 80)

    def _print_footer(self) -> None:
        """Print pipeline footer."""
        print("\n" + "=" * 80)
        print("PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 80)

    def _load_raw_data(self) -> bool:
        """
        Load raw data from CSV.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print("\n[STEP 1] Loading raw data...")
            print(f"Source: {self.data_path.raw_data_dir}")
            
            self.loader.csv_loader(
                data_dir=self.data_path.raw_data_dir,
                df_name=self.config.raw_file_name
            )
            
            rows, cols = self.loader.df.shape
            print(f"Loaded: {rows:,} rows, {cols} columns")
            return True
            
        except FileNotFoundError as e:
            print(f"ERROR: Raw data file not found - {e}")
            return False
        except Exception as e:
            print(f"ERROR: Failed to load raw data - {e}")
            return False

    def _clean_data(self) -> bool:
        """
        Clean and standardize the data.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print("\n[STEP 2] Starting data cleaning pipeline...")
            print(f"Output directory: {self.data_path.processed_data_dir}")
            print("-" * 80)
            
            with FILE_CLEANING(
                self.loader,
                file_path=self.data_path,
                file_name=self.config.raw_file_name
            ) as cleaner:
                cleaner.preview()
                cleaner.standardising_names()
                cleaner.drop_duplicates()
                cleaner.data_type_optimisation()
                cleaner.quality_check(export_to_csv=True)
                cleaner.finalize_report()
            
            print("-" * 80)
            print("\n[STEP 3] Data cleaning completed")
            print(f"Output files:")
            print(f"  - Markdown report")
            print(f"  - Cleaned CSV file")
            print(f"  - Quality assessment report")
            print(f"\nLocation: {self.data_path.processed_data_dir.absolute()}")
            return True
            
        except Exception as e:
            print(f"ERROR: Data cleaning failed - {e}")
            return False

    def _connect_mongodb(self) -> Optional[Connect]:
        """
        Establish MongoDB connection.
        
        Returns:
            Connect object if successful, None otherwise
        """
        try:
            print("\n[STEP 4] Connecting to MongoDB...")
            print(f"URI: {self.config.mongodb_uri}")
            
            conn = Connect()
            conn.conn_parameters(
                db_name=self.config.db_name,
                collection_name=self.config.collection_name,
                uri=self.config.mongodb_uri
            )
            
            print(f"Database: {self.config.db_name}")
            print(f"Collection: {self.config.collection_name}")
            return conn
            
        except Exception as e:
            print(f"ERROR: MongoDB connection failed - {e}")
            print("Check if MongoDB is running")
            return None

    def _load_cleaned_data(self) -> bool:
        """
        Load cleaned data for migration.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print("\n[STEP 5] Loading cleaned data...")
            print(f"Source: {self.data_path.processed_data_dir}")
            
            self.loader.csv_loader(
                data_dir=self.data_path.processed_data_dir,
                df_name='cleaned'
            )
            
            rows, cols = self.loader.df.shape
            print(f"Loaded: {rows:,} rows, {cols} columns")
            return True
            
        except FileNotFoundError as e:
            print(f"ERROR: Cleaned data file not found - {e}")
            return False
        except Exception as e:
            print(f"ERROR: Failed to load cleaned data - {e}")
            return False

    def _migrate_to_mongodb(self, conn: Connect) -> bool:
        """
        Migrate data to MongoDB.
        
        Args:
            conn: MongoDB connection object
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print("\n[STEP 6] Migrating data to MongoDB...")
            print("-" * 80)
            
            with LoadDb(conn, df=self.loader.df) as db_loader:
                db_loader.dbloader()
            
            print("-" * 80)
            print("Migration completed")
            return True
            
        except Exception as e:
            print(f"ERROR: Data migration failed - {e}")
            return False

    def _verify_integrity(self, conn: Connect) -> bool:
        """
        Verify data integrity after migration.
        
        Args:
            conn: MongoDB connection object
        
        Returns:
            bool: True if verification passed, False otherwise
        """
        try:
            print("\n[STEP 7] Verifying data integrity...")
            print("-" * 80)
            
            with DataIntegrityChecker(
                db_name=self.config.db_name,
                collection_name=self.config.collection_name,
                df=self.loader.df
            ) as checker:
                checker.test_document_count()
                checker.test_field_structure()
                checker.test_missing_values()
                checker.test_data_types()
                checker.test_duplicates()
            
            print("-" * 80)
            print("Data integrity verification PASSED")
            return True
        
        except AssertionError as e:
            print(f"ERROR: Integrity verification failed - {e}")
            return False
        except Exception as e:
            print(f"ERROR: Verification error - {e}")
            return False