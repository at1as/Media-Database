from src.worker import Worker
import sys
import os

def print_usage():
  print("Usage:")
  print("  run.py")
  print("  run.py --count <max-new-per-category>")
  print("  run.py --dry-run")
  print("  run.py --refresh <movie|series|standup> <count>")

if len(sys.argv) > 1 and sys.argv[1] in ["-d", "--dry-run"]:
  Worker().start(dry_run=True)
elif len(sys.argv) > 1 and sys.argv[1] == "--refresh":
  if len(sys.argv) != 4:
    print_usage()
    raise SystemExit(1)

  if os.getuid() != 0:
    print("You are not running this script as root. This may cause issues with reading files on filesystem\n")

  Worker().start(dry_run=False, refresh_media_type=sys.argv[2], refresh_count=sys.argv[3])
elif len(sys.argv) == 1 or (len(sys.argv) == 3 and sys.argv[1] == "--count"):
  count = None
  if len(sys.argv) == 3:
    try:
      count = int(sys.argv[2])
      if count < 0:
        raise ValueError
    except ValueError:
      print("Count must be a non-negative integer.", file=sys.stderr)
      raise SystemExit(2)

  if os.getuid() != 0:
    print("You are not running this script as root. This may cause issues with reading files on filesystem\n")
  worker = Worker()
  if count is not None:
    for settings in worker.config["assets"].values():
      configured_limit = settings.get("max_assets_chunk")
      if isinstance(configured_limit, int) and configured_limit >= 0:
        settings["max_assets_chunk"] = min(count, configured_limit)
      else:
        settings["max_assets_chunk"] = count
  worker.start(dry_run=False)
else:
  print_usage()
  raise SystemExit(1)
