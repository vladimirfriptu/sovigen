import argparse
import sys

from . import commands


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="sovigen")
    sub = parser.add_subparsers(dest="command", required=True)

    p_new = sub.add_parser("new")
    p_new.add_argument("title")

    p_build = sub.add_parser("build")
    p_build.add_argument("slug")

    sub.add_parser("build-all")

    p_ready = sub.add_parser("ready")
    p_ready.add_argument("slug")

    p_pub = sub.add_parser("publish")
    p_pub.add_argument("slug")

    sub.add_parser("status")

    args = parser.parse_args(argv)
    try:
        return _dispatch(args)
    except commands.CommandError as err:
        print(f"error: {err}", file=sys.stderr)
        return 1


def _dispatch(args) -> int:
    if args.command == "new":
        sdir = commands.cmd_new(args.title)
        print(f"created {sdir}")
        print("put cover.(jpg|png|webp) and track.mp3 inside, then set stage to 'ready'")
        return 0
    if args.command == "build":
        out = commands.cmd_build(args.slug)
        print(f"built {out}")
        return 0
    if args.command == "build-all":
        built = commands.cmd_build_all()
        if built:
            print("built: " + ", ".join(built))
        else:
            print("nothing to build (no songs at stage 'ready')")
        return 0
    if args.command == "ready":
        commands.cmd_ready(args.slug)
        print(f"{args.slug} -> ready")
        return 0
    if args.command == "publish":
        commands.cmd_publish(args.slug)
        print(f"published {args.slug}")
        return 0
    if args.command == "status":
        rows = commands.cmd_status()
        _print_status(rows)
        return 0
    return 2


def _print_status(rows) -> None:
    if not rows:
        print("no songs yet")
        return
    for row in rows:
        print(f"{row['stage']:<14} {row['slug']}")


if __name__ == "__main__":
    raise SystemExit(main())
