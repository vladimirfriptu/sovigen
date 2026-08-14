import argparse
import json
import sys

from . import commands


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="sovigen")
    sub = parser.add_subparsers(dest="command", required=True)

    p_new = sub.add_parser("new")
    p_new.add_argument("title")
    p_new.add_argument("--source", default=None)
    p_new.add_argument("--series", default=None)
    p_new.add_argument("--language", default="uk")

    p_build = sub.add_parser("build")
    p_build.add_argument("slug")
    p_build.add_argument("--viz", action="store_true")

    sub.add_parser("build-all")

    p_advance = sub.add_parser("advance")
    p_advance.add_argument("slug")

    p_choose = sub.add_parser("choose")
    p_choose.add_argument("slug")
    p_choose.add_argument("variant")

    p_import = sub.add_parser("import")
    p_import.add_argument("slug")
    p_import.add_argument("path")

    p_pub = sub.add_parser("publish")
    p_pub.add_argument("slug")

    p_status = sub.add_parser("status")
    p_status.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    try:
        return _dispatch(args)
    except commands.CommandError as err:
        print(f"error: {err}", file=sys.stderr)
        return 1


def _dispatch(args) -> int:
    if args.command == "new":
        sdir = commands.cmd_new(
            args.title, source=args.source, series=args.series, language=args.language
        )
        print(f"created {sdir}")
        print("write brief.md, then: sovigen advance <slug> to move stage by stage")
        print("bring downloads in with: sovigen import <slug> <path-to-file>")
        return 0
    if args.command == "build":
        out = commands.cmd_build(args.slug, viz=args.viz)
        print(f"built {out}")
        return 0
    if args.command == "build-all":
        built = commands.cmd_build_all()
        if built:
            print("built: " + ", ".join(built))
        else:
            print("nothing to build (no songs at stage 'ready')")
        return 0
    if args.command == "advance":
        moved_from, moved_to = commands.cmd_advance(args.slug)
        if moved_from == moved_to:
            print(f"{args.slug} already at {moved_to}")
        else:
            print(f"{args.slug}: {moved_from} -> {moved_to}")
        return 0
    if args.command == "choose":
        commands.cmd_choose(args.slug, args.variant)
        print(f"chose {args.variant} for {args.slug}")
        return 0
    if args.command == "import":
        dest = commands.cmd_import(args.slug, args.path)
        print(f"imported {dest}")
        return 0
    if args.command == "publish":
        commands.cmd_publish(args.slug)
        print(f"published {args.slug}")
        return 0
    if args.command == "status":
        rows = commands.cmd_status()
        if args.json:
            print(json.dumps(rows, ensure_ascii=False))
        else:
            _print_status(rows)
        return 0
    return 2


def _print_status(rows) -> None:
    if not rows:
        print("no songs yet")
        return
    for row in rows:
        print(f"{row['stage']:<14} {row['turn']:<7} {row['slug']}")


if __name__ == "__main__":
    raise SystemExit(main())
