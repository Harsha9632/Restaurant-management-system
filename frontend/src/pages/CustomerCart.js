import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import { Plus, Minus, ChevronRight, X, Search } from 'lucide-react';
import CookingInstructionsPopup from '@/components/CookingInstructionsPopup';

const RAW_BACKEND = process.env.REACT_APP_BACKEND_URL || '';
const BACKEND_URL = RAW_BACKEND.replace(/\/+$/, ''); 
const API = BACKEND_URL ? `${BACKEND_URL}/api` : '/api';


const CustomerCart = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [cart, setCart] = useState([]);
  const [orderType, setOrderType] = useState('takeaway'); 
  const [showCookingInstructions, setShowCookingInstructions] = useState(false);
  const [cookingInstructions, setCookingInstructions] = useState('');
  const [customerData, setCustomerData] = useState(null);
  const [tableNumber, setTableNumber] = useState('');
  const [swipePosition, setSwipePosition] = useState(0);
  const [isDragging, setIsDragging] = useState(false);

  useEffect(() => {
    const stored = sessionStorage.getItem('customerData');
    if (!stored) {
      navigate('/customer');
      return;
    }
    setCustomerData(JSON.parse(stored));

    if (location.state?.cart) {
      setCart(location.state.cart);
    } else {
      navigate('/customer/menu');
    }
  }, [navigate, location]);

  const updateQuantity = (itemId, delta) => {
    setCart(prevCart => {
      const newCart = prevCart.map(item => {
        if (item.id === itemId) {
          const newQuantity = item.quantity + delta;
          return newQuantity > 0 ? {...item, quantity: newQuantity} : null;
        }
        return item;
      }).filter(item => item !== null);
      
      
      if (newCart.length === 0) {
        navigate('/customer/menu');
        return prevCart;
      }
      
      return newCart;
    });
  };

  const removeItem = (itemId) => {
    const newCart = cart.filter(item => item.id !== itemId);
    if (newCart.length === 0) {
      navigate('/customer/menu');
    } else {
      setCart(newCart);
    }
  };

  const calculateTotal = () => {
    const itemTotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const taxes = itemTotal * 0.05;
    const deliveryCharge = orderType === 'takeaway' ? 50 : 0;
    const prepTime = cart.reduce((sum, item) => sum + (item.averagePreparationTime * item.quantity), 0);
    return { itemTotal, taxes, deliveryCharge, grandTotal: itemTotal + taxes + deliveryCharge, prepTime };
  };

  const handlePlaceOrder = async () => {
    
    if (orderType === 'dinein' && !tableNumber) {
      alert('Please enter table number');
      setSwipePosition(0);
      setIsDragging(false);
      return;
    }

    try {
      const orderData = {
        customerName: customerData.name,
        customerPhone: customerData.phone,
        customerAddress: customerData.address,
        type: orderType,
        tableNumber: orderType === 'dinein' ? parseInt(tableNumber) : null,
        items: cart.map(item => ({
          menuItemId: item.id,
          menuItemName: item.name,
          quantity: item.quantity,
          price: item.price,
          cookingInstructions: cookingInstructions
        }))
      };

      console.log('Placing order to:', `${API}/orders`, orderData);

      await axios.post(`${API}/orders`, orderData);
      sessionStorage.removeItem('customerData');
      navigate('/customer/thank-you');
    } catch (error) {
      console.error('Error placing order:', error);
      alert('Failed to place order: ' + (error.response?.data?.detail || error.message));
      setSwipePosition(0);
      setIsDragging(false);
    }
  };

  const handleSwipeStart = (e) => {
    setIsDragging(true);
  };

  const handleSwipeMove = (e) => {
    if (!isDragging) return;
    
    const touch = e.touches ? e.touches[0] : e;
    const container = e.currentTarget.parentElement;
    const containerWidth = container.offsetWidth;
    const buttonWidth = 60;
    const maxSwipe = containerWidth - buttonWidth - 24;
    
    const rect = container.getBoundingClientRect();
    const x = touch.clientX - rect.left - buttonWidth / 2;
    const newPosition = Math.max(0, Math.min(x, maxSwipe));
    
    setSwipePosition(newPosition);
    
   
    if (newPosition > maxSwipe * 0.8) {
      setIsDragging(false);
      console.log('Swipe completed! Placing order...');
      handlePlaceOrder();
    }
  };

  const handleSwipeEnd = () => {
    setIsDragging(false);
    
    setSwipePosition(0);
  };

  const totals = calculateTotal();

  return (
    <div className="mobile-container">
      <div className="min-h-screen bg-gray-50 flex flex-col">
        
        <div className="bg-white p-6 shadow-sm">
          <h1 className="text-2xl font-semibold text-gray-800 mb-1">Good evening</h1>
          <p className="text-gray-500 text-sm mb-4">Place you order here</p>
          
          
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search"
              className="w-full pl-10 pr-4 py-3 bg-gray-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6 pb-32">
          <div className="space-y-4 mb-6">
            {cart.map(item => (
              <div key={item.id} className="bg-white rounded-xl shadow-sm flex items-center p-4 relative">
                <img src={item.imageUrl} alt={item.name} className="w-24 h-24 rounded-lg object-cover" />
                <div className="flex-1 ml-4">
                  <h3 className="font-bold text-lg mb-1">{item.name}</h3>
                  <p className="text-gray-600 font-semibold">₹ {item.price}</p>
                  <p className="text-xs text-gray-400 mt-1">{item.averagePreparationTime}"</p>
                </div>
                <div className="flex items-center space-x-3">
                  <button
                    onClick={() => updateQuantity(item.id, -1)}
                    className="w-8 h-8 bg-gray-200 rounded flex items-center justify-center hover:bg-gray-300"
                    data-testid={`decrease-${item.id}`}
                  >
                    <Minus className="w-4 h-4" />
                  </button>
                  <span className="w-8 text-center font-bold" data-testid={`quantity-${item.id}`}>{item.quantity}</span>
                  <button
                    onClick={() => updateQuantity(item.id, 1)}
                    className="w-8 h-8 bg-gray-200 rounded flex items-center justify-center hover:bg-gray-300"
                    data-testid={`increase-${item.id}`}
                  >
                    <Plus className="w-4 h-4" />
                  </button>
                </div>
                <button
                  onClick={() => removeItem(item.id)}
                  className="absolute top-3 right-3 w-8 h-8 bg-red-500 rounded-full flex items-center justify-center hover:bg-red-600 transition-colors"
                  data-testid={`remove-${item.id}`}
                >
                  <X className="w-5 h-5 text-white" />
                </button>
              </div>
            ))}
          </div>

          <button
            onClick={() => setShowCookingInstructions(true)}
            className="w-full text-left text-sm text-blue-600 mb-6 hover:underline"
            data-testid="add-cooking-instructions-btn"
          >
            Add cooking instructions (optional)
          </button>

          <div className="mb-6">
            <div className="relative bg-gray-100 rounded-full p-1 flex">
              <button
                onClick={() => setOrderType('dinein')}
                className={`flex-1 py-3 rounded-full font-medium transition-all ${
                  orderType === 'dinein'
                    ? 'bg-white text-gray-800 shadow-sm'
                    : 'text-gray-600'
                }`}
                data-testid="dine-in-btn"
              >
                Dine In
              </button>
              <button
                onClick={() => setOrderType('takeaway')}
                className={`flex-1 py-3 rounded-full font-medium transition-all ${
                  orderType === 'takeaway'
                    ? 'bg-white text-gray-800 shadow-sm'
                    : 'text-gray-600'
                }`}
                data-testid="take-away-btn"
              >
                Take Away
              </button>
            </div>
          </div>

          {orderType === 'dinein' && (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Table Number <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                placeholder="Enter table number (Required)"
                value={tableNumber}
                onChange={(e) => setTableNumber(e.target.value)}
                className={`w-full px-4 py-3 border-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  !tableNumber ? 'border-red-300 bg-red-50' : 'border-gray-300'
                }`}
                data-testid="table-number-input"
                min="1"
                max="30"
                required
              />
              {!tableNumber && (
                <p className="text-red-500 text-sm mt-2 font-medium">⚠️ Please enter a table number to continue</p>
              )}
            </div>
          )}

          <div className="bg-white rounded-xl p-4 mb-6 space-y-2 shadow-sm">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Item Total</span>
              <span className="font-medium">₹ {totals.itemTotal.toFixed(2)}</span>
            </div>
            {orderType === 'takeaway' && (
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Delivery Charge</span>
                <span className="font-medium">₹ {totals.deliveryCharge.toFixed(2)}</span>
              </div>
            )}
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Taxes</span>
              <span className="font-medium">₹ {totals.taxes.toFixed(2)}</span>
            </div>
            <div className="border-t pt-2 flex justify-between font-bold">
              <span>Grand Total</span>
              <span data-testid="grand-total">₹ {totals.grandTotal.toFixed(2)}</span>
            </div>
          </div>

          <div className="mb-4">
            <p className="font-semibold mb-2">Your details</p>
            <p className="text-sm text-gray-600">{customerData?.name}, {customerData?.phone}</p>
          </div>

          {orderType === 'takeaway' && (
            <div className="space-y-2">
              <div className="flex items-start text-sm">
                <span className="text-green-600 mr-2">📍</span>
                <p className="text-gray-600">{customerData?.address}</p>
              </div>
              <div className="flex items-center text-sm">
                <span className="text-green-600 mr-2">⏱️</span>
                <p className="text-gray-600">Delivery in {totals.prepTime} mins</p>
              </div>
            </div>
          )}
        </div>

        <div className="fixed bottom-0 left-0 right-0 bg-white p-6 shadow-lg border-t">
          <div 
            className="relative w-full bg-white border-2 border-gray-300 rounded-full py-4 px-6 overflow-hidden"
            onMouseMove={handleSwipeMove}
            onMouseUp={handleSwipeEnd}
            onMouseLeave={handleSwipeEnd}
            onTouchMove={handleSwipeMove}
            onTouchEnd={handleSwipeEnd}
          >
            <div 
              className="absolute inset-0 flex items-center justify-center pointer-events-none"
              style={{
                background: swipePosition > 0 ? 'linear-gradient(to right, #10b981 0%, transparent 100%)' : 'transparent',
                opacity: swipePosition > 0 ? 0.1 : 0,
                transition: 'opacity 0.2s'
              }}
            />
            <div
              className="absolute left-3 top-1/2 transform -translate-y-1/2 w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center cursor-grab active:cursor-grabbing transition-colors z-10"
              style={{
                transform: `translateX(${swipePosition}px) translateY(-50%)`,
                backgroundColor: swipePosition > 100 ? '#10b981' : '#e5e7eb'
              }}
              onMouseDown={handleSwipeStart}
              onTouchStart={handleSwipeStart}
              data-testid="swipe-to-order-btn"
            >
              <ChevronRight className="w-6 h-6" style={{ color: swipePosition > 100 ? 'white' : '#374151' }} />
            </div>
            <span className="flex-1 text-center text-gray-500 font-medium block">
              Swipe to Order
            </span>
          </div>
        </div>

        {showCookingInstructions && (
          <CookingInstructionsPopup
            instructions={cookingInstructions}
            onClose={() => setShowCookingInstructions(false)}
            onSave={(instructions) => {
              setCookingInstructions(instructions);
              setShowCookingInstructions(false);
            }}
          />
        )}
      </div>
    </div>
  );
};

export default CustomerCart;
