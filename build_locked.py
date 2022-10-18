import argparse
from copy import deepcopy

from pdm.cli.actions import resolve_candidates_from_lockfile
from pdm.project import Project
from pdm.cli.commands.build import Command as BaseBuildCommand


class BuildLockedCommand(BaseBuildCommand):
    """Build artifacts for distribution"""

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        super().add_arguments(parser)
        parser.add_argument(
            "--locked",
            dest="locked",
            default=False,
            action="store_true",
            help="Build with all dependencies (including transitive) locked "
                 "to their versions from the lock file",
        )

    def handle(self, project: Project, options: argparse.Namespace) -> None:
        """The command handler function.
        :param project: the pdm project instance
        :param options: the parsed Namespace object
        """
        if not options.locked:
            return super().handle(project, options)
        orig_pyproject = deepcopy(project.pyproject)
        try:
            requirements = project.get_dependencies("default")
            candidates = resolve_candidates_from_lockfile(
                project, requirements.values()
            ).values()
            project.meta["dependencies"] = [
                str(c.req.as_pinned_version(c.version)) for c in candidates
            ]
            optional_groups = project.meta.get("optional-dependencies", {}).keys()
            for group in optional_groups:
                requirements = project.get_dependencies(group)
                candidates = resolve_candidates_from_lockfile(
                    project, requirements.values()
                ).values()
                project.meta.setdefault("optional-dependencies", {})[group] = [
                    str(c.req.as_pinned_version(c.version)) for c in candidates
                ]
            project.write_pyproject()
            return super().handle(project, options)
        finally:
            project.pyproject = orig_pyproject
            project.write_pyproject()


def register(core):
    core.register_command(BuildLockedCommand, "build")
