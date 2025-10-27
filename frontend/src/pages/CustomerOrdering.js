import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import { Search, Plus, ChevronRight } from 'lucide-react';


const RAW_BACKEND = process.env.REACT_APP_BACKEND_URL || '';
const BACKEND_URL = RAW_BACKEND.replace(/\/+$/, ''); 
const API = BACKEND_URL ? `${BACKEND_URL}/api` : '/api';


const BurgerIcon = ({ active }) => (
  <svg viewBox="0 0 64 64" className={`w-8 h-8 ${active ? 'stroke-white' : 'stroke-gray-700'}`} fill="none" strokeWidth="2">
    <path d="M8 32h48M8 28c0-6 6-12 24-12s24 6 24 12M8 36c0 6 6 12 24 12s24-6 24-12" strokeLinecap="round"/>
    <line x1="12" y1="24" x2="52" y2="24"/>
    <line x1="12" y1="40" x2="52" y2="40"/>
  </svg>
);

const PizzaIcon = ({ active }) => (
  <svg viewBox="0 0 64 64" className={`w-8 h-8 ${active ? 'stroke-white' : 'stroke-gray-700'}`} fill="none" strokeWidth="2">
    <circle cx="32" cy="32" r="24"/>
    <line x1="32" y1="8" x2="32" y2="56"/>
    <line x1="8" y1="32" x2="56" y2="32"/>
    <line x1="16" y1="16" x2="48" y2="48"/>
    <line x1="16" y1="48" x2="48" y2="16"/>
    <circle cx="26" cy="26" r="2" fill={active ? 'white' : '#374151'}/>
    <circle cx="38" cy="26" r="2" fill={active ? 'white' : '#374151'}/>
    <circle cx="32" cy="38" r="2" fill={active ? 'white' : '#374151'}/>
  </svg>
);

const DrinkIcon = ({ active }) => (
  <svg viewBox="0 0 64 64" className={`w-8 h-8 ${active ? 'stroke-white' : 'stroke-gray-700'}`} fill="none" strokeWidth="2">
    <path d="M20 12h24v4H20z"/>
    <path d="M22 16l4 40h12l4-40"/>
    <line x1="32" y1="8" x2="32" y2="14"/>
    <path d="M28 20h8" strokeLinecap="round"/>
  </svg>
);

const FriesIcon = ({ active }) => (
  <svg viewBox="0 0 64 64" className={`w-8 h-8 ${active ? 'stroke-white' : 'stroke-gray-700'}`} fill="none" strokeWidth="2">
    <path d="M16 28h32l4 24H12z"/>
    <line x1="24" y1="20" x2="22" y2="28"/>
    <line x1="32" y1="16" x2="32" y2="28"/>
    <line x1="40" y1="20" x2="42" y2="28"/>
    <path d="M16 28l-2 4h36l-2-4" strokeLinecap="round"/>
  </svg>
);

const VeggiesIcon = ({ active }) => (
  <svg viewBox="0 0 64 64" className={`w-8 h-8 ${active ? 'stroke-white' : 'stroke-gray-700'}`} fill="none" strokeWidth="2">
    <ellipse cx="32" cy="36" rx="18" ry="12"/>
    <path d="M20 36c0-3 2-6 5-8s7-3 7-3 4 1 7 3 5 5 5 8" strokeLinecap="round"/>
    <circle cx="26" cy="32" r="3"/>
    <circle cx="38" cy="32" r="3"/>
    <circle cx="32" cy="38" r="2"/>
  </svg>
);

const DessertIcon = ({ active }) => (
  <svg viewBox="0 0 64 64" className={`w-8 h-8 ${active ? 'stroke-white' : 'stroke-gray-700'}`} fill="none" strokeWidth="2">
    <path d="M16 40h32l-4 12H20z"/>
    <path d="M18 36h28c0-8-6-16-14-16s-14 8-14 16z"/>
    <circle cx="26" cy="30" r="1.5" fill={active ? 'white' : '#374151'}/>
    <circle cx="32" cy="28" r="1.5" fill={active ? 'white' : '#374151'}/>
    <circle cx="38" cy="30" r="1.5" fill={active ? 'white' : '#374151'}/>
  </svg>
);


const getCategoryIcon = (category, active = false) => {
  const icons = {
    'Burger': <BurgerIcon active={active} />,
    'Pizza': <PizzaIcon active={active} />,
    'Drink': <DrinkIcon active={active} />,
    'French Fries': <FriesIcon active={active} />,
    'Veggies': <VeggiesIcon active={active} />,
    'Dessert': <DessertIcon active={active} />
  };
  return icons[category] || <BurgerIcon active={active} />;
};

const CustomerOrdering = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [menuItems, setMenuItems] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [cart, setCart] = useState([]);

  useEffect(() => {
    
    const stored = sessionStorage.getItem('customerData');
    if (!stored) {
      navigate('/customer');
      return;
    }

    
    if (location.state?.cart) {
      setCart(location.state.cart);
    }
    
    fetchCategories();
  }, [navigate, location]);

  useEffect(() => {
    if (selectedCategory) {
      fetchMenuItems();
    }
  }, [selectedCategory]);

  const fetchCategories = async () => {
    try {
      
      const response = await axios.get(`${API}/menu/categories/list `);
      
      const cats = response.data?.categories ?? [];
      setCategories(cats);
      if (cats.length > 0 && !selectedCategory) {
        setSelectedCategory(cats[0]);
      }
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchMenuItems = async () => {
    try {
      const response = await axios.get(`${API}/menu?category=${encodeURIComponent(selectedCategory)}`);
      setMenuItems(response.data);
    } catch (error) {
      console.error('Error fetching menu items:', error);
    }
  };

  const addToCart = (item) => {
    const existing = cart.find(i => i.id === item.id);
    if (existing) {
      setCart(cart.map(i => i.id === item.id ? {...i, quantity: i.quantity + 1} : i));
    } else {
      setCart([...cart, {...item, quantity: 1}]);
    }
  };

  const handleGoToCart = () => {
    navigate('/customer/cart', { state: { cart } });
  };

  const filteredItems = menuItems.filter(item => 
    item.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="mobile-container">
      <div className="min-h-screen bg-gray-50">
        
        <div className="bg-white p-6 shadow-sm">
          <h1 className="text-2xl font-semibold text-gray-800 mb-1" data-testid="greeting">Good evening</h1>
          <p className="text-gray-500 text-sm">Place you order here</p>
          
          
          <div className="mt-4 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-3 bg-gray-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              data-testid="search-input"
            />
          </div>
        </div>

        
        <div className="bg-white px-6 py-4 overflow-x-auto">
          <div className="flex space-x-3">
            {categories.map(category => {
              const isActive = selectedCategory === category;
              return (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={`flex flex-col items-center px-5 py-3 rounded-xl text-sm font-medium whitespace-nowrap transition-colors ${
                    isActive
                      ? 'bg-gray-800 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                  data-testid={`category-${category.toLowerCase()}`}
                >
                  <div className="mb-1.5">
                    {getCategoryIcon(category, isActive)}
                  </div>
                  <span>{category}</span>
                </button>
              );
            })}
          </div>
        </div>

        
        <div className="p-6 pb-24">
          <h2 className="text-xl font-bold mb-4">{selectedCategory}</h2>
          <div className="grid grid-cols-2 gap-4">
            {filteredItems.map(item => (
              <div key={item.id} className="bg-white rounded-xl overflow-hidden shadow-sm" data-testid={`menu-item-${item.id}`}>
                <img 
                  src={item.imageUrl} 
                  alt={item.name}
                  className="w-full h-32 object-cover"
                />
                <div className="p-3">
                  <h3 className="font-semibold text-sm mb-1">{item.name}</h3>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-bold">₹ {item.price}</span>
                    <button
                      onClick={() => addToCart(item)}
                      className="bg-gray-200 p-1.5 rounded-lg hover:bg-gray-300 transition-colors"
                      data-testid={`add-to-cart-${item.id}`}
                    >
                      <Plus className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        
        {cart.length > 0 && (
          <button
            onClick={handleGoToCart}
            className="fixed bottom-8 right-8 bg-gray-800 text-white pl-6 pr-4 py-3 rounded-full shadow-xl hover:bg-gray-900 transition-all flex items-center space-x-2 z-50"
            data-testid="next-button"
          >
            <span className="font-medium">Next ({cart.length})</span>
            <ChevronRight className="w-5 h-5" />
          </button>
        )}
      </div>
    </div>
  );
};

export default CustomerOrdering;

