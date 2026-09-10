import { AlertCircle } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface ProjectErrorProps {
  message?: string;
  onRetry?: () => void;
}

export function ProjectError({ message = 'Failed to load projects. Please try again later.', onRetry }: ProjectErrorProps) {
  return (
    <Card className="flex flex-col items-center justify-center p-12 text-center border-destructive">
      <CardHeader>
        <div className="mx-auto mb-4 bg-destructive/10 p-4 rounded-full w-16 h-16 flex items-center justify-center">
          <AlertCircle className="w-8 h-8 text-destructive" />
        </div>
        <CardTitle className="text-2xl text-destructive">Error Loading Projects</CardTitle>
        <CardDescription className="max-w-md mx-auto mt-2">
          {message}
        </CardDescription>
      </CardHeader>
      {onRetry && (
        <CardContent>
          <Button variant="outline" onClick={onRetry}>Try Again</Button>
        </CardContent>
      )}
    </Card>
  );
}
