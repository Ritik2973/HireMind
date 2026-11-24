import { useState } from 'react';
import { BrainCircuit, Info } from 'lucide-react';

/**
 * SkillRadarChart
 * Six-axis radar (spider) SVG visualization for the 6 Career Readiness dimensions.
 *
 * Props:
 * - report: Object containing the 6 dimension scores (e.g. from career_readiness.latest_report)
 *   Expected fields:
 *     - technical_score (0-100)
 *     - problem_solving_score (0-100)
 *     - communication_score (0-100)
 *     - behavioral_score (0-100)
 *     - resume_skill_match_score (0-100)
 *     - interview_performance_score (0-100)
 * - className: Optional string for container styling
 */
const SkillRadarChart = ({ report = null, className = '' }) => {
  const [activeDimension, setActiveDimension] = useState(null);

  const dimensions = [
    { key: 'technical_score', label: 'Technical', weight: '25%', score: report?.technical_score },
    { key: 'problem_solving_score', label: 'Problem Solving', weight: '20%', score: report?.problem_solving_score },
    { key: 'communication_score', label: 'Communication', weight: '20%', score: report?.communication_score },
    { key: 'behavioral_score', label: 'Behavioral', weight: '15%', score: report?.behavioral_score },
    { key: 'resume_skill_match_score', label: 'Resume Match', weight: '10%', score: report?.resume_skill_match_score },
    { key: 'interview_performance_score', label: 'Interview Perf.', weight: '10%', score: report?.interview_performance_score },
  ];

  const hasData = report && dimensions.some((d) => typeof d.score === 'number' && !isNaN(d.score));

  // Chart coordinate geometry
  const size = 340;
  const center = size / 2;
  const radius = 105;
  const totalAxes = dimensions.length;
  const angleStep = (Math.PI * 2) / totalAxes;
  const startAngle = -Math.PI / 2; // Start from top (12 o'clock)

  // Helper to compute (x, y) for an angle and radius
  const getCoordinates = (angle, dist) => {
    return {
      x: center + dist * Math.cos(angle),
      y: center + dist * Math.sin(angle),
    };
  };

  // Concentric polygon grid points for background circles (25%, 50%, 75%, 100%)
  const gridLevels = [0.25, 0.5, 0.75, 1.0];
  const gridPolygons = gridLevels.map((lvl) => {
    const points = dimensions.map((_, i) => {
      const angle = startAngle + i * angleStep;
      const { x, y } = getCoordinates(angle, radius * lvl);
      return `${x},${y}`;
    }).join(' ');
    return { level: lvl, points };
  });

  // Data polygon calculation
  const dataPoints = dimensions.map((d, i) => {
    const angle = startAngle + i * angleStep;
    const scoreVal = typeof d.score === 'number' && !isNaN(d.score) ? Math.max(0, Math.min(100, d.score)) : 0;
    const dist = (scoreVal / 100) * radius;
    return getCoordinates(angle, dist);
  });
  const dataPolygonString = dataPoints.map((p) => `${p.x},${p.y}`).join(' ');

  // Labels coordinates (placed slightly beyond the 100% radius)
  const labelPositions = dimensions.map((d, i) => {
    const angle = startAngle + i * angleStep;
    const labelDist = radius + 36;
    const { x, y } = getCoordinates(angle, labelDist);
    return {
      ...d,
      angle,
      x,
      y,
      dataPoint: dataPoints[i],
    };
  });

  return (
    <div className={`bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl relative flex flex-col justify-between ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <BrainCircuit className="w-5 h-5 text-primary-400" />
          <h3 className="text-base font-bold text-white tracking-tight">Readiness Skill Radar</h3>
        </div>
        <span className="text-xs font-semibold px-2 py-0.5 rounded bg-primary-500/10 text-primary-400 border border-primary-500/20">
          6 Dimensions
        </span>
      </div>

      <p className="text-xs text-slate-400 mb-4">
        Multi-axis synthesis across all core career readiness pillars.
      </p>

      {/* Main Chart Container */}
      <div className="relative flex items-center justify-center min-h-[340px]">
        {!hasData && (
          <div className="absolute inset-0 z-20 flex flex-col items-center justify-center bg-slate-900/80 backdrop-blur-xs rounded-xl p-6 text-center">
            <Info className="w-8 h-8 text-slate-500 mb-2" />
            <h4 className="text-sm font-semibold text-slate-300 mb-1">No Skill Radar Data</h4>
            <p className="text-xs text-slate-500 max-w-[220px]">
              Complete an adaptive mock interview and upload a resume to view your 6-dimension skill radar.
            </p>
          </div>
        )}

        <svg
          viewBox={`0 0 ${size} ${size}`}
          className="w-full max-w-[340px] h-auto overflow-visible select-none"
        >
          <defs>
            <linearGradient id="radarAreaGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#22c55e" stopOpacity="0.45" />
              <stop offset="100%" stopColor="#059669" stopOpacity="0.15" />
            </linearGradient>
            <filter id="radarGlow" x="-20%" y="-20%" width="140%" height="140%">
              <feDropShadow dx="0" dy="0" stdDeviation="4" floodColor="#22c55e" floodOpacity="0.4" />
            </filter>
          </defs>

          {/* Concentric Grid Polygons */}
          {gridPolygons.map(({ level, points }) => (
            <polygon
              key={level}
              points={points}
              fill="none"
              stroke="#334155"
              strokeWidth={level === 1.0 ? '1.5' : '1'}
              strokeDasharray={level === 1.0 ? 'none' : '3,3'}
              opacity={level === 1.0 ? 0.7 : 0.4}
            />
          ))}

          {/* Level Markers (25, 50, 75, 100) along top axis */}
          {gridLevels.map((lvl) => (
            <text
              key={lvl}
              x={center + 4}
              y={center - radius * lvl + 10}
              fill="#64748b"
              fontSize="9"
              fontFamily="monospace"
              className="select-none pointer-events-none"
            >
              {Math.round(lvl * 100)}
            </text>
          ))}

          {/* Radial Axis Spokes */}
          {dimensions.map((_, i) => {
            const angle = startAngle + i * angleStep;
            const { x, y } = getCoordinates(angle, radius);
            return (
              <line
                key={i}
                x1={center}
                y1={center}
                x2={x}
                y2={y}
                stroke="#334155"
                strokeWidth="1"
                opacity="0.5"
              />
            );
          })}

          {/* Active Data Filled Polygon */}
          {hasData && (
            <>
              <polygon
                points={dataPolygonString}
                fill="url(#radarAreaGradient)"
                stroke="#22c55e"
                strokeWidth="2"
                filter="url(#radarGlow)"
                className="transition-all duration-700 ease-out"
              />

              {/* Data Vertex Dots */}
              {dataPoints.map((pt, i) => {
                const dim = dimensions[i];
                const isHovered = activeDimension === dim.key;
                return (
                  <g key={i}>
                    <circle
                      cx={pt.x}
                      cy={pt.y}
                      r={isHovered ? 6 : 4}
                      fill={isHovered ? '#4ade80' : '#22c55e'}
                      stroke="#0f172a"
                      strokeWidth="2"
                      className="transition-all duration-200 cursor-pointer"
                      onMouseEnter={() => setActiveDimension(dim.key)}
                      onMouseLeave={() => setActiveDimension(null)}
                    />
                  </g>
                );
              })}
            </>
          )}

          {/* Labels & Score Badges Outside the Polygon */}
          {labelPositions.map((pos) => {
            const isHovered = activeDimension === pos.key;
            const isTop = pos.y < center - 20;
            const isBottom = pos.y > center + 20;
            const textAnchor = Math.abs(pos.x - center) < 15 ? 'middle' : pos.x > center ? 'start' : 'end';

            return (
              <g
                key={pos.key}
                className="cursor-pointer transition-opacity"
                onMouseEnter={() => setActiveDimension(pos.key)}
                onMouseLeave={() => setActiveDimension(null)}
              >
                <text
                  x={pos.x}
                  y={isTop ? pos.y - 10 : isBottom ? pos.y + 12 : pos.y}
                  textAnchor={textAnchor}
                  fill={isHovered ? '#ffffff' : '#94a3b8'}
                  fontSize="11"
                  fontWeight={isHovered ? '700' : '500'}
                  className="transition-colors"
                >
                  {pos.label}
                </text>
                <text
                  x={pos.x}
                  y={isTop ? pos.y + 2 : isBottom ? pos.y + 24 : pos.y + 13}
                  textAnchor={textAnchor}
                  fill={hasData && typeof pos.score === 'number' ? '#22c55e' : '#64748b'}
                  fontSize="10"
                  fontWeight="600"
                  fontFamily="monospace"
                >
                  {typeof pos.score === 'number' && !isNaN(pos.score) ? `${pos.score.toFixed(1)}%` : '—'}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Legend Footer */}
      <div className="border-t border-slate-800/80 pt-3 mt-2 flex items-center justify-between text-xs text-slate-500">
        <span>Scale: 0–100%</span>
        <span>Benchmark: Role Target</span>
      </div>
    </div>
  );
};

export default SkillRadarChart;
