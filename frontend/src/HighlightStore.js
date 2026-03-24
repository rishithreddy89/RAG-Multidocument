/**
 * Highlight Store (lightweight local state helpers)
 */

export const createInitialHighlightState = () => ({
  activeDoc: null,
  activePage: 1,
  activeHighlightText: '',
  activeBbox: null,
  trigger: 0,
});

export const buildHighlightState = (highlight) => ({
  activeDoc: highlight?.doc_name || null,
  activePage: Number(highlight?.page) || 1,
  activeHighlightText: highlight?.text || '',
  activeBbox: highlight?.bbox || null,
  trigger: Date.now(),
});
