import React, { useState, useEffect } from 'react';
import { X, AlertTriangle } from 'lucide-react';
import { Button } from './button';

interface DeleteAllConfirmationDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  itemCount: number;
}

export function DeleteAllConfirmationDialog({
  isOpen,
  onClose,
  onConfirm,
  itemCount,
}: DeleteAllConfirmationDialogProps) {
  const [inputValue, setInputValue] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    if (!isOpen) {
      setInputValue('');
      setIsDeleting(false);
    }
  }, [isOpen]);

  const handleConfirm = async () => {
    if (inputValue.toLowerCase() === 'delete all') {
      setIsDeleting(true);
      await onConfirm();
      setIsDeleting(false);
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Dialog */}
      <div className="relative z-50 w-full max-w-md mx-4 bg-white rounded-lg shadow-xl">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-10 h-10 bg-red-100 rounded-full">
              <AlertTriangle className="w-5 h-5 text-red-600" />
            </div>
            <h2 className="text-lg font-semibold text-gray-900">Delete All Datasets</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          <p className="text-sm text-gray-600">
            This will permanently delete all {itemCount} dataset{itemCount !== 1 ? 's' : ''} and all associated charts. This action cannot be undone.
          </p>

          <div className="p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm font-semibold text-red-900 mb-2">You are about to delete:</p>
            <ul className="text-sm text-red-800 space-y-1">
              <li>• {itemCount} dataset{itemCount !== 1 ? 's' : ''}</li>
              <li>• All associated charts</li>
              <li>• All uploaded files</li>
            </ul>
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-black">
              Type <span className="font-mono font-bold text-red-600">delete all</span> to
              confirm
            </label>
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Type delete all here"
              className="w-full px-3 py-2 border text-black border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
              autoFocus
            />
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 p-6 bg-gray-50 border-t border-gray-200 rounded-b-lg">
          <Button onClick={onClose} variant="default" disabled={isDeleting}>
            Cancel
          </Button>
          <Button
            onClick={handleConfirm}
            variant="destructive"
            disabled={inputValue.toLowerCase() !== 'delete all' || isDeleting}
          >
            {isDeleting ? 'Deleting All...' : 'Delete All Datasets'}
          </Button>
        </div>
      </div>
    </div>
  );
}
