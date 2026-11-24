import { Link } from 'react-router-dom';
import { 
  FileText, 
  BrainCircuit, 
  BarChart3, 
  ArrowRight, 
  Sparkles
} from 'lucide-react';

/**
 * DashboardEmptyState
 * Guided onboarding banner displayed for first-time candidates
 * when no interviews or resumes have been registered yet.
 */
const DashboardEmptyState = ({ userName = 'Candidate', targetJobRole = null }) => {
  const steps = [
    {
      num: '1',
      title: 'Upload Your Resume',
      desc: 'Our NLP engine parses your technical skills and matches them against target job profiles.',
      icon: FileText,
      linkText: 'Upload Resume',
      linkTo: '/resume',
      accent: 'border-blue-500/20 bg-blue-500/10 text-blue-400'
    },
    {
      num: '2',
      title: 'Take Adaptive Interview',
      desc: 'Answer real questions where difficulty dynamically adapts to your response depth.',
      icon: BrainCircuit,
      linkText: 'Start Interview',
      linkTo: '/interview',
      accent: 'border-primary-500/20 bg-primary-500/10 text-primary-400'
    },
    {
      num: '3',
      title: 'Unlock Analytics & Readiness',
      desc: 'Receive deterministic 6-dimension evaluation scores and strategic recommendations.',
      icon: BarChart3,
      linkText: 'Learn More',
      linkTo: '/results',
      accent: 'border-purple-500/20 bg-purple-500/10 text-purple-400'
    }
  ];

  return (
    <div className="bg-slate-900 border border-primary-500/30 rounded-3xl p-8 sm:p-10 mb-10 shadow-2xl relative overflow-hidden">
      {/* Background ambient glow */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-primary-600/10 blur-[100px] rounded-full pointer-events-none" />

      <div className="relative z-10">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-primary-500/10 text-primary-400 border border-primary-500/20 mb-3">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Getting Started with HireMind</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Welcome, {userName}! Let's build your Career Readiness profile
            </h2>
            <p className="text-slate-400 text-sm mt-1 max-w-2xl leading-relaxed">
              Complete these three simple steps to unlock your personalized 6-dimensional skill radar, performance trends, and AI-driven readiness benchmarks for <span className="text-white font-medium">{targetJobRole || 'your target role'}</span>.
            </p>
          </div>

          <Link
            to="/interview"
            className="self-start md:self-auto flex items-center gap-2 bg-primary-600 hover:bg-primary-500 text-white text-sm font-semibold px-6 py-3 rounded-xl transition-all shadow-[0_0_15px_rgba(34,197,94,0.3)] hover:shadow-[0_0_25px_rgba(34,197,94,0.5)] shrink-0"
          >
            <span>Launch Interview</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        {/* 3 Step Process Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {steps.map((step) => {
            const Icon = step.icon;
            return (
              <div
                key={step.num}
                className="bg-slate-950/70 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between hover:border-slate-700 transition-all duration-200"
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <span className="w-7 h-7 rounded-full bg-slate-900 border border-slate-700 text-slate-300 text-xs font-bold flex items-center justify-center font-mono">
                      {step.num}
                    </span>
                    <div className={`p-2 rounded-xl border ${step.accent}`}>
                      <Icon className="w-4 h-4" />
                    </div>
                  </div>

                  <h3 className="text-base font-bold text-white mb-2">{step.title}</h3>
                  <p className="text-xs text-slate-400 leading-relaxed mb-6">
                    {step.desc}
                  </p>
                </div>

                <Link
                  to={step.linkTo}
                  className="inline-flex items-center gap-1.5 text-xs font-semibold text-primary-400 hover:text-primary-300 transition-colors pt-3 border-t border-slate-800/80"
                >
                  <span>{step.linkText}</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default DashboardEmptyState;
