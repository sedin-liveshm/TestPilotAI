/**
 * Core frontend domain types for TestPilot AI.
 * 
 * These interfaces represent the primary entities in the application.
 * Note: These are kept minimal until the exact backend schemas are finalized.
 */

export interface User {
  id: string;
  email: string;
  fullName: string;
  avatarUrl?: string;
  createdAt: string;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  target_base_url: string;
  created_at: string;
}

export interface Test {
  id: string;
  projectId: string;
  name: string;
  description?: string;
  testIrId?: string; // Reference to the canonical Test IR representation
  createdAt: string;
  updatedAt: string;
}

export interface TestRun {
  id: string;
  testId: string;
  projectId: string;
  status: 'pending' | 'running' | 'passed' | 'failed' | 'canceled';
  startedAt?: string;
  completedAt?: string;
  durationMs?: number;
}

export interface TestRunStep {
  id: string;
  testRunId: string;
  stepIndex: number;
  action: string;
  status: 'pending' | 'running' | 'passed' | 'failed';
  errorMessage?: string;
  startedAt?: string;
  completedAt?: string;
}

export interface Artifact {
  id: string;
  testRunId: string;
  testRunStepId?: string;
  type: 'screenshot' | 'video' | 'trace' | 'log';
  url: string;
  createdAt: string;
}

export interface Requirement {
  id: string;
  projectId: string;
  title: string;
  description?: string;
  status: 'draft' | 'active' | 'deprecated';
  createdAt: string;
  updatedAt: string;
}

export interface Scenario {
  id: string;
  projectId: string;
  name: string;
  description?: string;
  requirementIds: string[];
  createdAt: string;
  updatedAt: string;
}
