import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Beaker, ShieldCheck } from "lucide-react";

export function Industrial() {
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setTimeout(() => setIsLoading(false), 1500);
  };

  return (
    <div className="min-h-screen w-full bg-[#0a0a0d] relative overflow-hidden flex items-center justify-center font-mono selection:bg-[#00e5ff] selection:text-black">
      {/* Background Ambience: Glass Cylinders */}
      <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none opacity-40">
        <div className="absolute left-[10%] top-[-10%] w-24 h-[120%] bg-gradient-to-r from-transparent via-white/5 to-transparent border-x border-white/10 rounded-full blur-[1px]" style={{ boxShadow: "inset 10px 0 20px rgba(0,229,255,0.05), inset -10px 0 20px rgba(0,229,255,0.05)" }}></div>
        <div className="absolute left-[30%] top-[-5%] w-16 h-[110%] bg-gradient-to-r from-transparent via-white/5 to-transparent border-x border-white/10 rounded-full blur-[2px]" style={{ boxShadow: "inset 8px 0 15px rgba(0,229,255,0.05), inset -8px 0 15px rgba(0,229,255,0.05)" }}></div>
        <div className="absolute left-[50%] top-[-15%] w-32 h-[130%] bg-gradient-to-r from-transparent via-white/5 to-transparent border-x border-white/10 rounded-full blur-[1px]" style={{ boxShadow: "inset 15px 0 30px rgba(0,229,255,0.08), inset -15px 0 30px rgba(0,229,255,0.08)" }}></div>
        <div className="absolute left-[75%] top-[-10%] w-20 h-[120%] bg-gradient-to-r from-transparent via-white/5 to-transparent border-x border-white/10 rounded-full blur-[2px]" style={{ boxShadow: "inset 10px 0 20px rgba(255,179,0,0.05), inset -10px 0 20px rgba(255,179,0,0.05)" }}></div>
        <div className="absolute left-[90%] top-[-5%] w-28 h-[110%] bg-gradient-to-r from-transparent via-white/5 to-transparent border-x border-white/10 rounded-full blur-[1px]" style={{ boxShadow: "inset 12px 0 25px rgba(0,229,255,0.05), inset -12px 0 25px rgba(0,229,255,0.05)" }}></div>
        
        {/* Horizontal structural lines */}
        <div className="absolute top-[30%] left-0 w-full h-[1px] bg-white/5"></div>
        <div className="absolute top-[70%] left-0 w-full h-[1px] bg-white/5"></div>
        
        {/* Glows */}
        <div className="absolute top-[20%] left-[50%] w-[600px] h-[600px] bg-[#00e5ff] rounded-full mix-blend-screen filter blur-[120px] opacity-[0.03] transform -translate-x-1/2"></div>
      </div>

      <div className="relative z-10 w-full max-w-md mx-auto p-6">
        {/* The Card */}
        <div 
          className="relative bg-[#111116]/80 border border-white/10 p-10 rounded-lg shadow-2xl overflow-hidden"
          style={{ backdropFilter: "blur(16px)", WebkitBackdropFilter: "blur(16px)" }}
        >
          {/* Top Edge Highlight */}
          <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-[#00e5ff]/50 to-transparent"></div>
          
          <div className="mb-10 text-center flex flex-col items-center">
            <div className="w-14 h-14 rounded-full border border-[#00e5ff]/30 bg-[#00e5ff]/10 flex items-center justify-center mb-6 shadow-[0_0_20px_rgba(0,229,255,0.15)] relative">
              <Beaker className="w-6 h-6 text-[#00e5ff]" />
              <div className="absolute top-0 left-1/2 w-4 h-[1px] bg-[#00e5ff] -translate-x-1/2 shadow-[0_0_8px_#00e5ff]"></div>
            </div>
            <h1 className="text-2xl tracking-[0.2em] font-medium text-white mb-2 uppercase flex items-center gap-2">
              Ampoule<span className="text-[#00e5ff] font-bold">X</span>
            </h1>
            <p className="text-xs text-[#888899] tracking-widest uppercase">Process Control System</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2 relative group">
              <div className="absolute left-3 top-9 text-[#888899] group-focus-within:text-[#00e5ff] transition-colors">
                <ShieldCheck className="w-4 h-4" />
              </div>
              <Label htmlFor="username" className="text-xs tracking-wider text-[#888899] uppercase">Operator ID</Label>
              <Input
                id="username"
                type="text"
                placeholder="Enter ID"
                className="pl-10 bg-black/40 border-white/10 text-white placeholder:text-white/20 focus-visible:ring-1 focus-visible:ring-[#00e5ff] focus-visible:border-[#00e5ff] rounded h-11 transition-all rounded-none border-b-2 focus-visible:border-b-[#00e5ff]"
                required
              />
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="password" className="text-xs tracking-wider text-[#888899] uppercase">Security Key</Label>
              </div>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                className="bg-black/40 border-white/10 text-white placeholder:text-white/20 focus-visible:ring-1 focus-visible:ring-[#00e5ff] focus-visible:border-[#00e5ff] rounded h-11 transition-all rounded-none border-b-2 focus-visible:border-b-[#00e5ff]"
                required
              />
            </div>

            <div className="pt-2">
              <Button 
                type="submit" 
                className="w-full bg-[#00e5ff] hover:bg-[#00b3cc] text-black font-bold tracking-widest uppercase h-12 rounded-none transition-all hover:shadow-[0_0_20px_rgba(0,229,255,0.4)] relative overflow-hidden group"
                disabled={isLoading}
              >
                <div className="absolute inset-0 w-full h-full bg-white/20 -translate-x-full group-hover:animate-[shimmer_1.5s_infinite]"></div>
                {isLoading ? (
                  <span className="flex items-center gap-2">
                    <span className="w-4 h-4 border-2 border-black/20 border-t-black rounded-full animate-spin"></span>
                    Authenticating
                  </span>
                ) : (
                  "Initialize Session"
                )}
              </Button>
            </div>
            
            <div className="mt-6 flex items-center justify-between text-[10px] text-[#555566] tracking-widest uppercase border-t border-white/5 pt-6">
              <span>SYS_STAT: <span className="text-green-500">ONLINE</span></span>
              <span>Default: admin / admin123</span>
            </div>
          </form>
        </div>
        
        {/* Environmental Readout */}
        <div className="absolute bottom-6 left-6 text-[10px] text-[#444455] tracking-widest uppercase font-mono hidden md:flex flex-col gap-1">
          <div>ZONE: A-CLNRM</div>
          <div>TEMP: 19.4°C</div>
          <div>HUM: 42%</div>
        </div>
      </div>
    </div>
  );
}
