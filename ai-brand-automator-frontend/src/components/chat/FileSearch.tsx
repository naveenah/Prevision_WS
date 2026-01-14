'use client';

import { useState } from 'react';

export interface FileResult {
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
      <h2 className="text-lg font-heading font-semibold text-white mb-4">File Search</h2>

      <div className="mb-4">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Search your files..."
          className="input-dark"
        />
        <button
          onClick={handleSearch}
          disabled={isSearching}
          className="mt-2 w-full btn-primary disabled:opacity-50"
        >
          {isSearching ? 'Searching...' : 'Search'}
        </button>
      </div>

      {results.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-brand-silver/70">Results</h3>
          {results.map((result) => (
            <div key={result.id} className="flex items-center justify-between p-3 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors">
              <div>
                <p className="text-sm font-medium text-white">{result.name}</p>
                <p className="text-xs text-brand-silver/50">{result.type}</p>
              </div>
              <span className="text-xs text-brand-electric">
                {(result.relevance * 100).toFixed(0)}% match
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}