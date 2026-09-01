import { test, expect } from '@playwright/test';
import { TestIRSchema } from '../src/ir/schema';

test.describe('Test IR v1 Validation', () => {
  test('should validate a minimal valid Test IR', () => {
    const validData = {
      version: '1',
      id: 'test-1',
      name: 'Minimal Test',
      actions: [
        {
          type: 'navigate',
          url: '/'
        }
      ]
    };
    
    const result = TestIRSchema.safeParse(validData);
    expect(result.success).toBe(true);
  });

  test('should validate a test with multiple actions and locator strategies', () => {
    const validData = {
      version: '1',
      id: 'full-test',
      name: 'Full Test',
      description: 'A test covering multiple actions',
      actions: [
        { type: 'navigate', url: '/login' },
        { type: 'fill', target: { strategy: 'label', value: 'Email' }, value: 'test@example.com' },
        { type: 'fill', target: { strategy: 'placeholder', value: 'Password' }, value: 'pwd' },
        { type: 'click', target: { strategy: 'role', role: 'button', name: 'Submit' } },
        { type: 'wait', durationMs: 1000 },
        { type: 'assertText', target: { strategy: 'testId', value: 'welcome-message' }, text: 'Welcome' },
        { type: 'assertVisible', target: { strategy: 'css', value: '.dashboard-header' } },
        { type: 'assertUrl', url: '/dashboard' },
        { type: 'screenshot', name: 'after-login' },
        { type: 'check', target: { strategy: 'text', value: 'Remember me' } },
        { type: 'uncheck', target: { strategy: 'text', value: 'Subscribe' } },
        { type: 'select', target: { strategy: 'label', value: 'Country' }, value: 'US' },
        { type: 'press', target: { strategy: 'role', role: 'combobox' }, key: 'Enter' },
        { type: 'press', key: 'Escape' }
      ]
    };

    const result = TestIRSchema.safeParse(validData);
    expect(result.success).toBe(true);
  });

  test('should reject missing version', () => {
    const data = {
      id: 't1',
      name: 'N',
      actions: [{ type: 'navigate', url: '/' }]
    };
    expect(TestIRSchema.safeParse(data).success).toBe(false);
  });

  test('should reject unsupported version', () => {
    const data = {
      version: '2',
      id: 't1',
      name: 'N',
      actions: [{ type: 'navigate', url: '/' }]
    };
    expect(TestIRSchema.safeParse(data).success).toBe(false);
  });

  test('should reject missing test ID', () => {
    const data = {
      version: '1',
      name: 'N',
      actions: [{ type: 'navigate', url: '/' }]
    };
    expect(TestIRSchema.safeParse(data).success).toBe(false);
  });

  test('should reject missing name', () => {
    const data = {
      version: '1',
      id: 't1',
      actions: [{ type: 'navigate', url: '/' }]
    };
    expect(TestIRSchema.safeParse(data).success).toBe(false);
  });

  test('should reject empty actions', () => {
    const data = {
      version: '1',
      id: 't1',
      name: 'N',
      actions: []
    };
    expect(TestIRSchema.safeParse(data).success).toBe(false);
  });

  test('should reject unknown action type', () => {
    const data = {
      version: '1',
      id: 't1',
      name: 'N',
      actions: [{ type: 'unknown_action' }]
    };
    expect(TestIRSchema.safeParse(data).success).toBe(false);
  });

  test('should reject missing required action field', () => {
    const data = {
      version: '1',
      id: 't1',
      name: 'N',
      actions: [{ type: 'fill', target: { strategy: 'text', value: 'Hi' } }] // missing 'value' for fill
    };
    expect(TestIRSchema.safeParse(data).success).toBe(false);
  });

  test('should reject invalid locator strategy', () => {
    const data = {
      version: '1',
      id: 't1',
      name: 'N',
      actions: [{ type: 'click', target: { strategy: 'xpath', value: '//div' } }]
    };
    expect(TestIRSchema.safeParse(data).success).toBe(false);
  });

  test('should reject invalid field type', () => {
    const data = {
      version: '1',
      id: 't1',
      name: 'N',
      actions: [{ type: 'wait', durationMs: '1000' }] // string instead of number
    };
    expect(TestIRSchema.safeParse(data).success).toBe(false);
  });

  test('should reject invalid enum value (unsupported strategy)', () => {
    const data = {
      version: '1',
      id: 't1',
      name: 'N',
      actions: [{ type: 'click', target: { strategy: 'testId' } }] // missing value
    };
    expect(TestIRSchema.safeParse(data).success).toBe(false);
  });
});
