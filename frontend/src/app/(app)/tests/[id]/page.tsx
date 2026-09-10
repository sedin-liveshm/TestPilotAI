"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { Test, Project } from "@/types/domain";
import { testsApi } from "@/services/tests-api";
import { projectsApi } from "@/services/projects-api";
import { TestMetadata } from "@/components/tests/TestMetadata";
import { Spinner } from "@/components/ui/spinner";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { ChevronRight, ArrowLeft, AlertCircle, RefreshCw, Layers, Wand2 } from "lucide-react";

export default function TestDetailPage() {
  const params = useParams<{ id: string }>();
  const testId = params?.id;
  const router = useRouter();

  const [test, setTest] = useState<Test | null>(null);
  const [project, setProject] = useState<Project | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadTest = useCallback(() => {
    if (!testId) return;
    setIsLoading(true);
    setError(null);

    testsApi
      .getTest(testId)
      .then((testRes) => {
        const testData = testRes.data;
        setTest(testData);

        const projId = testData.projectId || testData.project_id;
        if (projId) {
          projectsApi
            .getProject(projId)
            .then((projRes) => setProject(projRes.data))
            .catch(() => setProject(null));
        }
        setIsLoading(false);
      })
      .catch((err) => {
        const message =
          err instanceof Error ? err.message : "Failed to load test details. Please try again.";
        setError(message);
        setIsLoading(false);
      });
  }, [testId]);

  useEffect(() => {
    if (!testId) return;
    let isMounted = true;

    testsApi
      .getTest(testId)
      .then((testRes) => {
        if (!isMounted) return;
        const testData = testRes.data;
        setTest(testData);

        const projId = testData.projectId || testData.project_id;
        if (projId) {
          projectsApi
            .getProject(projId)
            .then((projRes) => {
              if (isMounted) setProject(projRes.data);
            })
            .catch(() => {
              if (isMounted) setProject(null);
            });
        }
        setIsLoading(false);
      })
      .catch((err) => {
        if (!isMounted) return;
        const message =
          err instanceof Error ? err.message : "Failed to load test details. Please try again.";
        setError(message);
        setIsLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [testId]);


  const handleTestUpdate = (updatedTest: Test) => {
    setTest((prev) => (prev ? { ...prev, ...updatedTest } : updatedTest));
  };

  const projectId = test?.projectId || test?.project_id || project?.id;

  return (
    <div className="flex flex-col gap-6 max-w-5xl mx-auto w-full">
      {/* Breadcrumb & Navigation Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <nav aria-label="Breadcrumb" className="flex items-center gap-1.5 text-sm text-muted-foreground">
          <Link
            href="/projects"
            className="hover:text-foreground transition-colors"
          >
            Projects
          </Link>
          <ChevronRight className="h-4 w-4 shrink-0" />
          {projectId ? (
            <Link
              href={`/projects/${projectId}`}
              className="hover:text-foreground transition-colors font-medium text-foreground truncate max-w-[180px]"
            >
              {project?.name || "Project"}
            </Link>
          ) : (
            <span>Project</span>
          )}
          <ChevronRight className="h-4 w-4 shrink-0" />
          <span className="text-primary font-medium truncate max-w-[200px]">
            {test?.name || "Test Details"}
          </span>
        </nav>

        <Button
          variant="outline"
          size="sm"
          onClick={() => {
            if (projectId) {
              router.push(`/projects/${projectId}`);
            } else {
              router.push("/tests");
            }
          }}
          className="gap-1.5"
        >
          <ArrowLeft className="h-4 w-4" />
          Back
        </Button>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex flex-col items-center justify-center py-20 gap-3">
          <Spinner />
          <p className="text-sm text-muted-foreground animate-pulse">Loading test details...</p>
        </div>
      )}

      {/* Error State */}
      {!isLoading && error && (
        <Card className="border-destructive/30 bg-destructive/5">
          <CardHeader>
            <div className="flex items-center gap-2 text-destructive">
              <AlertCircle className="h-5 w-5 shrink-0" />
              <CardTitle className="text-lg">Unable to Load Test</CardTitle>
            </div>
            <CardDescription className="text-muted-foreground">
              {error}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button
              variant="outline"
              size="sm"
              onClick={() => loadTest()}
              className="gap-2"
            >
              <RefreshCw className="h-4 w-4" />
              Retry
            </Button>

          </CardContent>
        </Card>
      )}

      {/* Loaded Content */}
      {!isLoading && !error && test && (
        <div className="space-y-6">
          {/* Main Test Metadata Component */}
          <TestMetadata
            test={test}
            projectName={project?.name}
            onUpdate={handleTestUpdate}
          />

          {/* Test IR & Builder Foundation Container (Task 11) */}
          <Card className="border-dashed bg-card/50">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Layers className="h-5 w-5 text-primary" />
                  <CardTitle className="text-base font-heading">
                    Test Steps & Canonical IR
                  </CardTitle>
                </div>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-secondary/10 text-secondary font-medium">
                  Test Builder (Upcoming)
                </span>
              </div>
              <CardDescription>
                Test execution steps will be managed through the visual builder and browser recorder.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="rounded-lg bg-muted/40 p-4 text-center sm:text-left flex flex-col sm:flex-row items-center justify-between gap-4">
                <div className="space-y-1">
                  <p className="text-sm font-medium text-foreground">
                    Canonical Test IR: Version {test.ir_version || 1}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Metadata is synchronized and ready for visual step authoring.
                  </p>
                </div>
                <Button variant="outline" size="sm" disabled className="gap-1.5 shrink-0">
                  <Wand2 className="h-3.5 w-3.5" />
                  Launch Builder (Day 6)
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
