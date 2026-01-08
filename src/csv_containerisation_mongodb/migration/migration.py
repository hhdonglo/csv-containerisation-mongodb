"""
MongoDB Migration Module

Handles MongoDB connection management and data migration from CSV to MongoDB.
Implements structured document transformation and bulk insertion.

Author: hhdonglo - OpenClassrooms (DataSoluTech)
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import pandas as pd
from datetime import datetime, timezone
import logging
import os

from csv_containerisation_mongodb.utils.file_manager import FILE_PATH_MANAGER
from csv_containerisation_mongodb.data.load_data import LOAD_DATA

logger = logging.getLogger(__name__)


class Connect:
    """MongoDB connection manager."""
    
    def __init__(self, db_name=None, collection_name=None, uri=None):
        """
        Initialize MongoDB connection.
        
        Args:
            db_name: Database name
            collection_name: Collection name
            uri: MongoDB URI (defaults to MONGO_URI env var or localhost)
        """
        self.db_name = db_name
        self.collection_name = collection_name
        self.uri = uri or os.getenv('MONGO_URI', 'mongodb://localhost:27017')
        self.client = None
        self.db = None
        self.collection = None

        if db_name is not None and collection_name is not None:
            self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB."""
        self.client = MongoClient(self.uri)
        try:
            self.client.admin.command('ismaster')
            print(f"Connected to MongoDB successfully")
        except ConnectionFailure as e:
            print(f"ERROR: MongoDB connection failed - {e}")
            raise
            
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]

    def conn_parameters(self, db_name, collection_name, uri='mongodb://localhost:27017'):
        """
        Configure connection parameters and establish connection.
        
        Args:
            db_name: Database name
            collection_name: Collection name
            uri: MongoDB URI
        """
        self.uri = uri
        self.db_name = db_name
        self.collection_name = collection_name
        self._connect()


class LoadDb:
    """Handles data migration from DataFrame to MongoDB."""
    
    def __init__(self, db: Connect, df=None):
        """
        Initialize database loader.
        
        Args:
            db: MongoDB connection object
            df: DataFrame to migrate
        """
        self.collection = db.collection
        self.collection_name = db.collection_name
        self.df = df

    def transform_row_to_mongodb(self, row):
        """
        Convert CSV row to structured MongoDB document.
        
        Args:
            row: DataFrame row
            
        Returns:
            dict: Structured MongoDB document
        """
        document = {
            "patient_info": {
                "name": row['Name'],
                "age": int(row['Age']),
                "gender": row['Gender'],
                "blood_type": row['Blood Type']
            },
            
            "medical_details": {
                "medical_condition": row['Medical Condition'],
                "medication": row['Medication'],
                "test_results": row['Test Results']
            },
            
            "admission_details": {
                "admission_date": row['Admission Date'],
                "admission_type": row['Admission Type'],
                "room_number": int(row['Room Number']),
                "discharge_date": row['Discharge Date']
            },
            
            "hospital_info": {
                "hospital": row['Hospital'],
                "doctor": row['Doctor']
            },
            
            "billing": {
                "insurance_provider": row['Insurance Provider'],
                "billing_amount": float(round(row['Billing Amount'], 2))
            },
            
            "metadata": {
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "data_source": "CSV_migration",
                "migrated_by": "Hope - DataSoluTech"
            }
        }
        
        return document

    def dbloader(self):
        """Load DataFrame into MongoDB collection with bulk insertion."""
        
        try:
            deleted_count = self.collection.delete_many({})
            print(f"Collection '{self.collection_name}' reset: {deleted_count.deleted_count} documents removed")
        except Exception as e:
            print(f"ERROR: Collection reset failed - {e}")
            raise

        print('-' * 80)
        print('INSERTING DATA INTO MONGODB')
        print('-' * 80)
        
        try:
            documents = []
            total_rows = len(self.df)
            
            print(f"Transforming {total_rows:,} records...")
            
            for idx, row in self.df.iterrows():
                doc = self.transform_row_to_mongodb(row)
                documents.append(doc)
                
                if (idx + 1) % 5000 == 0:
                    print(f"  Progress: {idx + 1:,}/{total_rows:,} records")
            
            print(f"Inserting {len(documents):,} documents...")
            result = self.collection.insert_many(documents, ordered=False)
            
            print(f"Successfully inserted {len(result.inserted_ids):,} documents")
            
        except Exception as e:
            logger.error(f"Data insertion failed: {e}", exc_info=True)
            print(f"ERROR: Data insertion failed - {e}")
            raise
        
        try:
            self.create_indexes()
            print("Indexes created successfully")
        except Exception as e:
            logger.error(f"Index creation failed: {e}")
            print(f"WARNING: Index creation failed - {e}")
        
        inserted_count = self.collection.count_documents({})
        expected_count = len(self.df)
        
        if inserted_count != expected_count:
            error_msg = f"Document count mismatch! Expected: {expected_count:,}, Got: {inserted_count:,}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        print('-' * 80)
        print(f"Total documents inserted: {inserted_count:,}")
        print("DONE")
        print('-' * 80)

    def create_indexes(self):
        """Create indexes for optimized query performance."""
        print("\n[CREATING INDEXES]")
        
        self.collection.create_index("patient_info.name")
        print("- Created index on patient_info.name")
        
        self.collection.create_index("admission_details.admission_date")
        print("- Created index on admission_details.admission_date")
        
        self.collection.create_index([
            ("medical_details.medical_condition", 1),
            ("hospital_info.hospital", 1)
        ])
        print("- Created compound index on medical_condition + hospital")
        
        print("[INDEXES CREATED]\n")
        return self

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass