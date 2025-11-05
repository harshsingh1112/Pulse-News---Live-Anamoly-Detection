"use client";

import { useEffect, useState } from "react";
import { getAggregate, getNews, getAnomalies, type Article, type Count, type Anomaly } from "./lib/api";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "./components/ui/card";
import { Badge } from "./components/ui/badge";
import { formatDate, getTopicColor } from "./lib/utils";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";

type Topic = "environment" | "politics" | "humanity" | null;
type BucketSize = "1m" | "5m" | "60m";

export default function Dashboard() {
  const [topic, setTopic] = useState<Topic>(null);
  const [bucketSize, setBucketSize] = useState<BucketSize>("5m");
  const [timeframe, setTimeframe] = useState<"1h" | "6h" | "24h">("24h");
  const [aggregateData, setAggregateData] = useState<Count[]>([]);
  const [latestNews, setLatestNews] = useState<Article[]>([]);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [topic, bucketSize, timeframe]);

  async function loadData() {
    setLoading(true);
    try {
      const since = getSinceTimestamp(timeframe);
      
      const [agg, news, anom] = await Promise.all([
        getAggregate({ bucket_size: bucketSize, topic: topic || undefined, since }).catch(e => { console.error("Aggregate error:", e); return { buckets: [] }; }),
        getNews({ topic: topic || undefined, limit: 20, since }).catch(e => { console.error("News error:", e); return { items: [] }; }), // Get more recent articles within timeframe
        getAnomalies({ topic: topic || undefined, limit: 10, since }).catch(e => { console.error("Anomalies error:", e); return { items: [] }; }),
      ]);

      setAggregateData(agg.buckets || []);
      // Filter news to show most recent first and only from selected timeframe
      const filteredNews = (news.items || [])
        .filter(item => {
          const itemDate = new Date(item.published_at_utc);
          const sinceDate = new Date(since);
          return itemDate >= sinceDate;
        })
        .sort((a, b) => new Date(b.published_at_utc).getTime() - new Date(a.published_at_utc).getTime()) // Most recent first
        .slice(0, 15); // Show latest 15
      setLatestNews(filteredNews);
      setAnomalies(anom.items || []);
    } catch (error) {
      console.error("Error loading data:", error);
      // Set empty data on error so UI doesn't break
      setAggregateData([]);
      setLatestNews([]);
      setAnomalies([]);
    } finally {
      setLoading(false);
    }
  }

  function getSinceTimestamp(timeframe: "1h" | "6h" | "24h"): string {
    const hours = timeframe === "1h" ? 1 : timeframe === "6h" ? 6 : 24;
    const date = new Date();
    date.setHours(date.getHours() - hours);
    return date.toISOString();
  }

  // Prepare chart data - group by time bucket, filtered by selected timeframe
  const since = getSinceTimestamp(timeframe);
  const sinceDate = new Date(since);
  
  const chartDataMap = new Map<string, { time: string; timestamp: number; [key: string]: number | string }>();
  
  aggregateData
    .filter((b) => {
      // Filter by timeframe
      const bucketDate = new Date(b.bucket_start_utc);
      if (bucketDate < sinceDate) return false;
      
      // Filter by topic if selected
      if (topic && b.topic !== topic) return false;
      
      return true;
    })
    .forEach((b) => {
      const timeKey = new Date(b.bucket_start_utc).toISOString();
      const timeLabel = new Date(b.bucket_start_utc).toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
      
      if (!chartDataMap.has(timeKey)) {
        chartDataMap.set(timeKey, {
          time: timeLabel,
          timestamp: new Date(b.bucket_start_utc).getTime(),
          environment: 0,
          politics: 0,
          humanity: 0,
          total: 0,
        });
      }
      
      const data = chartDataMap.get(timeKey)!;
      data[b.topic] = (data[b.topic] as number) + b.count;
      data.total = (data.total as number) + b.count;
    });

  const chartData = Array.from(chartDataMap.values()).sort((a, b) => (a.timestamp as number) - (b.timestamp as number));

  // Create anomaly markers - filtered by timeframe and topic
  const anomalyMarkers = anomalies
    .filter((a) => {
      const anomalyDate = new Date(a.bucket_start_utc);
      if (anomalyDate < sinceDate) return false;
      if (topic && a.topic !== topic) return false;
      return true;
    })
    .map((a) => ({
      time: new Date(a.bucket_start_utc).toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" }),
      timestamp: new Date(a.bucket_start_utc).getTime(),
      topic: a.topic,
      observed: a.observed,
      deviation: a.deviation,
    }));

  return (
    <div className="min-h-screen bg-background p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold">Live Breaking News Pulse</h1>
          <p className="text-muted-foreground">Real-time anomaly detection for environmental, political, and humanity news</p>
        </div>

        {/* Filters */}
        <Card>
          <CardContent className="p-4">
            <div className="flex flex-wrap gap-4 items-center">
              <div>
                <label className="text-sm font-medium mr-2">Topic:</label>
                <div className="inline-flex gap-2">
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
              </div>
              <div>
                <label className="text-sm font-medium mr-2">Timeframe:</label>
                <select
                  value={timeframe}
                  onChange={(e) => setTimeframe(e.target.value as "1h" | "6h" | "24h")}
                  className="px-3 py-1 rounded border"
                >
                  <option value="1h">Last 1h</option>
                  <option value="6h">Last 6h</option>
                  <option value="24h">Last 24h</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-medium mr-2">Bucket:</label>
                <select
                  value={bucketSize}
                  onChange={(e) => setBucketSize(e.target.value as BucketSize)}
                  className="px-3 py-1 rounded border"
                >
                  <option value="1m">1m</option>
                  <option value="5m">5m</option>
                  <option value="60m">60m</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Spike Now Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {(["environment", "politics", "humanity"] as const).map((t) => {
            const topicAnomalies = anomalies.filter((a) => a.topic === t);
            const latest = topicAnomalies[0];
            // Also check aggregate data for current spike
            const topicData = aggregateData.filter((b) => b.topic === t);
            const recentCount = topicData.length > 0 ? topicData[topicData.length - 1]?.count || 0 : 0;
            const avgCount = topicData.length > 0 
              ? topicData.reduce((sum, b) => sum + b.count, 0) / topicData.length 
              : 0;
            const isCurrentSpike = recentCount > avgCount * 2 && recentCount > 5;
            
            return (
              <Card key={t}>
                <CardHeader>
                  <CardTitle className="text-lg capitalize">{t}</CardTitle>
                </CardHeader>
                <CardContent>
                  {latest ? (
                    <div className="space-y-2">
                      <div className="text-2xl font-bold text-destructive">
                        🚨 Spike Detected
                      </div>
                      <div className="text-sm text-muted-foreground">
                        Deviation: {latest.deviation.toFixed(2)}
                      </div>
                      <div className="text-sm">
                        Observed: {latest.observed} (Expected: {latest.expected.toFixed(0)})
                      </div>
                      <div className="text-xs text-muted-foreground mt-2">
                        {new Date(latest.bucket_start_utc).toLocaleString()}
                      </div>
                    </div>
                  ) : isCurrentSpike ? (
                    <div className="space-y-2">
                      <div className="text-xl font-bold text-orange-600">
                        ⚠️ High Activity
                      </div>
                      <div className="text-sm">
                        Current: {recentCount} articles
                      </div>
                      <div className="text-sm text-muted-foreground">
                        Average: {avgCount.toFixed(1)}
                      </div>
                    </div>
                  ) : (
                    <div className="text-muted-foreground">No spikes detected</div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Volume Over Time</CardTitle>
            <CardDescription>News volume with anomaly markers</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="h-64 flex items-center justify-center">Loading...</div>
            ) : chartData.length === 0 ? (
              <div className="h-64 flex items-center justify-center text-muted-foreground">
                No data available. Data will appear as news is ingested.
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis 
                    dataKey="time" 
                    stroke="#6b7280"
                    style={{ fontSize: '12px' }}
                  />
                  <YAxis 
                    stroke="#6b7280"
                    style={{ fontSize: '12px' }}
                  />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '4px' }}
                    formatter={(value: any) => [value, 'Articles']}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="total" 
                    stroke="#3b82f6" 
                    strokeWidth={2} 
                    dot={{ r: 3 }}
                    name="Total"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="politics" 
                    stroke="#ef4444" 
                    strokeWidth={1.5} 
                    dot={{ r: 2 }}
                    name="Politics"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="environment" 
                    stroke="#10b981" 
                    strokeWidth={1.5} 
                    dot={{ r: 2 }}
                    name="Environment"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="humanity" 
                    stroke="#8b5cf6" 
                    strokeWidth={1.5} 
                    dot={{ r: 2 }}
                    name="Humanity"
                  />
                  {anomalyMarkers.map((marker, idx) => {
                    const chartPoint = chartData.find(d => d.time === marker.time);
                    if (!chartPoint) return null;
                    return (
                      <ReferenceLine 
                        key={`${marker.topic}-${idx}`}
                        x={marker.time}
                        stroke="#ef4444"
                        strokeWidth={2}
                        strokeDasharray="5 5"
                        label={{ value: `🚨 ${marker.topic}`, position: "top", fill: "#ef4444", fontSize: 10 }}
                      />
                    );
                  })}
                </LineChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        {/* Live Ticker */}
        <Card>
          <CardHeader>
            <CardTitle>Latest Headlines</CardTitle>
            <CardDescription>
              Showing {latestNews.length} articles from last {timeframe}
              {topic && ` • ${topic}`}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {latestNews.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No articles found for the selected filters. Try changing the timeframe or topic.
                </div>
              ) : (
                latestNews.map((article) => (
                  <div key={article.id} className="flex items-start gap-3 p-2 hover:bg-secondary rounded transition-colors">
                    <Badge className={getTopicColor(article.topic)}>{article.topic}</Badge>
                    <div className="flex-1 min-w-0">
                      <a
                        href={article.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm font-medium hover:underline block"
                      >
                        {article.title}
                      </a>
                      <div className="text-xs text-muted-foreground mt-1">
                        {article.source} • {formatDate(article.published_at_utc, "relative")}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

