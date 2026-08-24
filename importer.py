import csv
from typing import Dict, List, Any


class DataImporter:
    """Utility to import historical cycle data for applications and awards.

    The class stores imported cycles in memory and provides a summary report.
    """

    def __init__(self) -> None:
        # In‑memory storage of imported cycles; each cycle is a dict.
        self.cycles: List[Dict[str, Any]] = []

    # ---------------------------------------------------------------------
    # Data loading and validation
    # ---------------------------------------------------------------------
    def load_sample_data(self, file_path: str) -> List[Dict[str, str]]:
        """Read a CSV file and return a list of rows as dictionaries.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the CSV is malformed or required fields are missing.
        """
        with open(file_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        if not rows:
            raise ValueError("CSV file is empty")
        return rows

    def validate_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Validate a CSV row and enrich it with derived boolean fields.

        Required fields: cycle_year, status, applicant_name.
        Status must be 'closed' or 'open' (case‑insensitive).
        primary_contact must be a recognizable yes/no indicator.

        Returns a copy of the row with an additional ``primary_contact_bool`` key.
        """
        # Required fields
        for field in ('cycle_year', 'status', 'applicant_name'):
            if not row.get(field):
                raise ValueError(f"Missing required field '{field}' in row: {row}")

        # Status validation
        status = row['status'].strip().lower()
        if status not in ('closed', 'open'):
            raise ValueError(f"Invalid status '{row['status']}'")
        row['status'] = status

        # Primary contact validation
        pc_raw = row.get('primary_contact', '').strip().lower()
        if pc_raw not in ('yes', 'no', 'true', 'false'):
            raise ValueError(f"Invalid primary_contact value '{row.get('primary_contact')}'")
        row['primary_contact_bool'] = pc_raw in ('yes', 'true')

        # Ensure cycle_year is integer
        try:
            row['cycle_year'] = int(row['cycle_year'])
        except ValueError as exc:
            raise ValueError(f"cycle_year must be integer, got '{row['cycle_year']}'") from exc

        return dict(row)  # return a shallow copy

    # ---------------------------------------------------------------------
    # Processing logic
    # ---------------------------------------------------------------------
    def _ensure_cycle(self, year: int) -> Dict[str, Any]:
        """Return the cycle dict for the given year, creating it if necessary.

        The cycle dict contains keys: 'year', 'status', 'application' (the row).
        """
        for cycle in self.cycles:
            if cycle['year'] == year:
                return cycle
        cycle = {'year': year, 'status': '', 'application': None}
        self.cycles.append(cycle)
        return cycle

    def process_closed_application(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Process a closed application row and store it in the appropriate cycle.

        Closed applications are expected to have exactly one row per cycle year.
        """
        cycle = self._ensure_cycle(row['cycle_year'])
        cycle['status'] = 'closed'
        cycle['application'] = row
        return cycle

    def process_open_application(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Process an open application row and store it in the appropriate cycle.

        Open applications may have any primary_contact value; no special handling is required.
        """
        cycle = self._ensure_cycle(row['cycle_year'])
        cycle['status'] = 'open'
        cycle['application'] = row
        return cycle

    def import_cycles(self, file_paths: Dict[int, str]) -> None:
        """Import cycles from a mapping of cycle_year -> CSV file path.

        The method clears any existing test data (simulated by resetting ``self.cycles``) before processing.
        """
        # Simulate deletion of test submission data
        self.cycles.clear()

        for year, path in file_paths.items():
            rows = self.load_sample_data(path)
            for raw_row in rows:
                validated = self.validate_row(raw_row)
                if validated['status'] == 'closed':
                    self.process_closed_application(validated)
                else:
                    self.process_open_application(validated)

    def get_import_summary(self) -> Dict[str, int]:
        """Return a summary of the imported cycles.

        Keys:
            total_cycles: total number of cycles imported
            closed_cycles: number of cycles with status 'closed'
            open_cycles: number of cycles with status 'open'
        """
        total = len(self.cycles)
        closed = sum(1 for c in self.cycles if c['status'] == 'closed')
        open_cnt = sum(1 for c in self.cycles if c['status'] == 'open')
        return {
            'total_cycles': total,
            'closed_cycles': closed,
            'open_cycles': open_cnt
        }


# Example usage (not part of the library API):
if __name__ == "__main__":
    importer = DataImporter()
    # Example: import cycles for years 2020-2024 (closed) and 2025-2026 (open)
    # file_paths = {2020: "closed_2020.csv", 2021: "closed_2021.csv", ...}
    # importer.import_cycles(file_paths)
    # print(importer.get_import_summary())
