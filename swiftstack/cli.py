#!/usr/bin/env python3
"""
SwiftStack CLI — generate a FastAPI project from plain English.

Usage:
    swiftstack generate --prompt "Build a blog with User and Post entities"
    swiftstack generate --template blog
    swiftstack generate --template ecommerce --out ./my-project
    swiftstack templates
"""

import argparse
import sys
import os
from pathlib import Path


HOSTED_URL = "https://swiftstackapi.up.railway.app"


def cmd_generate(args):
    from swiftstack.core.generator import generate, MAX_ENTITIES
    from swiftstack.templates import ALL as TEMPLATES

    if args.template:
        key = args.template.lower()
        if key not in TEMPLATES:
            print(f"Unknown template '{key}'. Available: {', '.join(TEMPLATES)}")
            sys.exit(1)
        prompt = TEMPLATES[key]
        api_name = key.replace("taskmanager", "Task Manager").title() + " API"
    elif args.prompt:
        prompt = args.prompt
        api_name = args.name or "API"
    else:
        print("Error: provide --prompt or --template")
        sys.exit(1)

    print(f"\n⚡ SwiftStack — generating (up to {MAX_ENTITIES} entities)...\n")
    files = generate(prompt, api_name=api_name)

    out_dir = Path(args.out) if args.out else Path(api_name.lower().replace(" ", "_"))
    out_dir.mkdir(parents=True, exist_ok=True)

    for filename, content in files.items():
        dest = out_dir / filename
        dest.write_text(content, encoding="utf-8")
        print(f"  ✓  {dest}")

    if "UPGRADE.md" in files:
        print(f"\n⚠  Your prompt had more than {MAX_ENTITIES} entities.")
        print(f"   Additional entities were skipped.")
        print(f"   → Full version: {HOSTED_URL}\n")
    else:
        print(f"\n✅ Done! Project written to: {out_dir}/")
        print(f"\nNext steps:")
        print(f"  cd {out_dir}")
        print(f"  pip install -r requirements.txt")
        print(f"  uvicorn main:app --reload")
        print(f"\n🔗 Need relationships, more entities, or other frameworks?")
        print(f"   {HOSTED_URL}\n")


def cmd_templates(_args):
    from swiftstack.templates import ALL as TEMPLATES
    print("\nAvailable templates:\n")
    for name in TEMPLATES:
        print(f"  swiftstack generate --template {name}")
    print(f"\nFull template list & hosted API: {HOSTED_URL}\n")


def main():
    parser = argparse.ArgumentParser(
        prog="swiftstack",
        description="Generate a production-ready FastAPI project from plain English.",
    )
    subs = parser.add_subparsers(dest="command")

    gen = subs.add_parser("generate", help="Generate a project")
    gen.add_argument("--prompt",   "-p", type=str, help="Plain-English description")
    gen.add_argument("--template", "-t", type=str, help="Use a built-in template")
    gen.add_argument("--out",      "-o", type=str, help="Output directory")
    gen.add_argument("--name",     "-n", type=str, help="API name", default="API")

    subs.add_parser("templates", help="List available templates")

    args = parser.parse_args()

    if args.command == "generate":
        cmd_generate(args)
    elif args.command == "templates":
        cmd_templates(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
