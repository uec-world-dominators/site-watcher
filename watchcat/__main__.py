import sys
import termcolor
from watchcat import cli
from watchcat.config.config import ConfigLoader
from watchcat.diff_detector.simple import SimpleDiffDetector
from watchcat.storage.sql_storage import SqlStorage


def main():
    parser = cli.build_parser()
    args = parser.parse_args()

    config = ConfigLoader(args.config)
    diff_detector = SimpleDiffDetector()
    with SqlStorage(args.db) as storage:
        for resource_id, resource in config.resources.items():
            new_snapshot = resource.get()
            old_snapshot = storage.get(resource_id)
            storage.set(new_snapshot)
            if old_snapshot is not None:
                if diff_detector.has_update(old_snapshot, new_snapshot):
                    message = f"{resource.title} has updated!\n{diff_detector.diff(old_snapshot, new_snapshot)}"
                    resource.notifier.send(message)
                    termcolor.cprint(f"update found for {resource_id}", file=sys.stderr, color="green")
                else:
                    termcolor.cprint(f"no update found for {resource_id}", file=sys.stderr)
            else:
                termcolor.cprint(f"first fetch for {resource_id}", file=sys.stderr, color="yellow")
