import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Register = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    target_job_role: ''
  });
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);
    
    // Basic frontend validation
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      setIsSubmitting(false);
      return;
    }
    
    try {
      await register(formData);
      navigate('/dashboard');
    } catch (err) {
      if (err.response?.status === 409) {
        setError('This email is already registered.');
      } else if (err.response?.status === 422) {
        setError('Please check your input format. Name > 2 chars, valid email.');
      } else {
        setError('Registration failed. Please try again later.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-slate-950">
      <div className="max-w-md w-full space-y-8 bg-slate-900 p-10 rounded-2xl border border-slate-800 shadow-2xl">
        <div>
          <h2 className="mt-2 text-center text-3xl font-extrabold text-white">
            Create an account
          </h2>
          <p className="mt-2 text-center text-sm text-slate-400">
            Start your journey to interview success
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-500/10 border border-red-500/50 text-red-400 p-3 rounded-lg text-sm text-center">
              {error}
            </div>
          )}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Full Name</label>
              <input
                type="text"
                name="name"
                required
                value={formData.name}
                onChange={handleChange}
                className="appearance-none relative block w-full px-4 py-3 bg-slate-950 border border-slate-700 placeholder-slate-500 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors sm:text-sm"
                placeholder="John Doe"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Email address</label>
              <input
                type="email"
                name="email"
                required
                value={formData.email}
                onChange={handleChange}
                className="appearance-none relative block w-full px-4 py-3 bg-slate-950 border border-slate-700 placeholder-slate-500 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors sm:text-sm"
                placeholder="you@example.com"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Target Job Role (Optional)</label>
              <input
                type="text"
                name="target_job_role"
                value={formData.target_job_role}
                onChange={handleChange}
                className="appearance-none relative block w-full px-4 py-3 bg-slate-950 border border-slate-700 placeholder-slate-500 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors sm:text-sm"
                placeholder="e.g. Software Engineer"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Password</label>
              <input
                type="password"
                name="password"
                required
                value={formData.password}
                onChange={handleChange}
                className="appearance-none relative block w-full px-4 py-3 bg-slate-950 border border-slate-700 placeholder-slate-500 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors sm:text-sm"
                placeholder="Minimum 8 characters"
              />
            </div>
          </div>

          <div>
            <button 
              type="submit" 
              disabled={isSubmitting}
              className={`group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900 focus:ring-primary-500 transition-colors ${isSubmitting ? 'opacity-70 cursor-not-allowed' : ''}`}
            >
              {isSubmitting ? 'Creating account...' : 'Create account'}
            </button>
          </div>
          
          <div className="text-center text-sm">
            <span className="text-slate-400">Already have an account? </span>
            <Link to="/login" className="font-medium text-primary-400 hover:text-primary-300 transition-colors">
              Log in
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Register;
