import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function App() {
  const [metrics, setMetrics] = useState(null);
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch('http://localhost:8080/api/metrics');
        const data = await response.json();
        setMetrics(data);

        // Add the new data point to our chart history (keeping the last 20 ticks)
        setChartData(prevData => {
          const newPoint = {
            time: new Date().toLocaleTimeString('en-US', { hour12: false, hour: "numeric", minute: "numeric", second: "numeric" }),
            R1_Latency: data.paths['5001']?.latency || 0,
            R2_Latency: data.paths['5002']?.latency || 0,
          };
          return [...prevData.slice(-20), newPoint];
        });
      } catch (error) {
        console.error("Error fetching network data. Is the Flask API running?", error);
      }
    };

    // Poll the Flask API every 500ms
    const interval = setInterval(fetchMetrics, 500);
    return () => clearInterval(interval);
  }, []);

  if (!metrics) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-900 text-white text-xl">
        Connecting to Adaptive Controller...
      </div>
    );
  }

  const r1 = metrics.paths['5001'];
  const r2 = metrics.paths['5002'];
  const target = metrics.current_target;

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-8 font-sans">
      <div className="max-w-6xl mx-auto">
        
        {/* Header */}
        <header className="mb-8 border-b border-slate-700 pb-4 flex justify-between items-end">
          <div>
            <h1 className="text-3xl font-bold text-blue-400">Adaptive Multipath Controller</h1>
            <p className="text-slate-400 mt-1">Live Routing Telemetry & Path Selection</p>
          </div>
          <div className="text-right">
            <p className="text-sm text-slate-400">Total Packets Sent</p>
            <p className="text-2xl font-mono text-emerald-400">{metrics.total_packets_sent}</p>
          </div>
        </header>

        {/* Top Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          
          {/* R1 Card */}
          <div className={`p-6 rounded-xl border-2 transition-colors ${target === 5001 ? 'border-blue-500 bg-slate-800' : 'border-slate-700 bg-slate-800/50'}`}>
            <h2 className="text-xl font-semibold mb-4 flex justify-between">
              <span>Path 1 (R1)</span>
              <span className={r1.status === 'healthy' ? 'text-emerald-400' : 'text-red-500'}>
                {r1.status.toUpperCase()}
              </span>
            </h2>
            <div className="space-y-2 font-mono text-lg">
              <p>Latency: <span className="text-blue-400">{r1.latency} ms</span></p>
              <p>Score: <span>{r1.score}</span></p>
            </div>
            {target === 5001 && <div className="mt-4 text-xs font-bold text-blue-400 tracking-wider uppercase">Active Route</div>}
          </div>

          {/* R2 Card */}
          <div className={`p-6 rounded-xl border-2 transition-colors ${target === 5002 ? 'border-purple-500 bg-slate-800' : 'border-slate-700 bg-slate-800/50'}`}>
            <h2 className="text-xl font-semibold mb-4 flex justify-between">
              <span>Path 2 (R2)</span>
              <span className={r2.status === 'healthy' ? 'text-emerald-400' : 'text-red-500'}>
                {r2.status.toUpperCase()}
              </span>
            </h2>
            <div className="space-y-2 font-mono text-lg">
              <p>Latency: <span className="text-purple-400">{r2.latency} ms</span></p>
              <p>Score: <span>{r2.score}</span></p>
            </div>
            {target === 5002 && <div className="mt-4 text-xs font-bold text-purple-400 tracking-wider uppercase">Active Route</div>}
          </div>

          {/* Controller Decision Card */}
          <div className="p-6 rounded-xl border border-slate-700 bg-slate-800 flex flex-col justify-center items-center text-center">
            <h2 className="text-sm text-slate-400 uppercase tracking-wider mb-2">Algorithm Routing Decision</h2>
            <div className="text-5xl font-bold text-white mb-2">
              Port {target || 'NONE'}
            </div>
            <p className="text-sm text-slate-400">Targeting lowest path score</p>
          </div>
        </div>

        {/* Live Latency Chart */}
        <div className="p-6 rounded-xl border border-slate-700 bg-slate-800">
          <h2 className="text-xl font-semibold mb-6">Real-Time Path Latency (ms)</h2>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="time" stroke="#94a3b8" tick={{fontSize: 12}} />
                <YAxis stroke="#94a3b8" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#f8fafc' }}
                />
                <Legend />
                <Line type="monotone" dataKey="R1_Latency" stroke="#3b82f6" strokeWidth={3} dot={false} animationDuration={300} />
                <Line type="monotone" dataKey="R2_Latency" stroke="#a855f7" strokeWidth={3} dot={false} animationDuration={300} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </div>
  );
}

export default App;