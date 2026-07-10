# Backup And Restore

Create a SQLite backup:

```bash
python scripts/backup_restore.py backup
```

Restore from a backup:

```bash
python scripts/backup_restore.py restore --backup-file backups/niyamguard_YYYYMMDDTHHMMSSZ.db
```

For production pilots, run backups from a restricted service account and store encrypted copies outside the application host.
