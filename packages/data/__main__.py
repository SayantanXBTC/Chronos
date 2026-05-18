import argparse
import json
import os
import sys

from .ingest import run


def _get_db_conn():
    """Read DATABASE_URL from env and return a psycopg2 connection."""
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    import psycopg2
    return psycopg2.connect(db_url)


def _cmd_stats(args) -> None:
    from .reporting import stats
    conn = _get_db_conn()
    try:
        result = stats(conn)
    finally:
        conn.close()
    print(json.dumps(result, indent=2, default=str))


def _cmd_diff(args) -> None:
    from .reporting import diff_entity
    conn = _get_db_conn()
    try:
        result = diff_entity(conn, slug=args.entity, raw_dir=args.raw_dir)
    finally:
        conn.close()
    print(json.dumps(result, indent=2, default=str))


def _cmd_audit_source(args) -> None:
    from .reporting import audit_source
    conn = _get_db_conn()
    try:
        rows = audit_source(conn, source_id=args.source)
    finally:
        conn.close()
    print(json.dumps(rows, indent=2, default=str))


def _cmd_coverage_report(args) -> None:
    from .reporting import coverage_report
    conn = _get_db_conn()
    try:
        rows = coverage_report(conn)
    finally:
        conn.close()
    print(json.dumps(rows, indent=2, default=str))


def _cmd_update_coverage(args) -> None:
    from .reporting import update_coverage
    conn = _get_db_conn()
    try:
        update_coverage(
            conn,
            region_name=args.region,
            year_start=args.year_start,
            year_end=args.year_end,
            completeness=args.completeness,
            entity_count=args.entity_count,
            primary_source=args.source,
            notes=args.notes,
        )
    finally:
        conn.close()
    print(
        f"Coverage updated: {args.region} [{args.year_start}, {args.year_end}] "
        f"completeness={args.completeness}"
    )


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

    # --- stats subcommand ---
    subparsers.add_parser(
        "stats",
        help="Print DB summary stats (requires DATABASE_URL)",
    )

    # --- diff subcommand ---
    diff_parser = subparsers.add_parser(
        "diff",
        help="Diff DB territory count vs raw GeoJSON phase files (requires DATABASE_URL)",
    )
    diff_parser.add_argument("--entity", required=True, help="Entity slug to diff")
    diff_parser.add_argument(
        "--raw-dir",
        default="data/raw/political",
        help="Root directory for raw GeoJSON files (default: data/raw/political)",
    )

    # --- audit-source subcommand ---
    audit_source_parser = subparsers.add_parser(
        "audit-source",
        help="List territories by source name (requires DATABASE_URL)",
    )
    audit_source_parser.add_argument(
        "--source",
        required=True,
        help="Source name fragment (fuzzy match via ILIKE)",
    )

    # --- coverage-report subcommand ---
    subparsers.add_parser(
        "coverage-report",
        help="Print region_coverage table (requires DATABASE_URL)",
    )

    # --- update-coverage subcommand ---
    update_cov_parser = subparsers.add_parser(
        "update-coverage",
        help="Upsert a row into region_coverage (requires DATABASE_URL)",
    )
    update_cov_parser.add_argument("--region", required=True, help="Region name")
    update_cov_parser.add_argument(
        "--year-start", required=True, type=int, help="Start year (negative = BCE)"
    )
    update_cov_parser.add_argument(
        "--year-end", default=None, type=int, help="End year (optional)"
    )
    update_cov_parser.add_argument(
        "--completeness",
        required=True,
        choices=["complete", "partial", "sparse", "none"],
        help="Coverage completeness level",
    )
    update_cov_parser.add_argument(
        "--entity-count", default=0, type=int, help="Number of entities in region"
    )
    update_cov_parser.add_argument(
        "--source", default=None, help="Primary source name"
    )
    update_cov_parser.add_argument(
        "--notes", default=None, help="Free-text notes"
    )

    # --- validate subcommand ---
    validate_parser = subparsers.add_parser(
        "validate",
        help="Schema linter for GeoJSON phase files and place-names CSV",
    )
    validate_parser.add_argument(
        "file",
        nargs="?",
        help="Path to a single GeoJSON file to validate",
    )
    validate_parser.add_argument(
        "--all",
        action="store_true",
        dest="validate_all",
        help="Validate all GeoJSON files under data/raw/political/",
    )
    validate_parser.add_argument(
        "--place-names",
        action="store_true",
        dest="place_names",
        help="Validate data/raw/place_names/ancient_cities.csv",
    )

    # --- qa subcommand ---
    qa_parser = subparsers.add_parser(
        "qa",
        help="QA checks against the PostGIS database (requires DATABASE_URL)",
    )
    qa_parser.add_argument(
        "--check-overlaps",
        action="store_true",
        dest="check_overlaps",
        help="Find territory pairs with significant spatial + temporal overlap",
    )
    qa_parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Overlap area fraction threshold for --check-overlaps (default: 0.5)",
    )
    qa_parser.add_argument(
        "--invalid-geoms",
        action="store_true",
        dest="invalid_geoms",
        help="Find territories with invalid geometries (ST_IsValid = false)",
    )
    qa_parser.add_argument(
        "--temporal-gaps",
        action="store_true",
        dest="temporal_gaps",
        help="Find entities with temporal gaps between consecutive phases",
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
    elif args.command == "stats":
        _cmd_stats(args)
    elif args.command == "diff":
        _cmd_diff(args)
    elif args.command == "audit-source":
        _cmd_audit_source(args)
    elif args.command == "coverage-report":
        _cmd_coverage_report(args)
    elif args.command == "update-coverage":
        _cmd_update_coverage(args)
    elif args.command == "validate":
        from pathlib import Path
        from .validate import (
            validate_geojson_file,
            validate_all_geojson,
            validate_place_names_csv,
            print_results,
        )
        if args.place_names:
            csv_path = Path("data/raw/place_names/ancient_cities.csv")
            sys.exit(print_results([validate_place_names_csv(csv_path)]))
        elif args.validate_all:
            sys.exit(print_results(validate_all_geojson("data/raw/political")))
        elif args.file:
            sys.exit(print_results([validate_geojson_file(args.file)]))
        else:
            validate_parser.print_help()
            sys.exit(1)
    elif args.command == "qa":
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            print(
                "ERROR: DATABASE_URL environment variable is not set.\n"
                "Set it to a valid PostgreSQL connection string, e.g.:\n"
                "  export DATABASE_URL=postgresql://user:pass@host:5432/dbname",
                file=sys.stderr,
            )
            sys.exit(1)
        import psycopg2
        from .qa import check_overlaps, check_invalid_geoms, check_temporal_gaps
        try:
            conn = psycopg2.connect(database_url)
        except Exception as exc:
            print(f"ERROR: Could not connect to database: {exc}", file=sys.stderr)
            sys.exit(1)
        exit_code = 0
        try:
            if args.check_overlaps:
                rows = check_overlaps(conn, threshold=args.threshold)
                if not rows:
                    print("No significant territory overlaps found.")
                else:
                    print(f"Found {len(rows)} overlapping territory pair(s):")
                    for row in rows:
                        print(
                            f"  {row['entity_a']} <-> {row['entity_b']}"
                            f"  years {row['year_overlap_start']}–{row['year_overlap_end']}"
                            f"  overlap_fraction={row['overlap_fraction']:.3f}"
                            f"  territory_ids=({row['territory_a_id']}, {row['territory_b_id']})"
                        )
                    exit_code = 1
            elif args.invalid_geoms:
                rows = check_invalid_geoms(conn)
                if not rows:
                    print("No invalid geometries found.")
                else:
                    print(f"Found {len(rows)} territory/ies with invalid geometry:")
                    for row in rows:
                        print(
                            f"  entity={row['entity_slug']}"
                            f"  territory_id={row['territory_id']}"
                            f"  years={row['year_start']}–{row['year_end']}"
                        )
                    exit_code = 1
            elif args.temporal_gaps:
                rows = check_temporal_gaps(conn)
                if not rows:
                    print("No temporal gaps found.")
                else:
                    print(f"Found {len(rows)} temporal gap(s):")
                    for row in rows:
                        print(
                            f"  entity={row['entity_slug']}"
                            f"  gap={row['gap_start']}–{row['gap_end']}"
                            f"  ({row['gap_years']} years)"
                        )
                    exit_code = 1
            else:
                qa_parser.print_help()
                exit_code = 1
        finally:
            conn.close()
        sys.exit(exit_code)
    else:
        # No subcommand — fall back to ingest (legacy behaviour)
        run(entity_filter=args.entity, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
