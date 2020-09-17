import os
import re
import subprocess
from typing import Any, List, Union

from .utils.exceptions import CommandListError, CommandNotRecognizedError, XFError


class XFManager:

    def __init__(self, results_dir: str = os.getcwd()):

        """Base XFOIL Manager Class.

        Parameters
        ----------
        results_dir: str
            Path to save results to.
        """

        self.process: Union[subprocess.Popen, None] = None

        self._cmd_list: Union[List[str], None] = None
        self._cmds_set: bool = False

        self.results_dir: str = results_dir

        self.stdout: Union[bytes, None] = None
        self.stderr: Union[bytes, None] = None

        self._gen_path()

    @property
    def cmd_list(self) -> List[str]:
        return self._cmd_list

    @cmd_list.setter
    def cmd_list(self, cmds: List[Any]) -> None:
        self._cmd_list = list(map(str, cmds))
        self._cmds_set = True

    def __del__(self) -> None:

        """Ensures that XFOIL process is stopped upon object delete."""

        if self.process is not None:
            self.process.kill()

    def _gen_path(self) -> None:

        """Generates `self.results_dir` if it doesn't exist.    """

        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)

    def config_cmd(self, cmds: List[Any]) -> None:

        """Configures commands sent to XFOIL.

        Parameters
        ----------
        cmds : List[Any]
            Any parameters that the user wishes to provide.
        """

        self.cmd_list = cmds

    def _check_commands(self) -> None:

        """Checks if cmd_list is appropriate.

        Raises
        ------
        CommandListError
            Ensures that `self.cmd_list` starts / ends appropriately.
        """
        if not self._cmds_set:
            raise CommandListError('Must provide a cmd_list')
        if self.cmd_list[:3] != ['PLOP', 'G', '']:
            raise CommandListError("cmd_list must begin with ['PLOP', 'G', '']")
        if self.cmd_list[-2:] != ['', 'QUIT']:
            raise CommandListError("cmd_list must end with ['', 'QUIT']")

    def _check_exit(self) -> None:

        """Checks if XFOIL ran successfully.

        Raises
        ------
        XFError
            Raises if XFOIL exits with a non-zero returncode.
        CommandNotRecognizedError
            Raises if XFOIL was unable to recognise a command.
        """

        if self.process.returncode != 0:
            raise XFError('XFOIL produced a non-zero returncode.')

        if cnr_match := re.search('XFOIL\s+c>\s+(\S+)\s+command not recognized.', self.stdout.decode()):
            raise CommandNotRecognizedError(f'{cnr_match.group(1)} command not recognized.')

    def run(self, timeout: float = 15.0) -> None:

        """Runs XFOIL Simulations.

        Parameters
        ----------
        timeout : float
            Number of seconds to wait for timeout.
        """

        self._check_commands()

        self.process = subprocess.Popen(
            ['xfoil'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.results_dir
        )

        try:
            self.stdout, self.stderr = self.process.communicate('\n'.join(self._cmd_list).encode(), timeout=timeout)
        except subprocess.TimeoutExpired as e:
            raise e

        self._check_exit()
