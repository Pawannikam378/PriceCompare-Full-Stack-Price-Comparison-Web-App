/**
 * App.jsx
 * --------
 * Root application component.
 *
 * Features:
 *  - Product search  → /search API (real DummyJSON data)
 *  - Price comparison cards (sorted, cheapest highlighted)
 *  - Price history chart → /history API
 *  - AI Price Prediction → /predict API
 *  - Dark / Light mode toggle
 *  - Error & empty states
 *  - Last search caching via localStorage
 */

import React, { useState, useEffect, useCallback } from 'react';
import SearchBar from './components/SearchBar';
import ProductCard from './components/ProductCard';
import PriceHistoryChart from './components/PriceHistoryChart';
import LoadingSpinner from './components/LoadingSpinner';
import Prediction from './components/Prediction';
import { searchProducts, fetchPriceHistory, fetchPrediction } from './services/api';

const App = () => {
  // ─── State ─────────────────────────────────────────────────────────────────
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem('pricecompare-theme') !== 'light';
  });
  const [searchResults, setSearchResults]     = useState(null);
  const [historyData, setHistoryData]         = useState(null);
  const [predictionData, setPredictionData]   = useState(null);
  const [currentQuery, setCurrentQuery]       = useState(() => localStorage.getItem('pricecompare-last-search') || '');
  const [isSearching, setIsSearching]         = useState(false);
  const [isPredicting, setIsPredicting]       = useState(false);
  const [error, setError]                     = useState(null);

  // ─── Theme persistence ──────────────────────────────────────────────────────
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light');
    localStorage.setItem('pricecompare-theme', darkMode ? 'dark' : 'light');
  }, [darkMode]);

  // ─── Restore last search on first load ─────────────────────────────────────
  useEffect(() => {
    if (currentQuery) handleSearch(currentQuery);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ─── Search handler ─────────────────────────────────────────────────────────
  const handleSearch = useCallback(async (query) => {
    if (!query.trim()) return;
    setCurrentQuery(query);
    setError(null);
    setSearchResults(null);
    setHistoryData(null);
    setPredictionData(null);
    setIsSearching(true);
    localStorage.setItem('pricecompare-last-search', query);

    try {
      const [results, history] = await Promise.allSettled([
        searchProducts(query),
        fetchPriceHistory(query),
      ]);

      if (results.status === 'fulfilled') {
        setSearchResults(results.value);
      } else {
        throw new Error(results.reason?.response?.data?.detail || 'Failed to fetch prices.');
      }

      if (history.status === 'fulfilled') {
        setHistoryData(history.value);
      }
    } catch (err) {
      setError(err.message || 'Something went wrong. Is the backend running?');
    } finally {
      setIsSearching(false);
    }

    // Fetch AI prediction separately (non-blocking, shows after search)
    setIsPredicting(true);
    try {
      const prediction = await fetchPrediction(query);
      setPredictionData(prediction);
    } catch (err) {
      console.warn('Prediction fetch failed (non-critical):', err.message);
      setPredictionData(null);
    } finally {
      setIsPredicting(false);
    }
  }, []);

  // ─── Cheapest summary ───────────────────────────────────────────────────────
  const cheapest = searchResults?.cheapest;

  // ─── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="app">
      {/* ── Header ── */}
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <span className="logo-icon">💸</span>
            <div>
              <h1 className="logo-title">PriceCompare</h1>
              <p className="logo-tagline">AI-powered price tracking across India's top shops</p>
            </div>
          </div>
          <button
            id="theme-toggle-btn"
            className="theme-toggle"
            onClick={() => setDarkMode((d) => !d)}
            aria-label="Toggle dark mode"
          >
            {darkMode ? '☀️ Light' : '🌙 Dark'}
          </button>
        </div>
      </header>

      {/* ── Hero / Search ── */}
      <section className="hero">
        <h2 className="hero-title">Find the <span className="gradient-text">Best Price</span> Instantly</h2>
        <p className="hero-sub">Real prices from Amazon, Flipkart &amp; Croma · Powered by AI prediction</p>
        <SearchBar onSearch={handleSearch} isLoading={isSearching} />
      </section>

      {/* ── Main content ── */}
      <main className="main-content">
        {/* Loading */}
        {isSearching && <LoadingSpinner />}

        {/* Error state */}
        {error && !isSearching && (
          <div className="error-state" role="alert">
            <span className="error-icon">⚠️</span>
            <h3>Oops! Something went wrong</h3>
            <p>{error}</p>
            <button className="retry-btn" onClick={() => handleSearch(currentQuery)}>
              Try Again
            </button>
          </div>
        )}

        {/* No-results state */}
        {!isSearching && !error && searchResults && searchResults.results.length === 0 && (
          <div className="empty-state">
            <span className="empty-icon">🔎</span>
            <h3>No Results Found</h3>
            <p>We couldn't find any prices for &quot;<strong>{currentQuery}</strong>&quot;. Try a different search.</p>
          </div>
        )}

        {/* Results */}
        {!isSearching && searchResults && searchResults.results.length > 0 && (
          <section className="results-section">
            {/* Summary bar */}
            {cheapest && (
              <div className="summary-bar">
                <span className="summary-icon">🏆</span>
                <p>
                  Cheapest on <strong>{cheapest.platform}</strong> at{' '}
                  <strong className="highlight-price">₹{cheapest.price.toLocaleString('en-IN')}</strong>
                </p>
              </div>
            )}

            <h2 className="section-title">
              Comparing prices for &quot;<span className="query-text">{currentQuery}</span>&quot;
            </h2>

            <div className="cards-grid">
              {searchResults.results.map((result, index) => (
                <ProductCard key={result.platform} result={result} rank={index + 1} />
              ))}
            </div>
          </section>
        )}

        {/* AI Price Prediction */}
        {!isSearching && (searchResults?.results?.length > 0 || isPredicting || predictionData) && (
          <Prediction
            predictionData={predictionData}
            productName={currentQuery}
            isLoading={isPredicting}
          />
        )}

        {/* Price History Chart (with predicted point) */}
        {!isSearching && historyData && (
          <PriceHistoryChart
            historyData={historyData}
            productName={currentQuery}
            predictedPrice={predictionData?.predicted_price ?? null}
          />
        )}

        {/* No history info hint */}
        {!isSearching && searchResults && searchResults.results.length > 0 && historyData && historyData.history.length === 0 && (
          <div className="hint-card">
            <span>💡</span>
            <p>Search a few more times to build up price history and enable AI prediction for this product.</p>
          </div>
        )}
      </main>

      {/* ── Footer ── */}
      <footer className="footer">
        <p>© 2025 PriceCompare · Real data via DummyJSON · AI prediction powered by Linear Regression</p>
      </footer>
    </div>
  );
};

export default App;
