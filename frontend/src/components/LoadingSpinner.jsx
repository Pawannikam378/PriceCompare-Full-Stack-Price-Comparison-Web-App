/**
 * LoadingSpinner.jsx
 * Animated loading state with a pulsing message.
 */

import React from 'react';

const LoadingSpinner = ({ message = 'Fetching prices...' }) => (
  <div className="loading-container" role="status" aria-live="polite">
    <div className="spinner-ring">
      <div /><div /><div /><div />
    </div>
    <p className="loading-message">{message}</p>
    <p className="loading-sub">Checking Amazon, Flipkart &amp; Croma</p>
  </div>
);

export default LoadingSpinner;
