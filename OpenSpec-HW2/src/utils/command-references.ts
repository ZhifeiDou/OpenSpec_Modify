/**
 * Command Reference Utilities
 *
 * Utilities for transforming command references to tool-specific formats.
 */

/**
 * Transforms colon-based command references to hyphen-based format.
 * Converts `/opsx-hw2:` patterns to `/opsx-hw2-` for tools that use hyphen syntax.
 *
 * @param text - The text containing command references
 * @returns Text with command references transformed to hyphen format
 *
 * @example
 * transformToHyphenCommands('/opsx-hw2:new') // returns '/opsx-hw2-new'
 * transformToHyphenCommands('Use /opsx-hw2:apply to implement') // returns 'Use /opsx-hw2-apply to implement'
 */
export function transformToHyphenCommands(text: string): string {
  return text.replace(/\/opsx-hw2:/g, '/opsx-hw2-');
}
