import os


class Config:
    SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.example.com')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 25))
    SMTP_USER = os.environ.get('SMTP_USER', '')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
    FROM_ADDRESS = os.environ.get('FROM_ADDRESS', 'noreply@example.com')
    TO_ADDRESS = os.environ.get('TO_ADDRESS', 'alabama.sbs@example.com')
    OUTBOUND_FOLDER = os.environ.get('OUTBOUND_FOLDER', './outbound')
    PROCESSED_FOLDER = os.environ.get('PROCESSED_FOLDER', './processed')
    BACKUP_RETENTION_DAYS = int(os.environ.get('BACKUP_RETENTION_DAYS', 30))
