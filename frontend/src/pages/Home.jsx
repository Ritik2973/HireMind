import { Link } from 'react-router-dom';
import { Brain, Target, LineChart } from 'lucide-react';

const Home = () => {
  return (
    <div className="flex flex-col min-h-screen bg-slate-950">
      {/* Hero Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 flex-grow flex items-center relative overflow-hidden">
        {/* Subtle background glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-primary-600/10 blur-[100px] rounded-full pointer-events-none"></div>
        
        <div className="max-w-7xl mx-auto text-center relative z-10">
          <h1 className="text-5xl md:text-6xl font-extrabold text-white tracking-tight mb-6">
            Master your interview.<br/>
            <span className="text-primary-500">Land your dream job.</span>
          </h1>
          <p className="mt-4 text-xl text-slate-400 max-w-3xl mx-auto mb-10">
            HireMind uses Deep Learning to simulate adaptive interviews, evaluate your answers, and calculate your Career Readiness score.
          </p>
          <div className="flex justify-center gap-4">
            <Link to="/register" className="bg-primary-600 hover:bg-primary-500 text-white px-8 py-4 rounded-xl font-semibold text-lg transition-all shadow-[0_0_15px_rgba(34,197,94,0.3)] hover:shadow-[0_0_25px_rgba(34,197,94,0.5)]">
              Start Free Trial
            </Link>
            <Link to="/login" className="bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700 px-8 py-4 rounded-xl font-semibold text-lg transition-all">
              Sign In
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-slate-900 border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white">Powered by AI, designed for students</h2>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="p-6 rounded-2xl bg-slate-950 border border-slate-800 hover:border-slate-700 hover:bg-slate-900/80 transition-all">
              <div className="w-12 h-12 bg-primary-900/30 border border-primary-500/20 rounded-lg flex items-center justify-center mb-4">
                <Brain className="text-primary-400 h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Adaptive Difficulty</h3>
              <p className="text-slate-400">The engine automatically adjusts question difficulty based on your previous answers using NLP-based evaluation.</p>
            </div>
            <div className="p-6 rounded-2xl bg-slate-950 border border-slate-800 hover:border-slate-700 hover:bg-slate-900/80 transition-all">
              <div className="w-12 h-12 bg-primary-900/30 border border-primary-500/20 rounded-lg flex items-center justify-center mb-4">
                <LineChart className="text-primary-400 h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Readiness Metrics</h3>
              <p className="text-slate-400">Get a transparent, multi-component Career Readiness Score covering technical knowledge, communication, and more.</p>
            </div>
            <div className="p-6 rounded-2xl bg-slate-950 border border-slate-800 hover:border-slate-700 hover:bg-slate-900/80 transition-all">
              <div className="w-12 h-12 bg-primary-900/30 border border-primary-500/20 rounded-lg flex items-center justify-center mb-4">
                <Target className="text-primary-400 h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Skill Gap Analysis</h3>
              <p className="text-slate-400">We analyze your resume against target roles to identify missing skills and provide a personalized improvement roadmap.</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
