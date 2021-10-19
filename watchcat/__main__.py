import sys
from watchcat import cli
from watchcat.config.config import ConfigLoader
from watchcat.diff_detector.simple import SimpleDiffDetector
from watchcat.storage.storage import Storage
from watchcat.storage.sql_storage import SqlStorage


def main():
    parser = cli.build_parser()
    args = parser.parse_args()

    config = ConfigLoader(args.config)
    diff_detector = SimpleDiffDetector()
    storage: Storage = SqlStorage("hoge.db")

    for resource_id, resource in config.resources.items():
        new_snapshot = resource.get()
        old_snapshot = storage.get(resource_id)
        storage.set(new_snapshot)
        print(resource)
        if old_snapshot is not None:
            if diff_detector.has_update(old_snapshot, new_snapshot):
                message = f"{resource.title} has updated!"
                resource.notifier.send(message)
            else:
                print(f"no update found for {resource_id}", file=sys.stderr)
        else:
            print(f"first fetch for {resource_id}", file=sys.stderr)
