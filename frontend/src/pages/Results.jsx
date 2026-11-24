import { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { 
  Award, 
  Code2, 
  Cpu, 
  MessageSquare, 
  Users, 
  FileText, 
  BarChart3, 
  TrendingUp, 
  CheckCircle2, 
  ArrowRight, 
  Loader2,
  Calendar,
  Sparkles,
  RefreshCw
} from 'lucide-react';
import api from '../api/client';

const Results = () => {
  const [searchParams] = useSearchParams();
  const reportId = searchParams.get('reportId');
  const sessionId = searchParams.get('sessionId');

  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchReport = async () => {
      setLoading(true);
      setError(null);
      try {
        let res;
        if (reportId) {
          res = await api.get(`/career-readiness/${reportId}`);
        } else if (sessionId) {
          res = await api.get(`/career-readiness/session/${sessionId}`);
        } else {
          res = await api.get('/career-readiness/latest');
        }
        setReport(res.data);
      } catch (err) {
        if (err.response?.status === 404) {
          setError('not_found');
        } else {
          setError(err.response?.data?.detail || 'Failed to load Career Readiness Report.');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchReport();
  }, [reportId, sessionId]);

  const getTierInfo = (score) => {
    if (score >= 85) {
      return {
        label: 'Strong',
        badgeBg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
        textColor: 'text-emerald-400',
        barBg: 'bg-emerald-500',
        glow: 'drop-shadow-[0_0_15px_rgba(16,185,129,0.35)]'
      };
    }
    if (score >= 70) {
      return {
        label: 'Solid',
        badgeBg: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
        textColor: 'text-blue-400',
        barBg: 'bg-blue-500',
        glow: 'drop-shadow-[0_0_15px_rgba(59,130,246,0.35)]'
      };
    }
    if (score >= 50) {
      return {
        label: 'Developing',
        badgeBg: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
        textColor: 'text-amber-400',
        barBg: 'bg-amber-500',
        glow: 'drop-shadow-[0_0_15px_rgba(245,158,11,0.35)]'
      };
    }
    return {
      label: 'Needs substantial improvement',
      badgeBg: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
      textColor: 'text-rose-400',
      barBg: 'bg-rose-500',
      glow: 'drop-shadow-[0_0_15px_rgba(244,63,94,0.35)]'
    };
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-24 text-center min-h-[70vh] flex flex-col justify-center items-center">
        <Loader2 className="w-12 h-12 text-primary-500 animate-spin mb-4" />
        <h2 className="text-xl font-bold text-white mb-2">Analyzing Career Readiness Report</h2>
        <p className="text-slate-400 text-sm">Aggregating 6 evaluation dimensions and MiniLM skill embeddings...</p>
      </div>
    );
  }

  if (error === 'not_found' || !report) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-20 text-center min-h-[70vh] flex flex-col justify-center items-center">
        <div className="w-20 h-20 bg-slate-900 border border-slate-800 rounded-full flex items-center justify-center mb-6">
          <Award className="w-10 h-10 text-slate-500" />
        </div>
        <h1 className="text-3xl font-bold text-white mb-3">No Career Readiness Report Found</h1>
        <p className="text-slate-400 max-w-lg mb-8 text-base">
          To generate an end-to-end Career Readiness Report, complete an adaptive AI interview session and have a resume uploaded for role-benchmark matching.
        </p>
        <div className="flex flex-wrap justify-center gap-4">
          <Link
            to="/interview"
            className="flex items-center gap-2 bg-primary-600 hover:bg-primary-500 text-white px-6 py-3 rounded-lg font-medium transition-all shadow-[0_0_15px_rgba(34,197,94,0.3)]"
          >
            Start Mock Interview <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            to="/resume"
            className="bg-slate-800 hover:bg-slate-700 text-white border border-slate-700 px-6 py-3 rounded-lg font-medium transition-colors"
          >
            Manage Resumes
          </Link>
        </div>
      </div>
    );
  }

  const overallTier = getTierInfo(report.overall_readiness_score);

  const dimensions = [
    {
      id: 'technical',
      title: 'Technical Accuracy',
      weight: '25% Weight',
      score: report.technical_score,
      icon: Code2,
      recommendation: report.component_recommendations?.technical,
      description: 'Depth of technical accuracy and core concept coverage across technical questions.'
    },
    {
      id: 'problem_solving',
      title: 'Problem Solving',
      weight: '20% Weight',
      score: report.problem_solving_score,
      icon: Cpu,
      recommendation: report.component_recommendations?.problem_solving,
      description: 'Analytical reasoning, algorithmic thinking, and methodical approach to complex problems.'
    },
    {
      id: 'communication',
      title: 'Communication & Articulation',
      weight: '20% Weight',
      score: report.communication_score,
      icon: MessageSquare,
      recommendation: report.component_recommendations?.communication,
      description: '60% semantic similarity with benchmark criteria and 40% answer completeness.'
    },
    {
      id: 'behavioral',
      title: 'Behavioral Alignment',
      weight: '15% Weight',
      score: report.behavioral_score,
      icon: Users,
      recommendation: report.component_recommendations?.behavioral,
      description: 'Evaluation of situational judgment, collaboration, accountability, and STAR structure.'
    },
    {
      id: 'resume_skill_match',
      title: 'Resume-Role Skill Match',
      weight: '10% Weight',
      score: report.resume_skill_match_score,
      icon: FileText,
      recommendation: report.component_recommendations?.resume_skill_match,
      description: 'MiniLM semantic embedding match between your resume text and target role benchmark.'
    },
    {
      id: 'interview_performance',
      title: 'Interview Performance',
      weight: '10% Weight',
      score: report.interview_performance_score,
      icon: BarChart3,
      recommendation: report.component_recommendations?.interview_performance,
      description: 'Overall average performance across all completed questions in the session.'
    }
  ];

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 min-h-[85vh]">
      
      {/* Header Info */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-primary-500/10 text-primary-400 border border-primary-500/20 uppercase tracking-wider">
              {report.target_job_role}
            </span>
            <span className="text-xs text-slate-500 font-mono">
              Report #{report.id}
            </span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">
            Career Readiness Analysis
          </h1>
          <p className="text-slate-400 mt-1 text-sm">
            Deterministic AI evaluation based on your completed interview responses and verified resume.
          </p>
        </div>

        <div className="flex items-center gap-3 text-xs text-slate-400 bg-slate-900 border border-slate-800 px-4 py-2.5 rounded-lg self-start md:self-auto">
          <Calendar className="w-4 h-4 text-slate-500" />
          <span>Generated: {new Date(report.generated_at).toLocaleDateString()} at {new Date(report.generated_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
        </div>
      </div>

      {/* Hero: Overall Readiness Score */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-8 sm:p-10 mb-10 shadow-2xl relative overflow-hidden backdrop-blur-sm">
        <div className="absolute top-0 right-0 w-80 h-80 bg-primary-600/10 blur-[100px] rounded-full pointer-events-none"></div>

        <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-center relative z-10">
          
          {/* Big Score Display */}
          <div className="md:col-span-5 text-center md:text-left flex flex-col items-center md:items-start">
            <span className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-2">
              Overall Career Readiness
            </span>
            <div className={`text-6xl sm:text-7xl font-extrabold text-white mb-3 tracking-tight ${overallTier.glow}`}>
              {report.overall_readiness_score.toFixed(1)}
              <span className="text-2xl sm:text-3xl font-normal text-slate-500 ml-1">/100</span>
            </div>
            <div className={`inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-sm font-semibold border ${overallTier.badgeBg}`}>
              <Sparkles className="w-4 h-4" />
              {overallTier.label} Readiness
            </div>
          </div>

          {/* Explanation & Weights breakdown */}
          <div className="md:col-span-7 border-t md:border-t-0 md:border-l border-slate-800 pt-6 md:pt-0 md:pl-8">
            <h3 className="text-base font-semibold text-white mb-2 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-primary-400" />
              Multi-Dimensional Synthesis
            </h3>
            <p className="text-slate-400 text-sm leading-relaxed mb-4">
              Your overall score is calculated through a deterministic weighted matrix across 6 key evaluation pillars: Technical (25%), Problem Solving (20%), Communication (20%), Behavioral (15%), Resume Match (10%), and Performance (10%).
            </p>
            <div className="w-full bg-slate-950 rounded-full h-3 overflow-hidden border border-slate-800">
              <div 
                className={`h-full ${overallTier.barBg} transition-all duration-1000`}
                style={{ width: `${Math.min(100, Math.max(0, report.overall_readiness_score))}%` }}
              ></div>
            </div>
          </div>

        </div>
      </div>

      {/* Section 2: 6 Component Dimensions Grid */}
      <div className="mb-12">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-white tracking-tight">Component Breakdown</h2>
          <p className="text-slate-400 text-sm mt-1">Detailed evaluation and recommendations for each of the six readiness dimensions.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {dimensions.map((dim) => {
            const tier = getTierInfo(dim.score);
            const IconComponent = dim.icon;

            return (
              <div 
                key={dim.id}
                className="bg-slate-900 border border-slate-800 hover:border-slate-700/80 rounded-2xl p-6 transition-all shadow-lg flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div className="p-2.5 bg-slate-950 border border-slate-800 rounded-xl">
                      <IconComponent className="w-5 h-5 text-primary-400" />
                    </div>
                    <span className="text-xs font-semibold px-2.5 py-1 rounded-md bg-slate-800 text-slate-300 border border-slate-700">
                      {dim.weight}
                    </span>
                  </div>

                  <h3 className="text-lg font-bold text-white mb-1">{dim.title}</h3>
                  <p className="text-xs text-slate-400 mb-4 line-clamp-2">{dim.description}</p>

                  <div className="flex items-baseline justify-between mb-2">
                    <div className="text-3xl font-extrabold text-white">
                      {dim.score.toFixed(1)}
                      <span className="text-sm font-normal text-slate-500 ml-1">/100</span>
                    </div>
                    <span className={`text-xs px-2.5 py-0.5 rounded-full font-medium border ${tier.badgeBg}`}>
                      {tier.label}
                    </span>
                  </div>

                  <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800/80 mb-5">
                    <div 
                      className={`h-full ${tier.barBg} transition-all duration-700`}
                      style={{ width: `${Math.min(100, Math.max(0, dim.score))}%` }}
                    ></div>
                  </div>
                </div>

                <div className="border-t border-slate-800 pt-4 mt-auto">
                  <div className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1 flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-primary-400" /> Recommendation
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {dim.recommendation || 'Maintain consistent performance across this dimension.'}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Section 3: Strategic Recommendations */}
      {report.recommendations && report.recommendations.length > 0 && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 mb-10 shadow-xl">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-primary-500/10 border border-primary-500/20 rounded-lg">
              <TrendingUp className="w-5 h-5 text-primary-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Strategic Action Plan</h2>
              <p className="text-xs text-slate-400">Actionable advice generated from your component weaknesses and strengths.</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {report.recommendations.map((rec, index) => (
              <div 
                key={index}
                className="bg-slate-950 border border-slate-800/90 rounded-xl p-4 flex items-start gap-3"
              >
                <div className="mt-0.5 shrink-0">
                  <CheckCircle2 className="w-4 h-4 text-primary-400" />
                </div>
                <p className="text-sm text-slate-300 leading-relaxed">{rec}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Section 4: Action Footer */}
      <div className="flex flex-wrap items-center justify-center gap-4 pt-4 border-t border-slate-800">
        <Link 
          to="/interview"
          className="flex items-center gap-2 bg-primary-600 hover:bg-primary-500 text-white px-6 py-3 rounded-lg font-medium transition-all shadow-[0_0_15px_rgba(34,197,94,0.3)] hover:shadow-[0_0_25px_rgba(34,197,94,0.5)] cursor-pointer"
        >
          <RefreshCw className="w-4 h-4" /> Retake Adaptive Interview
        </Link>
        <Link 
          to="/resume"
          className="bg-slate-800 hover:bg-slate-700 text-white border border-slate-700 px-6 py-3 rounded-lg font-medium transition-colors cursor-pointer"
        >
          Update Resume
        </Link>
        <Link 
          to="/dashboard"
          className="bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 px-6 py-3 rounded-lg font-medium transition-colors cursor-pointer"
        >
          Back to Dashboard
        </Link>
      </div>

    </div>
  );
};

export default Results;