/**
 * Resizer Component
 * Draggable divider for resizing panels
 */

import React from 'react';
import { GripVertical } from 'lucide-react';

const Resizer = ({ onMouseDown, isResizing }) => {
  return (
    <div
      onMouseDown={onMouseDown}
      className={`
        group relative w-1 bg-gray-200 hover:bg-primary-400 cursor-col-resize
        transition-colors duration-150 flex items-center justify-center
        ${isResizing ? 'bg-primary-500' : ''}
      `}
    >
      <div className={`
        absolute inset-y-0 -left-1 -right-1 flex items-center justify-center
        ${isResizing ? 'bg-primary-500/10' : ''}
      `}>
        <GripVertical className={`
          w-4 h-4 text-gray-400 group-hover:text-primary-600 transition-colors
          ${isResizing ? 'text-primary-600' : ''}
        `} />
      </div>
    </div>
  );
};

export default Resizer;
