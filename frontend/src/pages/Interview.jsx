import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Target, 
  CheckCircle, 
  BrainCircuit, 
  Play, 
  MessageSquare, 
  AlertCircle, 
  BarChart3, 
  ChevronRight, 
  Loader2,
  Sparkles,
  FileText
} from 'lucide-react';
import api from '../api/client';

const Interview = () => {
  const navigate = useNavigate();
  const [role, setRole] = useState('Software Engineer');
  const [session, setSession] = useState(null);
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [evaluation, setEvaluation] = useState(null);

  // Completed session state for Career Readiness report generation
  const [resumes, setResumes] = useState([]);
  const [selectedResumeId, setSelectedResumeId] = useState(null);
  const [generatingReport, setGeneratingReport] = useState(false);
  const [reportError, setReportError] = useState('');

  const JOB_ROLES = [
    "Software Engineer",
    "Data Scientist",
    "Machine Learning Engineer",
    "Backend Developer",
    "Frontend Developer"
  ];

  // Fetch candidate's resumes when interview completes
  useEffect(() => {
    if (session?.status === 'COMPLETED') {
      const fetchResumes = async () => {
        try {
          const res = await api.get('/resumes');
          setResumes(res.data);
          if (res.data.length > 0) {
            setSelectedResumeId(res.data[0].id);
          }
        } catch (err) {
          console.error("Failed to load resumes", err);
        }
      };
      fetchResumes();
    }
  }, [session?.status]);

  const handleStart = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await api.post('/interviews/start', { target_job_role: role });
      setSession(response.data);
      setEvaluation(null);
      setAnswer('');
      setReportError('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start interview.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!answer.trim()) {
      setError("Answer cannot be empty.");
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const response = await api.post(`/interviews/${session.id}/answer`, {
        question_id: session.current_question.id,
        answer_text: answer
      });
      
      setSession(response.data);
      setEvaluation(response.data.latest_evaluation);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit answer.');
    } finally {
      setLoading(false);
    }
  };

  const handleNextQuestion = () => {
    setEvaluation(null);
    setAnswer('');
  };

  const handleGenerateReport = async () => {
    if (!selectedResumeId) {
      setReportError("Please select a resume to generate your Career Readiness Report.");
      return;
    }
    setGeneratingReport(true);
    setReportError('');
    try {
      const response = await api.post('/career-readiness/generate', {
        interview_session_id: session.id,
        resume_id: Number(selectedResumeId)
      });
      navigate(`/results?reportId=${response.data.id}`);
    } catch (err) {
      setReportError(err.response?.data?.detail || 'Failed to generate Career Readiness Report.');
    } finally {
      setGeneratingReport(false);
    }
  };

  if (session?.status === 'COMPLETED' && !evaluation) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl text-center">
          <div className="w-16 h-16 bg-green-500/10 border border-green-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="w-10 h-10 text-green-400" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">Interview Completed!</h1>
          <p className="text-slate-400 max-w-xl mx-auto mb-8">
            You have successfully completed all required interview questions for the <span className="text-primary-400 font-semibold">{session.target_job_role}</span> role.
          </p>

          <div className="bg-slate-950 border border-slate-800 rounded-xl p-6 text-left mb-8">
            <div className="flex items-center gap-3 mb-4">
              <Sparkles className="w-5 h-5 text-primary-400" />
              <h2 className="text-lg font-semibold text-white">Generate Career Readiness Report</h2>
            </div>
            <p className="text-sm text-slate-400 mb-6">
              Our 6-dimensional AI engine evaluates your Technical, Problem Solving, Communication, and Behavioral performance joined with your uploaded resume skill match.
            </p>

            {reportError && (
              <div className="mb-6 p-3 bg-red-500/10 border border-red-500/50 text-red-400 rounded-lg text-sm flex items-start gap-2">
                <AlertCircle className="w-5 h-5 shrink-0" />
                <span>{reportError}</span>
              </div>
            )}

            {resumes.length > 0 ? (
              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
                    Select Resume for Skill Profile Matching
                  </label>
                  <select
                    value={selectedResumeId || ''}
                    onChange={(e) => setSelectedResumeId(Number(e.target.value))}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-primary-500 text-sm"
                  >
                    {resumes.map(r => (
                      <option key={r.id} value={r.id}>
                        {r.original_filename} (Uploaded: {new Date(r.created_at).toLocaleDateString()})
                      </option>
                    ))}
                  </select>
                </div>

                <button
                  onClick={handleGenerateReport}
                  disabled={generatingReport}
                  className="w-full bg-primary-600 hover:bg-primary-500 text-white font-medium py-3.5 px-6 rounded-lg transition-all shadow-[0_0_15px_rgba(34,197,94,0.3)] hover:shadow-[0_0_25px_rgba(34,197,94,0.5)] flex items-center justify-center gap-2 cursor-pointer disabled:cursor-not-allowed disabled:opacity-70"
                >
                  {generatingReport ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Analyzing 6 Readiness Dimensions...
                    </>
                  ) : (
                    <>
                      <BrainCircuit className="w-5 h-5" />
                      Generate Career Readiness Report
                    </>
                  )}
                </button>
              </div>
            ) : (
              <div className="bg-slate-900 border border-amber-500/30 rounded-lg p-5 text-center">
                <p className="text-sm text-slate-300 mb-4">
                  You haven't uploaded a resume yet. To calculate your 6-dimension Career Readiness score, please upload your resume first.
                </p>
                <button
                  onClick={() => navigate('/resume')}
                  className="inline-flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-white border border-slate-700 px-5 py-2.5 rounded-lg text-sm font-medium transition-colors cursor-pointer"
                >
                  <FileText className="w-4 h-4 text-primary-400" />
                  Upload Resume Now
                </button>
              </div>
            )}
          </div>

          <div className="flex justify-center gap-4">
            <button
              onClick={() => {
                setSession(null);
                setEvaluation(null);
              }}
              className="bg-slate-800 hover:bg-slate-700 text-white border border-slate-700 px-6 py-2.5 rounded-lg text-sm font-medium transition-colors cursor-pointer"
            >
              Start Another Interview
            </button>
            <button
              onClick={() => navigate('/dashboard')}
              className="bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 px-6 py-2.5 rounded-lg text-sm font-medium transition-colors cursor-pointer"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 min-h-[80vh]">
      
      {!session ? (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-xl text-center max-w-lg mx-auto mt-12">
          <BrainCircuit className="w-16 h-16 text-primary-500 mx-auto mb-6" />
          <h1 className="text-2xl font-bold text-white mb-2">Adaptive AI Interview</h1>
          <p className="text-slate-400 mb-8 text-sm">
            Our NLP engine evaluates your answers in real-time and dynamically adjusts difficulty based on your performance. Select a role to begin.
          </p>

          {error && (
            <div className="mb-6 p-3 bg-red-500/10 border border-red-500/50 text-red-400 rounded-lg text-sm flex items-start gap-2">
              <AlertCircle className="w-5 h-5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="text-left mb-6">
            <label className="block text-sm font-medium text-slate-300 mb-2">Target Job Role</label>
            <select 
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-primary-500"
            >
              {JOB_ROLES.map(r => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
          </div>

          <button
            onClick={handleStart}
            disabled={loading}
            className="w-full bg-primary-600 hover:bg-primary-500 text-white font-medium py-3 px-4 rounded-lg transition-colors flex justify-center items-center gap-2 cursor-pointer disabled:cursor-not-allowed"
          >
            {loading ? <><Loader2 className="w-5 h-5 animate-spin" /> Starting...</> : <><Play className="w-5 h-5" /> Start Interview</>}
          </button>
        </div>
      ) : evaluation ? (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-xl max-w-3xl mx-auto">
          <div className="flex items-center gap-3 mb-6">
            <BarChart3 className="w-8 h-8 text-primary-500" />
            <h2 className="text-2xl font-bold text-white">Evaluation Result</h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 text-center">
              <div className="text-sm text-slate-400 mb-1">Overall Score</div>
              <div className="text-3xl font-bold text-primary-400">{evaluation.overall_score.toFixed(0)}<span className="text-lg text-slate-500">/100</span></div>
            </div>
            <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 text-center">
              <div className="text-sm text-slate-400 mb-1">Semantic Match</div>
              <div className="text-2xl font-bold text-white">{evaluation.semantic_similarity.toFixed(0)}%</div>
            </div>
            <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 text-center">
              <div className="text-sm text-slate-400 mb-1">Concepts</div>
              <div className="text-2xl font-bold text-white">{evaluation.concept_coverage.toFixed(0)}%</div>
            </div>
            <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 text-center">
              <div className="text-sm text-slate-400 mb-1">Completeness</div>
              <div className="text-2xl font-bold text-white">{evaluation.completeness_score.toFixed(0)}%</div>
            </div>
          </div>
          
          <div className="bg-slate-950 border border-slate-800 rounded-xl p-6 mb-8">
            <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-3">AI Feedback</h3>
            <p className="text-white leading-relaxed">{evaluation.feedback}</p>
          </div>
          
          <div className="flex justify-end">
            <button
              onClick={handleNextQuestion}
              className="bg-primary-600 hover:bg-primary-500 text-white font-medium py-3 px-8 rounded-lg transition-colors flex items-center gap-2 cursor-pointer"
            >
              {session.status === 'COMPLETED' ? 'Finish Interview & View Readiness' : 'Next Question'}
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="flex justify-between items-center border-b border-slate-800 pb-6">
            <div>
              <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                <Target className="w-6 h-6 text-primary-500" />
                {session.target_job_role} Interview
              </h1>
              <p className="text-sm text-slate-400 mt-1">Session ID: #{session.id}</p>
            </div>
            <div className="flex flex-col items-end">
              <span className="text-xs text-slate-500 uppercase tracking-wider mb-1">Current Difficulty</span>
              <span className={`px-3 py-1 rounded-full text-xs font-bold border ${
                session.current_difficulty === 'EASY' ? 'bg-green-500/10 text-green-400 border-green-500/20' :
                session.current_difficulty === 'HARD' ? 'bg-red-500/10 text-red-400 border-red-500/20' :
                'bg-yellow-500/10 text-yellow-400 border-yellow-500/20'
              }`}>
                {session.current_difficulty}
              </span>
            </div>
          </div>

          {error && (
            <div className="p-3 bg-red-500/10 border border-red-500/50 text-red-400 rounded-lg text-sm flex items-start gap-2">
              <AlertCircle className="w-5 h-5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
            <h3 className="text-sm font-semibold text-primary-400 uppercase tracking-widest mb-4 flex items-center gap-2">
              <MessageSquare className="w-4 h-4" /> Question
            </h3>
            <p className="text-xl text-white leading-relaxed font-medium">
              {session.current_question?.question_text}
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
            <label className="block text-sm font-semibold text-slate-300 mb-3">Your Answer</label>
            <textarea
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder="Type your answer here..."
              className="w-full bg-slate-950 border border-slate-700 rounded-lg p-4 text-white placeholder-slate-600 focus:outline-none focus:border-primary-500 min-h-[200px] resize-y mb-6"
              disabled={loading}
            />
            
            <div className="flex justify-end">
              <button
                onClick={handleSubmitAnswer}
                disabled={loading || !answer.trim()}
                className={`w-full sm:w-auto py-3 px-8 rounded-lg font-medium text-white transition-colors flex justify-center items-center gap-2 ${
                  loading || !answer.trim()
                    ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                    : 'bg-primary-600 hover:bg-primary-500 cursor-pointer'
                }`}
              >
                {loading ? <><Loader2 className="w-5 h-5 animate-spin" /> Analyzing your answer...</> : 'Submit Answer'}
              </button>
            </div>
          </div>
          
        </div>
      )}
    </div>
  );
};

export default Interview;