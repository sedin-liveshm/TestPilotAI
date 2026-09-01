import { z } from 'zod';
import {
  LocatorTargetSchema,
  NavigateActionSchema,
  ClickActionSchema,
  FillActionSchema,
  SelectActionSchema,
  CheckActionSchema,
  UncheckActionSchema,
  PressActionSchema,
  WaitActionSchema,
  AssertTextActionSchema,
  AssertVisibleActionSchema,
  AssertUrlActionSchema,
  ScreenshotActionSchema,
  TestActionSchema,
  TestIRSchema
} from './schema';

export type LocatorTarget = z.infer<typeof LocatorTargetSchema>;
export type NavigateAction = z.infer<typeof NavigateActionSchema>;
export type ClickAction = z.infer<typeof ClickActionSchema>;
export type FillAction = z.infer<typeof FillActionSchema>;
export type SelectAction = z.infer<typeof SelectActionSchema>;
export type CheckAction = z.infer<typeof CheckActionSchema>;
export type UncheckAction = z.infer<typeof UncheckActionSchema>;
export type PressAction = z.infer<typeof PressActionSchema>;
export type WaitAction = z.infer<typeof WaitActionSchema>;
export type AssertTextAction = z.infer<typeof AssertTextActionSchema>;
export type AssertVisibleAction = z.infer<typeof AssertVisibleActionSchema>;
export type AssertUrlAction = z.infer<typeof AssertUrlActionSchema>;
export type ScreenshotAction = z.infer<typeof ScreenshotActionSchema>;
export type TestAction = z.infer<typeof TestActionSchema>;
export type TestIR = z.infer<typeof TestIRSchema>;
