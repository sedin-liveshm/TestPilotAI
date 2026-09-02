import Link from 'next/link';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Project } from '@/types/domain';

interface ProjectCardProps {
  project: Project;
}

export function ProjectCard({ project }: ProjectCardProps) {
  return (
    <Card className="flex flex-col h-full hover:border-primary/50 transition-colors">
      <CardHeader>
        <CardTitle className="text-xl">{project.name}</CardTitle>
        {project.description && (
          <CardDescription className="line-clamp-2">{project.description}</CardDescription>
        )}
      </CardHeader>
      <CardContent className="flex-1">
        <div className="text-sm text-muted-foreground">
          <p>Base URL: {project.target_base_url}</p>
          <p>Created: {new Date(project.created_at).toLocaleDateString()}</p>
        </div>
      </CardContent>
      <CardFooter>
        <Link href={`/projects/${project.id}`} passHref legacyBehavior>
          <Button className="w-full">
            View Project
          </Button>
        </Link>
      </CardFooter>
    </Card>
  );
}
