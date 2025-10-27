import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart3, Users, IndianRupee, ShoppingBag, ChefHat } from 'lucide-react';
import { LineChart, Line, PieChart, Pie, Cell, BarChart, Bar, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import Sidebar from '@/components/Sidebar';


const RAW_BACKEND = process.env.REACT_APP_BACKEND_URL || '';
const BACKEND_URL = RAW_BACKEND.replace(/\/+$/, ''); 
const API = BACKEND_URL ? `${BACKEND_URL}/api` : '/api';

console.log('Dashboard using API base ->', API);

const Dashboard = () => {
  const [analytics, setAnalytics] = useState(null);
  const [tables, setTables] = useState([]);
  const [loading, setLoading] = useState(true);
  const [orderSummaryView, setOrderSummaryView] = useState('Day');
  const [revenueView, setRevenueView] = useState('Day');
  const [focusedElement, setFocusedElement] = useState(null);

  const handleElementClick = (elementId) => {
    if (focusedElement === elementId) {
      setFocusedElement(null); 
    } else {
      setFocusedElement(elementId); 
    }
  };

  useEffect(() => {
    fetchAnalytics();
    fetchTables();
    const interval = setInterval(() => {
      fetchAnalytics();
      fetchTables();
    }, 30000); 
    return () => clearInterval(interval);
  }, []);

  const fetchAnalytics = async () => {
    try {
      const response = await axios.get(`${API}/analytics`);
      setAnalytics(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching analytics:', error);
      setLoading(false);
    }
  };

  const fetchTables = async () => {
    try {
      const response = await axios.get(`${API}/tables`);
      setTables(response.data);
    } catch (error) {
      console.error('Error fetching tables:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const COLORS = ['#10b981', '#3b82f6', '#f59e0b'];

  const pieData = [
    { name: 'Served', value: analytics?.ordersByType?.served || 1 },
    { name: 'Dine In', value: analytics?.ordersByType?.dinein || 1 },
    { name: 'Take Away', value: analytics?.ordersByType?.takeaway || 1 },
  ];
  
  console.log('Pie Data:', pieData);
  console.log('Analytics:', analytics);

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      
      <div className="flex-1 overflow-auto">
        <div className="p-6">
          
          <div className="flex items-center space-x-4 mb-4">
            <div className="relative">
              <input 
                type="text"
                placeholder="Filter..."
                className="bg-white border border-gray-300 rounded-lg px-4 py-2 pr-10 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button className="absolute right-2 top-1/2 transform -translate-y-1/2 text-green-600 hover:text-green-700">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            </div>
          </div>

          
          <h1 className="text-3xl font-bold text-gray-800 mb-6">Analytics</h1>

          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
            <div 
              onClick={() => handleElementClick('chef-card')}
              className={`bg-white rounded-xl p-6 shadow-sm border-2 border-gray-200 cursor-pointer transition-all duration-300 ${
                focusedElement && focusedElement !== 'chef-card' ? 'opacity-40 blur-sm' : 'opacity-100'
              }`}
              data-testid="total-chefs-card"
            >
              <div className="flex items-center space-x-4">
                <div className="bg-blue-100 p-3 rounded-full">
                  <ChefHat className="w-8 h-8 text-blue-600" />
                </div>
                <div>
                  <p className="text-3xl font-bold text-gray-800">{String(analytics?.totalChefs || 0).padStart(2, '0')}</p>
                  <p className="text-sm text-gray-500">TOTAL CHEF</p>
                </div>
              </div>
            </div>

            <div 
              onClick={() => handleElementClick('revenue-card')}
              className={`bg-white rounded-xl p-6 shadow-sm border-2 border-gray-200 cursor-pointer transition-all duration-300 ${
                focusedElement && focusedElement !== 'revenue-card' ? 'opacity-40 blur-sm' : 'opacity-100'
              }`}
              data-testid="total-revenue-card"
            >
              <div className="flex items-center space-x-4">
                <div className="bg-green-100 p-3 rounded-full">
                  <IndianRupee className="w-8 h-8 text-green-600" />
                </div>
                <div>
                  <p className="text-3xl font-bold text-gray-800">{(analytics?.totalRevenue / 1000).toFixed(0)}K</p>
                  <p className="text-sm text-gray-500">TOTAL REVENU</p>
                </div>
              </div>
            </div>

            <div 
              onClick={() => handleElementClick('orders-card')}
              className={`bg-white rounded-xl p-6 shadow-sm border-2 border-gray-200 cursor-pointer transition-all duration-300 ${
                focusedElement && focusedElement !== 'orders-card' ? 'opacity-40 blur-sm' : 'opacity-100'
              }`}
              data-testid="total-orders-card"
            >
              <div className="flex items-center space-x-4">
                <div className="bg-purple-100 p-3 rounded-full">
                  <ShoppingBag className="w-8 h-8 text-purple-600" />
                </div>
                <div>
                  <p className="text-3xl font-bold text-gray-800">{String(analytics?.totalOrders || 0).padStart(2, '0')}</p>
                  <p className="text-sm text-gray-500">TOTAL ORDERS</p>
                </div>
              </div>
            </div>

            <div 
              onClick={() => handleElementClick('clients-card')}
              className={`bg-white rounded-xl p-6 shadow-sm border-2 border-gray-200 cursor-pointer transition-all duration-300 ${
                focusedElement && focusedElement !== 'clients-card' ? 'opacity-40 blur-sm' : 'opacity-100'
              }`}
              data-testid="total-clients-card"
            >
              <div className="flex items-center space-x-4">
                <div className="bg-orange-100 p-3 rounded-full">
                  <Users className="w-8 h-8 text-orange-600" />
                </div>
                <div>
                  <p className="text-3xl font-bold text-gray-800">{String(analytics?.totalClients || 0).padStart(2, '0')}</p>
                  <p className="text-sm text-gray-500">TOTAL CLIENTS</p>
                </div>
              </div>
            </div>
          </div>

          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-3 mb-3">
            
            <div 
              onClick={() => handleElementClick('order-summary')}
              className={`bg-white rounded-xl p-3 shadow-sm border-2 border-gray-200 cursor-pointer transition-all duration-300 ${
                focusedElement && focusedElement !== 'order-summary' ? 'opacity-40 blur-sm' : 'opacity-100'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-base font-semibold text-gray-800">Order Summary</h2>
                <div className="relative">
                  <button className="flex items-center space-x-1 bg-white border border-gray-300 rounded-full px-3 py-1 text-xs text-gray-700 hover:bg-gray-50">
                    <span>{orderSummaryView}</span>
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                </div>
              </div>
              
              
              <div className="grid grid-cols-3 gap-2 w-full mb-4">
                <div className="bg-gray-50 rounded-lg p-2 text-center">
                  <p className="text-xl font-bold text-gray-800">{String(pieData[0].value).padStart(2, '0')}</p>
                  <p className="text-xs text-gray-600">Served</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-2 text-center">
                  <p className="text-xl font-bold text-gray-800">{String(pieData[1].value).padStart(2, '0')}</p>
                  <p className="text-xs text-gray-600">Dine In</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-2 text-center">
                  <p className="text-xl font-bold text-gray-800">{String(pieData[2].value).padStart(2, '0')}</p>
                  <p className="text-xs text-gray-600">Take Away</p>
                </div>
              </div>
              
              
              <div className="flex items-center justify-center gap-6 py-4">
                <ResponsiveContainer width={200} height={200}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={80}
                      fill="#8884d8"
                      paddingAngle={3}
                      dataKey="value"
                    >
                      {pieData.map((entry, index) => (
                        <Cell 
                          key={`cell-${index}`} 
                          fill={COLORS[index % COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
                
                
                <div className="flex flex-col space-y-3">
                  {pieData.map((entry, index) => {
                    const total = pieData.reduce((sum, item) => sum + item.value, 0);
                    const percentage = total > 0 ? Math.round((entry.value / total) * 100) : 0;
                    return (
                      <div key={entry.name} className="flex items-center gap-2">
                        <div 
                          className="w-3 h-3 rounded-sm" 
                          style={{backgroundColor: COLORS[index % COLORS.length]}}
                        ></div>
                        <span className="text-sm text-gray-600">{entry.name}</span>
                        <span className="text-sm font-semibold text-gray-800">({percentage}%)</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            
            <div 
              onClick={() => handleElementClick('revenue-chart')}
              className={`bg-white rounded-xl p-3 shadow-sm border-2 border-gray-200 cursor-pointer transition-all duration-300 ${
                focusedElement && focusedElement !== 'revenue-chart' ? 'opacity-40 blur-sm' : 'opacity-100'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-base font-semibold text-gray-800">Revenue</h2>
                <div className="relative">
                  <button className="flex items-center space-x-1 bg-white border border-gray-300 rounded-full px-3 py-1 text-xs text-gray-700 hover:bg-gray-50">
                    <span>{revenueView}</span>
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                </div>
              </div>
              <ResponsiveContainer width="100%" height={120}>
                <AreaChart data={analytics?.revenueByDay || []}>
                  <defs>
                    <linearGradient id="revenueGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.05}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis 
                    dataKey="day" 
                    style={{ fontSize: '10px' }} 
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis 
                    style={{ fontSize: '10px' }} 
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: '#fff',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      fontSize: '12px'
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="revenue"
                    stroke="#3b82f6"
                    strokeWidth={3}
                    fill="url(#revenueGradient)"
                    dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
                    activeDot={{ r: 6, fill: '#3b82f6' }}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            
            <div 
              onClick={() => handleElementClick('tables-preview')}
              className={`bg-white rounded-xl p-3 shadow-sm border-2 border-gray-200 cursor-pointer transition-all duration-300 ${
                focusedElement && focusedElement !== 'tables-preview' ? 'opacity-40 blur-sm' : 'opacity-100'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-base font-semibold text-gray-800">Tables</h2>
                <div className="flex items-center space-x-2 text-xs">
                  <div className="flex items-center">
                    <div className="w-2 h-2 bg-green-400 rounded-full mr-1"></div>
                    <span className="text-gray-600">Reserved</span>
                  </div>
                  <div className="flex items-center">
                    <div className="w-2 h-2 bg-white border border-gray-300 rounded-full mr-1"></div>
                    <span className="text-gray-600">Available</span>
                  </div>
                </div>
              </div>
              <div className="grid grid-cols-7 gap-1">
                {tables.slice(0, 30).map(table => {
                  const isReserved = table.status === 'reserved';
                  return (
                    <div 
                      key={table.id} 
                      className={`aspect-square rounded-lg flex items-center justify-center text-xs font-semibold cursor-pointer transition-colors ${
                        isReserved ? 'bg-green-400 text-white' : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      {String(table.number).padStart(2, '0')}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          
          <div 
            onClick={() => handleElementClick('chef-table')}
            className={`bg-white rounded-xl p-3 shadow-sm border-2 border-gray-200 cursor-pointer transition-all duration-300 ${
              focusedElement && focusedElement !== 'chef-table' ? 'opacity-40 blur-sm' : 'opacity-100'
            }`}
          >
            <h2 className="text-base font-semibold text-gray-800 mb-2">Chef Order Distribution</h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-300">
                    <th className="text-left py-2 px-4 font-semibold text-gray-700 text-sm">Chef Name</th>
                    <th className="text-left py-2 px-4 font-semibold text-gray-700 text-sm">Order Taken</th>
                  </tr>
                </thead>
                <tbody>
                  {analytics?.chefOrderDistribution?.map((chef, idx) => (
                    <tr key={idx} className="border-b border-gray-200 last:border-0">
                      <td className="py-2 px-4 text-sm text-gray-800">{chef.name}</td>
                      <td className="py-2 px-4 text-sm text-gray-800">{String(chef.orders).padStart(2, '0')}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
