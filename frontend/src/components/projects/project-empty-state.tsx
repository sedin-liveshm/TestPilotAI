import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { FolderOpen } from 'lucide-react';

export function ProjectEmptyState() {
  return (
    <Card className="flex flex-col items-center justify-center p-12 text-center border-dashed">
      <CardHeader>
        <div className="mx-auto mb-4 bg-muted p-4 rounded-full w-16 h-16 flex items-center justify-center">
          <FolderOpen className="w-8 h-8 text-muted-foreground" />
        </div>
        <CardTitle className="text-2xl">No projects yet</CardTitle>
        <CardDescription className="max-w-md mx-auto mt-2">
          Create or connect a project to start creating automated tests.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {/* Placeholder for future project creation feature */}
        <Button disabled>Create Project</Button>
      </CardContent>
    </Card>
  );
}
