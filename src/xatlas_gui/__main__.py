from __future__ import annotations

import sys
import traceback

from .cli import build_parser, run_cli


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.input is not None:
        try:
            return run_cli(args)
        except Exception as exc:
            if not args.silent:
                print(f"Error: {exc}", file=sys.stderr)
                if args.verbose_xatlas:
                    traceback.print_exc()
            return 1

    from .gui import run_gui

    return run_gui(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
