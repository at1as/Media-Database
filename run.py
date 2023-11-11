from src.worker import Worker
import sys
import os

if len(sys.argv) > 1 and sys.argv[1] in ["-d", "--dry-run"]:
  Worker().start(dry_run=True)
else:
  if os.getuid() != 0:
    print("You are not running this script as root. This may cause issues with reading files on filesystem\n")
  Worker().start(dry_run=False)
