"use client";

import { useEffect, useState } from "react";
import { getAnomalies, type Anomaly } from "../lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { formatDate } from "../lib/utils";

export default function AnomaliesPage() {
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [loading, setLoading] = useState(true);
  const [topic, setTopic] = useState<"environment" | "politics" | "humanity" | null>(null);

  useEffect(() => {
    loadAnomalies();
    const interval = setInterval(loadAnomalies, 60000);
    return () => clearInterval(interval);
  }, [topic]);

  async function loadAnomalies() {
    setLoading(true);
    try {
      const result = await getAnomalies({ topic: topic || undefined, limit: 100 });
      setAnomalies(result.items);
    } catch (error) {
      console.error("Error loading anomalies:", error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-background p-4 md:p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold">Detected Anomalies</h1>
          <p className="text-muted-foreground">Spikes in news volume over time</p>
        </div>

        {/* Filters */}
        <Card>
          <CardContent className="p-4">
            <div className="flex gap-2">
              {[null, "environment", "politics", "humanity"].map((t) => (
                <button
                  key={t || "all"}
                  onClick={() => setTopic(t)}
                  className={`px-3 py-1 rounded-full text-sm ${
                    topic === t
                      ? "bg-primary text-primary-foreground"
                      : "bg-secondary text-secondary-foreground"
                  }`}
                >
                  {t || "All"}
                </button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Table */}
        <Card>
          <CardHeader>
            <CardTitle>Anomalies</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-8">Loading...</div>
            ) : anomalies.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">No anomalies detected</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-2">Time (IST)</th>
                      <th className="text-left p-2">Topic</th>
                      <th className="text-left p-2">Observed</th>
                      <th className="text-left p-2">Expected</th>
                      <th className="text-left p-2">Deviation</th>
                      <th className="text-left p-2">Method</th>
                    </tr>
                  </thead>
                  <tbody>
                    {anomalies.map((anomaly) => (
                      <tr key={anomaly.id} className="border-b hover:bg-secondary">
                        <td className="p-2 text-sm">
                          {formatDate(anomaly.bucket_start_utc, "absolute")}
                        </td>
                        <td className="p-2">
                          <Badge className="capitalize">{anomaly.topic}</Badge>
                        </td>
                        <td className="p-2">{anomaly.observed}</td>
                        <td className="p-2">{anomaly.expected.toFixed(1)}</td>
                        <td className="p-2 font-semibold text-destructive">
                          {anomaly.deviation.toFixed(2)}
                        </td>
                        <td className="p-2 text-sm">{anomaly.method}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

