// src/components/ResultCard.jsx
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card.jsx";
import { Badge } from "@/components/ui/badge.jsx";
import { Alert, AlertDescription } from "@/components/ui/alert.jsx";
import { ExternalLink, AlertCircle, CheckCircle, Clock } from "lucide-react";

/**
 * Component to safely display API results without [object Object]
 * @param {Object} props
 * @param {import('../lib/types.js').ResearchResult} props.data
 */
export function ResultCard({ data }) {
  if (!data) {
    return (
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>No data to display</AlertDescription>
      </Alert>
    );
  }

  const hasErrors = data.errors && data.errors.length > 0;
  const hasResults = data.results && data.results.length > 0;

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Research Results</CardTitle>
          <div className="flex items-center gap-2">
            <Badge 
              variant={data.status === 'success' ? 'default' : 'destructive'}
              className="capitalize"
            >
              {data.status === 'success' ? (
                <CheckCircle className="h-3 w-3 mr-1" />
              ) : (
                <AlertCircle className="h-3 w-3 mr-1" />
              )}
              {data.status}
            </Badge>
            {data.execution_time_ms && (
              <Badge variant="outline">
                <Clock className="h-3 w-3 mr-1" />
                {data.execution_time_ms}ms
              </Badge>
            )}
          </div>
        </div>
        {data.query && (
          <p className="text-sm text-muted-foreground">
            Query: <code className="bg-muted px-1 py-0.5 rounded">{data.query}</code>
          </p>
        )}
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Error Display */}
        {hasErrors && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              <div className="space-y-1">
                {data.errors.map((error, idx) => (
                  <div key={idx} className="text-sm">
                    {error.provider && <strong>[{error.provider}]</strong>} 
                    {error.code}: {error.message || 'Unknown error'}
                  </div>
                ))}
              </div>
            </AlertDescription>
          </Alert>
        )}

        {/* Results Display */}
        {hasResults && (
          <div className="space-y-3">
            <h4 className="font-medium">Results ({data.results.length})</h4>
            <div className="space-y-2">
              {data.results.map((result, idx) => (
                <div key={idx} className="border rounded-lg p-3 space-y-2">
                  <div className="flex items-start justify-between">
                    <h5 className="font-medium text-sm leading-tight">
                      {result.title || 'Untitled'}
                    </h5>
                    {result.url && (
                      <a
                        href={result.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 ml-2 flex-shrink-0"
                      >
                        <ExternalLink className="h-4 w-4" />
                      </a>
                    )}
                  </div>
                  {result.snippet && (
                    <p className="text-sm text-muted-foreground">
                      {result.snippet}
                    </p>
                  )}
                  {result.url && (
                    <p className="text-xs text-muted-foreground truncate">
                      {result.url}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Summary Display */}
        {data.summary && data.summary.text && (
          <div className="space-y-2">
            <h4 className="font-medium">Summary</h4>
            <p className="text-sm text-muted-foreground">{data.summary.text}</p>
            {data.summary.confidence > 0 && (
              <p className="text-xs text-muted-foreground">
                Confidence: {Math.round(data.summary.confidence * 100)}%
              </p>
            )}
          </div>
        )}

        {/* Raw JSON Fallback (Collapsible) */}
        <details className="mt-4">
          <summary className="cursor-pointer text-sm text-muted-foreground hover:text-foreground">
            View Raw Response
          </summary>
          <pre className="mt-2 p-3 bg-muted rounded-lg text-xs overflow-auto max-h-64">
            {JSON.stringify(data, null, 2)}
          </pre>
        </details>
      </CardContent>
    </Card>
  );
}

export default ResultCard;

