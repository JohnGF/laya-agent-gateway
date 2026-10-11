import subprocess
import os

def test_agy_route_help(tmp_path):
    result = subprocess.run(["bash", "bin/agy-route"], capture_output=True, text=True)
    assert result.returncode == 1
    assert "Usage: agy-route <prompt> [extra agy options...]" in result.stdout

def test_agy_route_execution(tmp_path, monkeypatch):
    # Mock laya-router
    router_script = tmp_path / "laya-router"
    router_script.write_text("#!/usr/bin/env bash\necho 'flash_lite print'\n")
    router_script.chmod(0o755)
    
    # Mock agy
    agy_script = tmp_path / "agy"
    agy_script.write_text("#!/usr/bin/env bash\necho \"AGY CALLED: $@\"\n")
    agy_script.chmod(0o755)
    
    # Update PATH
    monkeypatch.setenv("PATH", f"{tmp_path}:{os.environ['PATH']}")
    
    # Since agy-route has `exec agy`, we'll run it in bash
    result = subprocess.run(["bash", "bin/agy-route", "test prompt"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "AGY CALLED: --model gemini-3.8-flash-low --print test prompt" in result.stdout

def test_agy_route_interactive_override(tmp_path, monkeypatch):
    router_script = tmp_path / "laya-router"
    router_script.write_text("#!/usr/bin/env bash\necho 'flash_lite print'\n")
    router_script.chmod(0o755)
    
    agy_script = tmp_path / "agy"
    agy_script.write_text("#!/usr/bin/env bash\necho \"AGY CALLED: $@\"\n")
    agy_script.chmod(0o755)
    
    monkeypatch.setenv("PATH", f"{tmp_path}:{os.environ['PATH']}")
    
    result = subprocess.run(["bash", "bin/agy-route", "test prompt", "-i"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "AGY CALLED: --model gemini-3.8-flash-low --prompt-interactive test prompt -i" in result.stdout

def test_install_script_dry_run(tmp_path, monkeypatch):
    # Since install.sh uses HOME, let's mock HOME to point to tmp_path
    monkeypatch.setenv("HOME", str(tmp_path))
    
    result = subprocess.run(["bash", "install.sh"], capture_output=True, text=True)
    assert result.returncode == 0
    
    # Check if directories were created
    assert (tmp_path / ".local" / "bin").exists()
    assert (tmp_path / ".agents" / "skills").exists()
    
    # Check if symlinks were created
    assert (tmp_path / ".local" / "bin" / "laya-router").is_symlink()
    assert (tmp_path / ".local" / "bin" / "agy-route").is_symlink()
    assert (tmp_path / ".agents" / "skills" / "laya-router").is_symlink()
