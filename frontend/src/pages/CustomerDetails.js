import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const CustomerDetails = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    address: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    sessionStorage.setItem('customerData', JSON.stringify(formData));
    navigate('/customer/menu');
  };

  return (
    <div className="mobile-container">
      <div 
        className="min-h-screen flex items-center justify-center p-6" 
        style={{
          backgroundImage: 'url(https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          position: 'relative'
        }}
      >
        
        <div className="absolute inset-0 bg-black bg-opacity-40"></div>

        
        <div className="relative bg-white rounded-2xl p-8 w-full max-w-md shadow-2xl z-10">
          <div className="mb-8 text-center">
            <h1 className="text-3xl font-bold text-gray-800 mb-2">Good evening</h1>
            <p className="text-gray-500">Place you order here</p>
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

            <button
              type="submit"
              className="w-full bg-gray-800 text-white py-4 rounded-full font-medium hover:bg-gray-900 transition-colors mt-6"
              data-testid="continue-btn"
            >
              Continue
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default CustomerDetails;