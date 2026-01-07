"""
Output Management Module for Data Processing Pipelines
This module provides classes for managing output files and paths
for data processing workflows.
"""

from pathlib import Path
from datetime import datetime
import os


class FILE_PATH_MANAGER:
    def __init__(self):
        """Works with your Docker setup automatically"""
        # In Docker: WORKDIR=/app makes this resolve to /app
        # Locally: resolves to your project root
        self.project_root = self._find_project_root()
        self.data_dir = self.project_root / 'data'
        self.raw_data_dir = self.data_dir / 'raw'
        self.processed_data_dir = self.data_dir / 'processed'
        self.output_dir = self.project_root / 'outputs'
        
        # Automatically ensure directories exist
        self.ensure_directories()


    
    def _find_project_root(self):
        """Detect project root - works locally and in Docker"""
        # Check for explicit environment variable
        if os.getenv('PROJECT_ROOT'):
            return Path(os.getenv('PROJECT_ROOT'))
        
        current = Path(__file__).resolve()
        
        # Look for project markers (pyproject.toml exists!)
        for parent in [current] + list(current.parents):
            if (parent / 'pyproject.toml').exists():
                return parent
        
        # Fallback: 3 levels up
        return current.parent.parent.parent


    
    def ensure_directories(self):
        """Create directories if missing"""
        for directory in [self.raw_data_dir, self.processed_data_dir, self.output_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        return self
    

    
    def __repr__(self):return f"FILE_MANAGEMENT(project_root='{self.project_root}')"
    



class OUTPUT_MANAGER:
    """
    Manages output files and paths for data processing.
    
    This class handles:
    - Creating output directories
    - Managing file paths for cleaned data and reports
    
    Attributes:
        output_dir (Path): Directory where all outputs are saved
        file_name (str): Base name for output files
        report_file (Path): Path to markdown report file
        cleaned_csv_file (Path): Path to cleaned CSV file
        timestamp (str): Timestamp used for file naming (if enabled)
    """
    
    def __init__(self, output_dir, file_name='unnamed', report_title='Data Processing Report', use_timestamp=False):
        """
        Initialize OUTPUT_MANAGER.
        
        Args:
            output_dir (Path or str): Directory where outputs should be saved
            file_name (str): Base name for output files
            report_title (str): Title for the markdown report
            use_timestamp (bool): Whether to add timestamps to filenames (default: False)
        """
        self.output_dir = Path(output_dir)
        self.file_name = file_name
        self.report_title = report_title
        self.use_timestamp = use_timestamp
        
        # Generate timestamp if enabled
        if self.use_timestamp:
            self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            timestamp_suffix = f"_{self.timestamp}"
        else:
            self.timestamp = None
            timestamp_suffix = ""
        
        # File paths with or without timestamps
        self.report_file = self.output_dir / f"cleaning_report_{self.file_name}{timestamp_suffix}.md"
        self.cleaned_csv_file = self.output_dir / f"cleaned_{self.file_name}{timestamp_suffix}.csv"
        self.quality_csv_file = self.output_dir / f"quality_report_{self.file_name}{timestamp_suffix}.csv"
        
        # Create output directory
        self._create_output_directory()




    
    def _create_output_directory(self):
        """Create the output directory if it doesn't exist."""
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            print(f"Output directory created/confirmed: {self.output_dir.absolute()}")
        except Exception as e:
            print(f"Error creating output directory: {e}")
            raise



    
    def write_to_report(self, message):
        """
        Write a message directly to the report file.
        
        Args:
            message (str): Message to write to report
        """
        try:
            with open(self.report_file, 'a', encoding='utf-8') as f:
                f.write(message + "\n")
        except Exception as e:
            print(f"Error writing to report: {e}")



    
    def finalize_report(self, final_stats=None):
        """
        Finalize the report with summary information.
        
        Args:
            final_stats (dict, optional): Dictionary of final statistics to include
        """
        print("\n" + "=" * 80)
        print(f"Output directory: {self.output_dir.absolute()}")
        
        # List all files in output directory
        print("\nFiles in output directory:")
        for file in sorted(self.output_dir.glob('*')):
            if file.is_file():
                size = file.stat().st_size / 1024  # KB
                print(f"  - {file.name} ({size:.2f} KB)")
        print("=" * 80 + "\n")



    
    def get_output_path(self, file_type='cleaned_csv'):
        """
        Get the output path for a specific file type.
        
        Args:
            file_type (str): Type of file ('cleaned_csv', 'quality_csv', 'report')
        
        Returns:
            Path: Path to the requested file
        """
        if file_type == 'cleaned_csv':
            return self.cleaned_csv_file
        elif file_type == 'quality_csv':
            return self.quality_csv_file
        else:
            raise ValueError(f"Unknown file type: {file_type}")
        


    # CONTEXT MANAGER 
    def __enter__(self):return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            print(f"\n[ERROR] Cleaning failed: {exc_val}")
            import traceback
            traceback.print_exception(exc_type, exc_val, exc_tb)
        return False