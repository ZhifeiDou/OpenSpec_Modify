## MODIFIED Requirements

### Requirement: Directory Creation
The command SHALL create the complete OpenSpec-HW2 directory structure with all required directories and files.

#### Scenario: Creating OpenSpec-HW2 structure
- **WHEN** `openspec-hw2 init` is executed
- **THEN** create the following directory structure:
```
openspec-hw2/
├── project.md
├── AGENTS.md
├── specs/
└── changes/
    └── archive/
```

### Requirement: File Generation
The command SHALL generate required template files with appropriate content for immediate use.

#### Scenario: Generating template files
- **WHEN** initializing OpenSpec-HW2
- **THEN** generate `AGENTS.md` containing complete OpenSpec-HW2 instructions for AI assistants
- **AND** generate `project.md` with project context template

### Requirement: AI Tool Configuration Details

The command SHALL properly configure selected AI tools with OpenSpec-HW2-specific instructions using a marker system.

#### Scenario: Creating new CLAUDE.md
- **WHEN** CLAUDE.md does not exist
- **THEN** create new file with OpenSpec-HW2 content wrapped in markers including reference to `@openspec-hw2/AGENTS.md`

### Requirement: Success Output

The command SHALL provide clear, actionable next steps upon successful initialization.

#### Scenario: Displaying success message
- **WHEN** initialization completes successfully
- **THEN** include prompt: "Please explain the OpenSpec-HW2 workflow from openspec-hw2/AGENTS.md and how I should work with you on this project"
