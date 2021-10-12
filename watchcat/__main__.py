from watchcat import cli
from watchcat.config.config import ConfigLoader


def main():
    parser = cli.build_parser()
    args = parser.parse_args()

    config = ConfigLoader(args.config)

    for resource in config.resources:
        snapshot = resource.get()
        # store
        # diff
        # resource.notifier.send()
