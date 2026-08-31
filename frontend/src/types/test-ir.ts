/**
 * Test Intermediate Representation (Test IR) types.
 * 
 * This is the canonical representation of a test in PilotAI.
 * It is completely agnostic of the execution runner (e.g. Playwright)
 * and serves as the bridge between the UI builder, AI generation, and execution.
 */

export interface TestIR {
  id: string;
  name: string;
  description?: string;
  steps: TestStep[];
  version: string;
}

export type ActionType = 'navigate' | 'click' | 'type' | 'select' | 'hover' | 'assert';

// Base step interface
export interface BaseStep {
  id: string;
  action: ActionType;
  metadata?: {
    description?: string;
    aiGenerated?: boolean;
    confidenceScore?: number;
    [key: string]: unknown;
  };
}

export interface NavigateStep extends BaseStep {
  action: 'navigate';
  target: string; // The URL to navigate to
}

export interface ClickStep extends BaseStep {
  action: 'click';
  target: string; // Generic locator (e.g., semantic label, CSS selector, XPath)
}

export interface TypeStep extends BaseStep {
  action: 'type';
  target: string;
  value: string;
}

export interface SelectStep extends BaseStep {
  action: 'select';
  target: string;
  value: string; // Option value or text
}

export interface HoverStep extends BaseStep {
  action: 'hover';
  target: string;
}

export type AssertCondition = 'isVisible' | 'isHidden' | 'equals' | 'contains' | 'notContains';

export interface AssertStep extends BaseStep {
  action: 'assert';
  target: string;
  condition: AssertCondition;
  expectedValue?: string;
}

// Union of all possible steps
export type TestStep = NavigateStep | ClickStep | TypeStep | SelectStep | HoverStep | AssertStep;
