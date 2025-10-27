import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Trash2, Plus, Users } from 'lucide-react';
import Sidebar from '@/components/Sidebar';

const RAW_BACKEND = process.env.REACT_APP_BACKEND_URL || '';
const BACKEND_URL = RAW_BACKEND.replace(/\/+$/, ''); 
const API = BACKEND_URL ? `${BACKEND_URL}/api` : '/api';

const Tables = () => {
  const [tables, setTables] = useState([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newTable, setNewTable] = useState({ chairCount: 2, name: '' });
  const [addCardPosition, setAddCardPosition] = useState(null);

  useEffect(() => {
    fetchTables();
  }, []);

  const fetchTables = async () => {
    try {
      const response = await axios.get(`${API}/tables`);
      setTables(response.data);
    } catch (error) {
      console.error('Error fetching tables:', error);
    }
  };

  const handleAddClick = (event) => {
    if (tables.length >= 30) {
      alert('No more tables available here !!!');
      return;
    }
    const rect = event.currentTarget.getBoundingClientRect();
    setAddCardPosition({
      top: rect.top,
      left: rect.left,
      width: rect.width
    });
    setShowAddModal(true);
  };

  const createTable = async () => {
    
    if (tables.length >= 30) {
      alert('No more tables available here !!!');
      setShowAddModal(false);
      return;
    }
    
    try {
      await axios.post(`${API}/tables`, newTable);
      setShowAddModal(false);
      setNewTable({ chairCount: 2, name: '' });
      setAddCardPosition(null);
      fetchTables();
    } catch (error) {
      console.error('Error creating table:', error);
    }
  };

  const deleteTable = async (tableId) => {
    if (!window.confirm('Are you sure you want to delete this table?')) return;
    
    try {
      await axios.delete(`${API}/tables/${tableId}`);
      fetchTables();
    } catch (error) {
      console.error('Error deleting table:', error);
      alert(error.response?.data?.detail || 'Failed to delete table');
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      
     
      {showAddModal && (
        <div 
          className="fixed inset-0 z-40"
          onClick={() => {
            setShowAddModal(false);
            setNewTable({ chairCount: 2, name: '' });
          }}
        />
      )}
      
      <div className="flex-1 overflow-auto">
        <div className="p-8">
         
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-800">Tables</h1>
            <p className="text-gray-500 mt-1">{tables.length} total tables</p>
          </div>

          
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-7 gap-4">
            {tables.map(table => (
              <div
                key={table.id}
                className={`relative bg-white rounded-xl p-6 shadow-sm border-2 transition-all hover:shadow-md ${
                  table.status === 'reserved'
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-200'
                }`}
                data-testid={`table-${table.number}`}
              >
                {table.status !== 'reserved' && (
                  <button
                    onClick={() => deleteTable(table.id)}
                    className="absolute top-2 right-2 p-1 hover:bg-gray-100 rounded transition-colors"
                    data-testid={`delete-table-${table.number}`}
                  >
                    <Trash2 className="w-4 h-4 text-gray-800" />
                  </button>
                )}
                
                <div className="text-center">
                  <h3 className="text-lg font-bold mb-2">Table</h3>
                  <p className="text-3xl font-bold text-gray-800 mb-2">{String(table.number).padStart(2, '0')}</p>
                  
                  <div className="flex items-center justify-center text-gray-700">
                    <Users className="w-4 h-4 mr-1.5" strokeWidth={2.5} />
                    <span className="text-base font-medium">{String(table.chairCount).padStart(2, '0')}</span>
                  </div>
                  
                  {table.status === 'reserved' && (
                    <div className="mt-2 text-xs bg-green-600 text-white px-2 py-1 rounded font-medium">
                      Reserved
                    </div>
                  )}
                </div>
              </div>
            ))}
            
           
            {tables.length < 30 && (
              <div className="relative">
                <button
                  onClick={handleAddClick}
                  className="bg-gray-100 border-2 border-dashed border-gray-300 rounded-xl p-6 hover:border-blue-500 hover:bg-blue-50 transition-all flex items-center justify-center w-full h-full"
                  data-testid="add-table-card"
                >
                  <div className="text-center">
                    <Plus className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                    <span className="text-sm text-gray-600">Add Table</span>
                  </div>
                </button>
                
                
                {showAddModal && (
                  <div className="absolute top-0 left-0 w-full bg-white rounded-xl shadow-lg border-2 border-blue-500 p-3 z-50">
                    <div className="space-y-2">
                      <div className="text-center">
                        <label className="block text-xs font-medium text-gray-700 mb-1">
                          Table
                        </label>
                        <p className="text-2xl font-bold text-gray-800 border-b-2 border-gray-800 pb-1 inline-block">
                          {String(tables.length + 1).padStart(2, '0')}
                        </p>
                      </div>
                      
                      <div className="flex flex-col items-center">
                        <label className="block text-xs font-medium text-gray-700 mb-1">
                          Chair
                        </label>
                        <select
                          value={newTable.chairCount}
                          onChange={(e) => setNewTable({...newTable, chairCount: parseInt(e.target.value)})}
                          className="w-20 px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-center"
                          data-testid="chair-count-select"
                        >
                          <option value={2}>02</option>
                          <option value={4}>04</option>
                          <option value={6}>06</option>
                          <option value={8}>08</option>
                        </select>
                      </div>
                      
                      <button
                        onClick={createTable}
                        className="w-full px-4 py-1.5 bg-gray-800 text-white text-sm rounded-lg hover:bg-gray-900 transition-colors"
                        data-testid="confirm-add-table"
                      >
                        Create
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Tables;