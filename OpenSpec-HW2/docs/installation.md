# Installation

## Prerequisites

- **Node.js 20.19.0 or higher** — Check your version: `node --version`

## Package Managers

### npm

```bash
npm install -g @fission-ai/openspec-hw2@latest
```

### pnpm

```bash
pnpm add -g @fission-ai/openspec-hw2@latest
```

### yarn

```bash
yarn global add @fission-ai/openspec-hw2@latest
```

### bun

```bash
bun add -g @fission-ai/openspec-hw2@latest
```

## Nix

Run OpenSpec-HW2 directly without installation:

```bash
nix run github:Fission-AI/OpenSpec-HW2 -- init
```

Or install to your profile:

```bash
nix profile install github:Fission-AI/OpenSpec-HW2
```

Or add to your development environment in `flake.nix`:

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    openspec-hw2.url = "github:Fission-AI/OpenSpec-HW2";
  };

  outputs = { nixpkgs, openspec-hw2, ... }: {
    devShells.x86_64-linux.default = nixpkgs.legacyPackages.x86_64-linux.mkShell {
      buildInputs = [ openspec-hw2.packages.x86_64-linux.default ];
    };
  };
}
```

## Verify Installation

```bash
openspec-hw2 --version
```

## Next Steps

After installing, initialize OpenSpec-HW2 in your project:

```bash
cd your-project
openspec-hw2 init
```

See [Getting Started](getting-started.md) for a full walkthrough.
