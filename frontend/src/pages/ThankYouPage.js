import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle } from 'lucide-react';

const ThankYouPage = () => {
  const [countdown, setCountdown] = useState(3);
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          navigate('/customer');
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [navigate]);

  return (
    <div className="mobile-container">
      <div className="min-h-screen bg-gradient-to-br from-green-400 to-green-600 flex items-center justify-center p-8">
        <div className="text-center text-white animate-fadeIn">
          <div className="mb-8 flex justify-center">
            <div className="bg-white rounded-full p-6 animate-pulse">
              <CheckCircle className="w-20 h-20 text-green-500" />
            </div>
          </div>
          
          <h1 className="text-4xl font-bold mb-4" data-testid="thank-you-title">
            Thanks For Ordering
          </h1>
          
          <p className="text-xl mb-8 opacity-90">
            Your order has been placed successfully!
          </p>
          
          <div className="text-6xl font-bold mb-4" data-testid="countdown">
            {countdown}
          </div>
          
          <p className="text-lg opacity-75">
            Redirecting in {countdown} second{countdown !== 1 ? 's' : ''}...
          </p>
        </div>
      </div>
    </div>
  );
};

export default ThankYouPage;