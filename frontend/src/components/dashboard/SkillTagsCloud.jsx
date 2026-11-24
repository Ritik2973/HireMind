import { Link } from 'react-router-dom';
import { FileText, Sparkles, UploadCloud, CheckCircle2 } from 'lucide-react';

/**
 * SkillTagsCloud
 * Displays the verified skills extracted from the candidate's latest resume.
 *
 * Props:
 * - skills: Array of skill strings (from resume_stats.extracted_skills)
 * - latestResume: Optional object with resume metadata (from resume_stats.latest_resume):
 *     - id: number
 *     - original_filename: string
 *     - created_at: string/Date
 *     - skills_count: number
 * - className: Optional string for container styling
 */
const SkillTagsCloud = ({ skills = [], latestResume = null, className = "" }) => {
  const hasSkills = Array.isArray(skills) && skills.length > 0;

  return (
    <div className={`bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between ${className}`}>
      
      {/* Header */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-primary-400" />
            <h3 className="text-base font-bold text-white tracking-tight">Verified Resume Skills</h3>
          </div>
          {hasSkills && (
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-primary-500/10 text-primary-400 border border-primary-500/20 font-mono">
              {skills.length} detected
            </span>
          )}
        </div>

        <p className="text-xs text-slate-400 mb-5">
          {latestResume ? (
            <span>
              Extracted from <span className="text-slate-300 font-medium">{latestResume.original_filename}</span>
            </span>
          ) : (
            'Skills parsed from your uploaded resume via NLP analysis.'
          )}
        </p>

        {/* Tags Grid / Empty State */}
        {!hasSkills ? (
          <div className="flex flex-col items-center justify-center p-6 text-center bg-slate-950/40 rounded-xl border border-slate-800/60 my-2">
            <FileText className="w-8 h-8 text-slate-500 mb-2" />
            <h4 className="text-sm font-semibold text-slate-300 mb-1">No Skills Extracted Yet</h4>
            <p className="text-xs text-slate-500 max-w-xs mb-4">
              Upload a PDF resume to allow HireMind's NLP engine to extract and match your skills against target roles.
            </p>
            <Link
              to="/resume"
              className="inline-flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold px-4 py-2 rounded-lg border border-slate-700 transition-colors"
            >
              <UploadCloud className="w-3.5 h-3.5 text-primary-400" />
              Upload Resume
            </Link>
          </div>
        ) : (
          <div className="flex flex-wrap gap-2 max-h-[220px] overflow-y-auto pr-1">
            {skills.map((skill, index) => (
              <span
                key={index}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-950 border border-slate-800 text-slate-300 hover:text-white hover:border-primary-500/40 hover:bg-slate-900 transition-all select-none shadow-xs group"
              >
                <CheckCircle2 className="w-3 h-3 text-primary-500/70 group-hover:text-primary-400 transition-colors" />
                <span>{skill}</span>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Footer Navigation */}
      <div className="border-t border-slate-800/80 pt-3 mt-5 flex items-center justify-between text-xs text-slate-500">
        <span className="text-[11px]">NLP-extracted & benchmarked</span>
        <Link
          to="/resume"
          className="text-primary-400 hover:text-primary-300 font-medium transition-colors text-xs"
        >
          {latestResume ? 'Manage Resumes →' : 'Upload Resume →'}
        </Link>
      </div>

    </div>
  );
};

export default SkillTagsCloud;
