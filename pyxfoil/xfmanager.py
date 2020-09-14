import abc
import os
import subprocess
from typing import Any, List, NoReturn, Union

from .utils.exceptions import CommandListError, XFError


class BaseXFManager(abc.ABC):

    def __init__(self, results_dir: str = os.getcwd()):

        self.process: Union[subprocess.Popen, None] = None
        self.cmd_list: List[str] = ['PLOP', 'G', '']

        self.results_dir: str = results_dir

        self.stdout: Union[str, None] = None
        self.stderr: Union[str, None] = None

    def __del__(self) -> None:

        """Ensures that XFOIL process is stopped upon object delete."""

        if self.process is not None:
            self.process.kill()

    @abc.abstractmethod
    def config_cmd(self, *args: Any) -> NoReturn:

        """Configures commands sent to XFOIL.

        The user must override this method to add the relevant commands
        to `self.cmd_list` - there will be a check to ensure that XFOIL
        runs without a display and exits at the end of the run.

        Parameters
        ----------
        *args : Any
            Any parameters that the user wishes to provide.

        Raises
        ------
        NotImplementedError
            BaseXFManager::config_cmd()
        """

        raise NotImplementedError('BaseXFManager::config_cmd()')

    def _check_commands(self) -> None:

        """Checks if cmd_list is appropriate.

        Raises
        ------
        CommandListError
            Ensures that `self.cmd_list` starts / ends appropriately.
        """

        if self.cmd_list[:3] != ['PLOP', 'G', '']:
            raise CommandListError("cmd_list must begin with ['PLOP', 'G', '']")
        if self.cmd_list[-2:] != ['', 'QUIT']:
            raise CommandListError("cmd_list must end with ['', 'QUIT']")

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
            self.stdout, self.stderr = self.process.communicate('\n'.join(self.cmd_list).encode(), timeout=timeout)
        except subprocess.TimeoutExpired as e:
            raise e

        if self.process.returncode != 0:
            raise XFError('XFOIL produced a non-zero returncode.')
