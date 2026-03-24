/**
 * PDFViewer Component
 * Modern PDF viewer with navigation and zoom controls
 */

import React, { useEffect, useRef, useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { ChevronLeft, ChevronRight, ZoomIn, ZoomOut } from 'lucide-react';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import 'react-pdf/dist/esm/Page/TextLayer.css';

// Set up PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.js`;

const USE_UNDERLINE_HIGHLIGHT = true;
const STOPWORDS = new Set(['the', 'and', 'for', 'with', 'from', 'that', 'this', 'was', 'are', 'in', 'on', 'to', 'of', 'by', 'as', 'an', 'a']);

const escapeRegExp = (text) => text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

function highlightText(text, query, useUnderline = false) {
  if (!query) return text;
  const escaped = escapeRegExp(query);
  const regex = new RegExp(`(${escaped})`, 'gi');
  const className = useUnderline ? 'highlight-underline' : 'highlight';
  return text.replace(regex, `<span class="${className}">$1</span>`);
}

function highlightByTokens(text, tokens, useUnderline = false) {
  if (!tokens || tokens.length === 0) return text;
  const className = useUnderline ? 'highlight-underline' : 'highlight';
  const pattern = tokens
    .map((token) => escapeRegExp(token))
    .sort((a, b) => b.length - a.length)
    .join('|');

  if (!pattern) return text;

  const regex = new RegExp(`\\b(${pattern})\\b`, 'gi');
  return text.replace(regex, `<span class="${className}">$1</span>`);
}

function normalizeHighlightQuery(rawQuery) {
  if (!rawQuery) return '';
  let q = String(rawQuery).trim();
  q = q.replace(/^\s*(?:[>\-•]+\s*)+/, '');
  q = q.replace(/^"|"$/g, '');
  q = q.replace(/\s+/g, ' ').trim();
  return q;
}

const PDFViewer = ({ file, activePage, activeHighlightText, highlightTrigger }) => {
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [scale, setScale] = useState(1.0);
  const [loading, setLoading] = useState(true);
  const containerRef = useRef(null);

  // Generate PDF URL from document ID or use file object directly
  const pdfSource = file.documentId 
    ? `http://localhost:8000/upload/documents/${file.documentId}/file`
    : file;

  const onDocumentLoadSuccess = ({ numPages }) => {
    setNumPages(numPages);
    setLoading(false);
  };

  const onDocumentLoadError = (error) => {
    console.error('Error loading PDF:', error);
    setLoading(false);
  };

  useEffect(() => {
    if (activePage && Number.isFinite(Number(activePage))) {
      setPageNumber(Math.max(1, Number(activePage)));
    }
  }, [activePage, highlightTrigger]);

  const applyTextHighlight = () => {
    const root = containerRef.current;
    if (!root) return;

    const textLayer = root.querySelector('.react-pdf__Page__textContent');
    if (!textLayer) return;

    const spans = Array.from(textLayer.querySelectorAll('span'));

    const queryText = normalizeHighlightQuery(activeHighlightText || '');
    spans.forEach((span) => {
      const originalText = span.dataset.originalText ?? span.textContent ?? '';
      span.dataset.originalText = originalText;
      span.innerHTML = originalText;
    });

    if (!queryText) return;

    const normalizedQuery = queryText.replace(/\s+/g, ' ').trim();
    if (!normalizedQuery) return;
    const queryRegex = new RegExp(escapeRegExp(normalizedQuery), 'i');

    let firstHighlighted = null;
    spans.forEach((span) => {
      const text = span.dataset.originalText ?? span.textContent ?? '';
      if (!text || !text.trim()) return;

      if (queryRegex.test(text)) {
        span.innerHTML = highlightText(text, normalizedQuery, USE_UNDERLINE_HIGHLIGHT);
        if (!firstHighlighted) {
          firstHighlighted = span;
        }
      }
    });

    // Fallback for PDF text-layer fragmentation:
    // if full phrase isn't found inside any one span, highlight key words instead.
    if (!firstHighlighted) {
      const tokens = Array.from(
        new Set(
          (normalizedQuery.match(/[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*/g) || [])
            .map((t) => t.trim())
            .filter((t) => t.length >= 4)
            .filter((t) => !STOPWORDS.has(t.toLowerCase()))
        )
      ).slice(0, 8);

      spans.forEach((span) => {
        const text = span.dataset.originalText ?? span.textContent ?? '';
        if (!text || !text.trim()) return;

        const hasAnyToken = tokens.some((token) => new RegExp(`\\b${escapeRegExp(token)}\\b`, 'i').test(text));
        if (!hasAnyToken) return;

        span.innerHTML = highlightByTokens(text, tokens, USE_UNDERLINE_HIGHLIGHT);
        if (!firstHighlighted) {
          firstHighlighted = span;
        }
      });
    }

    if (firstHighlighted) {
      firstHighlighted.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => applyTextHighlight(), 120);
    return () => clearTimeout(timer);
  }, [pageNumber, activeHighlightText, highlightTrigger, scale]);

  const goToPrevPage = () => setPageNumber(prev => Math.max(prev - 1, 1));
  const goToNextPage = () => setPageNumber(prev => Math.min(prev + 1, numPages));
  const zoomIn = () => setScale(prev => Math.min(prev + 0.2, 2.5));
  const zoomOut = () => setScale(prev => Math.max(prev - 0.2, 0.5));

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-3 bg-white border-b border-gray-200 shadow-sm">
        <div className="flex items-center space-x-2">
          <button
            onClick={goToPrevPage}
            disabled={pageNumber <= 1}
            className="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          
          <div className="px-3 py-1 bg-gray-100 rounded-lg text-sm font-medium">
            <span className="text-gray-700">{pageNumber}</span>
            <span className="text-gray-400"> / {numPages || '...'}</span>
          </div>
          
          <button
            onClick={goToNextPage}
            disabled={pageNumber >= numPages}
            className="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={zoomOut}
            disabled={scale <= 0.5}
            className="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            <ZoomOut className="w-5 h-5" />
          </button>
          
          <div className="px-3 py-1 bg-gray-100 rounded-lg text-sm font-medium text-gray-700 min-w-[4rem] text-center">
            {Math.round(scale * 100)}%
          </div>
          
          <button
            onClick={zoomIn}
            disabled={scale >= 2.5}
            className="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            <ZoomIn className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* PDF Content */}
      <div className="flex-1 overflow-auto p-6" ref={containerRef}>
        <div className="flex justify-center">
          {loading && (
            <div className="flex items-center justify-center py-20">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
            </div>
          )}
          
          <Document
            file={pdfSource}
            onLoadSuccess={onDocumentLoadSuccess}
            onLoadError={onDocumentLoadError}
            loading=""
            className="shadow-lg"
          >
            <Page
              pageNumber={pageNumber}
              scale={scale}
              renderTextLayer={true}
              renderAnnotationLayer={true}
              onRenderSuccess={applyTextHighlight}
              className="bg-white shadow-xl rounded-lg overflow-hidden"
            />
          </Document>
        </div>
      </div>
    </div>
  );
};

export default PDFViewer;
