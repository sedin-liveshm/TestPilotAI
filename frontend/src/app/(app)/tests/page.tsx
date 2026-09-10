"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Test, Project } from "@/types/domain";
import { projectsApi } from "@/services/projects-api";
import { testsApi } from "@/services/tests-api";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { TestTube2, ArrowRight, Folder, RefreshCw, AlertCircle, Calendar } from "lucide-react";

export default function TestsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [tests, setTests] = useState<Test[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = () => {
    setIsLoading(true);
    setError(null);

    projectsApi
      .getProjects()
      .then((projRes) => {
        const projList = Array.isArray(projRes.data) ? projRes.data : [];
        setProjects(projList);

        const testPromises = projList.map((p) =>
          testsApi
            .getTests(p.id)
            .then((res) => (Array.isArray(res.data) ? res.data : []))
            .catch(() => [])
        );

        return Promise.all(testPromises);
      })
      .then((testResults) => {
        setTests(testResults.flat());
        setIsLoading(false);
      })
      .catch((err) => {
        const message = err instanceof Error ? err.message : "Failed to load tests. Please try again.";
        setError(message);
        setIsLoading(false);
      });
  };

  useEffect(() => {
    let isMounted = true;

    projectsApi
      .getProjects()
      .then((projRes) => {
        const projList = Array.isArray(projRes.data) ? projRes.data : [];
        if (isMounted) setProjects(projList);

        const testPromises = projList.map((p) =>
          testsApi
            .getTests(p.id)
            .then((res) => (Array.isArray(res.data) ? res.data : []))
            .catch(() => [])
        );

        return Promise.all(testPromises);
      })
      .then((testResults) => {
        if (!isMounted) return;
        setTests(testResults.flat());
        setIsLoading(false);
      })
      .catch((err) => {
        if (!isMounted) return;
        const message = err instanceof Error ? err.message : "Failed to load tests. Please try again.";
        setError(message);
        setIsLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);


  const getProjectName = (test: Test) => {
    const pId = test.projectId || test.project_id;
    const found = projects.find((p) => p.id === pId);
    return found?.name || "Unassigned";
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return "Recently";
    try {
      return new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric", year: "numeric" }).format(
        new Date(dateStr)
      );
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="flex flex-col gap-6 max-w-5xl mx-auto w-full">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-heading font-semibold text-primary">Tests</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Browse and manage test metadata across all projects.
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={loadData} disabled={isLoading} className="gap-2">
          <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      {isLoading && (
        <div className="flex flex-col items-center justify-center py-16 gap-3">
          <Spinner />
          <p className="text-sm text-muted-foreground animate-pulse">Loading tests...</p>
        </div>
      )}

      {!isLoading && error && (
        <Card className="border-destructive/30 bg-destructive/5">
          <CardHeader>
            <div className="flex items-center gap-2 text-destructive">
              <AlertCircle className="h-5 w-5 shrink-0" />
              <CardTitle className="text-base">Error Loading Tests</CardTitle>
            </div>
            <CardDescription className="text-muted-foreground">{error}</CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" size="sm" onClick={loadData}>
              Retry
            </Button>
          </CardContent>
        </Card>
      )}

      {!isLoading && !error && tests.length === 0 && (
        <Card className="text-center py-12 border-dashed">
          <CardContent className="flex flex-col items-center gap-3">
            <div className="rounded-full bg-primary/10 p-3 text-primary">
              <TestTube2 className="h-6 w-6" />
            </div>
            <h3 className="text-lg font-heading font-medium text-foreground">No Tests Found</h3>
            <p className="text-sm text-muted-foreground max-w-sm">
              Create tests under a project to manage their metadata and canonical Test IR.
            </p>
            <Link href="/projects">
              <Button className="mt-2">Go to Projects</Button>
            </Link>
          </CardContent>
        </Card>
      )}

      {!isLoading && !error && tests.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2">
          {tests.map((t) => (
            <Card key={t.id} className="hover:shadow-md transition-shadow flex flex-col justify-between">
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="text-base font-heading font-medium text-foreground line-clamp-1">
                    {t.name}
                  </CardTitle>
                  <span className="font-mono text-xs px-2 py-0.5 rounded bg-primary/10 text-primary shrink-0">
                    v{t.ir_version || 1}
                  </span>
                </div>
                <CardDescription className="line-clamp-2 text-xs">
                  {t.description || "No description provided."}
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-2 border-t mt-auto flex items-center justify-between text-xs text-muted-foreground">
                <div className="flex items-center gap-1.5 truncate max-w-[180px]">
                  <Folder className="h-3.5 w-3.5 text-primary shrink-0" />
                  <span className="truncate">{getProjectName(t)}</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1">
                    <Calendar className="h-3.5 w-3.5" />
                    <span>{formatDate(t.createdAt || t.created_at)}</span>
                  </div>
                  <Link href={`/tests/${t.id}`}>
                    <Button variant="ghost" size="sm" className="h-7 px-2 gap-1 text-primary">
                      Details
                      <ArrowRight className="h-3 w-3" />
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

    </div>
  );
}
