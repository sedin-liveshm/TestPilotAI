import { Browser, BrowserContext, Page } from 'playwright';
import { TestIR, TestAction, LocatorTarget } from '../ir/types';
import { RunnerResult, TestRunner } from './runner';

export interface AuthenticatedRunnerOptions {
  browser: Browser;
  baseURL?: string;
  storageStatePath?: string;
}

/**
 * AuthenticatedRunner Placeholder
 * 
 * This runner creates a Playwright BrowserContext that can consume an authenticated state
 * (via storageStatePath). It maps Test IR actions to Playwright commands.
 * 
 * Note: Authentication logic (like signing in with Supabase) should be handled prior to 
 * calling this runner. The runner simply consumes the resulting state.
 */
export class AuthenticatedRunner implements TestRunner {
  private browser: Browser;
  private baseURL?: string;
  private storageStatePath?: string;

  constructor(options: AuthenticatedRunnerOptions) {
    this.browser = options.browser;
    this.baseURL = options.baseURL;
    this.storageStatePath = options.storageStatePath;
  }

  public async run(test: TestIR): Promise<RunnerResult> {
    let context: BrowserContext | null = null;
    let page: Page | null = null;
    let executedActionsCount = 0;

    try {
      // 1. Setup authenticated context
      if (!this.storageStatePath) {
        console.warn(`[Runner] No storage state provided for test '${test.id}'. Running unauthenticated.`);
      }

      context = await this.browser.newContext({
        baseURL: this.baseURL,
        storageState: this.storageStatePath
      });

      // 2. Create page
      page = await context.newPage();
      page.setDefaultTimeout(2000); // Fail fast for runner testing

      // 3. Execute actions (minimal placeholder support)
      for (const action of test.actions) {
        await this.executeAction(page, action);
        executedActionsCount++;
      }

      return {
        success: true,
        testId: test.id,
        executedActionsCount
      };

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      return {
        success: false,
        testId: test.id,
        error: errorMessage,
        executedActionsCount
      };
    } finally {
      if (page) await page.close();
      if (context) await context.close();
    }
  }

  private async executeAction(page: Page, action: TestAction): Promise<void> {
    switch (action.type) {
      case 'navigate':
        await page.goto(action.url);
        break;
      case 'click':
        await this.resolveLocator(page, action.target).click();
        break;
      case 'fill':
        await this.resolveLocator(page, action.target).fill(action.value);
        break;
      case 'assertVisible':
        await this.resolveLocator(page, action.target).waitFor({ state: 'visible' });
        break;
      case 'assertUrl':
        const currentUrl = page.url();
        // A minimal check; in reality Playwright's expect(page).toHaveURL() is better, 
        // but this requires no extra test-runner wrapper.
        if (!currentUrl.includes(action.url)) {
          throw new Error(`URL Assertion failed: expected url to include ${action.url}, but got ${currentUrl}`);
        }
        break;
      case 'wait':
        await page.waitForTimeout(action.durationMs);
        break;
      default:
        // Placeholder for unimplemented actions
        console.log(`[Runner] Action '${action.type}' is currently a placeholder and not fully implemented.`);
        break;
    }
  }

  private resolveLocator(page: Page, target: LocatorTarget) {
    switch (target.strategy) {
      case 'role':
        // simplified mapping to internal Playwright role types
        return page.getByRole(target.role as any, target.name ? { name: target.name } : undefined);
      case 'text':
        return page.getByText(target.value);
      case 'label':
        return page.getByLabel(target.value);
      case 'placeholder':
        return page.getByPlaceholder(target.value);
      case 'testId':
        return page.getByTestId(target.value);
      case 'css':
        return page.locator(target.value);
      default:
        throw new Error(`Unsupported locator strategy`);
    }
  }
}
