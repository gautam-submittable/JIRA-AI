import csv
import io
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

from po_importer import ImportResult


def build_success_email(result: ImportResult, from_addr: str, to_addrs: List[str]) -> MIMEMultipart:
    """Builds an email message indicating successful import."""
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = ', '.join(to_addrs)
    msg['Subject'] = f'PO Import - {result.job_name} - Successful'

    body = (
        f'The PO import job "{result.job_name}" completed successfully.\n\n'
        f'No errors were encountered during processing.'
    )
    msg.attach(MIMEText(body, 'plain'))
    return msg


def build_failure_email(result: ImportResult, from_addr: str, to_addrs: List[str]) -> MIMEMultipart:
    """Builds an email message indicating failed import, with CSV attachment of errored rows."""
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = ', '.join(to_addrs)
    msg['Subject'] = f'PO Import - {result.job_name} - Failed'

    body = (
        f'The PO import job "{result.job_name}" encountered {len(result.errors)} error(s) during processing.\n\n'
        f'Please see the attached CSV for details on the errored rows.'
    )
    msg.attach(MIMEText(body, 'plain'))

    # Build CSV attachment
    if result.errors:
        csv_buffer = io.StringIO()
        # Collect all possible field names preserving order
        fieldnames_set = set()
        for err in result.errors:
            fieldnames_set.update(err.keys())
        fieldnames = list(fieldnames_set)
        # Ensure row_number and error are last
        if 'row_number' in fieldnames:
            fieldnames.remove('row_number')
        if 'error' in fieldnames:
            fieldnames.remove('error')
        fieldnames.extend(['row_number', 'error'])

        writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
        writer.writeheader()
        for err in result.errors:
            writer.writerow(err)

        csv_data = csv_buffer.getvalue().encode('utf-8')
        attachment = MIMEApplication(csv_data, _subtype='csv')
        attachment.add_header(
            'Content-Disposition',
            'attachment',
            filename=f'{result.job_name}_errors.csv'
        )
        msg.attach(attachment)

    return msg


def send_email(msg: MIMEMultipart, smtp_host: str, smtp_port: int,
               smtp_user: str, smtp_password: str) -> None:
    """Sends an email via SMTP."""
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        if smtp_user and smtp_password:
            server.starttls()
            server.login(smtp_user, smtp_password)
        server.sendmail(msg['From'], msg['To'].split(', '), msg.as_string())
