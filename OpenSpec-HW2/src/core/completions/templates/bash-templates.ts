/**
 * Static template strings for Bash completion scripts.
 * These are Bash-specific helper functions that never change.
 */

export const BASH_DYNAMIC_HELPERS = `# Dynamic completion helpers

_openspec_hw2_complete_changes() {
  local changes
  changes=$(openspec-hw2 __complete changes 2>/dev/null | cut -f1)
  COMPREPLY=($(compgen -W "$changes" -- "$cur"))
}

_openspec_hw2_complete_specs() {
  local specs
  specs=$(openspec-hw2 __complete specs 2>/dev/null | cut -f1)
  COMPREPLY=($(compgen -W "$specs" -- "$cur"))
}

_openspec_hw2_complete_items() {
  local items
  items=$(openspec-hw2 __complete changes 2>/dev/null | cut -f1; openspec-hw2 __complete specs 2>/dev/null | cut -f1)
  COMPREPLY=($(compgen -W "$items" -- "$cur"))
}`;
