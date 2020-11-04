import logging
import os
import re
import shutil
import subprocess
from datetime import datetime

from typing import List, Set, Optional


def call_git(*args: str, cwd: str, git_exec: str = "/usr/bin/git") -> str:
    to_exec = [git_exec] + list(args)

    logging.debug(to_exec)
    logging.debug(cwd)
    return subprocess.check_output(to_exec, cwd=cwd, stderr=subprocess.STDOUT).decode(
        "utf-8"
    )


class Repository(object):
    def __init__(self, path: str, *, branch_name: str = "master"):
        self.path = path
        self.branch_name = branch_name
        self._tags: Set[str] = set()  # populated on demand.

        # Make sure we're using the appropriate branch
        self.__call_git("symbolic-ref", "HEAD", f"refs/heads/{branch_name}")

    def __call_git(self, *args: str) -> str:
        return call_git(*args, cwd=self.path)

    def commits(
        self, reachable_from: Optional[str] = None, merges_only: bool = False
    ) -> List[str]:
        args = ["log", "--pretty=format:%H"]
        if reachable_from:
            args.append(reachable_from)
        if merges_only:
            args.append("--merges")
        return self.__call_git(*args).split()

    def merges_between(self, old, new):
        args = ["log", "--pretty=format:%H", "--merges", f"{old}...{new}"]
        try:
            return self.__call_git(*args).split()
        except:
            return []

    def message(self, commit_hash: str) -> str:
        return self.__call_git("show", commit_hash, "--pretty=format:%s")

    def tag_date(self, tag_name: str) -> datetime:
        return datetime.fromtimestamp(
            int(self.__call_git("tag", "-l", tag_name, "--format=%(taggerdate:unix)"))
        )

    def sha_for_date(self, date: datetime):
        return self.__call_git(
            "rev-list", "-1", f'--before="{date}"', self.branch_name
        ).strip()

    @property
    def tags(self) -> Set[str]:
        if not self._tags:
            self._tags = set(tag for tag in self.__call_git("tag").split())
        return self._tags

    def add_tag(self, tag_name: str, target: str) -> None:
        if tag_name in self.tags:
            self.__call_git("tag", "-d", tag_name)
        self.__call_git("tag", tag_name, target)
        self._tags.add(tag_name)

    def update(self) -> str:
        return self.__call_git(
            "fetch", "origin", f"{self.branch_name}:{self.branch_name}"
        )

    @staticmethod
    def ticket(message: str) -> Optional[str]:
        try:
            result = re.search(r"(DM-\d+)", message, re.IGNORECASE).group(1)  # type: ignore[union-attr]
        except AttributeError:
            logging.debug(message)
            result = None
        return result

    @classmethod
    def materialize(
        cls, url: str, target_dir: str, *, branch_name: str = "master"
    ) -> "Repository":
        # Try to re-use an on disk repository. However, if it's corrupted,
        # blow it away and clone a fresh copy.
        repo_dir_name = re.sub(r".git$", "", url.split("/")[-1])
        clone_path = os.path.join(target_dir, repo_dir_name)
        os.makedirs(target_dir, exist_ok=True)

        def clone() -> None:
            """Clone repo at url into a subdirectory target_dir, clobbering
            pre-existing content, returning the resulting path.
            """
            call_git(
                "clone",
                "--bare",
                "--branch",
                branch_name,
                url,
                repo_dir_name,
                cwd=target_dir,
            )

        if not os.path.exists(clone_path):
            clone()
        repo = cls(clone_path, branch_name=branch_name)
        try:
            repo.update()
        except subprocess.CalledProcessError as e:
            logging.warn(f"Unable to update {clone_path}: {e}; {e.output}; resetting")
            shutil.rmtree(clone_path)
            clone()
            repo = cls(clone_path, branch_name=branch_name)
            repo.update()
        return repo
