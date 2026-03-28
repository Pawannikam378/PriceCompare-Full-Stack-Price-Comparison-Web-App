/**
 * SearchBar.jsx
 * Handles product search input with keyboard support and loading state.
 */

import React, { useState } from 'react';

const SearchBar = ({ onSearch, isLoading }) => {
  const [inputValue, setInputValue] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = inputValue.trim();
    if (trimmed) onSearch(trimmed);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleSubmit(e);
  };

  const suggestions = ['iPhone 15', 'Samsung Galaxy S24', 'MacBook Air', 'Sony Headphones', 'iPad Pro', 'Smart TV'];

  return (
    <div className="search-container">
      <form className="search-form" onSubmit={handleSubmit}>
        <div className="search-input-wrapper">
          <span className="search-icon">🔍</span>
          <input
            id="product-search-input"
            className="search-input"
            type="text"
            placeholder="Search for any product..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            autoComplete="off"
            aria-label="Product search"
          />
          {inputValue && (
            <button
              type="button"
              className="clear-btn"
              onClick={() => setInputValue('')}
              aria-label="Clear search"
            >
              ✕
            </button>
          )}
        </div>
        <button
          id="search-btn"
          type="submit"
          className="search-btn"
          disabled={isLoading || !inputValue.trim()}
        >
          {isLoading ? (
            <span className="btn-spinner" />
          ) : (
            'Compare Prices'
          )}
        </button>
      </form>
      <div className="suggestions">
        {suggestions.map((s) => (
          <button
            key={s}
            className="suggestion-chip"
            onClick={() => {
              setInputValue(s);
              onSearch(s);
            }}
            disabled={isLoading}
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  );
};

export default SearchBar;
