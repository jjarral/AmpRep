import React, { useState } from "react";
import { Activity, ArrowRight, ArrowUpRight, FlaskConical, Package, Settings, ShieldCheck, TrendingUp } from "lucide-react";

export function SplitScreen() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setTimeout(() => setIsLoading(false), 1500);
  };

  return (
    <div className="min-h-screen w-full flex bg-white font-sans text-slate-900">
      {/* Left Panel - Operational Dashboard */}
      <div className="hidden lg:flex w-1/2 bg-slate-950 flex-col justify-between p-12 text-white relative overflow-hidden">
        {/* Background Accents */}
        <div className="absolute top-0 right-0 -mr-20 -mt-20 w-96 h-96 bg-teal-900/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 -ml-20 -mb-20 w-96 h-96 bg-blue-900/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-overlay pointer-events-none"></div>

        <div className="relative z-10 space-y-12">
          {/* Brand */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-teal-500 rounded-lg flex items-center justify-center">
              <Activity className="text-slate-950 h-6 w-6" />
            </div>
            <div>
              <h2 className="text-2xl font-bold tracking-tight text-white">AmpouleX ERP</h2>
              <p className="text-teal-400 text-sm font-medium tracking-wide uppercase">Operational Control</p>
            </div>
          </div>

          {/* Live System Status */}
          <div className="space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <h3 className="text-lg font-medium text-slate-200">Live System Status</h3>
              <div className="flex items-center gap-2">
                <span className="relative flex h-3 w-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-teal-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-teal-500"></span>
                </span>
                <span className="text-sm font-medium text-teal-400">All Systems Nominal</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {/* KPI 1 */}
              <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-5 backdrop-blur-sm">
                <div className="flex items-start justify-between mb-4">
                  <div className="p-2 bg-blue-500/10 rounded-lg">
                    <TrendingUp className="h-5 w-5 text-blue-400" />
                  </div>
                  <span className="flex items-center text-xs font-medium text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded-full">
                    <ArrowUpRight className="h-3 w-3 mr-1" />
                    12.4%
                  </span>
                </div>
                <p className="text-sm font-medium text-slate-400">Today's Production</p>
                <h4 className="text-3xl font-bold text-white mt-1">142,500 <span className="text-sm font-normal text-slate-500">units</span></h4>
                <div className="w-full bg-slate-800 h-1.5 rounded-full mt-4">
                  <div className="bg-blue-500 h-1.5 rounded-full w-[78%]"></div>
                </div>
              </div>

              {/* KPI 2 */}
              <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-5 backdrop-blur-sm">
                <div className="flex items-start justify-between mb-4">
                  <div className="p-2 bg-teal-500/10 rounded-lg">
                    <FlaskConical className="h-5 w-5 text-teal-400" />
                  </div>
                  <span className="text-xs font-medium text-slate-300 bg-slate-800 px-2 py-1 rounded-full">
                    3 Urgent
                  </span>
                </div>
                <p className="text-sm font-medium text-slate-400">Batches in QC</p>
                <h4 className="text-3xl font-bold text-white mt-1">24 <span className="text-sm font-normal text-slate-500">active</span></h4>
                <div className="flex gap-1 mt-4">
                  {Array.from({ length: 12 }).map((_, i) => (
                    <div key={i} className={`h-1.5 flex-1 rounded-full ${i < 8 ? 'bg-teal-500' : i < 10 ? 'bg-amber-500' : 'bg-slate-800'}`}></div>
                  ))}
                </div>
              </div>

              {/* KPI 3 */}
              <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-5 backdrop-blur-sm col-span-2 flex items-center justify-between">
                <div className="flex items-center gap-4">
                   <div className="p-3 bg-purple-500/10 rounded-xl">
                    <Package className="h-6 w-6 text-purple-400" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-400">Active Orders Pending Dispatch</p>
                    <h4 className="text-xl font-bold text-white">18 Orders <span className="text-sm font-normal text-slate-500">· 45 pallets</span></h4>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-xs font-medium text-purple-400">Next dispatch in 45m</span>
                  <div className="w-24 bg-slate-800 h-1.5 rounded-full mt-2 ml-auto">
                    <div className="bg-purple-500 h-1.5 rounded-full w-[60%]"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="relative z-10 flex items-center justify-between border-t border-slate-800 pt-6 mt-12 text-sm text-slate-400">
          <div className="flex items-center gap-2">
             <ShieldCheck className="h-4 w-4 text-emerald-500" />
             <span>Secure connection established</span>
          </div>
          <span>v2.4.1</span>
        </div>
      </div>

      {/* Right Panel - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 sm:p-12 lg:p-24 bg-white relative">
        <div className="w-full max-w-md space-y-8">
          {/* Mobile Header (Hidden on LG) */}
          <div className="flex lg:hidden items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-teal-600 rounded-lg flex items-center justify-center">
              <Activity className="text-white h-6 w-6" />
            </div>
            <div>
              <h2 className="text-2xl font-bold tracking-tight text-slate-900">AmpouleX</h2>
              <p className="text-teal-600 text-sm font-medium tracking-wide uppercase">ERP System</p>
            </div>
          </div>

          <div className="space-y-2">
            <h1 className="text-3xl font-bold tracking-tight text-slate-900">Welcome back</h1>
            <p className="text-slate-500">Sign in to access the operational control center.</p>
          </div>

          <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 text-sm text-slate-600 flex items-start gap-3">
             <Settings className="h-5 w-5 text-slate-400 mt-0.5 shrink-0" />
             <div>
               <p className="font-medium text-slate-900">Demo Environment</p>
               <p className="mt-1">Default credentials: <strong className="font-mono text-xs bg-slate-200 px-1 py-0.5 rounded">admin</strong> / <strong className="font-mono text-xs bg-slate-200 px-1 py-0.5 rounded">admin123</strong></p>
             </div>
          </div>

          <form onSubmit={handleLogin} className="space-y-6">
            <div className="space-y-4">
              <div className="space-y-2">
                <label htmlFor="username" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                  Username
                </label>
                <input
                  id="username"
                  type="text"
                  placeholder="Enter your username"
                  className="flex h-11 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm ring-offset-white file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-slate-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-colors"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label htmlFor="password" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                    Password
                  </label>
                  <a href="#" className="text-sm font-medium text-teal-600 hover:text-teal-500 hover:underline underline-offset-4">
                    Forgot password?
                  </a>
                </div>
                <input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  className="flex h-11 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm ring-offset-white file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-slate-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-colors"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-white transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-500 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-slate-900 text-slate-50 hover:bg-slate-900/90 h-11 px-8 py-2 w-full group"
            >
              {isLoading ? (
                <div className="flex items-center gap-2">
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-slate-400 border-t-white"></div>
                  <span>Authenticating...</span>
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <span>Sign In</span>
                  <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                </div>
              )}
            </button>
          </form>

          <p className="text-center text-sm text-slate-500">
             Having trouble signing in? <a href="#" className="font-medium text-slate-900 hover:underline">Contact IT Support</a>
          </p>
        </div>
      </div>
    </div>
  );
}
