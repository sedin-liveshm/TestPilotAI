"use client";

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, ExternalLink, Settings, PlayCircle, BarChart3, ShieldCheck } from 'lucide-react';
import { Project } from '@/types/domain';
import { projectsApi } from '@/services/projects-api';
import { useUIStore } from '@/store/ui-store';
import { ProjectLoading } from '@/components/projects/project-loading';
import { ProjectError } from '@/components/projects/project-error';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';

export default function ProjectDetailPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.projectId as string;
  const { setActiveProject } = useUIStore();
  
  const [project, setProject] = useState<Project | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProject = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await projectsApi.getProject(projectId);
      setProject(response.data);
      setActiveProject(projectId); // Set context for navigation/sidebar
    } catch (err: any) {
      setError(err.message || 'Failed to load project details');
      if (err.status === 404) {
        router.push('/projects');
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (projectId) {
      fetchProject();
    }
    // Cleanup active project when leaving
    return () => setActiveProject(null);
  }, [projectId]);

  if (isLoading) {
    return (
      <div className="container mx-auto py-8 max-w-5xl">
        <ProjectLoading />
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="container mx-auto py-8 max-w-5xl">
        <Link href="/projects" passHref legacyBehavior>
          <Button variant="ghost" className="mb-6 -ml-4">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Projects
          </Button>
        </Link>
        <ProjectError message={error || 'Project not found'} onRetry={fetchProject} />
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 max-w-5xl space-y-8">
      {/* Header section */}
      <div>
        <Link href="/projects" passHref legacyBehavior>
          <Button variant="ghost" className="mb-4 -ml-4 text-muted-foreground">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Projects
          </Button>
        </Link>
        
        <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{project.name}</h1>
            {project.description && (
              <p className="text-muted-foreground mt-2 max-w-2xl">{project.description}</p>
            )}
            <div className="flex items-center gap-2 mt-4 text-sm">
              <span className="font-medium">Base URL:</span>
              <a 
                href={project.target_base_url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-primary hover:underline flex items-center"
              >
                {project.target_base_url}
                <ExternalLink className="ml-1 h-3 w-3" />
              </a>
            </div>
          </div>
          
          <Button>
            <PlayCircle className="mr-2 h-4 w-4" />
            Run Suite
          </Button>
        </div>
      </div>

      {/* Modules Dashboard Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="hover:border-primary/50 transition-colors cursor-pointer" onClick={() => router.push(`/projects/${projectId}/tests`)}>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">Test Cases</CardTitle>
              <ShieldCheck className="h-5 w-5 text-muted-foreground" />
            </div>
            <CardDescription>Manage and create Test IR specifications</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Access the Visual Builder and manage your testing scenarios.</p>
          </CardContent>
        </Card>

        <Card className="hover:border-primary/50 transition-colors cursor-pointer" onClick={() => router.push(`/projects/${projectId}/runs`)}>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">Execution Runs</CardTitle>
              <PlayCircle className="h-5 w-5 text-muted-foreground" />
            </div>
            <CardDescription>View test history and execution steps</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Monitor Playwright executions, artifacts, and AI self-healing events.</p>
          </CardContent>
        </Card>

        <Card className="hover:border-primary/50 transition-colors cursor-pointer" onClick={() => router.push(`/projects/${projectId}/reports`)}>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">Coverage & Reports</CardTitle>
              <BarChart3 className="h-5 w-5 text-muted-foreground" />
            </div>
            <CardDescription>Analyze requirement coverage and metrics</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Detailed pass rates, performance trends, and coverage analytics.</p>
          </CardContent>
        </Card>

        <Card className="hover:border-primary/50 transition-colors cursor-pointer" onClick={() => router.push(`/projects/${projectId}/settings`)}>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">Project Settings</CardTitle>
              <Settings className="h-5 w-5 text-muted-foreground" />
            </div>
            <CardDescription>Configure project variables and integration</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Manage environment variables, access control, and integrations.</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
