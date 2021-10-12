from watchcat import cli
from watchcat.config.config import ConfigLoader
from watchcat.diff_detector.simple import SimpleDiffDetector


def main():
    parser = cli.build_parser()
    args = parser.parse_args()

    config = ConfigLoader(args.config)
    diff_detector = SimpleDiffDetector()

    for resource in config.resources:
        new_snapshot = resource.get()
        # storage.set(resource_id, new_snapshot)
        # old_snapshot = storage.get(resource_id)
        if diff_detector.has_update(old_snapshot, new_snapshot):
            message = f"{resource.title} has updated!"
            resource.notifier.send(message)
