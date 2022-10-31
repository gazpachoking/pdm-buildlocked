import atexit
from copy import deepcopy

from pdm.cli.actions import resolve_candidates_from_lockfile
from pdm.project import Project
from pdm.signals import pre_build, post_build


class BuildLocker:
    def __init__(self):
        self.project = None
        self.orig_pyproject = None

    def lock(self, project: Project, **kwargs):
        enabled = project.tool_settings.get("build", {}).get("buildlocked")
        if not enabled:
            return
        project.core.ui.echo("Locking dependencies before building...")
        self.project = project
        self.orig_pyproject = deepcopy(project.pyproject)

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

    def unlock(self, *args, **kwargs):
        if self.project and self.orig_pyproject:
            self.project.core.ui.echo("Restoring dependencies after build...")
            self.project.pyproject = self.orig_pyproject
            self.project.write_pyproject()
            self.project = None
            self.orig_pyproject = None


def register(core):
    locker = BuildLocker()
    pre_build.connect(locker.lock)
    post_build.connect(locker.unlock)
    # In case something went wrong during build and post_build doesn't fire,
    # make sure we still restore the pyproject file. This also holds a reference
    # to 'locker', and makes sure it isn't garbage collected.
    atexit.register(locker.unlock)
