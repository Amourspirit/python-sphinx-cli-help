import shutil
import os
import subprocess
from pathlib import Path
from typing import Dict
import toml


def main() -> int:
    root_path = Path(__file__).parent.parent.parent

    # region Read config values from pyproject.toml
    cfg = toml.load(root_path / "pyproject.toml")
    cfg_meta: Dict[str, str] = cfg["tool"]["template"]["metadata"]
    cfg_pkg_name = cfg_meta["pkg_out_name"]
    cfg_build_dir = cfg_meta["build_dir"]
    cfg_build_readme = cfg_meta["build_readme"]
    cfg_build_license = cfg_meta["build_license"]
    cfg_entry_name = cfg_meta["entry_point_name"]
    # endregion Read config values from pyproject.toml

    # region Set up build and dist directories
    build_path = root_path / cfg_build_dir
    if build_path.exists():
        shutil.rmtree(build_path, ignore_errors=True)
    build_path.mkdir(parents=True, exist_ok=True)

    dist_path = build_path / "dist"
    if dist_path.exists():
        shutil.rmtree(dist_path, ignore_errors=True)
    # endregion Set up build and dist directories

    # region Copy sphinx_cli_help directory to build directory
    dev_help_path = root_path / "sphinx_cli_help"
    build_dev_help_path = build_path / cfg_pkg_name
    shutil.copytree(dev_help_path, build_dev_help_path)
    # endregion Copy sphinx_cli_help directory to build directory

    # region Readme
    # Copy README.md to build directory
    readme_path = None
    if cfg_build_readme:
        readme_path = Path(cfg_build_readme)
        if not readme_path.is_absolute():
            readme_path = root_path / readme_path
        if readme_path.exists():
            shutil.copy(readme_path, build_path)
    # endregion Readme

    # region License
    if cfg_build_license:
        license_path = Path(cfg_build_license)
        if not license_path.is_absolute():
            license_path = root_path / license_path
        if license_path.exists():
            shutil.copy(license_path, build_path)

    shutil.copy(root_path / "pyproject.toml", build_path)
    # endregion License

    _process_interactive_toml(build_path=build_path)
    _process_interactive_hlp(build_dev_help_path, cfg_entry_name, cfg_pkg_name)

    # region Run Poetry Build on build directory
    env = os.environ.copy()
    subprocess.run(["poetry", "build", "--no-interaction", "-C", str(build_path)], env=env)
    # endregion Run Poetry Build on build directory

    # region Clean up build directory
    shutil.rmtree(build_dev_help_path, ignore_errors=True)
    build_license = build_path / "LICENSE"
    if build_license.exists():
        os.remove(build_license)
    # endregion Clean up build directory

    return 0


def _process_interactive_toml(build_path: Path) -> None:
    cfg = toml.load(build_path / "pyproject.toml")
    cfg_meta: Dict[str, str] = cfg["tool"]["template"]["metadata"]
    cfg_pkg_name = cfg_meta["pkg_out_name"]
    cfg_entry_name = cfg_meta["entry_point_name"]

    cli_hlp = str(cfg["tool"]["poetry"]["scripts"]["cli-hlp"])
    cfg["tool"]["poetry"]["scripts"][f"{cfg_entry_name}"] = cli_hlp.replace("sphinx_cli_help", cfg_pkg_name)
    del cfg["tool"]["poetry"]["scripts"]["cli-hlp"]
    cfg["tool"]["poetry"]["packages"][0] = {"include": f"{cfg_pkg_name}"}
    with open(build_path / "pyproject.toml", "w") as f:
        toml.dump(cfg, f)


def _process_interactive_hlp(build_dev_help_path: Path, cfg_entry_name: str, cfg_pkg_name: str) -> None:
    i_help = build_dev_help_path / "cli" / "interactive_hlp.py"
    with open(i_help, "r") as f:
        content = f.read()
        content = content.replace("cli-hlp", cfg_entry_name)
        content = content.replace("sphinx_cli_help", cfg_pkg_name)

    with open(i_help, "w") as f:
        f.write(content)


if __name__ == "__main__":
    SystemExit(main())
