import React from 'react';
import { Sun, Moon, Monitor } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';

export const ThemeToggle: React.FC = () => {
    const { theme, setTheme } = useTheme();

    return (
        <div className="flex items-center gap-1 bg-gray-100 dark:bg-gray-800/80 p-1 rounded-lg border border-gray-200 dark:border-gray-700 transition-colors">
            <button
                onClick={() => setTheme('light')}
                className={`p-1.5 rounded-md transition-all outline-none focus:ring-2 focus:ring-primary-500 ${theme === 'light'
                    ? 'bg-white text-yellow-500 shadow-sm dark:bg-gray-700'
                    : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
                    }`}
                title="Modo Claro"
            >
                <Sun className="w-4 h-4" />
            </button>
            <button
                onClick={() => setTheme('system')}
                className={`p-1.5 rounded-md transition-all outline-none focus:ring-2 focus:ring-primary-500 ${theme === 'system'
                    ? 'bg-white text-primary-500 shadow-sm dark:bg-gray-700'
                    : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
                    }`}
                title="Padrão do Sistema"
            >
                <Monitor className="w-4 h-4" />
            </button>
            <button
                onClick={() => setTheme('dark')}
                className={`p-1.5 rounded-md transition-all outline-none focus:ring-2 focus:ring-primary-500 ${theme === 'dark'
                    ? 'bg-white text-indigo-500 shadow-sm dark:bg-gray-700 dark:text-indigo-400'
                    : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
                    }`}
                title="Modo Escuro"
            >
                <Moon className="w-4 h-4" />
            </button>
        </div>
    );
};
