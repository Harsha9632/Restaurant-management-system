import React, { useState } from 'react';
import { X } from 'lucide-react';

const LoginPopup = ({ orderType, onClose, onSubmit, isInitial = false }) => {
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    address: '',
    tableNumber: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!isInitial && orderType === 'dinein' && !formData.tableNumber) {
      alert('Please select a table number');
      return;
    }
    
    if (!isInitial && orderType === 'takeaway' && !formData.address) {
      alert('Please enter your address');
      return;
    }
    
    onSubmit({
      ...formData,
      tableNumber: orderType === 'dinein' ? parseInt(formData.tableNumber) : null
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div 
        className="bg-white rounded-2xl p-8 max-w-md w-full animate-fadeIn mobile-container"
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold">Enter Your Details</h2>
          {!isInitial && (
            <button 
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-full transition-colors"
              data-testid="close-login-popup"
            >
              <X className="w-6 h-6" />
            </button>
          )}
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Name</label>
            <input
              type="text"
              required
              placeholder="Full name"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              data-testid="name-input"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Contact</label>
            <input
              type="tel"
              required
              placeholder="Phone number"
              pattern="[0-9]{10}"
              value={formData.phone}
              onChange={(e) => setFormData({...formData, phone: e.target.value})}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              data-testid="phone-input"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Address</label>
            <textarea
              required
              placeholder="Complete address"
              rows="3"
              value={formData.address}
              onChange={(e) => setFormData({...formData, address: e.target.value})}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              data-testid="address-input"
            />
          </div>

          {!isInitial && orderType === 'dinein' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Table Number</label>
              <input
                type="number"
                required
                placeholder="Enter table number"
                value={formData.tableNumber}
                onChange={(e) => setFormData({...formData, tableNumber: e.target.value})}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                data-testid="table-number-input"
                min="1"
                max="30"
              />
            </div>
          )}

          <button
            type="submit"
            className="w-full bg-gray-800 text-white py-4 rounded-full font-medium hover:bg-gray-900 transition-colors mt-6"
            data-testid="order-now-btn"
          >
            {isInitial ? 'Continue' : 'Order Now'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default LoginPopup;