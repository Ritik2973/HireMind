import { useState, useEffect } from 'react';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, BrainCircuit } from 'lucide-react';
import api from '../api/client';

const Resume = () => {
  const [file, setFile] = useState(null);
  const [resumes, setResumes] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [status, setStatus] = useState({ type: '', message: '' });
  const [loading, setLoading] = useState(true);

  // New ML State
  const [selectedResumeId, setSelectedResumeId] = useState('');
  const [selectedRole, setSelectedRole] = useState('Software Engineer');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [mlResult, setMlResult] = useState(null);
  const [mlError, setMlError] = useState('');

  const JOB_ROLES = [
    "Software Engineer",
    "Data Scientist",
    "Machine Learning Engineer",
    "Backend Developer",
    "Frontend Developer"
  ];

  useEffect(() => {
    fetchResumes();
  }, []);

  const fetchResumes = async () => {
    try {
      const response = await api.get('/resumes');
      const sorted = response.data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      setResumes(sorted);
      if (sorted.length > 0 && !selectedResumeId) {
        setSelectedResumeId(sorted[0].id.toString());
      }
    } catch (error) {
      console.error('Failed to fetch resumes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (selectedFile.type !== 'application/pdf') {
        setStatus({ type: 'error', message: 'Only PDF files are supported.' });
        setFile(null);
        return;
      }
      if (selectedFile.size > 5 * 1024 * 1024) {
        setStatus({ type: 'error', message: 'File exceeds the 5MB size limit.' });
        setFile(null);
        return;
      }
      setFile(selectedFile);
      setStatus({ type: '', message: '' });
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    setStatus({ type: '', message: '' });

    const formData = new FormData();
    formData.append('file', file);

    try {
      await api.post('/resumes/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      setStatus({ type: 'success', message: 'Resume uploaded and parsed successfully!' });
      setFile(null);
      const input = document.getElementById('resume-upload');
      if (input) input.value = '';
      await fetchResumes();
    } catch (error) {
      if (error.response?.status === 422) {
        setStatus({ type: 'error', message: error.response.data.detail || 'Could not parse the PDF.' });
      } else if (error.response?.status === 413) {
        setStatus({ type: 'error', message: 'File is too large.' });
      } else {
        setStatus({ type: 'error', message: 'An error occurred during upload. Please try again.' });
      }
    } finally {
      setIsUploading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedResumeId) return;
    
    setIsAnalyzing(true);
    setMlError('');
    setMlResult(null);

    try {
      const response = await api.post('/ml/analyze-resume', {
        resume_id: parseInt(selectedResumeId),
        target_job_role: selectedRole
      });
      setMlResult(response.data);
    } catch (error) {
      setMlError(error.response?.data?.detail || 'An error occurred during analysis.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 min-h-[80vh]">
      <div className="mb-8 border-b border-slate-800 pb-6">
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <FileText className="h-8 w-8 text-primary-500" />
          Resume Management
        </h1>
        <p className="text-slate-400 mt-2">Upload your resume to extract skills and run semantic NLP analysis.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: Upload & NLP Analysis */}
        <div className="lg:col-span-1 space-y-8">
          
          {/* Upload Section */}
          <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800 shadow-xl">
            <h2 className="text-xl font-semibold text-white mb-4">Upload New Resume</h2>
            
            {status.message && (
              <div className={`mb-4 p-3 rounded-lg text-sm flex items-start gap-2 ${
                status.type === 'error' ? 'bg-red-500/10 border border-red-500/50 text-red-400' : 'bg-green-500/10 border border-green-500/50 text-green-400'
              }`}>
                {status.type === 'error' ? <AlertCircle className="w-5 h-5 shrink-0" /> : <CheckCircle2 className="w-5 h-5 shrink-0" />}
                <span>{status.message}</span>
              </div>
            )}

            <div className="border-2 border-dashed border-slate-700 rounded-xl p-8 text-center bg-slate-950/50 relative hover:bg-slate-800/50 transition-colors">
              <input
                type="file"
                id="resume-upload"
                accept=".pdf,application/pdf"
                onChange={handleFileChange}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                disabled={isUploading}
              />
              <div className="flex flex-col items-center pointer-events-none">
                <UploadCloud className={`h-12 w-12 mb-3 ${file ? 'text-primary-500' : 'text-slate-500'}`} />
                <span className="text-slate-300 font-medium mb-1 truncate max-w-full px-2">
                  {file ? file.name : 'Click or drag PDF to upload'}
                </span>
                <span className="text-slate-500 text-sm">
                  {file ? `${(file.size / (1024 * 1024)).toFixed(2)} MB` : 'Maximum file size: 5MB'}
                </span>
              </div>
            </div>

            <button
              onClick={handleUpload}
              disabled={!file || isUploading}
              className={`w-full mt-4 py-3 px-4 rounded-lg font-medium text-white transition-colors flex justify-center items-center ${
                !file || isUploading 
                  ? 'bg-slate-800 text-slate-500 cursor-not-allowed' 
                  : 'bg-primary-600 hover:bg-primary-500'
              }`}
            >
              {isUploading ? 'Uploading & Parsing...' : 'Upload Resume'}
            </button>
          </div>

          {/* NLP Analysis Section */}
          <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800 shadow-xl">
            <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
              <BrainCircuit className="h-6 w-6 text-primary-400" />
              Semantic Analysis
            </h2>
            <p className="text-sm text-slate-400 mb-4">
              Compare your resume against a job profile using deep learning transformer embeddings.
            </p>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Select Resume</label>
                <select 
                  value={selectedResumeId}
                  onChange={(e) => setSelectedResumeId(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-primary-500"
                  disabled={resumes.length === 0}
                >
                  {resumes.length === 0 && <option value="">No resumes available</option>}
                  {resumes.map(r => (
                    <option key={r.id} value={r.id}>{r.original_filename}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Target Job Role</label>
                <select 
                  value={selectedRole}
                  onChange={(e) => setSelectedRole(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-primary-500"
                >
                  {JOB_ROLES.map(role => (
                    <option key={role} value={role}>{role}</option>
                  ))}
                </select>
              </div>

              <button
                onClick={handleAnalyze}
                disabled={!selectedResumeId || isAnalyzing}
                className={`w-full py-3 px-4 rounded-lg font-medium text-white transition-colors flex justify-center items-center ${
                  !selectedResumeId || isAnalyzing 
                    ? 'bg-slate-800 text-slate-500 cursor-not-allowed' 
                    : 'bg-primary-600 hover:bg-primary-500'
                }`}
              >
                {isAnalyzing ? 'Running Model...' : 'Analyze Semantic Similarity'}
              </button>

              {mlError && (
                <div className="p-3 bg-red-500/10 border border-red-500/50 text-red-400 rounded-lg text-sm">
                  {mlError}
                </div>
              )}

              {mlResult && (
                <div className="mt-4 p-4 bg-slate-950 border border-primary-500/30 rounded-lg">
                  <h3 className="text-sm font-semibold text-primary-400 mb-2 uppercase tracking-wider">Analysis Results</h3>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-slate-400 text-sm">Semantic Similarity:</span>
                    <span className="text-white font-bold text-lg">{(mlResult.semantic_similarity * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400 text-sm">Embedding Dimension:</span>
                    <span className="text-slate-300 font-mono text-sm">{mlResult.embedding_dimension}</span>
                  </div>
                  <div className="mt-3 text-xs text-slate-500 italic">
                    Score computed via Cosine Similarity between Sentence Transformer vectors.
                  </div>
                </div>
              )}
            </div>
          </div>

        </div>

        {/* Right Column: Resumes List Section */}
        <div className="lg:col-span-2">
          <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800 shadow-xl h-full">
            <h2 className="text-xl font-semibold text-white mb-6">Your Resumes</h2>
            
            {loading ? (
              <div className="flex justify-center items-center h-40 text-slate-500">Loading resumes...</div>
            ) : resumes.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-64 text-slate-500 bg-slate-950/30 rounded-xl border border-slate-800 border-dashed">
                <FileText className="h-12 w-12 mb-3 opacity-50" />
                <p>No resumes uploaded yet.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {resumes.map((resume) => (
                  <div key={resume.id} className="bg-slate-950 rounded-xl p-5 border border-slate-800 flex flex-col sm:flex-row gap-6 hover:border-slate-700 transition-colors">
                    <div className="flex-1">
                      <div className="flex items-center justify-between gap-3 mb-2">
                        <div className="flex items-center gap-3">
                          <FileText className="h-5 w-5 text-primary-500" />
                          <h3 className="text-white font-medium truncate" title={resume.original_filename}>
                            {resume.original_filename}
                          </h3>
                        </div>
                      </div>
                      <div className="text-xs text-slate-500 mb-4 flex gap-4">
                        <span>Uploaded on {new Date(resume.created_at).toLocaleDateString()}</span>
                        <span>{resume.extracted_text_length} chars extracted</span>
                      </div>
                      
                      <div>
                        <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Detected Skills</h4>
                        {resume.skills && resume.skills.length > 0 ? (
                          <div className="flex flex-wrap gap-2">
                            {resume.skills.map((skill, idx) => (
                              <span key={idx} className="bg-primary-500/10 text-primary-400 px-2.5 py-1 rounded-md text-xs font-medium border border-primary-500/20">
                                {skill}
                              </span>
                            ))}
                          </div>
                        ) : (
                          <p className="text-sm text-slate-500 italic">No exact skill matches found.</p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Resume;
