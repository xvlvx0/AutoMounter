import subprocess
import logging


log = logging.getLogger(__name__)


class GitInfo:
    """A git history information class."""

    def __init__(self) -> None:
        """Initialize the class."""
        self.main_version = "0.9."

    def get_revision_nr(self) -> str:
        """Retrieve git version number."""
        try:
            log.debug("--get_revision_nr--")
            cmd = ["/usr/bin/git", "rev-list", "HEAD", "--count"]
            output = subprocess.check_output(cmd)
            log.debug(f"output: {output}")
            return f"{self.main_version}{str(int(output)).zfill(3)}"
        except subprocess.CalledProcessError as err:
            # raise FailedGettingGitRevisionError(err)
            return "000"
