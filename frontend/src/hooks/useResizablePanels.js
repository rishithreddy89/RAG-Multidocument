/**
 * useResizablePanels Hook
 * Custom hook for managing resizable panel widths with drag interactions
 */

import { useState, useCallback, useEffect } from 'react';

const useResizablePanels = (initialSidebarWidth = 320, initialChatWidth = 400) => {
  const [sidebarWidth, setSidebarWidth] = useState(initialSidebarWidth);
  const [chatWidth, setChatWidth] = useState(initialChatWidth);
  const [isChatCollapsed, setIsChatCollapsed] = useState(false);
  const [isViewerMaximized, setIsViewerMaximized] = useState(false);
  const [isResizing, setIsResizing] = useState(null); // 'sidebar' | 'chat' | null

  // Store original widths for restoration
  const [originalSidebarWidth] = useState(initialSidebarWidth);
  const [originalChatWidth] = useState(initialChatWidth);

  // Handle mouse down on resizer
  const handleMouseDown = useCallback((panelType) => (e) => {
    e.preventDefault();
    setIsResizing(panelType);
  }, []);

  // Handle mouse move during resize
  const handleMouseMove = useCallback((e) => {
    if (!isResizing) return;

    if (isResizing === 'sidebar') {
      const newWidth = e.clientX;
      if (newWidth >= 200 && newWidth <= 500) {
        setSidebarWidth(newWidth);
      }
    } else if (isResizing === 'chat') {
      const newWidth = window.innerWidth - e.clientX;
      if (newWidth >= 300 && newWidth <= 700) {
        setChatWidth(newWidth);
      }
    }
  }, [isResizing]);

  // Handle mouse up to stop resizing
  const handleMouseUp = useCallback(() => {
    setIsResizing(null);
  }, []);

  // Attach/detach event listeners
  useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    } else {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'default';
      document.body.style.userSelect = 'auto';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'default';
      document.body.style.userSelect = 'auto';
    };
  }, [isResizing, handleMouseMove, handleMouseUp]);

  // Toggle chat collapse
  const toggleChatCollapse = useCallback(() => {
    setIsChatCollapsed(prev => !prev);
  }, []);

  // Toggle viewer maximize
  const toggleViewerMaximize = useCallback(() => {
    setIsViewerMaximized(prev => !prev);
  }, []);

  // Calculate viewer width
  const getViewerWidth = () => {
    if (isViewerMaximized) {
      return '100%';
    }
    
    const chatWidthValue = isChatCollapsed ? 50 : chatWidth;
    return `calc(100% - ${sidebarWidth}px - ${chatWidthValue}px)`;
  };

  return {
    sidebarWidth,
    chatWidth,
    isChatCollapsed,
    isViewerMaximized,
    isResizing,
    handleMouseDown,
    toggleChatCollapse,
    toggleViewerMaximize,
    getViewerWidth,
    originalSidebarWidth,
    originalChatWidth,
  };
};

export default useResizablePanels;
