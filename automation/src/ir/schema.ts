import { z } from 'zod';

export const LocatorTargetSchema = z.discriminatedUnion('strategy', [
  z.object({
    strategy: z.literal('role'),
    role: z.string().min(1),
    name: z.string().optional()
  }),
  z.object({
    strategy: z.literal('text'),
    value: z.string().min(1)
  }),
  z.object({
    strategy: z.literal('label'),
    value: z.string().min(1)
  }),
  z.object({
    strategy: z.literal('placeholder'),
    value: z.string().min(1)
  }),
  z.object({
    strategy: z.literal('testId'),
    value: z.string().min(1)
  }),
  z.object({
    strategy: z.literal('css'),
    value: z.string().min(1)
  })
]);

export const NavigateActionSchema = z.object({
  type: z.literal('navigate'),
  url: z.string().min(1)
});

export const ClickActionSchema = z.object({
  type: z.literal('click'),
  target: LocatorTargetSchema
});

export const FillActionSchema = z.object({
  type: z.literal('fill'),
  target: LocatorTargetSchema,
  value: z.string()
});

export const SelectActionSchema = z.object({
  type: z.literal('select'),
  target: LocatorTargetSchema,
  value: z.string()
});

export const CheckActionSchema = z.object({
  type: z.literal('check'),
  target: LocatorTargetSchema
});

export const UncheckActionSchema = z.object({
  type: z.literal('uncheck'),
  target: LocatorTargetSchema
});

export const PressActionSchema = z.object({
  type: z.literal('press'),
  target: LocatorTargetSchema.optional(),
  key: z.string().min(1)
});

export const WaitActionSchema = z.object({
  type: z.literal('wait'),
  durationMs: z.number().positive()
});

export const AssertTextActionSchema = z.object({
  type: z.literal('assertText'),
  target: LocatorTargetSchema,
  text: z.string()
});

export const AssertVisibleActionSchema = z.object({
  type: z.literal('assertVisible'),
  target: LocatorTargetSchema
});

export const AssertUrlActionSchema = z.object({
  type: z.literal('assertUrl'),
  url: z.string().min(1)
});

export const ScreenshotActionSchema = z.object({
  type: z.literal('screenshot'),
  name: z.string().optional()
});

export const TestActionSchema = z.discriminatedUnion('type', [
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
  ScreenshotActionSchema
]);

export const TestIRSchema = z.object({
  version: z.literal('1'),
  id: z.string().min(1),
  name: z.string().min(1),
  description: z.string().optional(),
  actions: z.array(TestActionSchema).min(1)
});
