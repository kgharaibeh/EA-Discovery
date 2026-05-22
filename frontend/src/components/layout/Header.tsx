import React from 'react';
import { Search } from 'lucide-react';
import { useFilterStore } from '../../stores/useFilterStore';

export default function Header() {
  const { globalSearch, setGlobalSearch } = useFilterStore();

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-3 flex items-center justify-between shrink-0">
      <div className="text-sm text-gray-500">
        <span className="font-medium text-gray-900">EA Discovery</span>
      </div>

      <div className="relative w-72">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        <input
          type="text"
          placeholder="Search assets, scans..."
          value={globalSearch}
          onChange={(e) => setGlobalSearch(e.target.value)}
          className="w-full pl-9 pr-4 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>
    </header>
  );
}
