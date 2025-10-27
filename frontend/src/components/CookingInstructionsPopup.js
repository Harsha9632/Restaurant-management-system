import React, { useState } from 'react';
import { X } from 'lucide-react';

const CookingInstructionsPopup = ({ instructions, onClose, onSave }) => {
  const [text, setText] = useState(instructions || '');

  const handleSave = () => {
    onSave(text);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div 
        className="bg-white rounded-2xl p-8 max-w-md w-full animate-fadeIn mobile-container"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold">Add Cooking instructions</h2>
          <button 
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            data-testid="close-cooking-instructions"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="mb-4">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="e.g., Extra spicy, no onions..."
            rows="6"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            data-testid="cooking-instructions-input"
          />
        </div>

        <p className="text-xs text-gray-500 mb-6">
          The restaurant will try its best to follow your request. However, refunds or cancellations in this regard won't be possible.
        </p>

        <div className="flex space-x-4">
          <button
            onClick={onClose}
            className="flex-1 px-6 py-3 border border-gray-300 rounded-full hover:bg-gray-50 transition-colors"
            data-testid="cancel-cooking-instructions"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="flex-1 px-6 py-3 bg-gray-800 text-white rounded-full hover:bg-gray-900 transition-colors"
            data-testid="save-cooking-instructions"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
};

export default CookingInstructionsPopup;