import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Network,
  Server,
  Radar,
  Brain,
  GitCompare,
  KeyRound,
  Download,
  Shield,
} from 'lucide-react';

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/topology', label: 'Topology', icon: Network },
  { to: '/assets', label: 'Assets', icon: Server },
  { to: '/scans', label: 'Scans', icon: Radar },
  { to: '/intelligence', label: 'Intelligence', icon: Brain },
  { to: '/drift', label: 'Drift', icon: GitCompare },
  { to: '/credentials', label: 'Credentials', icon: KeyRound },
  { to: '/exports', label: 'Exports', icon: Download },
];

export default function Sidebar() {
  return (
    <aside className="w-64 bg-[#1e293b] flex flex-col shrink-0">
      <div className="flex items-center gap-2 px-6 py-5 border-b border-slate-700">
        <Shield className="h-6 w-6 text-blue-400" />
        <span className="text-lg font-semibold text-white">EA Discovery</span>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-slate-700 text-white'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`
            }
          >
            <item.icon className="h-5 w-5 shrink-0" />
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
