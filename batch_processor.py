"""
Comprehensive Batch Processing Module for CSV and JSON Feeds

This module provides functionality for processing, validating, and transforming
batch data from CSV and JSON feed sources with error handling, logging, and
performance optimization.

Author: deepakgargct
Date: 2026-01-06
"""

import csv
import json
import logging
import os
import sys
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import io
from collections import defaultdict


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('batch_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FeedFormat(Enum):
    """Supported feed formats"""
    CSV = "csv"
    JSON = "json"


class ProcessingStatus(Enum):
    """Processing status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass
class ProcessingResult:
    """Data class for batch processing results"""
    status: ProcessingStatus
    total_records: int
    successful_records: int
    failed_records: int
    skipped_records: int
    processing_time: float
    errors: List[Dict[str, Any]]
    warnings: List[str]
    file_hash: Optional[str] = None
    output_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        result = asdict(self)
        result['status'] = self.status.value
        return result

    def to_json(self) -> str:
        """Convert result to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class BatchConfig:
    """Configuration for batch processing"""
    batch_size: int = 1000
    max_retries: int = 3
    timeout: int = 300
    validate_data: bool = True
    skip_on_error: bool = True
    output_format: str = "json"
    verbose: bool = False
    deduplicate: bool = True


class FeedValidator(ABC):
    """Abstract base class for feed validators"""

    @abstractmethod
    def validate(self, record: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate a single record
        
        Args:
            record: Data record to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        pass

    @abstractmethod
    def validate_schema(self, headers: List[str]) -> Tuple[bool, Optional[str]]:
        """
        Validate feed schema/headers
        
        Args:
            headers: List of field names
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        pass


class DefaultValidator(FeedValidator):
    """Default validator implementation"""

    def __init__(self, required_fields: Optional[List[str]] = None):
        """
        Initialize validator
        
        Args:
            required_fields: List of required field names
        """
        self.required_fields = required_fields or []

    def validate(self, record: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate record has required fields"""
        for field in self.required_fields:
            if field not in record or record[field] is None:
                return False, f"Missing required field: {field}"
        return True, None

    def validate_schema(self, headers: List[str]) -> Tuple[bool, Optional[str]]:
        """Validate all required fields exist in headers"""
        missing = set(self.required_fields) - set(headers)
        if missing:
            return False, f"Missing required columns: {', '.join(missing)}"
        return True, None


class CSVBatchProcessor:
    """Processor for CSV feed files"""

    def __init__(self, config: Optional[BatchConfig] = None,
                 validator: Optional[FeedValidator] = None):
        """
        Initialize CSV processor
        
        Args:
            config: Batch configuration
            validator: Data validator
        """
        self.config = config or BatchConfig()
        self.validator = validator or DefaultValidator()
        self.logger = logger

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def process_file(self, file_path: str,
                     output_path: Optional[str] = None) -> ProcessingResult:
        """
        Process CSV file with validation and transformation
        
        Args:
            file_path: Path to CSV file
            output_path: Optional path for output file
            
        Returns:
            ProcessingResult with processing statistics
        """
        start_time = datetime.now()
        result = ProcessingResult(
            status=ProcessingStatus.IN_PROGRESS,
            total_records=0,
            successful_records=0,
            failed_records=0,
            skipped_records=0,
            processing_time=0.0,
            errors=[],
            warnings=[]
        )

        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            result.file_hash = self._calculate_file_hash(file_path)
            self.logger.info(f"Processing CSV file: {file_path}")

            processed_records = []
            seen_records = set() if self.config.deduplicate else None

            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                # Validate schema
                if reader.fieldnames is None:
                    raise ValueError("CSV file has no headers")

                schema_valid, schema_error = self.validator.validate_schema(
                    reader.fieldnames
                )
                if not schema_valid and not self.config.skip_on_error:
                    raise ValueError(f"Schema validation failed: {schema_error}")
                if not schema_valid:
                    result.warnings.append(schema_error)

                # Process records
                for row_num, record in enumerate(reader, start=2):
                    result.total_records += 1

                    # Validate record
                    if self.config.validate_data:
                        is_valid, error_msg = self.validator.validate(record)
                        if not is_valid:
                            result.failed_records += 1
                            error_detail = {
                                "row": row_num,
                                "error": error_msg,
                                "record": record
                            }
                            result.errors.append(error_detail)
                            if not self.config.skip_on_error:
                                raise ValueError(f"Validation failed at row {row_num}: {error_msg}")
                            self.logger.warning(f"Row {row_num} validation failed: {error_msg}")
                            continue

                    # Check for duplicates
                    if self.config.deduplicate:
                        record_hash = hashlib.md5(
                            json.dumps(record, sort_keys=True).encode()
                        ).hexdigest()
                        if record_hash in seen_records:
                            result.skipped_records += 1
                            self.logger.debug(f"Duplicate record at row {row_num}")
                            continue
                        seen_records.add(record_hash)

                    processed_records.append(record)
                    result.successful_records += 1

                    # Batch processing
                    if len(processed_records) >= self.config.batch_size:
                        processed_records = self._process_batch(processed_records)

            # Process remaining records
            if processed_records:
                self._process_batch(processed_records)

            # Save output if requested
            if output_path:
                self._save_output(processed_records, output_path)
                result.output_path = output_path

            result.status = ProcessingStatus.COMPLETED if result.failed_records == 0 else ProcessingStatus.PARTIAL

        except Exception as e:
            result.status = ProcessingStatus.FAILED
            result.errors.append({
                "type": type(e).__name__,
                "message": str(e)
            })
            self.logger.error(f"Error processing CSV file: {str(e)}", exc_info=True)

        finally:
            result.processing_time = (datetime.now() - start_time).total_seconds()
            self.logger.info(f"Processing completed. Results: {result.to_dict()}")

        return result

    def _process_batch(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process a batch of records
        
        Args:
            batch: List of records to process
            
        Returns:
            Processed records
        """
        # Placeholder for batch processing logic
        if self.config.verbose:
            self.logger.info(f"Processing batch of {len(batch)} records")
        return batch

    def _save_output(self, records: List[Dict[str, Any]], output_path: str):
        """
        Save processed records to output file
        
        Args:
            records: Records to save
            output_path: Path for output file
        """
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        if self.config.output_format == "json":
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(records, f, indent=2, ensure_ascii=False)
        else:
            if not records:
                return
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=records[0].keys())
                writer.writeheader()
                writer.writerows(records)

        self.logger.info(f"Output saved to: {output_path}")

    def stream_process(self, file_path: str) -> Generator[Dict[str, Any], None, None]:
        """
        Process CSV file in streaming mode
        
        Args:
            file_path: Path to CSV file
            
        Yields:
            Individual validated records
        """
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for record in reader:
                if self.config.validate_data:
                    is_valid, _ = self.validator.validate(record)
                    if not is_valid:
                        continue
                yield record


class JSONBatchProcessor:
    """Processor for JSON feed files"""

    def __init__(self, config: Optional[BatchConfig] = None,
                 validator: Optional[FeedValidator] = None):
        """
        Initialize JSON processor
        
        Args:
            config: Batch configuration
            validator: Data validator
        """
        self.config = config or BatchConfig()
        self.validator = validator or DefaultValidator()
        self.logger = logger

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def process_file(self, file_path: str,
                     output_path: Optional[str] = None) -> ProcessingResult:
        """
        Process JSON file with validation and transformation
        
        Args:
            file_path: Path to JSON file
            output_path: Optional path for output file
            
        Returns:
            ProcessingResult with processing statistics
        """
        start_time = datetime.now()
        result = ProcessingResult(
            status=ProcessingStatus.IN_PROGRESS,
            total_records=0,
            successful_records=0,
            failed_records=0,
            skipped_records=0,
            processing_time=0.0,
            errors=[],
            warnings=[]
        )

        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            result.file_hash = self._calculate_file_hash(file_path)
            self.logger.info(f"Processing JSON file: {file_path}")

            with open(file_path, 'r', encoding='utf-8') as jsonfile:
                data = json.load(jsonfile)

            # Handle both list and single object
            records = data if isinstance(data, list) else [data]
            processed_records = []
            seen_records = set() if self.config.deduplicate else None

            for idx, record in enumerate(records):
                result.total_records += 1

                if not isinstance(record, dict):
                    result.failed_records += 1
                    error_detail = {
                        "index": idx,
                        "error": "Record is not a dictionary",
                        "type": type(record).__name__
                    }
                    result.errors.append(error_detail)
                    if not self.config.skip_on_error:
                        raise ValueError(f"Invalid record type at index {idx}")
                    continue

                # Validate record
                if self.config.validate_data:
                    is_valid, error_msg = self.validator.validate(record)
                    if not is_valid:
                        result.failed_records += 1
                        error_detail = {
                            "index": idx,
                            "error": error_msg,
                            "record": record
                        }
                        result.errors.append(error_detail)
                        if not self.config.skip_on_error:
                            raise ValueError(f"Validation failed at index {idx}: {error_msg}")
                        self.logger.warning(f"Record {idx} validation failed: {error_msg}")
                        continue

                # Check for duplicates
                if self.config.deduplicate:
                    record_hash = hashlib.md5(
                        json.dumps(record, sort_keys=True).encode()
                    ).hexdigest()
                    if record_hash in seen_records:
                        result.skipped_records += 1
                        self.logger.debug(f"Duplicate record at index {idx}")
                        continue
                    seen_records.add(record_hash)

                processed_records.append(record)
                result.successful_records += 1

                # Batch processing
                if len(processed_records) >= self.config.batch_size:
                    processed_records = self._process_batch(processed_records)

            # Process remaining records
            if processed_records:
                self._process_batch(processed_records)

            # Save output if requested
            if output_path:
                self._save_output(processed_records, output_path)
                result.output_path = output_path

            result.status = ProcessingStatus.COMPLETED if result.failed_records == 0 else ProcessingStatus.PARTIAL

        except json.JSONDecodeError as e:
            result.status = ProcessingStatus.FAILED
            result.errors.append({
                "type": "JSONDecodeError",
                "message": f"Invalid JSON format: {str(e)}"
            })
            self.logger.error(f"JSON parsing error: {str(e)}")

        except Exception as e:
            result.status = ProcessingStatus.FAILED
            result.errors.append({
                "type": type(e).__name__,
                "message": str(e)
            })
            self.logger.error(f"Error processing JSON file: {str(e)}", exc_info=True)

        finally:
            result.processing_time = (datetime.now() - start_time).total_seconds()
            self.logger.info(f"Processing completed. Results: {result.to_dict()}")

        return result

    def _process_batch(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process a batch of records
        
        Args:
            batch: List of records to process
            
        Returns:
            Processed records
        """
        if self.config.verbose:
            self.logger.info(f"Processing batch of {len(batch)} records")
        return batch

    def _save_output(self, records: List[Dict[str, Any]], output_path: str):
        """
        Save processed records to output file
        
        Args:
            records: Records to save
            output_path: Path for output file
        """
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Output saved to: {output_path}")

    def stream_process(self, file_path: str) -> Generator[Dict[str, Any], None, None]:
        """
        Process JSON file in streaming mode (for line-delimited JSON)
        
        Args:
            file_path: Path to JSONL file
            
        Yields:
            Individual validated records
        """
        with open(file_path, 'r', encoding='utf-8') as jsonfile:
            for line in jsonfile:
                if line.strip():
                    try:
                        record = json.loads(line)
                        if self.config.validate_data:
                            is_valid, _ = self.validator.validate(record)
                            if not is_valid:
                                continue
                        yield record
                    except json.JSONDecodeError:
                        self.logger.warning(f"Skipping invalid JSON line: {line[:100]}")
                        continue


class BatchProcessorFactory:
    """Factory for creating appropriate batch processors"""

    _processors = {
        FeedFormat.CSV: CSVBatchProcessor,
        FeedFormat.JSON: JSONBatchProcessor
    }

    @classmethod
    def create_processor(cls, file_format: Union[FeedFormat, str],
                        config: Optional[BatchConfig] = None,
                        validator: Optional[FeedValidator] = None):
        """
        Create a processor for the specified format
        
        Args:
            file_format: Feed format (CSV or JSON)
            config: Batch configuration
            validator: Data validator
            
        Returns:
            Appropriate processor instance
            
        Raises:
            ValueError: If format is not supported
        """
        if isinstance(file_format, str):
            try:
                file_format = FeedFormat(file_format.lower())
            except ValueError:
                raise ValueError(f"Unsupported format: {file_format}")

        if file_format not in cls._processors:
            raise ValueError(f"No processor for format: {file_format}")

        processor_class = cls._processors[file_format]
        return processor_class(config=config, validator=validator)


class BatchProcessingManager:
    """High-level manager for batch processing operations"""

    def __init__(self, config: Optional[BatchConfig] = None):
        """
        Initialize manager
        
        Args:
            config: Batch configuration
        """
        self.config = config or BatchConfig()
        self.logger = logger
        self.processing_history: List[Dict[str, Any]] = []

    def process(self, file_path: str,
                file_format: Union[FeedFormat, str],
                output_path: Optional[str] = None,
                validator: Optional[FeedValidator] = None) -> ProcessingResult:
        """
        Process a feed file
        
        Args:
            file_path: Path to feed file
            file_format: Feed format
            output_path: Optional output path
            validator: Optional custom validator
            
        Returns:
            ProcessingResult with statistics
        """
        processor = BatchProcessorFactory.create_processor(
            file_format,
            config=self.config,
            validator=validator
        )

        result = processor.process_file(file_path, output_path)
        
        # Record in history
        self.processing_history.append({
            "timestamp": datetime.now().isoformat(),
            "file": file_path,
            "format": file_format if isinstance(file_format, str) else file_format.value,
            "result": result.to_dict()
        })

        return result

    def get_processing_history(self) -> List[Dict[str, Any]]:
        """Get processing history"""
        return self.processing_history

    def export_history(self, output_path: str):
        """
        Export processing history to file
        
        Args:
            output_path: Path for history file
        """
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.processing_history, f, indent=2)

        self.logger.info(f"History exported to: {output_path}")


def main():
    """Example usage and testing"""
    # Configure batch processing
    config = BatchConfig(
        batch_size=500,
        validate_data=True,
        skip_on_error=True,
        verbose=True
    )

    # Create manager
    manager = BatchProcessingManager(config=config)

    # Example: Process a CSV file
    csv_file = "sample_products.csv"
    if os.path.exists(csv_file):
        result = manager.process(
            csv_file,
            FeedFormat.CSV,
            output_path="output/processed_products.json"
        )
        print(f"CSV Processing Result:\n{result.to_json()}")

    # Example: Process a JSON file
    json_file = "sample_products.json"
    if os.path.exists(json_file):
        result = manager.process(
            json_file,
            FeedFormat.JSON,
            output_path="output/processed_products.json"
        )
        print(f"JSON Processing Result:\n{result.to_json()}")

    # Export history
    manager.export_history("processing_history.json")


if __name__ == "__main__":
    main()
