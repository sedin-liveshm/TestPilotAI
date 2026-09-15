/**
 * Recorder Types for TestPilot AI Extension
 * 
 * Defines the extension UI state machine and future message passing interfaces.
 */

export type RecorderStatus = 'idle' | 'recording' | 'paused' | 'stopped';

export interface RecorderState {
  status: RecorderStatus;
  activeTabId?: number;
  activeTabUrl?: string;
  actionCount: number;
  recordingStartTime?: number;
  errorMessage?: string;
}

export type ExtensionMessageType =
  | 'GET_RECORDER_STATE'
  | 'START_RECORDING'
  | 'PAUSE_RECORDING'
  | 'RESUME_RECORDING'
  | 'STOP_RECORDING'
  | 'ACTION_RECORDED';

export interface ExtensionMessage<T = unknown> {
  type: ExtensionMessageType;
  payload?: T;
  timestamp: number;
}
