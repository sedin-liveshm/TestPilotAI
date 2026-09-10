import { Card, CardHeader, CardContent, CardFooter } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';

export function ProjectLoading() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {Array.from({ length: 6 }).map((_, i) => (
        <Card key={i} className="flex flex-col h-full">
          <CardHeader>
            <Skeleton className="h-6 w-2/3 mb-2" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-4/5 mt-1" />
          </CardHeader>
          <CardContent className="flex-1">
            <Skeleton className="h-4 w-1/2" />
            <Skeleton className="h-4 w-1/3 mt-2" />
          </CardContent>
          <CardFooter>
            <Skeleton className="h-10 w-full" />
          </CardFooter>
        </Card>
      ))}
    </div>
  );
}
