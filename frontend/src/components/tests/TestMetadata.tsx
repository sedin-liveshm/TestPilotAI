"use client";

import { useState } from "react";
import { Test } from "@/types/domain";
import { testsApi } from "@/services/tests-api";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Pencil, Check, X, AlertCircle, Loader2, Folder, Calendar, Clock, Tag } from "lucide-react";
import { cn } from "@/lib/utils";

interface TestMetadataProps {
  test: Test;
  projectName?: string;
  onUpdate?: (updatedTest: Test) => void | Promise<void>;
  isEditable?: boolean;
  className?: string;
}

export function TestMetadata({
  test,
  projectName,
  onUpdate,
  isEditable = true,
  className,
}: TestMetadataProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState(test.name);
  const [description, setDescription] = useState(test.description || "");
  const [isSaving, setIsSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleStartEditing = () => {
    setName(test.name);
    setDescription(test.description || "");
    setValidationError(null);
    setSaveError(null);
    setIsEditing(true);
  };

  const handleCancel = () => {
    setName(test.name);
    setDescription(test.description || "");
    setValidationError(null);
    setSaveError(null);
    setIsEditing(false);
  };

  const validate = (): boolean => {
    const trimmedName = name.trim();
    if (!trimmedName) {
      setValidationError("Test name is required.");
      return false;
    }
    if (trimmedName.length > 255) {
      setValidationError("Test name cannot exceed 255 characters.");
      return false;
    }
    if (description.length > 2000) {
      setValidationError("Description cannot exceed 2000 characters.");
      return false;
    }
    setValidationError(null);
    return true;
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setIsSaving(true);
    setSaveError(null);

    try {
      const payload = {
        name: name.trim(),
        description: description.trim() || undefined,
      };

      const response = await testsApi.updateTest(test.id, payload);
      const updatedTest = response.data;

      if (onUpdate) {
        await onUpdate(updatedTest);
      }

      setIsEditing(false);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to save test metadata. Please try again.";
      setSaveError(message);
    } finally {
      setIsSaving(false);
    }
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return "N/A";
    try {
      return new Intl.DateTimeFormat("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      }).format(new Date(dateStr));
    } catch {
      return dateStr;
    }
  };

  return (
    <Card className={cn("w-full transition-all shadow-sm", className)}>
      <CardHeader className="flex flex-row items-start justify-between pb-3">
        <div>
          <CardTitle className="text-xl font-heading font-semibold text-primary">
            Test Details
          </CardTitle>
          <CardDescription>
            Basic metadata and canonical Test IR identity.
          </CardDescription>
        </div>

        {isEditable && !isEditing && (
          <Button
            variant="outline"
            size="sm"
            onClick={handleStartEditing}
            className="gap-1.5"
            aria-label="Edit test metadata"
          >
            <Pencil className="h-3.5 w-3.5" />
            Edit
          </Button>
        )}
      </CardHeader>

      {isEditing ? (
        <form onSubmit={handleSave}>
          <CardContent className="space-y-4">
            {saveError && (
              <div
                className="flex items-center gap-2 rounded-lg border border-destructive/20 bg-destructive/10 p-3 text-sm text-destructive"
                role="alert"
              >
                <AlertCircle className="h-4 w-4 shrink-0" />
                <span>{saveError}</span>
              </div>
            )}

            <div className="space-y-1.5">
              <Label htmlFor="test-name" className="text-foreground">
                Test Name <span className="text-destructive">*</span>
              </Label>
              <Input
                id="test-name"
                value={name}
                onChange={(e) => {
                  setName(e.target.value);
                  if (validationError) setValidationError(null);
                }}
                disabled={isSaving}
                placeholder="e.g. Valid User Login"
                aria-invalid={!!validationError}
              />
              {validationError && (
                <p className="text-xs text-destructive mt-1">{validationError}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <div className="flex justify-between items-center">
                <Label htmlFor="test-description" className="text-foreground">
                  Description
                </Label>
                <span className="text-xs text-muted-foreground">
                  {description.length} / 2000
                </span>
              </div>
              <Textarea
                id="test-description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                disabled={isSaving}
                placeholder="Describe what user flow or requirement this test verifies..."
                className="min-h-[100px]"
                maxLength={2000}
              />
            </div>

            <div className="space-y-1.5">
              <Label className="text-muted-foreground">Associated Project</Label>
              <div className="flex items-center gap-2 text-sm text-foreground bg-muted/30 px-3 py-2 rounded-lg border">
                <Folder className="h-4 w-4 text-muted-foreground" />
                <span>{projectName || test.projectId || test.project_id || "Unassigned"}</span>
              </div>
            </div>
          </CardContent>

          <CardFooter className="flex justify-end gap-2 border-t pt-4">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={handleCancel}
              disabled={isSaving}
            >
              <X className="h-3.5 w-3.5 mr-1" />
              Cancel
            </Button>
            <Button
              type="submit"
              size="sm"
              disabled={isSaving}
              className="gap-1.5"
            >
              {isSaving ? (
                <>
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Check className="h-3.5 w-3.5" />
                  Save Changes
                </>
              )}
            </Button>
          </CardFooter>
        </form>
      ) : (
        <CardContent className="space-y-5">
          <div className="space-y-1">
            <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
              Test Name
            </span>
            <p className="text-lg font-semibold text-foreground font-heading">
              {test.name}
            </p>
          </div>

          <div className="space-y-1">
            <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
              Description
            </span>
            <p className="text-sm text-foreground whitespace-pre-line leading-relaxed">
              {test.description ? (
                test.description
              ) : (
                <span className="text-muted-foreground italic">No description provided.</span>
              )}
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-3 border-t">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Folder className="h-4 w-4 text-primary shrink-0" />
              <div>
                <span className="text-xs block text-muted-foreground">Project</span>
                <span className="font-medium text-foreground">
                  {projectName || test.projectId || test.project_id || "Unassigned"}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Tag className="h-4 w-4 text-primary shrink-0" />
              <div>
                <span className="text-xs block text-muted-foreground">Test IR Version</span>
                <span className="font-mono text-xs font-semibold px-2 py-0.5 rounded bg-primary/10 text-primary">
                  v{test.ir_version || 1}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Calendar className="h-4 w-4 text-muted-foreground shrink-0" />
              <div>
                <span className="text-xs block text-muted-foreground">Created</span>
                <span className="text-foreground text-xs">
                  {formatDate(test.createdAt || test.created_at)}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Clock className="h-4 w-4 text-muted-foreground shrink-0" />
              <div>
                <span className="text-xs block text-muted-foreground">Last Updated</span>
                <span className="text-foreground text-xs">
                  {formatDate(test.updatedAt || test.updated_at)}
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      )}
    </Card>
  );
}
