#!/usr/bin/env bash
# ==============================================================================
# Installer for Laya Agent Gateway
# ==============================================================================

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"
SKILLS_DIR="$HOME/.agents/skills"

echo "=== Installing Laya Agent Gateway ==="

# 1. Symlink CLI binaries into ~/.local/bin
mkdir -p "$BIN_DIR"
for bin in "$REPO_DIR/bin/"*; do
    if [[ -f "$bin" ]]; then
        target="$BIN_DIR/$(basename "$bin")"
        chmod +x "$bin"
        ln -sf "$bin" "$target"
        echo "  [+] Linked $target -> $bin"
    fi
done

# 2. Symlink skill into ~/.agents/skills (Codex, OpenCode, Claude Code, Pi)
mkdir -p "$SKILLS_DIR"
ln -sfn "$REPO_DIR/skills/laya-router" "$SKILLS_DIR/laya-router"
echo "  [+] Installed skill to $SKILLS_DIR/laya-router"

# 3. If OpenCode config exists, install skill there as well
if [[ -d "$HOME/.config/opencode/skills" ]]; then
    ln -sfn "$REPO_DIR/skills/laya-router" "$HOME/.config/opencode/skills/laya-router"
    echo "  [+] Linked skill to ~/.config/opencode/skills/laya-router"
fi

echo ""
echo "Installation complete!"
echo "Verify health with: laya-router health"
