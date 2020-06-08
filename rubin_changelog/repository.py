import logging
import os
import re
import subprocess
from datetime import datetime

from typing import List, Optional


def call_git(*args: str, cwd: str, git_exec: str = "/usr/bin/git") -> str:
    to_exec = [git_exec] + list(args)

    logging.debug(to_exec)
    logging.debug(cwd)
    return subprocess.check_output(to_exec, cwd=cwd).decode("utf-8")


class Repository(object):
    def __init__(self, path: str, *, branch_name: str = "master"):
        self.path = path
        self.branch_name = branch_name

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
        return datetime.fromtimestamp(int(self.__call_git("tag", "-l", tag_name, "--format=%(taggerdate:unix)")))

    def tags(self, pattern: str = r".*") -> List[str]:
        return [
            tag for tag in self.__call_git("tag").split() if re.search(pattern, tag)
        ]

    def add_tag(self, tag_name: str, target: str) -> None:
        if tag_name in self.tags():
            self.__call_git("tag", "-d", tag_name)
        self.__call_git("tag", tag_name, target)

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
        os.makedirs(target_dir, exist_ok=True)
        repo_dir_name = re.sub(r".git$", "", url.split("/")[-1])
        clone_path = os.path.join(target_dir, repo_dir_name)
        if not os.path.exists(clone_path):
            call_git(
                "clone",
                "--bare",
                "--branch",
                branch_name,
                url,
                repo_dir_name,
                cwd=target_dir,
            )
        repo = cls(clone_path, branch_name=branch_name)
        repo.update()
        return repo
