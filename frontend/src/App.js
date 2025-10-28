import React from 'react';
import { HashRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import '@/App.css';
import Dashboard from '@/pages/Dashboard';
import Tables from '@/pages/Tables';
import OrderLine from '@/pages/OrderLine';
import MenuManagement from '@/pages/MenuManagement';
import CustomerOrdering from '@/pages/CustomerOrdering';
import CustomerCart from '@/pages/CustomerCart';
import CustomerDetails from '@/pages/CustomerDetails';
import ThankYouPage from '@/pages/ThankYouPage';
import './badge.css';

function App() {
  return (
    <Router>
      <Routes>
        
        <Route
          path="/_test"
          element={
            <div style={{ padding: 40, fontSize: 20 }}>
              ROUTES WORK — test page
            </div>
          }
        />
        <Route
          path="/_showpath"
          element={
            <div style={{ padding: 40, fontSize: 18 }}>
              React sees path: {window.location.pathname}
            </div>
          }
        />

        
        <Route path="/" element={<Navigate to="/customer" replace />} />
        <Route path="/customer" element={<CustomerDetails />} />
        <Route path="/customer/menu" element={<CustomerOrdering />} />
        <Route path="/customer/cart" element={<CustomerCart />} />
        <Route path="/customer/thank-you" element={<ThankYouPage />} />

        
        <Route path="/restaurant/dashboard" element={<Dashboard />} />
        <Route path="/restaurant/analytics" element={<Dashboard />} />
        <Route path="/restaurant/tables" element={<Tables />} />
        <Route path="/restaurant/orders" element={<OrderLine />} />
        <Route path="/restaurant/menu" element={<MenuManagement />} />

        
        <Route
      
          element={
            <div style={{ padding: 40, fontSize: 18 }}>
              404 — No matching app route — React pathname: {window.location.pathname}
            </div>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;


