import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';

const Profile = () => {
  const { user, fetchUser } = useAuth();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    target_job_role: ''
  });
  const [status, setStatus] = useState({ type: '', message: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (user) {
      setFormData({
        name: user.name || '',
        email: user.email || '',
        target_job_role: user.target_job_role || ''
      });
    }
  }, [user]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus({ type: '', message: '' });
    setIsSubmitting(true);

    try {
      const payload = {
        name: formData.name,
        email: formData.email,
        target_job_role: formData.target_job_role
      };
      
      await api.put('/users/me', payload);
      setStatus({ type: 'success', message: 'Profile updated successfully!' });
      
      // Update global context seamlessly
      if (fetchUser) await fetchUser();
    } catch (err) {
      if (err.response?.status === 409) {
        setStatus({ type: 'error', message: 'Email is already taken by another account.' });
      } else if (err.response?.status === 422) {
        setStatus({ type: 'error', message: 'Invalid data format. Please check your inputs.' });
      } else {
        setStatus({ type: 'error', message: 'Failed to update profile.' });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12 min-h-[80vh]">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-xl overflow-hidden">
        <div className="px-8 py-6 border-b border-slate-800">
          <h1 className="text-2xl font-bold text-white">Your Profile</h1>
          <p className="text-slate-400 mt-1">Manage your personal information and preferences.</p>
        </div>
        
        <div className="px-8 py-8">
          {status.message && (
            <div className={`mb-6 p-4 rounded-lg text-sm ${status.type === 'error' ? 'bg-red-500/10 border border-red-500/50 text-red-400' : 'bg-green-500/10 border border-green-500/50 text-green-400'}`}>
              {status.message}
            </div>
          )}
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Full Name</label>
              <input
                type="text"
                name="name"
                required
                value={formData.name}
                onChange={handleChange}
                className="appearance-none relative block w-full px-4 py-3 bg-slate-950 border border-slate-700 placeholder-slate-500 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 transition-colors sm:text-sm"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Email Address</label>
              <input
                type="email"
                name="email"
                required
                value={formData.email}
                onChange={handleChange}
                className="appearance-none relative block w-full px-4 py-3 bg-slate-950 border border-slate-700 placeholder-slate-500 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 transition-colors sm:text-sm"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">Target Job Role</label>
              <input
                type="text"
                name="target_job_role"
                value={formData.target_job_role}
                onChange={handleChange}
                className="appearance-none relative block w-full px-4 py-3 bg-slate-950 border border-slate-700 placeholder-slate-500 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 transition-colors sm:text-sm"
                placeholder="e.g. Frontend Developer"
              />
            </div>
            
            <div className="pt-4 flex justify-end">
              <button 
                type="submit" 
                disabled={isSubmitting}
                className={`bg-primary-600 hover:bg-primary-500 text-white px-6 py-2.5 rounded-lg font-medium transition-colors ${isSubmitting ? 'opacity-70 cursor-not-allowed' : ''}`}
              >
                {isSubmitting ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Profile;
