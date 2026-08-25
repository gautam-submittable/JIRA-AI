import csv
import os
from datetime import datetime, timedelta
from typing import List, Tuple


class ImportResult:
    def __init__(self, job_name: str, success: bool, errors: List[dict] = None):
        self.job_name = job_name
        self.success = success
        self.errors = errors or []

    def __repr__(self):
        return f"ImportResult(job_name={self.job_name}, success={self.success}, errors={len(self.errors)})"


def read_csv_file(file_path: str) -> Tuple[List[dict], List[str]]:
    """Reads a CSV file and returns rows and column headers."""
    with open(file_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        headers = reader.fieldnames or []
    return rows, headers


def validate_row(row: dict) -> str:
    """Validates a single PO row. Returns error message if invalid, empty string if valid."""
    if not row.get('po_number'):
        return 'Missing po_number'
    if not row.get('vendor_id'):
        return 'Missing vendor_id'
    if not row.get('amount'):
        return 'Missing amount'
    try:
        amount = float(row['amount'])
        if amount < 0:
            return 'Negative amount not allowed'
    except ValueError:
        return 'Invalid amount format'
    if not row.get('date'):
        return 'Missing date'
    return ''


def process_po_file(file_path: str) -> ImportResult:
    """Processes a single PO CSV file. Returns ImportResult with errors if any."""
    job_name = os.path.splitext(os.path.basename(file_path))[0]
    errors = []
    rows, headers = read_csv_file(file_path)

    for index, row in enumerate(rows, start=1):
        error_msg = validate_row(row)
        if error_msg:
            error_record = {**row, 'error': error_msg, 'row_number': index}
            errors.append(error_record)

    return ImportResult(job_name=job_name, success=len(errors) == 0, errors=errors)


def move_file(source_path: str, destination_folder: str) -> str:
    """Moves a file to the destination folder. Returns the new file path."""
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    file_name = os.path.basename(source_path)
    destination_path = os.path.join(destination_folder, file_name)
    os.rename(source_path, destination_path)
    return destination_path


def cleanup_old_files(processed_folder: str, retention_days: int) -> int:
    """Removes files older than retention_days from the processed folder. Returns count of files removed."""
    if not os.path.exists(processed_folder):
        return 0

    cutoff = datetime.now() - timedelta(days=retention_days)
    removed_count = 0

    for file_name in os.listdir(processed_folder):
        file_path = os.path.join(processed_folder, file_name)
        if os.path.isfile(file_path):
            file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_mtime < cutoff:
                os.remove(file_path)
                removed_count += 1

    return removed_count


def get_outbound_files(outbound_folder: str) -> List[str]:
    """Returns a list of CSV file paths in the outbound folder."""
    if not os.path.exists(outbound_folder):
        return []
    return [
        os.path.join(outbound_folder, f)
        for f in os.listdir(outbound_folder)
        if os.path.isfile(os.path.join(outbound_folder, f)) and f.lower().endswith('.csv')
    ]
