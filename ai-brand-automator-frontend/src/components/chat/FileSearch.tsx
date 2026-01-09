'use client';

import { useState } from 'react';

interface FileResult {
  id: string;
  name: string;
  type: string;
  relevance: number;
}

export function FileSearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<FileResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setIsSearching(true);
    // TODO: Implement file search API
    setTimeout(() => {
      setResults([
        { id: '1', name: 'Brand Guidelines.pdf', type: 'document', relevance: 0.95 },
        { id: '2', name: 'Logo Assets.zip', type: 'archive', relevance: 0.87 },
        { id: '3', name: 'Marketing Plan.docx', type: 'document', relevance: 0.82 },
      ]);
      setIsSearching(false);
    }, 500);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">File Search</h2>

      <div className="mb-4">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Search your files..."
          className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-indigo-500 focus:border-indigo-500"
        />
        <button
          onClick={handleSearch}
          disabled={isSearching}
          className="mt-2 w-full bg-indigo-600 text-white px-3 py-2 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
        >
          {isSearching ? 'Searching...' : 'Search'}
        </button>
      </div>

      {results.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-gray-700">Results</h3>
          {results.map((result) => (
            <div key={result.id} className="flex items-center justify-between p-2 bg-gray-50 rounded-md">
              <div>
                <p className="text-sm font-medium text-gray-900">{result.name}</p>
                <p className="text-xs text-gray-500">{result.type}</p>
              </div>
              <span className="text-xs text-gray-500">
                {(result.relevance * 100).toFixed(0)}% match
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}