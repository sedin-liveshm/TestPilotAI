import { TestIR, TestAction } from '../ir/types';

export interface RunnerResult {
  success: boolean;
  testId: string;
  error?: string;
  executedActionsCount: number;
}

export interface TestRunner {
  run(test: TestIR): Promise<RunnerResult>;
}
