import { Link } from 'react-router-dom';
import { 
  PlayCircle, 
  CheckCircle, 
  Clock, 
  ChevronRight, 
  ExternalLink, 
  Calendar,
  AlertCircle
} from 'lucide-react';

/**
 * RecentInterviewsTable
 * Displays the candidate's recent adaptive interview sessions,
 * status, difficulty tier, score, and direct navigation links.
 *
 * Props:
 * - interviews: Array of recent interview objects (from recent_interviews):
 *     - id: number
 *     - target_job_role: string
 *     - status: "COMPLETED" | "IN_PROGRESS"
 *     - current_difficulty: "EASY" | "MEDIUM" | "HARD"
 *     - started_at: string/Date
 *     - completed_at: Optional string/Date
 *     - response_count: number
 *     - average_score: Optional number or null
 * - className: Optional string for container styling
 */
const RecentInterviewsTable = ({ interviews = [], className = "" }) => {
  const getDifficultyBadge = (difficulty) => {
    switch (difficulty) {
      case 'HARD':
        return 'bg-red-500/10 text-red-400 border-red-500/20';
      case 'EASY':
        return 'bg-green-500/10 text-green-400 border-green-500/20';
      case 'MEDIUM':
      default:
        return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
    }
  };

  const hasInterviews = Array.isArray(interviews) && interviews.length > 0;

  return (
    <div className={`bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl ${className}`}>
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-6">
        <div>
          <div className="flex items-center gap-2">
            <PlayCircle className="w-5 h-5 text-primary-400" />
            <h3 className="text-base font-bold text-white tracking-tight">Recent Interview Sessions</h3>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            History of your recent adaptive mock interviews and evaluation states.
          </p>
        </div>

        <Link
          to="/interview"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-primary-400 hover:text-primary-300 transition-colors self-start sm:self-auto"
        >
          <span>Start New Interview</span>
          <ChevronRight className="w-4 h-4" />
        </Link>
      </div>

      {/* Table / List Container */}
      {!hasInterviews ? (
        <div className="flex flex-col items-center justify-center p-8 text-center bg-slate-950/40 rounded-xl border border-slate-800/60">
          <AlertCircle className="w-8 h-8 text-slate-500 mb-2" />
          <h4 className="text-sm font-semibold text-slate-300 mb-1">No Interview Sessions Yet</h4>
          <p className="text-xs text-slate-500 max-w-sm mb-4">
            You haven't participated in any mock interview sessions yet. Start an adaptive interview to evaluate your technical and behavioral skills.
          </p>
          <Link
            to="/interview"
            className="inline-flex items-center gap-2 bg-primary-600 hover:bg-primary-500 text-white text-xs font-semibold px-4 py-2 rounded-lg transition-all shadow-[0_0_10px_rgba(34,197,94,0.2)]"
          >
            Launch First Interview
          </Link>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider font-semibold">
                <th className="pb-3 pl-2">Session & Role</th>
                <th className="pb-3">Date</th>
                <th className="pb-3">Difficulty</th>
                <th className="pb-3">Responses</th>
                <th className="pb-3">Score</th>
                <th className="pb-3">Status</th>
                <th className="pb-3 pr-2 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {interviews.map((session) => {
                const isCompleted = session.status === 'COMPLETED';
                const dateObj = new Date(session.started_at);
                const formattedDate = !isNaN(dateObj.getTime())
                  ? dateObj.toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })
                  : '—';

                return (
                  <tr 
                    key={session.id}
                    className="hover:bg-slate-800/30 transition-colors group"
                  >
                    {/* Role & Session ID */}
                    <td className="py-3.5 pl-2 font-medium text-white">
                      <div className="flex flex-col">
                        <span className="font-semibold text-slate-200">{session.target_job_role}</span>
                        <span className="text-[10px] text-slate-500 font-mono">Session #{session.id}</span>
                      </div>
                    </td>

                    {/* Date */}
                    <td className="py-3.5 text-slate-400">
                      <div className="flex items-center gap-1.5">
                        <Calendar className="w-3.5 h-3.5 text-slate-500" />
                        <span>{formattedDate}</span>
                      </div>
                    </td>

                    {/* Difficulty */}
                    <td className="py-3.5">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getDifficultyBadge(session.current_difficulty)}`}>
                        {session.current_difficulty}
                      </span>
                    </td>

                    {/* Question Count */}
                    <td className="py-3.5 text-slate-300 font-mono">
                      {session.response_count} questions
                    </td>

                    {/* Score */}
                    <td className="py-3.5 font-mono">
                      {typeof session.average_score === 'number' ? (
                        <span className="font-bold text-primary-400">
                          {session.average_score.toFixed(1)}/100
                        </span>
                      ) : (
                        <span className="text-slate-600">—</span>
                      )}
                    </td>

                    {/* Status */}
                    <td className="py-3.5">
                      {isCompleted ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          <CheckCircle className="w-3 h-3" /> Completed
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                          <Clock className="w-3 h-3" /> In Progress
                        </span>
                      )}
                    </td>

                    {/* Action Link */}
                    <td className="py-3.5 pr-2 text-right">
                      {isCompleted ? (
                        <Link
                          to={`/results?sessionId=${session.id}`}
                          className="inline-flex items-center gap-1 text-[11px] font-semibold text-primary-400 hover:text-primary-300 transition-colors"
                        >
                          <span>Report</span>
                          <ExternalLink className="w-3 h-3" />
                        </Link>
                      ) : (
                        <Link
                          to="/interview"
                          className="inline-flex items-center gap-1 text-[11px] font-semibold text-slate-300 hover:text-white transition-colors"
                        >
                          <span>Resume</span>
                          <ChevronRight className="w-3 h-3" />
                        </Link>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

    </div>
  );
};

export default RecentInterviewsTable;
