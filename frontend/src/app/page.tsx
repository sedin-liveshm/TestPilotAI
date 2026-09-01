import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-heading font-semibold text-primary">Dashboard</h1>
        <Button>New Project</Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Total Tests</CardDescription>
            <CardTitle className="text-4xl font-heading">142</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-xs text-muted-foreground">+12% from last month</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Passed</CardDescription>
            <CardTitle className="text-4xl font-heading text-green-600">128</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-xs text-muted-foreground">90% success rate</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Failed</CardDescription>
            <CardTitle className="text-4xl font-heading text-destructive">14</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-xs text-muted-foreground">Requires attention</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>AI Generated</CardDescription>
            <CardTitle className="text-4xl font-heading text-secondary">86</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-xs text-muted-foreground">60% of total tests</div>
          </CardContent>
        </Card>
      </div>
      
      <div className="grid gap-6 md:grid-cols-2">
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle className="font-heading">Recent Executions</CardTitle>
            <CardDescription>Latest test runs across your projects.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-muted-foreground">No recent executions found.</div>
          </CardContent>
        </Card>
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle className="font-heading">AI Insights</CardTitle>
            <CardDescription>Suggestions to improve your test coverage.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-muted-foreground">Generate more tests to see insights.</div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
