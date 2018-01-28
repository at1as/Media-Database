from src.worker import Worker
import sys

if len(sys.argv) > 1 and sys.argv[1] in ["-d", "--dry-run"]:
  Worker().start(dry_run=True)
else:
  Worker().start(dry_run=False)
