import { BrainCircuit } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-slate-950 border-t border-slate-800 mt-auto">
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="md:flex md:items-center md:justify-between">
          <div className="flex justify-center md:justify-start items-center gap-2 mb-4 md:mb-0">
            <BrainCircuit className="h-6 w-6 text-slate-500" />
            <span className="text-slate-400 font-medium">HireMind &copy; {new Date().getFullYear()}</span>
          </div>
          <div className="flex justify-center space-x-6 text-sm text-slate-400">
            <span className="hover:text-white cursor-pointer transition-colors">Academic Project</span>
            <span className="hover:text-white cursor-pointer transition-colors">Deep Learning</span>
            <span className="hover:text-white cursor-pointer transition-colors">Career Readiness</span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
