import React from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const activities = [
  {
    id: 1,
    time: "2 min ago",
    text: "Batch #B-2047 completed QC inspection — 10,000 units cleared",
    module: "production",
    color: "bg-blue-500",
  },
  {
    id: 2,
    time: "5 min ago",
    text: "Invoice #INV-3891 issued to Al-Shifa Hospital — PKR 284,500",
    module: "finance",
    color: "bg-green-500",
  },
  {
    id: 3,
    time: "14 min ago",
    text: "Payroll processed for March 2026 — 47 employees",
    module: "payroll",
    color: "bg-amber-500",
  },
  {
    id: 4,
    time: "22 min ago",
    text: "Purchase Order #PO-1123 approved — Raw glass tubes",
    module: "purchasing",
    color: "bg-purple-500",
  },
  {
    id: 5,
    time: "38 min ago",
    text: "Production batch B-2048 started — 5ml ampoules",
    module: "production",
    color: "bg-blue-500",
  },
];

export function AmbientProof() {
  return (
    <div className="min-h-[100dvh] bg-[#fdfbf7] flex text-stone-900 font-sans overflow-hidden">
      <style dangerouslySetInnerHTML={{ __html: `
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&display=swap');
        
        @keyframes ticker-scroll {
          0% { transform: translateY(0); }
          100% { transform: translateY(-50%); }
        }
        .animate-ticker {
          animation: ticker-scroll 40s linear infinite;
        }
        .animate-ticker:hover {
          animation-play-state: paused;
        }
      ` }} />
      
      {/* Left side: System Activity Ticker */}
      <div className="hidden lg:flex flex-col w-[45%] border-r border-stone-200/60 p-16 relative overflow-hidden bg-[#fdfbf7]">
        <div className="absolute top-0 left-0 right-0 h-40 bg-gradient-to-b from-[#fdfbf7] to-transparent z-10 pointer-events-none" />
        <div className="absolute bottom-0 left-0 right-0 h-40 bg-gradient-to-t from-[#fdfbf7] to-transparent z-10 pointer-events-none" />
        
        <div className="mb-12 z-20 flex items-center gap-3">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          <h2 className="text-xs font-semibold tracking-widest text-stone-400 uppercase">System Pulse</h2>
        </div>

        <div className="flex-1 relative overflow-hidden">
          <div className="absolute inset-0 flex flex-col pt-12 animate-ticker">
            {[...activities, ...activities].map((activity, index) => (
              <div key={index} className="flex gap-6 items-start group opacity-60 hover:opacity-100 transition-opacity duration-300 mb-8">
                <div className="mt-1.5 flex flex-col items-center">
                  <div className={`w-2.5 h-2.5 rounded-full ${activity.color} ring-4 ring-[#fdfbf7]`} />
                  <div className="w-px h-16 bg-stone-200 mt-2 group-last:hidden" />
                </div>
                <div className="flex flex-col pb-2">
                  <span className="text-[11px] font-bold tracking-wider text-stone-400 uppercase mb-1.5">{activity.time}</span>
                  <p className="text-[15px] text-stone-700 leading-relaxed max-w-[280px] font-medium">{activity.text}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right side: Login Form */}
      <div className="flex-1 flex flex-col items-center justify-center p-8 sm:p-12 lg:p-24 relative">
        <div className="w-full max-w-[360px]">
          
          <div className="space-y-4 text-center lg:text-left mb-16">
            <h1 className="text-5xl md:text-6xl text-stone-800 tracking-tight" style={{ fontFamily: '"Playfair Display", serif' }}>AmpouleX</h1>
            <p className="text-stone-500 text-sm md:text-base tracking-wide uppercase text-[11px] font-semibold">Enterprise Resource Planning</p>
          </div>

          <form className="space-y-8" onSubmit={(e) => e.preventDefault()}>
            <div className="space-y-6">
              <div className="space-y-3">
                <Label htmlFor="username" className="text-stone-500 font-medium text-xs uppercase tracking-wider">Username</Label>
                <Input 
                  id="username" 
                  placeholder="admin" 
                  className="bg-transparent border-0 border-b border-stone-300 focus-visible:ring-0 focus-visible:border-stone-800 rounded-none px-0 shadow-none text-lg h-12 transition-colors placeholder:text-stone-300"
                />
              </div>
              
              <div className="space-y-3">
                <Label htmlFor="password" className="text-stone-500 font-medium text-xs uppercase tracking-wider">Password</Label>
                <Input 
                  id="password" 
                  type="password"
                  placeholder="••••••••" 
                  className="bg-transparent border-0 border-b border-stone-300 focus-visible:ring-0 focus-visible:border-stone-800 rounded-none px-0 shadow-none text-lg h-12 transition-colors placeholder:text-stone-300"
                />
              </div>
            </div>

            <div className="pt-4">
              <Button className="w-full bg-stone-800 hover:bg-stone-900 text-[#fdfbf7] rounded h-14 text-base font-medium shadow-xl shadow-stone-900/10 transition-all duration-300 hover:shadow-stone-900/20 hover:-translate-y-0.5">
                Sign In
              </Button>
            </div>
            
            <div className="text-center pt-6 opacity-60">
              <p className="text-xs text-stone-500 font-medium tracking-wide">Default: admin / admin123</p>
            </div>
          </form>

        </div>
      </div>
    </div>
  );
}
