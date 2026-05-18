import argparse
import sys

from .ingest import run


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingest historical entity data into PostGIS"
    )
    subparsers = parser.add_subparsers(dest="command")

    # --- ingest subcommand (default behaviour, kept for backwards compat) ---
    ingest_parser = subparsers.add_parser("ingest", help="Ingest entity data into PostGIS")
    ingest_parser.add_argument("--entity", help="Ingest only this entity slug")
    ingest_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate configs and GeoJSON files without writing to DB",
    )

    # --- audit-types subcommand ---
    subparsers.add_parser(
        "audit-types",
        help="Pre-migration audit: check entity YAML types against M3 taxonomy",
    )

    # Also keep top-level --entity / --dry-run for backwards compatibility
    # (when no subcommand is given).
    parser.add_argument("--entity", help="Ingest only this entity slug")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate configs and GeoJSON files without writing to DB",
    )

    args = parser.parse_args()

    if args.command == "audit-types":
        from .audit_entity_types import run_audit
        sys.exit(run_audit())
    elif args.command == "ingest":
        run(entity_filter=args.entity, dry_run=args.dry_run)
    else:
        # No subcommand — fall back to ingest (legacy behaviour)
        run(entity_filter=args.entity, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
