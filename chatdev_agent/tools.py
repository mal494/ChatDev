import subprocess

def execute_shell(command: str):
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )
        return result.stdout if result.returncode == 0 else result.stderr
    except Exception as e:
        return str(e)

TOOLS = {
    "execute_shell": execute_shell
}
