"use client";

import { useEffect, useState } from 'react';
import { Project } from '@/types/domain';
import { projectsApi } from '@/services/projects-api';
import { ProjectList } from '@/components/projects/project-list';
import { ProjectLoading } from '@/components/projects/project-loading';
import { ProjectError } from '@/components/projects/project-error';
import { ProjectEmptyState } from '@/components/projects/project-empty-state';

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProjects = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await projectsApi.getProjects();
      setProjects(response.data);
    } catch (err: any) {
      setError(err.message || 'Failed to load projects');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  return (
    <div className="container mx-auto py-8 max-w-5xl">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Projects</h1>
          <p className="text-muted-foreground mt-2">
            Manage your TestPilot AI automation projects.
          </p>
        </div>
      </div>

      {isLoading && <ProjectLoading />}
      
      {!isLoading && error && (
        <ProjectError message={error} onRetry={fetchProjects} />
      )}
      
      {!isLoading && !error && projects.length === 0 && (
        <ProjectEmptyState />
      )}
      
      {!isLoading && !error && projects.length > 0 && (
        <ProjectList projects={projects} />
      )}
    </div>
  );
}
