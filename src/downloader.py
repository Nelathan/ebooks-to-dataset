"""
downloader.py

Handles downloading and cleaning up Standard Ebooks repositories using sparse git checkout.
"""

import os
import shutil
import subprocess

def download_repo(repo_link, dest_dir, branch="master"):
    """
    Download the repo (shallow clone with sparse checkout of src/epub).
    Uses subprocess.run for robust timeout and exception handling.
    Suppresses git output.
    """
    # Prepare destination directory
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)
    os.makedirs(dest_dir, exist_ok=True)

    # Clone repository
    try:
        subprocess.run(
            [
                "git", "clone",
                "--depth=1",
                "--filter=blob:none",
                "--sparse",
                "--branch", branch,
                repo_link, dest_dir
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
            timeout=300
        )
    except subprocess.TimeoutExpired:
        print(f"Timeout cloning {repo_link}")
        cleanup_repo(dest_dir)
        raise
    except subprocess.CalledProcessError:
        print(f"Git clone failed for {repo_link}")
        cleanup_repo(dest_dir)
        raise

    # Perform sparse checkout of src/epub only
    sparse_commands = [
        ["git", "sparse-checkout", "init", "--cone"],
        ["git", "sparse-checkout", "set", "src/epub"],
        ["git", "pull"]
    ]

    for cmd in sparse_commands:
        try:
            subprocess.run(
                cmd,
                cwd=dest_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
        except subprocess.CalledProcessError:
            cmd_str = " ".join(cmd)
            print(f"Sparse checkout step failed ({cmd_str}) in {dest_dir}")
            cleanup_repo(dest_dir)
            raise

    return dest_dir


def cleanup_repo(repo_path):
    """
    Delete the repo folder after processing.
    """
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)
