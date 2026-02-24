/**
 * Continue Command Adapter
 *
 * Formats commands for Continue following its .prompt specification.
 */

import path from 'path';
import type { CommandContent, ToolCommandAdapter } from '../types.js';

/**
 * Continue adapter for command generation.
 * File path: .continue/prompts/opsx-hw2-<id>.prompt
 * Frontmatter: name, description, invokable
 */
export const continueAdapter: ToolCommandAdapter = {
  toolId: 'continue',

  getFilePath(commandId: string): string {
    return path.join('.continue', 'prompts', `opsx-hw2-${commandId}.prompt`);
  },

  formatFile(content: CommandContent): string {
    return `---
name: opsx-hw2-${content.id}
description: ${content.description}
invokable: true
---

${content.body}
`;
  },
};
