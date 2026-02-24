import { describe, it, expect } from 'vitest';
import { transformToHyphenCommands } from '../../src/utils/command-references.js';

describe('transformToHyphenCommands', () => {
  describe('basic transformations', () => {
    it('should transform single command reference', () => {
      expect(transformToHyphenCommands('/opsx-hw2:new')).toBe('/opsx-hw2-new');
    });

    it('should transform multiple command references', () => {
      const input = '/opsx-hw2:new and /opsx-hw2:apply';
      const expected = '/opsx-hw2-new and /opsx-hw2-apply';
      expect(transformToHyphenCommands(input)).toBe(expected);
    });

    it('should transform command reference in context', () => {
      const input = 'Use /opsx-hw2:apply to implement tasks';
      const expected = 'Use /opsx-hw2-apply to implement tasks';
      expect(transformToHyphenCommands(input)).toBe(expected);
    });

    it('should handle backtick-quoted commands', () => {
      const input = 'Run `/opsx-hw2:continue` to proceed';
      const expected = 'Run `/opsx-hw2-continue` to proceed';
      expect(transformToHyphenCommands(input)).toBe(expected);
    });
  });

  describe('edge cases', () => {
    it('should return unchanged text with no command references', () => {
      const input = 'This is plain text without commands';
      expect(transformToHyphenCommands(input)).toBe(input);
    });

    it('should return empty string unchanged', () => {
      expect(transformToHyphenCommands('')).toBe('');
    });

    it('should not transform similar but non-matching patterns', () => {
      const input = '/ops:new opsx: /other:command';
      expect(transformToHyphenCommands(input)).toBe(input);
    });

    it('should handle multiple occurrences on same line', () => {
      const input = '/opsx-hw2:new /opsx-hw2:continue /opsx-hw2:apply';
      const expected = '/opsx-hw2-new /opsx-hw2-continue /opsx-hw2-apply';
      expect(transformToHyphenCommands(input)).toBe(expected);
    });
  });

  describe('multiline content', () => {
    it('should transform references across multiple lines', () => {
      const input = `Use /opsx-hw2:new to start
Then /opsx-hw2:continue to proceed
Finally /opsx-hw2:apply to implement`;
      const expected = `Use /opsx-hw2-new to start
Then /opsx-hw2-continue to proceed
Finally /opsx-hw2-apply to implement`;
      expect(transformToHyphenCommands(input)).toBe(expected);
    });
  });

  describe('all known commands', () => {
    const commands = [
      'new',
      'continue',
      'apply',
      'ff',
      'sync',
      'archive',
      'bulk-archive',
      'verify',
      'explore',
      'onboard',
    ];

    for (const cmd of commands) {
      it(`should transform /opsx-hw2:${cmd}`, () => {
        expect(transformToHyphenCommands(`/opsx-hw2:${cmd}`)).toBe(`/opsx-hw2-${cmd}`);
      });
    }
  });
});
