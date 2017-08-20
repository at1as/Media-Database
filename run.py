from src.retriever import Retriever
import sys

if len(sys.argv) > 1 and sys.argv[1] in ["-d", "--dry-run"]:
  Retriever().start(dry_run=True)
else:
  Retriever().start(dry_run=False)
