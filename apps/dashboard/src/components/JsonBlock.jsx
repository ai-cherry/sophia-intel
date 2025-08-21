// src/components/JsonBlock.jsx
import React from 'react';

export function JsonBlock({ data }) {
  return (
    <details className="mt-2">
      <summary className="cursor-pointer opacity-80 text-sm">View Raw JSON</summary>
      <pre className="bg-black/40 p-3 rounded overflow-auto text-xs mt-2 max-h-64">
        {JSON.stringify(data, null, 2)}
      </pre>
    </details>
  );
}

export default JsonBlock;

