import subprocess
import shlex
from .utils import tw_env_var


class Tower:
    """
    A Python class that serves as a wrapper for 'tw' CLI commands.

    The class enables the execution of 'tw' commands in an object-oriented manner.
    You can call any subcommand of 'tw' as a method on instances of this class.
    The arguments of the subcommand can be passed as arguments to the method.

    Each command is run in a subprocess, with the output being captured and returned.
    """

    class TwCommand:
        def __init__(self, tw_instance, cmd):
            self.tw_instance = tw_instance
            self.cmd = cmd

        def __call__(self, *args, **kwargs):
            command = self.cmd.split()
            command.extend(args)
            return self.tw_instance._tw_run(command, **kwargs)

    # Constructs a new Tower instance with a specified workspace
    def __init__(self, workspace_name):
        env_var_name = "TOWER_WORKSPACE_ID"
        self.workspace = (
            tw_env_var(env_var_name) if workspace_name is None else workspace_name
        )
        if self.workspace is None:
            raise ValueError(
                "Neither an environment variable for workspace name nor an argument was provided."
            )
        self.workspace = workspace_name

    # Executes a 'tw' command in a subprocess and returns the output.
    def _tw_run(self, cmd, *args, **kwargs):
        """
        Run a tw command with supplied commands
        """
        command = ["tw"]
        if kwargs.get("to_json"):
            command.extend(["-o", "json"])
        command.extend(cmd)
        command.extend(args)

        if kwargs.get("config") is not None:
            config_path = kwargs["config"]
            command.append(f"--config={config_path}")

        if "params_file" in kwargs:
            params_path = kwargs["params_file"]
            command.append(f"--params-file={params_path}")

        full_cmd = " ".join(shlex.quote(arg) for arg in command)
        print(full_cmd)
        # Run the command and return the stdout
        process = subprocess.Popen(full_cmd, stdout=subprocess.PIPE, shell=True)
        stdout, _ = process.communicate()
        stdout = stdout.decode("utf-8").strip()

        return stdout

    # Allow any 'tw' subcommand to be called as a method.
    def __getattr__(self, cmd):
        """
        Magic method to allow any 'tw' subcommand to be called as a method.
        Returns a TwCommand object that can be called with arguments.
        """
        cmd = cmd.replace("_", "-")  # replace underscores with hyphens
        return self.TwCommand(self, cmd)