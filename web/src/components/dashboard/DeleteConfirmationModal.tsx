import React, { useState } from 'react';
import { Trash2, X } from 'lucide-react';

interface DeleteConfirmationModalProps {
  taskId: number;
  onConfirm: (taskId: number) => Promise<void>;
  onClose: () => void;
  itemName?: string;
}

export const DeleteConfirmationModal: React.FC<DeleteConfirmationModalProps> = ({
  taskId,
  onConfirm,
  onClose,
  itemName = 'tarefa',
}) => {
  const [isDeleting, setIsDeleting] = useState(false);

  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const handleConfirm = async () => {
    setIsDeleting(true);
    await onConfirm(taskId);
  };

  return (
    <div
      className="fixed inset-0 backdrop-blur-sm bg-black/30 flex items-center justify-center p-4 z-[60]"
      onClick={handleOverlayClick}
      aria-modal="true"
      role="dialog"
    >
      <div className="bg-white rounded-xl shadow-2xl max-w-sm w-full p-6 space-y-6 transform transition-all duration-300 scale-100 opacity-100">
        
        <div className="flex justify-between items-start border-b pb-4">
            <div className="flex items-center space-x-3">
                <div className="p-2 bg-red-100 rounded-full text-red-600">
                    <Trash2 className="w-6 h-6" />
                </div>
                <h2 className="text-lg font-bold text-gray-900">Confirmar Exclusão</h2>
            </div>
            <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 p-1 transition duration-150 rounded-full hover:bg-gray-100"
            >
                <X className="w-5 h-5" />
            </button>
        </div>

        <p className="text-gray-700 text-sm">
          Você tem certeza que deseja excluir permanentemente esta {itemName}? Esta ação não pode ser desfeita.
        </p>

        <div className="flex justify-end space-x-3 pt-4">
          <button
            type="button"
            onClick={onClose}
            disabled={isDeleting}
            className="px-4 py-2 text-sm font-bold text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition duration-150 disabled:opacity-50"
          >
            Cancelar
          </button>
          <button
            type="button"
            onClick={handleConfirm}
            disabled={isDeleting}
            className="px-4 py-2 text-sm font-bold text-white bg-red-600 border border-transparent rounded-lg hover:bg-red-700 disabled:opacity-50 transition duration-150 shadow-md"
          >
            {isDeleting ? 'Excluindo...' : 'Sim, Excluir'}
          </button>
        </div>
      </div>
    </div>
  );
};
