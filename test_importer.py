import csv
import os
import tempfile
import pytest
from io import StringIO

from importer import DataImporter


def write_csv(path: str, headers: list, rows: list) -> None:
    """Utility to write a CSV file to ``path`` with given headers and rows."""
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def create_csv_file(tmp_path: str, headers: list, rows: list) -> str:
    """Create a CSV file in the temporary directory and return its path."""
    file_path = os.path.join(tmp_path, 'sample.csv')
    write_csv(file_path, headers, rows)
    return file_path


def test_import_closed_cycles_success(tmp_path):
    """Import 5 closed application rows (one per cycle year) and verify summary."""
    headers = ['cycle_year', 'status', 'primary_contact', 'applicant_name', 'award_amount']
    rows = [
        {'cycle_year': '2020', 'status': 'closed', 'primary_contact': 'yes', 'applicant_name': 'Alice', 'award_amount': '1000'},
        {'cycle_year': '2021', 'status': 'closed', 'primary_contact': 'no', 'applicant_name': 'Bob', 'award_amount': '1500'},
        {'cycle_year': '2022', 'status': 'closed', 'primary_contact': 'yes', 'applicant_name': 'Carol', 'award_amount': '2000'},
        {'cycle_year': '2023', 'status': 'closed', 'primary_contact': 'no', 'applicant_name': 'Dave', 'award_amount': '2500'},
        {'cycle_year': '2024', 'status': 'closed', 'primary_contact': 'yes', 'applicant_name': 'Eve', 'award_amount': '3000'},
    ]
    csv_path = create_csv_file(tmp_path, headers, rows)

    importer = DataImporter()
    importer.import_cycles({2020: csv_path, 2021: csv_path, 2022: csv_path, 2023: csv_path, 2024: csv_path})
    summary = importer.get_import_summary()
    assert summary['total_cycles'] == 5
    assert summary['closed_cycles'] == 5
    assert summary['open_cycles'] == 0


def test_import_open_cycles_success(tmp_path):
    """Import 2 open application rows and verify summary."""
    headers = ['cycle_year', 'status', 'primary_contact', 'applicant_name', 'award_amount']
    rows = [
        {'cycle_year': '2025', 'status': 'open', 'primary_contact': 'yes', 'applicant_name': 'Frank', 'award_amount': '1200'},
        {'cycle_year': '2026', 'status': 'open', 'primary_contact': 'no', 'applicant_name': 'Grace', 'award_amount': '1800'},
    ]
    csv_path = create_csv_file(tmp_path, headers, rows)

    importer = DataImporter()
    importer.import_cycles({2025: csv_path, 2026: csv_path})
    summary = importer.get_import_summary()
    assert summary['total_cycles'] == 2
    assert summary['closed_cycles'] == 0
    assert summary['open_cycles'] == 2


def test_invalid_status_raises(tmp_path):
    """Row with an invalid status should raise a ValueError during validation."""
    headers = ['cycle_year', 'status', 'primary_contact', 'applicant_name', 'award_amount']
    rows = [
        {'cycle_year': '2020', 'status': 'invalid', 'primary_contact': 'yes', 'applicant_name': 'Test', 'award_amount': '100'},
    ]
    csv_path = create_csv_file(tmp_path, headers, rows)

    importer = DataImporter()
    with pytest.raises(ValueError, match="Invalid status"):
        importer.import_cycles({2020: csv_path})


def test_missing_required_field_raises(tmp_path):
    """Missing a required field should raise a ValueError."""
    headers = ['cycle_year', 'status', 'primary_contact', 'applicant_name', 'award_amount']
    rows = [
        {'cycle_year': '2020', 'status': 'closed', 'primary_contact': 'yes', 'applicant_name': '', 'award_amount': '100'},
    ]
    csv_path = create_csv_file(tmp_path, headers, rows)

    importer = DataImporter()
    with pytest.raises(ValueError, match="Missing required field 'applicant_name'") as exc:
        importer.import_cycles({2020: csv_path})
    assert "applicant_name" in str(exc.value)


def test_primary_contact_invalid_raises(tmp_path):
    """An invalid primary_contact value should raise a ValueError."""
    headers = ['cycle_year', 'status', 'primary_contact', 'applicant_name', 'award_amount']
    rows = [
        {'cycle_year': '2020', 'status': 'closed', 'primary_contact': 'maybe', 'applicant_name': 'Test', 'award_amount': '100'},
    ]
    csv_path = create_csv_file(tmp_path, headers, rows)

    importer = DataImporter()
    with pytest.raises(ValueError, match="Invalid primary_contact value"):
        importer.import_cycles({2020: csv_path})


def test_mixed_status_import(tmp_path):
    """Import a mix of closed and open rows and verify counts."""
    headers = ['cycle_year', 'status', 'primary_contact', 'applicant_name', 'award_amount']
    rows = [
        {'cycle_year': '2020', 'status': 'closed', 'primary_contact': 'yes', 'applicant_name': 'A', 'award_amount': '100'},
        {'cycle_year': '2020', 'status': 'open', 'primary_contact': 'no', 'applicant_name': 'B', 'award_amount': '200'},
        {'cycle_year': '2021', 'status': 'closed', 'primary_contact': 'no', 'applicant_name': 'C', 'award_amount': '300'},
    ]
    csv_path = create_csv_file(tmp_path, headers, rows)

    importer = DataImporter()
    importer.import_cycles({2020: csv_path, 2021: csv_path})
    summary = importer.get_import_summary()
    assert summary['total_cycles'] == 2
    assert summary['closed_cycles'] == 1
    assert summary['open_cycles'] == 1


def test_empty_file_raises(tmp_path):
    """An empty CSV file should raise a ValueError indicating the file is empty."""
    # Create an empty file
    empty_path = os.path.join(tmp_path, 'empty.csv')
    with open(empty_path, 'w', newline='', encoding='utf-8') as f:
        pass

    importer = DataImporter()
    with pytest.raises(ValueError, match="CSV file is empty"):
        importer.import_cycles({2020: empty_path})
