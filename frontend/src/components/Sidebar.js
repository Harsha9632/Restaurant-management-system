import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { BarChart3, Users, ShoppingBag, UtensilsCrossed, Home } from 'lucide-react';

const Sidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { icon: BarChart3, label: 'Analytics', path: '/restaurant/dashboard' },
    { icon: Users, label: 'Tables', path: '/restaurant/tables' },
    { icon: ShoppingBag, label: 'Orders', path: '/restaurant/orders' },
    { icon: UtensilsCrossed, label: 'Menu', path: '/restaurant/menu' },
  ];

  return (
    <div className="w-20 bg-white border-r border-gray-200 flex flex-col items-center py-6 space-y-6">
      {/* Logo */}
      <div className="w-12 h-12 bg-gradient-to-br from-yellow-600 to-yellow-500 rounded-full flex items-center justify-center mb-2">
        <span className="text-amber-900 font-bold text-xl">HP</span>
      </div>

      {/* Menu Items */}
      <div className="flex flex-col space-y-4">
        {menuItems.map((item, index) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          
          return (
            <button
              key={index}
              onClick={() => navigate(item.path)}
              className={`p-3 rounded-xl transition-all ${
                isActive 
                  ? 'bg-blue-50 text-blue-600' 
                  : 'text-gray-900 hover:text-gray-700 hover:bg-gray-50'
              }`}
              data-testid={`sidebar-${item.label.toLowerCase()}`}
              title={item.label}
            >
              <Icon className="w-6 h-6" strokeWidth={2.5} />
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default Sidebar;