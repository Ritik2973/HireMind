import { useState } from 'react';
import { TrendingUp, Calendar, Award } from 'lucide-react';

/**
 * PerformanceTrendChart
 * Visualizes historical career readiness and performance trends over time.
 *
 * Props:
 * - history: Array of historical items (e.g. from career_readiness.history)
 *   Expected item fields:
 *     - id: number
 *     - overall_readiness_score: number (0-100)
 *     - generated_at: string/Date
 *     - target_job_role: Optional string
 * - title: Optional string header
 * - className: Optional string for container styling
 */
const PerformanceTrendChart = ({ 
  history = [], 
  title = "Readiness Score Progression",
  className = "" 
}) => {
  const [hoveredPoint, setHoveredPoint] = useState(null);

  const hasHistory = Array.isArray(history) && history.length > 0;
  const isSinglePoint = hasHistory && history.length === 1;

  // Chart Dimensions
  const svgWidth = 560;
  const svgHeight = 220;
  const padding = { top: 25, right: 30, bottom: 40, left: 45 };

  const plotWidth = svgWidth - padding.left - padding.right;
  const plotHeight = svgHeight - padding.top - padding.bottom;

  // Compute Coordinates for historical data
  const points = hasHistory
    ? history.map((item, index) => {
        const score = typeof item.overall_readiness_score === 'number' ? item.overall_readiness_score : 0;
        const x = isSinglePoint
          ? padding.left + plotWidth / 2
          : padding.left + (index / (history.length - 1)) * plotWidth;
        const y = padding.top + plotHeight - (Math.max(0, Math.min(100, score)) / 100) * plotHeight;
        
        const dateObj = new Date(item.generated_at);
        const formattedDate = !isNaN(dateObj.getTime())
          ? dateObj.toLocaleDateString([], { month: 'short', day: 'numeric' })
          : `Session #${item.id || index + 1}`;

        return {
          ...item,
          x,
          y,
          score,
          formattedDate,
        };
      })
    : [];

  // Construct SVG Path
  const linePath = points.length > 1
    ? points.reduce((path, pt, i) => `${path} ${i === 0 ? 'M' : 'L'} ${pt.x} ${pt.y}`, '')
    : '';

  const areaPath = points.length > 1
    ? `${linePath} L ${points[points.length - 1].x} ${padding.top + plotHeight} L ${points[0].x} ${padding.top + plotHeight} Z`
    : '';

  // Trend Delta calculation
  let scoreDelta = null;
  if (points.length >= 2) {
    const firstScore = points[0].score;
    const latestScore = points[points.length - 1].score;
    scoreDelta = Math.round((latestScore - firstScore) * 10) / 10;
  }

  return (
    <div className={`bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl relative flex flex-col justify-between ${className}`}>
      
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-primary-400" />
            <h3 className="text-base font-bold text-white tracking-tight">{title}</h3>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Historical evolution of your readiness score across assessments.
          </p>
        </div>

        {scoreDelta !== null && (
          <div className={`px-2.5 py-1 rounded-full text-xs font-semibold flex items-center gap-1 border ${
            scoreDelta >= 0
              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
              : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
          }`}>
            <span>{scoreDelta >= 0 ? `+${scoreDelta}` : scoreDelta} pts</span>
          </div>
        )}
      </div>

      {/* Main Chart Body */}
      <div className="relative min-h-[220px] flex items-center justify-center">
        {!hasDataHelper(history) ? (
          <div className="flex flex-col items-center justify-center p-8 text-center bg-slate-950/40 rounded-xl border border-slate-800/60 w-full">
            <Calendar className="w-8 h-8 text-slate-500 mb-2" />
            <h4 className="text-sm font-semibold text-slate-300 mb-1">Insufficient Trend Data</h4>
            <p className="text-xs text-slate-500 max-w-xs">
              Complete multiple adaptive interview sessions to generate a progression curve tracking your score growth over time.
            </p>
          </div>
        ) : isSinglePoint ? (
          <div className="flex flex-col items-center justify-center p-6 text-center bg-slate-950/40 rounded-xl border border-slate-800/60 w-full">
            <div className="p-3 bg-primary-500/10 border border-primary-500/20 rounded-full mb-3">
              <Award className="w-6 h-6 text-primary-400" />
            </div>
            <h4 className="text-sm font-semibold text-white mb-1">
              Baseline Score Recorded: {points[0].score.toFixed(1)}/100
            </h4>
            <p className="text-xs text-slate-400 max-w-sm mb-2">
              Assessed on {points[0].formattedDate}. Take your next interview to establish your progression trajectory.
            </p>
            <span className="text-[11px] text-primary-400 font-mono">1 Assessment Logged</span>
          </div>
        ) : (
          <div className="w-full overflow-x-auto">
            <svg
              viewBox={`0 0 ${svgWidth} ${svgHeight}`}
              className="w-full h-auto overflow-visible select-none"
            >
              <defs>
                <linearGradient id="trendGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#22c55e" stopOpacity="0.35" />
                  <stop offset="100%" stopColor="#22c55e" stopOpacity="0.0" />
                </linearGradient>
              </defs>

              {/* Horizontal Y-Gridlines & Y-Axis Labels */}
              {[0, 25, 50, 75, 100].map((val) => {
                const y = padding.top + plotHeight - (val / 100) * plotHeight;
                return (
                  <g key={val}>
                    <line
                      x1={padding.left}
                      y1={y}
                      x2={svgWidth - padding.right}
                      y2={y}
                      stroke="#334155"
                      strokeWidth="1"
                      strokeDasharray="4,4"
                      opacity="0.4"
                    />
                    <text
                      x={padding.left - 10}
                      y={y + 3}
                      fill="#64748b"
                      fontSize="10"
                      textAnchor="end"
                      fontFamily="monospace"
                    >
                      {val}
                    </text>
                  </g>
                );
              })}

              {/* Shaded Area under Curve */}
              <path d={areaPath} fill="url(#trendGradient)" />

              {/* Trend Stroke Line */}
              <path
                d={linePath}
                fill="none"
                stroke="#22c55e"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />

              {/* Data Points and Hover Interaction */}
              {points.map((pt, idx) => {
                const isHovered = hoveredPoint?.id === pt.id || (hoveredPoint === null && idx === points.length - 1);
                return (
                  <g key={pt.id || idx}>
                    <circle
                      cx={pt.x}
                      cy={pt.y}
                      r={isHovered ? 6 : 4}
                      fill={isHovered ? '#4ade80' : '#22c55e'}
                      stroke="#0f172a"
                      strokeWidth="2"
                      className="cursor-pointer transition-all duration-200"
                      onMouseEnter={() => setHoveredPoint(pt)}
                      onMouseLeave={() => setHoveredPoint(null)}
                    />
                    {/* X-axis Date Label */}
                    <text
                      x={pt.x}
                      y={svgHeight - 12}
                      textAnchor="middle"
                      fill={isHovered ? '#f8fafc' : '#64748b'}
                      fontSize="10"
                      fontFamily="monospace"
                      fontWeight={isHovered ? '600' : '400'}
                    >
                      {pt.formattedDate}
                    </text>
                  </g>
                );
              })}

              {/* Hovered / Active Tooltip */}
              {hoveredPoint && (
                <g transform={`translate(${hoveredPoint.x}, ${hoveredPoint.y - 12})`}>
                  <rect
                    x="-45"
                    y="-30"
                    width="90"
                    height="26"
                    rx="6"
                    fill="#0f172a"
                    stroke="#334155"
                    strokeWidth="1"
                  />
                  <text
                    x="0"
                    y="-13"
                    fill="#22c55e"
                    fontSize="11"
                    fontWeight="bold"
                    textAnchor="middle"
                    fontFamily="monospace"
                  >
                    {hoveredPoint.score.toFixed(1)}/100
                  </text>
                </g>
              )}
            </svg>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="border-t border-slate-800/80 pt-3 mt-2 flex items-center justify-between text-xs text-slate-500">
        <span>Timeline: Oldest → Latest</span>
        <span>Goal Benchmark: 85+</span>
      </div>

    </div>
  );
};

function hasDataHelper(history) {
  return Array.isArray(history) && history.length > 0;
}

export default PerformanceTrendChart;
