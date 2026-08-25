from typing import List

from config import Config
from email_notifier import build_failure_email, build_success_email, send_email
from po_importer import (
    ImportResult,
    cleanup_old_files,
    get_outbound_files,
    move_file,
    process_po_file,
)


def run_import_job() -> List[ImportResult]:
    """Main job runner: processes all PO files in outbound folder, sends notifications, and moves files."""
    outbound_files = get_outbound_files(Config.OUTBOUND_FOLDER)
    results = []

    for file_path in outbound_files:
        result = process_po_file(file_path)

        if result.success:
            msg = build_success_email(result, Config.FROM_ADDRESS, [Config.TO_ADDRESS])
        else:
            msg = build_failure_email(result, Config.FROM_ADDRESS, [Config.TO_ADDRESS])

        try:
            send_email(
                msg,
                Config.SMTP_HOST,
                Config.SMTP_PORT,
                Config.SMTP_USER,
                Config.SMTP_PASSWORD,
            )
        except Exception:
            # Email failure should not prevent file movement and processing
            pass

        move_file(file_path, Config.PROCESSED_FOLDER)
        results.append(result)

    cleanup_old_files(Config.PROCESSED_FOLDER, Config.BACKUP_RETENTION_DAYS)
    return results
