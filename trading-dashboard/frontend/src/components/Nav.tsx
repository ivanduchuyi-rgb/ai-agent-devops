'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export function Nav() {
  const pathname = usePathname();

  const navItems = [
    { name: 'Dashboard', href: '/', icon: '📊' },
    { name: 'Trading', href: '/trading', icon: '📈' },
    { name: 'System', href: '/system', icon: '🖥️' },
    { name: 'Settings', href: '/settings', icon: '⚙️' },
    { name: 'Screenshots', href: '/screenshots', icon: '📷' },
  ];

  return (
    <nav className="bg-[#141a23] border-b border-[#2a3344] px-4 py-3 flex items-center gap-4 overflow-x-auto">
      <div className="text-[#00d2ff] font-bold text-lg mr-4 whitespace-nowrap">
        Bot v4.0
      </div>
      {navItems.map((item) => (
        <Link
          key={item.href}
          href={item.href}
          className={`px-3 py-2 rounded-md text-sm font-medium whitespace-nowrap transition-colors ${
            pathname === item.href
              ? 'bg-[#1a2233] text-[#00d2ff]'
              : 'text-[#8899aa] hover:text-[#c0d0e0]'
          }`}
        >
          <span className="mr-1">{item.icon}</span>
          {item.name}
        </Link>
      ))}
    </nav>
  );
}
