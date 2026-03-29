/**
 * PriceHistoryChart.jsx
 * ---------------------------
 * Renders a multi-line Recharts chart showing price history per platform.
 * Also displays lowest price, highest price, and a trend indicator.
 * Supports an optional "Predicted" reference line / dot on the chart.
 */

import React, { useMemo } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, ResponsiveContainer, ReferenceLine,
} from 'recharts';

const PLATFORM_COLORS = {
  Amazon:    '#FF9900',
  Flipkart:  '#2874F0',
  Croma:     '#67B346',
  Predicted: '#A855F7',   // purple for AI prediction
};

/** Custom tooltip shown on hover */
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="chart-tooltip">
        <p className="tooltip-date">{label}</p>
        {payload.map((p) => (
          <p key={p.dataKey} style={{ color: p.color }}>
            {p.dataKey}: ₹{p.value?.toLocaleString('en-IN')}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

const PriceHistoryChart = ({ historyData, productName, predictedPrice }) => {
  const { chartData, platforms } = useMemo(() => {
    if (!historyData?.history?.length) return { chartData: [], platforms: [] };

    // Pivot: date → { Amazon, Flipkart, Croma }
    const dateMap = {};
    const platformSet = new Set();

    historyData.history.forEach(({ date, price, platform }) => {
      if (!dateMap[date]) dateMap[date] = { date };
      if (platform) {
        dateMap[date][platform] = price;
        platformSet.add(platform);
      } else {
        dateMap[date]['Price'] = price;
        platformSet.add('Price');
      }
    });

    const sorted = Object.values(dateMap).sort((a, b) => a.date.localeCompare(b.date));

    // Append a "Predicted" data point if we have one
    if (predictedPrice != null) {
      const lastDate = sorted[sorted.length - 1]?.date ?? 'Predicted';
      // Create a synthetic next date label
      const lastDateObj = new Date(lastDate);
      const nextDate = isNaN(lastDateObj.getTime())
        ? 'Predicted'
        : new Date(lastDateObj.getTime() + 86400000)
            .toISOString()
            .slice(0, 10);

      sorted.push({ date: nextDate, Predicted: predictedPrice });
      platformSet.add('Predicted');
    }

    return {
      chartData: sorted,
      platforms: Array.from(platformSet),
    };
  }, [historyData, predictedPrice]);

  if (!historyData || !historyData.history?.length) return null;

  const { lowest_price, highest_price } = historyData;

  // Trend: compare last two data points across all platforms
  const allPrices = historyData.history.map((h) => h.price);
  const firstPrice = allPrices[0];
  const lastPrice = allPrices[allPrices.length - 1];
  const trendUp = lastPrice > firstPrice;
  const trendDown = lastPrice < firstPrice;
  const trendDiff = Math.abs(((lastPrice - firstPrice) / firstPrice) * 100).toFixed(1);

  return (
    <section className="history-section">
      <h2 className="section-title">
        📈 Price History
        {productName && <span className="history-product-name"> – {productName}</span>}
      </h2>

      {/* Stats Row */}
      <div className="stats-row">
        <div className="stat-card stat-card--low">
          <span className="stat-icon">⬇️</span>
          <div>
            <p className="stat-label">Lowest Price</p>
            <p className="stat-value">₹{lowest_price?.toLocaleString('en-IN') ?? '—'}</p>
          </div>
        </div>
        <div className="stat-card stat-card--high">
          <span className="stat-icon">⬆️</span>
          <div>
            <p className="stat-label">Highest Price</p>
            <p className="stat-value">₹{highest_price?.toLocaleString('en-IN') ?? '—'}</p>
          </div>
        </div>
        <div className={`stat-card ${trendUp ? 'stat-card--up' : trendDown ? 'stat-card--down' : 'stat-card--flat'}`}>
          <span className="stat-icon">{trendUp ? '📈' : trendDown ? '📉' : '➡️'}</span>
          <div>
            <p className="stat-label">Price Trend</p>
            <p className="stat-value">
              {trendUp ? '↑' : trendDown ? '↓' : '→'} {trendDiff}%
            </p>
          </div>
        </div>
        {predictedPrice != null && (
          <div className="stat-card stat-card--predicted">
            <span className="stat-icon">🤖</span>
            <div>
              <p className="stat-label">AI Predicted</p>
              <p className="stat-value">₹{predictedPrice.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</p>
            </div>
          </div>
        )}
      </div>

      {/* Chart */}
      <div className="chart-wrapper">
        <ResponsiveContainer width="100%" height={340}>
          <LineChart data={chartData} margin={{ top: 10, right: 30, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
            <XAxis
              dataKey="date"
              tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
              tickLine={false}
              axisLine={false}
              tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}k`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ paddingTop: 16, color: 'var(--text-secondary)' }}
            />
            {/* Horizontal reference line for predicted price */}
            {predictedPrice != null && (
              <ReferenceLine
                y={predictedPrice}
                stroke="#A855F7"
                strokeDasharray="6 3"
                label={{
                  value: 'AI Prediction',
                  position: 'insideTopRight',
                  fill: '#A855F7',
                  fontSize: 11,
                }}
              />
            )}
            {platforms.map((platform) => (
              <Line
                key={platform}
                type={platform === 'Predicted' ? 'monotone' : 'monotone'}
                dataKey={platform}
                stroke={PLATFORM_COLORS[platform] || '#8B5CF6'}
                strokeWidth={platform === 'Predicted' ? 2 : 2.5}
                strokeDasharray={platform === 'Predicted' ? '6 3' : undefined}
                dot={
                  platform === 'Predicted'
                    ? { r: 7, fill: '#A855F7', stroke: '#fff', strokeWidth: 2 }
                    : { r: 4, fill: PLATFORM_COLORS[platform] || '#8B5CF6' }
                }
                activeDot={{ r: 7 }}
                connectNulls
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
};

export default PriceHistoryChart;
