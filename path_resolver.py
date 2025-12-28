from pathlib import Path

def resolve_input_path(user_path: str) -> Path:
    """
    Convert the user path (relative or absolute) into an ABSOLUTE Path.

    Key behavior:
    - If user provides a relative path, we interpret it relative to the CURRENT WORKING DIRECTORY.
      (This matters a lot when the script is built into an .exe.)
    - If user provides an absolute path, we keep it as-is.

    Example:
      User runs from folder: C:\Projects\OCRApp
      User passes: .\images\a.jpg
      We resolve to: C:\Projects\OCRApp\images\a.jpg
    """

    # Turn the string into a Path object
    p = Path(user_path)

    # If p is NOT absolute, make it absolute using the current working directory
    if not p.is_absolute():
        p = (Path.cwd() / p).resolve()

    # Return the final absolute path
    return p