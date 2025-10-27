import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { UtensilsCrossed, Clock, Check } from 'lucide-react';
import Sidebar from '@/components/Sidebar';


const RAW_BACKEND = process.env.REACT_APP_BACKEND_URL || '';
const BACKEND_URL = RAW_BACKEND.replace(/\/+$/, ''); 
const API = BACKEND_URL ? `${BACKEND_URL}/api` : '/api';

console.log('OrderLine using API base ->', API);

const OrderLine = () => {
  const [orders, setOrders] = useState([]);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchOrders();
    const interval = setInterval(fetchOrders, 5000); 
    return () => clearInterval(interval);
  }, [filter]);

  const fetchOrders = async () => {
    try {
      const url = filter === 'all' ? `${API}/orders` : `${API}/orders?status=${filter}`;
      const response = await axios.get(url);
      setOrders(response.data);
    } catch (error) {
      console.error('Error fetching orders:', error);
    }
  };

  const updateOrderStatus = async (orderId, newStatus) => {
    try {
      await axios.put(`${API}/orders/${orderId}/status?status=${newStatus}`);
      fetchOrders();
    } catch (error) {
      console.error('Error updating order status:', error);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    return `${mins} Min`;
  };

  const getCardStyle = (order) => {
    if (order.status === 'done' && order.type === 'dinein') {
      return 'bg-green-50 border-green-200';
    } else if (order.type === 'takeaway' && order.status === 'done') {
      return 'bg-blue-50 border-blue-200';
    } else if (order.status === 'processing') {
      return 'bg-orange-50 border-orange-200';
    }
    return 'bg-gray-50 border-gray-200';
  };

  const getStatusBadge = (order) => {
    if (order.status === 'processing') {
      return <span className="text-xs bg-orange-400 text-white px-2 py-1 rounded">Ongoing {formatTime(order.remainingTime || 240)}</span>;
    } else if (order.status === 'done' && order.type === 'dinein') {
      return <span className="text-xs bg-green-600 text-white px-2 py-1 rounded">Done Served</span>;
    } else if (order.status === 'done' && order.type === 'takeaway') {
      return <span className="text-xs bg-blue-600 text-white px-2 py-1 rounded">Take Away Not Picked up</span>;
    }
    return <span className="text-xs bg-gray-400 text-white px-2 py-1 rounded">Completed</span>;
  };

  const getOrderTypeBadge = (type) => {
    if (type === 'dinein') {
      return <span className="text-xs bg-orange-500 text-white px-3 py-1 rounded-full">Dine In</span>;
    }
    return <span className="text-xs bg-blue-500 text-white px-3 py-1 rounded-full">Take Away</span>;
  };

  const getButtonStyle = (order) => {
    if (order.status === 'processing') {
      return 'bg-orange-500 hover:bg-orange-600 text-white';
    } else if (order.status === 'done') {
      return 'bg-green-600 hover:bg-green-700 text-white';
    }
    return 'bg-gray-400 text-white cursor-not-allowed';
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      
      <div className="flex-1 overflow-auto">
        <div className="p-8">
          
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-800">Orders</h1>
          </div>

         
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {orders.map((order, index) => {
              const orderNum = index + 1;
              
              
              let borderColor = 'border-gray-200';
              let buttonBg = 'bg-gray-400';
              let buttonText = 'Completed';
              
              if (order.status === 'processing') {
                borderColor = 'border-orange-200';
                buttonBg = 'bg-orange-400';
                buttonText = 'Processing';
              } else if (order.status === 'done') {
                if (order.type === 'takeaway') {
                  borderColor = 'border-gray-200'; 
                  buttonBg = 'bg-gray-300 text-gray-700'; 
                  buttonText = 'Order Done';
                } else {
                  borderColor = 'border-green-200';
                  buttonBg = 'bg-green-500';
                  buttonText = 'Order Done';
                }
              }
              
              return (
                <div
                  key={order.id}
                  className={`rounded-2xl shadow-md border-2 ${borderColor} overflow-hidden flex flex-col`}
                  data-testid={`order-${orderNum}`}
                >
                  
                  <div className={`p-4 ${
                    order.status === 'processing' ? 'bg-orange-50' :
                    order.status === 'done' && order.type === 'takeaway' ? 'bg-gray-50' : 
                    order.status === 'done' ? 'bg-green-50' : 'bg-gray-50'
                  }`}>
                    
                    <div className="flex items-center space-x-2 mb-3">
                      <UtensilsCrossed className="w-5 h-5 text-blue-600" strokeWidth={2.5} />
                      <span className="font-bold text-xl text-gray-800">#{String(orderNum).padStart(3, '0')}</span>
                    </div>

                    
                    <div className="flex items-center justify-between mb-3">
                      {getOrderTypeBadge(order.type)}
                      {getStatusBadge(order)}
                    </div>

                    
                    {order.type === 'dinein' && (
                      <div className="text-sm font-semibold text-gray-800 mb-1">
                        Table-{String(order.tableNumber).padStart(2, '0')}
                      </div>
                    )}
                    
                    
                    <div className="flex items-center text-gray-600 text-xs mb-3">
                      <Clock className="w-3 h-3 mr-1" />
                      {new Date(order.createdAt).toLocaleTimeString('en-US', {hour: 'numeric', minute:'2-digit', hour12: true})}
                    </div>

                    
                    <div className="text-sm font-bold text-gray-800">
                      {order.items.length} Item
                    </div>
                  </div>

                  
                  <div className="bg-white p-4 flex-1">
                    <div className="space-y-2">
                      {order.items.map((item, idx) => (
                        <div key={idx} className="text-gray-700 text-sm">
                          <span className="font-medium">{item.quantity} x</span> {item.menuItemName}
                        </div>
                      ))}
                    </div>
                  </div>

                  
                  <div className="p-3">
                    <button 
                      className={`w-full py-3 rounded-full text-white font-bold text-base ${buttonBg} shadow-md flex items-center justify-center space-x-2`}
                    >
                      {order.status === 'processing' && <Clock className="w-5 h-5" />}
                      {order.status === 'done' && <Check className="w-5 h-5" />}
                      <span>{buttonText}</span>
                    </button>
                  </div>
                </div>
              );
            })}
          </div>

          {orders.length === 0 && (
            <div className="text-center py-12">
              <UtensilsCrossed className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500 text-lg">No orders found</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default OrderLine;
