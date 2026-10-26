from ..base import Command


class CheckCommand(Command):
    name = "check"
    help = "check all code files"

    def run(self, args, context):
        library = context.library
        for remote in library.remotes.values():
            print("%s: %s, %d codes" % (remote.file, remote.name, len(remote.codes)))
        for problem in library.problems:
            print("Problem: %s" % problem)
        print("OK" if not library.problems else "%d problems" % len(library.problems))
        return 1 if library.problems else 0
