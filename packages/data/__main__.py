import argparse

from .ingest import run


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingest historical entity data into PostGIS"
    )
    parser.add_argument("--entity", help="Ingest only this entity slug")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate configs and GeoJSON files without writing to DB",
    )
    args = parser.parse_args()
    run(entity_filter=args.entity, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
