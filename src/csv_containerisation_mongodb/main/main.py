"""
Healthcare Data Processing Pipeline - Main Entry Point

Initializes and executes the complete ETL pipeline.

Usage:
    python -m csv_containerisation_mongodb.main.main

Author: Hope Donglo - OpenClassrooms (DataSoluTech)
"""

import sys
import traceback
from csv_containerisation_mongodb.main.pipeline import HealthcarePipeline, PipelineConfig


def main() -> int:
    """
    Execute the healthcare data processing pipeline.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    try:
        config = PipelineConfig()
        pipeline = HealthcarePipeline(config=config)
        
        success = pipeline.run()
        
        if success:
            print("Pipeline execution completed successfully")
            return 0
        else:
            print("Pipeline execution failed")
            return 1
        
    except KeyboardInterrupt:
        print("\nPipeline interrupted by user")
        return 1
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())