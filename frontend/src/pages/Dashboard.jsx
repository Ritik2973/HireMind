import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  PlayCircle, 
  CheckCircle2, 
  TrendingUp, 
  Award, 
  AlertCircle, 
  RefreshCw, 
  ArrowRight, 
  UploadCloud
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';

import SkillRadarChart from '../components/dashboard/SkillRadarChart';
import PerformanceTrendChart from '../components/dashboard/PerformanceTrendChart';
import CategoryBreakdown from '../components/dashboard/CategoryBreakdown';
import RecentInterviewsTable from '../components/dashboard/RecentInterviewsTable';
import SkillTagsCloud from '../components/dashboard/SkillTagsCloud';
import DashboardEmptyState from '../components/dashboard/DashboardEmptyState';

const Dashboard = () => {
  const { user } = useAuth();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboard = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get('/analytics/dashboard');
      setAnalytics(response.data);
    } catch (err) {
      console.error("Failed to load dashboard analytics:", err);
      setError(err.response?.data?.detail || "Unable to fetch dashboard analytics. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  const getTierBadge = (tier) => {
    switch (tier) {
      case 'Strong':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'Solid':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/30';
      case 'Developing':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'Needs substantial improvement':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      default:
        return 'bg-slate-800 text-slate-400 border-slate-700';
    }
  };

  // Skeleton Loader State
  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 min-h-[85vh]">
        {/* Welcome Skeleton */}
        <div className="mb-8 space-y-2.5 animate-pulse">
          <div className="h-8 bg-slate-900 rounded-lg w-72"></div>
          <div className="h-4 bg-slate-900/60 rounded-md w-96"></div>
        </div>

        {/* 4 Cards Skeleton */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8 animate-pulse">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 h-36">
              <div className="flex justify-between items-center mb-4">
                <div className="h-4 bg-slate-800 rounded w-28"></div>
                <div className="h-6 w-6 bg-slate-800 rounded-full"></div>
              </div>
              <div className="h-8 bg-slate-800 rounded w-20 mb-2"></div>
              <div className="h-3 bg-slate-800/60 rounded w-36"></div>
            </div>
          ))}
        </div>

        {/* Charts Row Skeleton */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8 animate-pulse">
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 h-96"></div>
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 h-96"></div>
        </div>
      </div>
    );
  }

  // Error State with Retry
  if (error && !analytics) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-20 min-h-[70vh] flex flex-col items-center justify-center text-center">
        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-2xl mb-4">
          <AlertCircle className="w-10 h-10 text-red-400" />
        </div>
        <h2 className="text-2xl font-bold text-white mb-2">Failed to Load Dashboard</h2>
        <p className="text-slate-400 text-sm max-w-md mb-6">{error}</p>
        <button
          onClick={fetchDashboard}
          className="inline-flex items-center gap-2 bg-primary-600 hover:bg-primary-500 text-white font-medium py-2.5 px-6 rounded-lg transition-colors cursor-pointer"
        >
          <RefreshCw className="w-4 h-4" /> Retry
        </button>
      </div>
    );
  }

  const interviewStats = analytics?.interview_stats || {};
  const careerReadiness = analytics?.career_readiness || {};
  const resumeStats = analytics?.resume_stats || {};
  const readinessScore = careerReadiness.overall_readiness_score;

  // Check if candidate is first-time / brand-new
  const isFirstTimeCandidate = 
    (interviewStats.total_sessions || 0) === 0 &&
    (resumeStats.resume_count || 0) === 0 &&
    !careerReadiness.latest_report;

  const totalSessions = interviewStats.total_sessions || 0;
  const completedSessions = interviewStats.completed_interviews || 0;
  const completionRate = totalSessions > 0 ? Math.round((completedSessions / totalSessions) * 100) : 0;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 bg-slate-950 min-h-[85vh]">
      
      {/* 1. Welcome Header Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8 border-b border-slate-800/80 pb-6">
        <div>
          <div className="flex items-center gap-3 mb-1.5">
            <h1 className="text-3xl font-extrabold text-white tracking-tight">
              Welcome back, {user?.name?.split(' ')[0] || 'Candidate'}!
            </h1>
            {analytics?.target_job_role && (
              <span className="hidden sm:inline-flex px-3 py-1 rounded-full text-xs font-semibold bg-primary-500/10 text-primary-400 border border-primary-500/20">
                {analytics.target_job_role}
              </span>
            )}
          </div>
          <p className="text-slate-400 text-sm">
            Here is your real-time career readiness analytics and adaptive interview performance overview.
          </p>
        </div>

        {/* Quick Actions Header */}
        <div className="flex flex-wrap items-center gap-3">
          <Link
            to="/interview"
            className="flex items-center gap-2 bg-primary-600 hover:bg-primary-500 text-white text-xs sm:text-sm font-semibold px-4 py-2.5 rounded-lg transition-all shadow-[0_0_12px_rgba(34,197,94,0.25)] hover:shadow-[0_0_20px_rgba(34,197,94,0.4)]"
          >
            <PlayCircle className="w-4 h-4" /> Start Interview
          </Link>
          <Link
            to="/resume"
            className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-white text-xs sm:text-sm font-medium px-4 py-2.5 rounded-lg border border-slate-700 transition-colors"
          >
            <UploadCloud className="w-4 h-4 text-primary-400" /> Manage Resume
          </Link>
          {careerReadiness.latest_report && (
            <Link
              to={`/results?reportId=${careerReadiness.latest_report.id}`}
              className="flex items-center gap-1.5 text-xs text-primary-400 hover:text-primary-300 font-semibold px-3 py-2 rounded-lg hover:bg-slate-900 transition-colors"
            >
              <span>View Latest Report</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          )}
        </div>
      </div>

      {/* 2. Onboarding Empty State for Brand New Candidates */}
      {isFirstTimeCandidate && (
        <DashboardEmptyState 
          userName={user?.name}
          targetJobRole={analytics?.target_job_role || user?.target_job_role}
        />
      )}

      {/* 3. Four Core Overview Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        
        {/* Card 1: Overall Career Readiness */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between relative overflow-hidden">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Career Readiness</span>
            <div className="p-2 bg-slate-950 border border-slate-800 rounded-xl">
              <Award className="w-4 h-4 text-primary-400" />
            </div>
          </div>
          <div className="my-1">
            <div className="text-3xl font-extrabold text-white font-mono">
              {typeof readinessScore === 'number' ? `${readinessScore.toFixed(1)}%` : '—'}
            </div>
            {careerReadiness.readiness_tier ? (
              <span className={`inline-block mt-2 text-[11px] font-semibold px-2.5 py-0.5 rounded-full border ${getTierBadge(careerReadiness.readiness_tier)}`}>
                {careerReadiness.readiness_tier}
              </span>
            ) : (
              <span className="text-xs text-slate-500 mt-1 block">Not assessed yet</span>
            )}
          </div>
          <div className="mt-3 pt-3 border-t border-slate-800/80 text-[11px] text-slate-400 truncate">
            Target: {analytics?.target_job_role || 'Not specified'}
          </div>
        </div>

        {/* Card 2: Total Interviews Taken */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Interviews Taken</span>
            <div className="p-2 bg-slate-950 border border-slate-800 rounded-xl">
              <PlayCircle className="w-4 h-4 text-blue-400" />
            </div>
          </div>
          <div className="my-1">
            <div className="text-3xl font-extrabold text-white font-mono">
              {totalSessions}
            </div>
            <span className="text-xs text-slate-400 mt-1 block">
              {completedSessions} completed • {interviewStats.in_progress_interviews || 0} active
            </span>
          </div>
          <div className="mt-3 pt-3 border-t border-slate-800/80 text-[11px] text-slate-500 flex items-center justify-between">
            <span>Adaptive NLP Sessions</span>
            <Link to="/interview" className="text-primary-400 hover:text-primary-300 font-semibold">Start →</Link>
          </div>
        </div>

        {/* Card 3: Completion Rate */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Completion Rate</span>
            <div className="p-2 bg-slate-950 border border-slate-800 rounded-xl">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            </div>
          </div>
          <div className="my-1">
            <div className="text-3xl font-extrabold text-white font-mono">
              {completionRate}%
            </div>
            <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden border border-slate-800 mt-2">
              <div 
                className="h-full bg-emerald-500 transition-all duration-700"
                style={{ width: `${completionRate}%` }}
              />
            </div>
          </div>
          <div className="mt-3 pt-3 border-t border-slate-800/80 text-[11px] text-slate-400">
            {completedSessions} of {totalSessions} sessions finished
          </div>
        </div>

        {/* Card 4: Average Interview Performance */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Average Performance</span>
            <div className="p-2 bg-slate-950 border border-slate-800 rounded-xl">
              <TrendingUp className="w-4 h-4 text-purple-400" />
            </div>
          </div>
          <div className="my-1">
            <div className="text-3xl font-extrabold text-white font-mono">
              {typeof interviewStats.average_score === 'number'
                ? `${interviewStats.average_score.toFixed(1)}/100`
                : '—'}
            </div>
            <span className="text-xs text-slate-400 mt-1 block">
              Across {interviewStats.total_responses || 0} evaluated questions
            </span>
          </div>
          <div className="mt-3 pt-3 border-t border-slate-800/80 text-[11px] text-slate-500 truncate">
            Deterministic AI metric scoring
          </div>
        </div>

      </div>

      {/* 4. Visual Analytics Row 1: Skill Radar & Performance Trend */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <SkillRadarChart report={careerReadiness.latest_report} />
        <PerformanceTrendChart history={careerReadiness.history} />
      </div>

      {/* 5. Visual Analytics Row 2: Category Breakdown & Extracted Resume Skills */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <CategoryBreakdown categoryPerformance={analytics?.category_performance} />
        <SkillTagsCloud 
          skills={resumeStats.extracted_skills} 
          latestResume={resumeStats.latest_resume} 
        />
      </div>

      {/* 6. Recent Interviews Activity Table */}
      <div className="mb-8">
        <RecentInterviewsTable interviews={analytics?.recent_interviews} />
      </div>

    </div>
  );
};

export default Dashboard;
