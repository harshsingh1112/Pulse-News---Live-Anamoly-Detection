"use client";

import { useEffect, useState } from "react";
import { getNews, type Article } from "../lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { formatDate, getTopicColor } from "../lib/utils";

export default function FeedPage() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [topic, setTopic] = useState<"environment" | "politics" | "humanity" | null>(null);
  const [source, setSource] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [offset, setOffset] = useState(0);
  const limit = 50;

  useEffect(() => {
    loadArticles();
  }, [topic, source, offset]);

  async function loadArticles() {
    setLoading(true);
    try {
      const result = await getNews({
        topic: topic || undefined,
        source: source || undefined,
        limit,
        offset,
      });
      setArticles(result.items);
    } catch (error) {
      console.error("Error loading articles:", error);
    } finally {
      setLoading(false);
    }
  }

  const filteredArticles = articles.filter((a) =>
    search ? a.title.toLowerCase().includes(search.toLowerCase()) : true
  );

  return (
    <div className="min-h-screen bg-background p-4 md:p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold">News Feed</h1>
          <p className="text-muted-foreground">Browse all aggregated news articles</p>
        </div>

        {/* Filters */}
        <Card>
          <CardContent className="p-4 space-y-4">
            <div>
              <input
                type="text"
                placeholder="Search headlines..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full px-4 py-2 rounded border"
              />
            </div>
            <div className="flex flex-wrap gap-2">
              {[null, "environment", "politics", "humanity"].map((t) => (
                <button
                  key={t || "all"}
                  onClick={() => {
                    setTopic(t);
                    setOffset(0);
                  }}
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

        {/* Articles */}
        {loading ? (
          <div className="text-center py-8">Loading...</div>
        ) : (
          <div className="space-y-4">
            {filteredArticles.map((article) => (
              <Card key={article.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <Badge className={getTopicColor(article.topic)}>{article.topic}</Badge>
                    <div className="flex-1 min-w-0">
                      <a
                        href={article.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-lg font-semibold hover:underline block mb-2"
                      >
                        {article.title}
                      </a>
                      {article.summary && (
                        <p className="text-sm text-muted-foreground mb-2 line-clamp-2">
                          {article.summary}
                        </p>
                      )}
                      <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        <span>{article.source}</span>
                        {article.author && <span>by {article.author}</span>}
                        <span>{formatDate(article.published_at_utc)}</span>
                        {article.score && <span>Score: {article.score}</span>}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Pagination */}
        <div className="flex justify-center gap-2">
          <button
            onClick={() => setOffset(Math.max(0, offset - limit))}
            disabled={offset === 0}
            className="px-4 py-2 rounded border disabled:opacity-50"
          >
            Previous
          </button>
          <button
            onClick={() => setOffset(offset + limit)}
            disabled={articles.length < limit}
            className="px-4 py-2 rounded border disabled:opacity-50"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}

