/**
 * Prediction.jsx
 * ---------------
 * AI Price Prediction section component.
 *
 * Displays:
 *  - Predicted next price
 *  - Trend direction (↑ ↓ →) with colour coding
 *  - Loading / no-data states
 */

import React from 'react';

const TREND_CONFIG = {
  UP: {
    arrow: '↑',
    label: 'Price likely going UP',
    className: 'prediction--up',
    arrowClass: 'trend-arrow--up',
    emoji: '📈',
  },
  DOWN: {
    arrow: '↓',
    label: 'Price likely going DOWN',
    className: 'prediction--down',
    arrowClass: 'trend-arrow--down',
    emoji: '📉',
  },
  STABLE: {
    arrow: '→',
    label: 'Price is STABLE',
    className: 'prediction--stable',
    arrowClass: 'trend-arrow--stable',
    emoji: '➡️',
  },
};

const Prediction = ({ predictionData, productName, isLoading }) => {
  if (isLoading) {
    return (
      <section className="prediction-section prediction-section--loading">
        <div className="prediction-header">
          <span className="prediction-icon">🤖</span>
          <h2 className="section-title" style={{ margin: 0 }}>AI Price Prediction</h2>
        </div>
        <div className="prediction-loading">
          <div className="prediction-spinner" />
          <p>Running AI model…</p>
        </div>
      </section>
    );
  }

  if (!predictionData) return null;

  const { predicted_price, trend, message } = predictionData;
  const cfg = trend ? TREND_CONFIG[trend] : null;

  // No prediction yet (insufficient history)
  if (!predicted_price || !trend) {
    return (
      <section className="prediction-section prediction-section--empty">
        <div className="prediction-header">
          <span className="prediction-icon">🤖</span>
          <h2 className="section-title" style={{ margin: 0 }}>AI Price Prediction</h2>
        </div>
        <div className="prediction-message">
          <span className="prediction-message-icon">💡</span>
          <p>{message || 'Search a few more times to enable AI price prediction.'}</p>
        </div>
      </section>
    );
  }

  return (
    <section className={`prediction-section ${cfg.className}`}>
      {/* Header */}
      <div className="prediction-header">
        <span className="prediction-icon">🤖</span>
        <h2 className="section-title" style={{ margin: 0 }}>
          AI Price Prediction
          {productName && <span className="history-product-name"> – {productName}</span>}
        </h2>
        <span className="prediction-badge">Powered by Linear Regression</span>
      </div>

      {/* Prediction body */}
      <div className="prediction-body">
        {/* Predicted price card */}
        <div className="prediction-price-card">
          <p className="prediction-label">Predicted Next Price</p>
          <div className="prediction-price">
            <span className="prediction-currency">₹</span>
            <span className="prediction-amount">
              {predicted_price.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
            </span>
          </div>
        </div>

        {/* Divider */}
        <div className="prediction-divider" />

        {/* Trend card */}
        <div className="prediction-trend-card">
          <p className="prediction-label">Price Trend</p>
          <div className="prediction-trend">
            <span className={`trend-arrow ${cfg.arrowClass}`}>{cfg.arrow}</span>
            <div>
              <p className="trend-label">{cfg.label}</p>
              <p className="trend-emoji">{cfg.emoji}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Footer note */}
      <p className="prediction-note">
        ⚠️ This is an AI estimate based on past price trends. Actual prices may vary.
      </p>
    </section>
  );
};

export default Prediction;
