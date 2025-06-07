"""
Script to create a comprehensive backup of the sentiment analysis project.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import tarfile
import logging

class ProjectBackup:
    def __init__(self):
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Setup paths
        self.project_root = Path(__file__).parent.parent
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_dir = self.project_root / 'backup' / f'sentiment_analysis_{self.timestamp}'

    def create_directory_structure(self):
        """Create backup directory structure"""
        try:
            # Create main backup directory
            os.makedirs(self.backup_dir)
            os.makedirs(self.backup_dir / 'scripts')
            os.makedirs(self.backup_dir / 'results')
            os.makedirs(self.backup_dir / 'utils' / 'config')
            self.logger.info(f"Created directory structure at {self.backup_dir}")
        except Exception as e:
            self.logger.error(f"Error creating directory structure: {e}")
            raise

    def copy_scripts(self):
        """Copy all script files"""
        script_files = [
            'a_sentiment_analysis.py',
            'b_custom_forecast.py',
            'c_external_forecast.py',
            'd_master_output.py',
            'e_open_html.py',
            'cleanup_project.py'
        ]
        
        for script in script_files:
            try:
                src = self.project_root / 'scripts' / script
                dst = self.backup_dir / 'scripts' / script
                if src.exists():
                    shutil.copy2(src, dst)
                    self.logger.info(f"Copied {script}")
                else:
                    self.logger.warning(f"Script not found: {script}")
            except Exception as e:
                self.logger.error(f"Error copying {script}: {e}")

    def copy_results(self):
        """Copy results and archives"""
        try:
            results_dir = self.project_root / 'results'
            
            # Core result files
            core_files = [
                'a1_sentiment_detailed.csv',
                'a2_sentiment_summary.csv',
                'd_master_output.csv',
                'sentiment_report.html'
            ]
            
            for file in core_files:
                src = results_dir / file
                if src.exists():
                    shutil.copy2(src, self.backup_dir / 'results' / file)
                    self.logger.info(f"Copied {file}")
                else:
                    self.logger.warning(f"Result file not found: {file}")
            
            # Copy archived sentiment files
            for archive in results_dir.glob('a2_sentiment_summary_*.csv'):
                shutil.copy2(archive, self.backup_dir / 'results' / archive.name)
                self.logger.info(f"Copied archive: {archive.name}")
                
        except Exception as e:
            self.logger.error(f"Error copying results: {e}")

    def copy_config(self):
        """Copy configuration files"""
        try:
            config_files = [
                'api_providers_config.py',
                'ticker_config.py'
            ]
            
            for config in config_files:
                src = self.project_root / 'utils' / 'config' / config
                dst = self.backup_dir / 'utils' / 'config' / config
                if src.exists():
                    shutil.copy2(src, dst)
                    self.logger.info(f"Copied {config}")
                else:
                    self.logger.warning(f"Config file not found: {config}")
        except Exception as e:
            self.logger.error(f"Error copying config files: {e}")

    def copy_root_files(self):
        """Copy files from project root"""
        try:
            root_files = [
                'master_runner.py',
                'README.md',
                'requirements.txt'
            ]
            
            for file in root_files:
                src = self.project_root / file
                if src.exists():
                    shutil.copy2(src, self.backup_dir / file)
                    self.logger.info(f"Copied {file}")
                else:
                    self.logger.warning(f"Root file not found: {file}")
        except Exception as e:
            self.logger.error(f"Error copying root files: {e}")

    def create_archive(self):
        """Create compressed archive of backup"""
        try:
            archive_path = f"{self.backup_dir}.tar.gz"
            with tarfile.open(archive_path, "w:gz") as tar:
                tar.add(self.backup_dir, arcname=self.backup_dir.name)
            self.logger.info(f"Created archive: {archive_path}")
        except Exception as e:
            self.logger.error(f"Error creating archive: {e}")

    def run_backup(self):
        """Execute complete backup process"""
        try:
            self.logger.info("Starting project backup...")
            self.create_directory_structure()
            self.copy_scripts()
            self.copy_results()
            self.copy_config()
            self.copy_root_files()
            self.create_archive()
            self.logger.info("Backup completed successfully!")
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            raise

def main():
    backup = ProjectBackup()
    backup.run_backup()

if __name__ == "__main__":
    main() 