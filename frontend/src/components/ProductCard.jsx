/**
 * ProductCard.jsx
 * Displays a single marketplace result with platform branding, price,
 * rating stars, and a visit link. Highlights the cheapest option.
 */

import React from 'react';

const PLATFORM_META = {
  Amazon: {
    color: '#FF9900',
    bg: 'rgba(255, 153, 0, 0.08)',
    emoji: '📦',
    accent: '#FF9900',
  },
  Flipkart: {
    color: '#2874F0',
    bg: 'rgba(40, 116, 240, 0.08)',
    emoji: '🛒',
    accent: '#2874F0',
  },
  Croma: {
    color: '#67B346',
    bg: 'rgba(103, 179, 70, 0.08)',
    emoji: '🏪',
    accent: '#67B346',
  },
};

const StarRating = ({ rating }) => {
  const stars = [];
  for (let i = 1; i <= 5; i++) {
    stars.push(
      <span key={i} className={`star ${i <= Math.round(rating) ? 'star--filled' : 'star--empty'}`}>
        ★
      </span>
    );
  }
  return (
    <div className="rating-wrapper">
      <div className="stars">{stars}</div>
      <span className="rating-value">{rating.toFixed(1)}</span>
    </div>
  );
};

const ProductCard = ({ result, rank }) => {
  const meta = PLATFORM_META[result.platform] || {
    color: '#8B5CF6',
    bg: 'rgba(139, 92, 246, 0.08)',
    emoji: '🛍️',
  };

  return (
    <div
      className={`product-card ${result.is_cheapest ? 'product-card--cheapest' : ''}`}
      style={{ '--platform-color': meta.color, '--platform-bg': meta.bg }}
    >
      {result.is_cheapest && (
        <div className="cheapest-badge">
          <span>🏆</span> Best Price
        </div>
      )}
      {!result.is_cheapest && rank && (
        <div className="rank-badge">#{rank}</div>
      )}

      <div className="card-header">
        <span className="platform-emoji">{meta.emoji}</span>
        <h3 className="platform-name">{result.platform}</h3>
      </div>

      <div className="card-price">
        <span className="currency">₹</span>
        <span className="price-amount">{result.price.toLocaleString('en-IN')}</span>
      </div>

      <StarRating rating={result.rating} />

      <a
        href={result.link}
        target="_blank"
        rel="noopener noreferrer"
        className="visit-btn"
        style={{ background: result.is_cheapest ? meta.color : 'transparent', color: result.is_cheapest ? '#fff' : meta.color, borderColor: meta.color }}
      >
        View on {result.platform} →
      </a>
    </div>
  );
};

export default ProductCard;
