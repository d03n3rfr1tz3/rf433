"""Writes code files in the format read by codefile.parser."""

from __future__ import annotations

from ..model import Code, Remote


def format_code(name: str, code: Code, repeat: int | None = None, indent: str = "    ") -> list[str]:
    """The lines of one code inside "begin raw_codes"."""
    lines = ["%sname %s" % (indent, name)]
    if repeat is not None:
        lines.append("%s  repeat %d" % (indent, repeat))
    lines.append("%s  %s" % (indent, code.format()))
    return lines


def format_remote(remote: Remote) -> str:
    lines = ["begin remote", "  name %s" % remote.name]
    if remote.repeat is not None:
        lines.append("  repeat %d" % remote.repeat)
    lines += ["", "  begin raw_codes"]
    for entry in remote.codes.values():
        lines += format_code(entry.name, entry.code, entry.repeat)
    lines += ["  end raw_codes", "end remote", ""]
    return "\n".join(lines)
