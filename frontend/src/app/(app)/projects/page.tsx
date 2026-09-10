"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Project } from "@/types/domain";
import { projectsApi } from "@/services/projects-api";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { FolderGit2, ArrowRight, Globe, Calendar, RefreshCw, AlertCircle } from "lucide-react";

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadProjects = () => {
    setIsLoading(true);
    setError(null);
    projectsApi
      .getProjects()
      .then((response) => {
        setProjects(Array.isArray(response.data) ? response.data : []);
        setIsLoading(false);
      })
      .catch((err) => {
        const message = err instanceof Error ? err.message : "Failed to load projects. Please try again.";
        setError(message);
        setIsLoading(false);
      });
  };

  useEffect(() => {
    let isMounted = true;
    projectsApi
      .getProjects()
      .then((response) => {
        if (!isMounted) return;
        setProjects(Array.isArray(response.data) ? response.data : []);
        setIsLoading(false);
      })
      .catch((err) => {
        if (!isMounted) return;
        const message = err instanceof Error ? err.message : "Failed to load projects. Please try again.";
        setError(message);
        setIsLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);


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
          <h1 className="text-3xl font-heading font-semibold text-primary">Projects</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Manage your web applications and their automated test suites.
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={loadProjects} disabled={isLoading} className="gap-2">
          <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      {isLoading && (
        <div className="flex flex-col items-center justify-center py-16 gap-3">
          <Spinner />
          <p className="text-sm text-muted-foreground animate-pulse">Loading projects...</p>
        </div>
      )}

      {!isLoading && error && (
        <Card className="border-destructive/30 bg-destructive/5">
          <CardHeader>
            <div className="flex items-center gap-2 text-destructive">
              <AlertCircle className="h-5 w-5 shrink-0" />
              <CardTitle className="text-base">Error Loading Projects</CardTitle>
            </div>
            <CardDescription className="text-muted-foreground">{error}</CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" size="sm" onClick={loadProjects}>
              Retry
            </Button>
          </CardContent>
        </Card>
      )}

      {!isLoading && !error && projects.length === 0 && (
        <Card className="text-center py-12 border-dashed">
          <CardContent className="flex flex-col items-center gap-3">
            <div className="rounded-full bg-primary/10 p-3 text-primary">
              <FolderGit2 className="h-6 w-6" />
            </div>
            <h3 className="text-lg font-heading font-medium text-foreground">No Projects Found</h3>
            <p className="text-sm text-muted-foreground max-w-sm">
              Your projects will appear here. Each project organizes tests and automation suites.
            </p>
          </CardContent>
        </Card>
      )}

      {!isLoading && !error && projects.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2">
          {projects.map((p) => (
            <Card key={p.id} className="hover:shadow-md transition-shadow flex flex-col justify-between">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg font-heading font-semibold text-primary line-clamp-1">
                  {p.name}
                </CardTitle>
                <CardDescription className="line-clamp-2 text-xs">
                  {p.description || "No description provided."}
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-2 border-t mt-auto flex items-center justify-between text-xs text-muted-foreground">
                <div className="flex items-center gap-1.5 truncate max-w-[200px]">
                  {(p.baseUrl || p.base_url) ? (
                    <>
                      <Globe className="h-3.5 w-3.5 text-primary shrink-0" />
                      <span className="truncate">{p.baseUrl || p.base_url}</span>
                    </>
                  ) : (
                    <>
                      <Calendar className="h-3.5 w-3.5" />
                      <span>{formatDate(p.createdAt || p.created_at)}</span>
                    </>
                  )}
                </div>
                <Link href={`/projects/${p.id}`}>
                  <Button variant="ghost" size="sm" className="h-7 px-2 gap-1 text-primary">
                    View
                    <ArrowRight className="h-3 w-3" />
                  </Button>
                </Link>

              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
