"""
Data Integrity Tests for Healthcare MongoDB Migration

Validates data integrity after CSV-to-MongoDB migration using pytest.

Usage:
    pytest tests/test_migration.py
    pytest tests/test_migration.py::TestDataIntegrity::test_document_count -v
    python -m csv_containerisation_mongodb.tests.test_migration

Author: Hope Donglo - OpenClassrooms (DataSoluTech)
"""

import pandas as pd
import pytest
from pymongo import MongoClient
import os
from pathlib import Path


class DataIntegrityChecker:
    """
    Validates data integrity after migration to MongoDB.
    
    Performs comprehensive checks: document count, field structure,
    data types, missing values, and duplicates.
    """
        
    def __init__(self, db_name, collection_name, df, uri=None):
        """
        Initialize checker with MongoDB connection parameters.
        
        Args:
            db_name: Database name
            collection_name: Collection name
            df: DataFrame to compare against
            uri: MongoDB URI (defaults to localhost)
        """
        self.uri = uri or os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        self.db_name = db_name
        self.collection_name = collection_name
        self.df = df
        self._connect()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        return False
    
    def _connect(self):
        """Establish MongoDB connection."""
        try:
            client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            self.db = client[self.db_name]
            self.collection = self.db[self.collection_name]
            print(f"[INFO] Connected to {self.db_name}.{self.collection_name}")
        except Exception as e:
            pytest.skip(f"MongoDB not available: {e}")

    def test_document_count(self):
        """Verify document count matches DataFrame row count."""
        total_docs = self.collection.count_documents({})
        expected_docs = len(self.df)
        
        assert total_docs == expected_docs, \
            f"Document count mismatch: Expected {expected_docs}, Found {total_docs}"
        
        print(f"[PASS] Document count: {total_docs} matches expected: {expected_docs}")

    def test_field_structure(self):
        """Verify all CSV columns exist in MongoDB documents."""
        print("=" * 70)
        print("FIELD STRUCTURE VALIDATION")
        print("=" * 70)
        
        doc = self.collection.find_one()
        assert doc is not None, "No documents found in collection"
        
        doc_structure = []
        for keys, values in doc.items():
            if keys in ['_id', 'metadata']:
                continue
            
            assert isinstance(values, dict), f"Expected nested dict for {keys}"
            
            for sub_key, sub_value in values.items():
                sub_key_formatted = sub_key.title().replace('_', ' ')
                doc_structure.append(sub_key_formatted)

        check_tab = pd.DataFrame({
            "MongoDB Field": pd.Series(doc_structure),
            "Expected (CSV)": pd.Series(self.df.columns.tolist())
        })
        
        print(check_tab.to_string())
        
        assert set(self.df.columns) == set(doc_structure), \
            f"Field mismatch: CSV has {set(self.df.columns) - set(doc_structure)}, " \
            f"MongoDB has {set(doc_structure) - set(self.df.columns)}"
        
        print('-' * 70)
        print("[PASS] Field structure validation passed")

    def test_missing_values(self):
        """Verify missing values match between CSV and MongoDB."""
        print("=" * 70)
        print("MISSING VALUES VALIDATION")
        print("=" * 70)

        fields_names = []
        for doc in self.collection.find({}).limit(1):
            for key, value in doc.items():
                if key not in ['_id', 'metadata']:
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            fields_names.append(f"{key}.{sub_key}")
                    else:
                        fields_names.append(key)
        
        total_docs = self.collection.count_documents({})
        assert total_docs > 0, "No documents in collection"

        missing_values = {}
        for field in fields_names:
            count_missing_docs = self.collection.count_documents({
                "$or": [
                    {field: None},
                    {field: {"$exists": False}}
                ]
            })
            missing_values[field] = count_missing_docs / total_docs * 100

        df_missing_mongo = pd.DataFrame.from_dict(
            missing_values, 
            orient='index', 
            columns=['MongoDB Missing (%)']
        )

        df_missing_csv = pd.DataFrame(
            self.df.isna().mean() * 100,
            columns=['CSV Missing (%)']
        )

        comparison = df_missing_mongo.join(df_missing_csv, how='outer').fillna(0)
        comparison['Match'] = abs(comparison['MongoDB Missing (%)'] - comparison['CSV Missing (%)']) < 0.01

        print(comparison.to_string())
        print("\n" + "=" * 70)
        print(f"Fields with matching missing values: {comparison['Match'].sum()}/{len(comparison)}")
        
        assert comparison['Match'].all(), \
            f"Missing values mismatch:\n{comparison[~comparison['Match']]}"
        
        print("[PASS] Missing values validation passed")
        print("=" * 70)

    def test_data_types(self):
        """Verify data types are correct in MongoDB."""
        doc = self.collection.find_one()
        assert doc is not None, "No documents found"
        
        datatype = {}
        for keys, values in doc.items():
            if keys in ['_id', 'metadata']:
                continue

            assert isinstance(values, dict), f"Expected dict for {keys}"
            
            for sub_key, sub_value in values.items():
                datatype[sub_key] = type(sub_value).__name__

        type_mapping = {
            'str': 'object',
            'int': 'int64',
            'float': 'float64',
            'bool': 'bool',
            'datetime': 'datetime64[ns]'
        }

        print("=" * 90)
        print("DATA TYPE VALIDATION")
        print("=" * 90)
        print(f"{'Field':<25} {'MongoDB Type':<15} {'Expected Type':<15}")
        print("-" * 90)

        all_match = True
        for field, mongo_type in datatype.items():
            expected_df_type = type_mapping.get(mongo_type, 'unknown')
            print(f"{field:<25} {mongo_type:<15} {expected_df_type:<15}")

        print("=" * 90)
        
        assert all_match, "Data type validation failed"
        
        print("[PASS] Data types validation passed")
        print("=" * 90)

    def test_duplicates(self):
        """Verify duplicate count matches between CSV and MongoDB."""
        print("\n" + "=" * 70)
        print("DUPLICATE VALIDATION")
        print("=" * 70)
        
        csv_total = len(self.df)
        csv_dup_count = self.df.duplicated().sum()
        
        pipeline = [
            {
                "$project": {
                    "_id": 0,
                    "metadata": 0
                }
            },
            {
                "$group": {
                    "_id": "$$ROOT",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        all_groups = list(self.collection.aggregate(pipeline))
        mongo_unique = len(all_groups)
        mongo_total = sum(g['count'] for g in all_groups)
        mongo_dup_count = mongo_total - mongo_unique
        
        print(f"\nDuplicate Count Comparison:")
        print(f"  CSV: {csv_dup_count}/{csv_total}")
        print(f"  MongoDB: {mongo_dup_count}/{mongo_total}")
        
        assert csv_dup_count == mongo_dup_count, \
            f"Duplicate count mismatch: CSV has {csv_dup_count}, MongoDB has {mongo_dup_count}"
        
        print(f"  [PASS] Status: MATCH")
        
        if mongo_dup_count > 0:
            duplicates = [g for g in all_groups if g['count'] > 1]
            print(f"\n  MongoDB has {len(duplicates)} sets of duplicates:")
            for dup in duplicates[:3]:
                print(f"    Count: {dup['count']}")
        
        print("=" * 70)


class TestDataIntegrity:
    """Pytest test class for data integrity validation."""
    
    @pytest.fixture(scope="class")
    def test_data(self):
        """Load test data from CSV."""
        data_path = 'data/processed/cleaned_healthcare.csv'
        df = pd.read_csv(data_path)
        return df
    
    @pytest.fixture(scope="class")
    def integrity_checker(self, test_data):
        """Provide configured DataIntegrityChecker instance."""
        checker = DataIntegrityChecker(
            db_name='medical_records',
            collection_name='healthcare_data',
            df=test_data,
            uri=os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        )
        return checker
    
    def test_document_count_matches(self, integrity_checker):
        """Test that document count matches CSV row count."""
        integrity_checker.test_document_count()
    
    def test_all_fields_present(self, integrity_checker):
        """Test that all CSV fields are present in MongoDB."""
        integrity_checker.test_field_structure()
    
    def test_missing_values_preserved(self, integrity_checker):
        """Test that missing values are correctly preserved."""
        integrity_checker.test_missing_values()
    
    def test_data_types_correct(self, integrity_checker):
        """Test that data types are correct in MongoDB."""
        integrity_checker.test_data_types()
    
    def test_duplicate_count_matches(self, integrity_checker):
        """Test that duplicate count matches between CSV and MongoDB."""
        integrity_checker.test_duplicates()


def run_all_integrity_checks(db_name='medical_records', 
                            collection_name='healthcare_data', 
                            df=None,
                            uri=None):
    """
    Run all integrity checks outside of pytest.
    
    Args:
        db_name: MongoDB database name
        collection_name: MongoDB collection name
        df: DataFrame to validate against
        uri: MongoDB connection URI
    
    Returns:
        bool: True if all checks passed, False otherwise
    """
    if df is None:
        raise ValueError("DataFrame is required")
    
    print("\n" + "=" * 70)
    print("RUNNING ALL DATA INTEGRITY CHECKS")
    print("=" * 70 + "\n")
    
    try:
        checker = DataIntegrityChecker(
            db_name=db_name,
            collection_name=collection_name,
            df=df,
            uri=uri
        )
        
        checker.test_document_count()
        checker.test_field_structure()
        checker.test_missing_values()
        checker.test_data_types()
        checker.test_duplicates()
        
        print("\n" + "=" * 70)
        print("[PASS] ALL INTEGRITY CHECKS PASSED")
        print("=" * 70 + "\n")
        return True
        
    except AssertionError as e:
        print("\n" + "=" * 70)
        print(f"[FAIL] INTEGRITY CHECK FAILED: {e}")
        print("=" * 70 + "\n")
        return False
    except Exception as e:
        print("\n" + "=" * 70)
        print(f"[ERROR] Unexpected error: {e}")
        print("=" * 70 + "\n")
        return False


if __name__ == '__main__':
    """Quick run for manual testing."""
    data_path = Path('data/processed/cleaned_healthcare.csv')
    if data_path.exists():
        df = pd.read_csv(data_path)
        success = run_all_integrity_checks(df=df)
        exit(0 if success else 1)
    else:
        print(f"[FAIL] Data file not found: {data_path}")
        exit(1)