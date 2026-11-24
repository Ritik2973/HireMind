import { Code2, Cpu, Users, Layers } from 'lucide-react';

/**
 * CategoryBreakdown
 * Visualizes candidate performance across the three core interview categories:
 * Technical, Problem Solving, and Behavioral.
 *
 * Props:
 * - categoryPerformance: Object with category averages:
 *     - technical_average: Optional number (0-100) or null
 *     - problem_solving_average: Optional number (0-100) or null
 *     - behavioral_average: Optional number (0-100) or null
 * - className: Optional string for container styling
 */
const CategoryBreakdown = ({ categoryPerformance = {}, className = "" }) => {
  const getTier = (score) => {
    if (typeof score !== 'number' || isNaN(score)) return null;
    if (score >= 85) return { label: 'Strong', badge: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' };
    if (score >= 70) return { label: 'Solid', badge: 'bg-blue-500/10 text-blue-400 border-blue-500/20' };
    if (score >= 50) return { label: 'Developing', badge: 'bg-amber-500/10 text-amber-400 border-amber-500/20' };
    return { label: 'Needs Improvement', badge: 'bg-rose-500/10 text-rose-400 border-rose-500/20' };
  };

  const categories = [
    {
      id: 'technical',
      name: 'Technical Competence',
      score: categoryPerformance?.technical_average,
      icon: Code2,
      accentColor: 'text-blue-400',
      barColor: 'bg-blue-500',
      description: 'System concepts, syntax depth, and accurate technical solution benchmarks.',
    },
    {
      id: 'problem_solving',
      name: 'Problem Solving',
      score: categoryPerformance?.problem_solving_average,
      icon: Cpu,
      accentColor: 'text-indigo-400',
      barColor: 'bg-indigo-500',
      description: 'Analytical logic, complexity evaluation, and methodical problem decomposition.',
    },
    {
      id: 'behavioral',
      name: 'Behavioral & Leadership',
      score: categoryPerformance?.behavioral_average,
      icon: Users,
      accentColor: 'text-emerald-400',
      barColor: 'bg-emerald-500',
      description: 'Situational judgment, communication clarity, teamwork, and STAR structure.',
    },
  ];

  return (
    <div className={`bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between ${className}`}>
      {/* Header */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Layers className="w-5 h-5 text-primary-400" />
            <h3 className="text-base font-bold text-white tracking-tight">Category Breakdown</h3>
          </div>
          <span className="text-xs text-slate-500 font-medium">3 Pillars</span>
        </div>
        <p className="text-xs text-slate-400 mb-6">
          Aggregated performance across distinct question categories in your interview sessions.
        </p>

        {/* Categories List */}
        <div className="space-y-5">
          {categories.map((cat) => {
            const Icon = cat.icon;
            const hasScore = typeof cat.score === 'number' && !isNaN(cat.score);
            const tier = getTier(cat.score);
            const clampedScore = hasScore ? Math.max(0, Math.min(100, cat.score)) : 0;

            return (
              <div 
                key={cat.id}
                className="bg-slate-950/60 border border-slate-800/80 hover:border-slate-700/80 rounded-xl p-4 transition-all duration-200"
              >
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center gap-2.5">
                    <div className="p-1.5 rounded-lg bg-slate-900 border border-slate-800">
                      <Icon className={`w-4 h-4 ${cat.accentColor}`} />
                    </div>
                    <span className="text-sm font-semibold text-white">{cat.name}</span>
                  </div>

                  <div className="flex items-center gap-2">
                    {tier && (
                      <span className={`text-[11px] px-2 py-0.5 rounded-full font-medium border ${tier.badge}`}>
                        {tier.label}
                      </span>
                    )}
                    <span className="text-sm font-extrabold text-white font-mono">
                      {hasScore ? `${cat.score.toFixed(1)}%` : '—'}
                    </span>
                  </div>
                </div>

                <p className="text-[11px] text-slate-400 mb-3 leading-relaxed">
                  {cat.description}
                </p>

                {/* Progress Bar */}
                <div className="w-full bg-slate-900 rounded-full h-2 overflow-hidden border border-slate-800">
                  {hasScore ? (
                    <div
                      className={`h-full ${cat.barColor} transition-all duration-700 ease-out`}
                      style={{ width: `${clampedScore}%` }}
                    />
                  ) : (
                    <div className="h-full bg-slate-800 text-[9px] text-slate-600 flex items-center justify-center">
                      Not tested yet
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Footer */}
      <div className="border-t border-slate-800/80 pt-3 mt-4 flex items-center justify-between text-xs text-slate-500">
        <span>Evaluated per response</span>
        <span>Target: 70%+ Solid</span>
      </div>
    </div>
  );
};

export default CategoryBreakdown;
