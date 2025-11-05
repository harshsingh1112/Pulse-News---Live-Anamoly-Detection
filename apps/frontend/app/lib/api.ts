/** API client functions */

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export interface Article {
  id: number;
  source: string;
  source_type: string;
  title: string;
  url: string;
  summary: string | null;
  topic: "environment" | "politics" | "humanity";
  published_at_utc: string;
  fetched_at_utc: string;
  author: string | null;
  score: number | null;
  raw: Record<string, any> | null;
}

export interface ArticleListResponse {
  items: Article[];
  total: number;
  limit: number;
  offset: number;
}

export interface Count {
  bucket_start_utc: string;
  bucket_size: "1m" | "5m" | "60m";
  topic: "environment" | "politics" | "humanity";
  source: string | null;
  count: number;
}

export interface AggregateResponse {
  buckets: Count[];
  bucket_size: "1m" | "5m" | "60m";
  topic: "environment" | "politics" | "humanity" | null;
  source: string | null;
}

export interface Anomaly {
  id: number;
  bucket_start_utc: string;
  bucket_size: "1m" | "5m" | "60m";
  topic: "environment" | "politics" | "humanity";
  observed: number;
  expected: number;
  deviation: number;
  method: string;
  created_at_utc: string;
}

export interface AnomalyListResponse {
  items: Anomaly[];
  total: number;
}

export interface Source {
  id: number;
  name: string;
  type: "rss" | "reddit_sub" | "reddit_user";
  url_or_id: string;
  topic: "environment" | "politics" | "humanity" | null;
  enabled: boolean;
}

export interface SourceListResponse {
  items: Source[];
}

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
}

export async function getNews(params?: {
  topic?: "environment" | "politics" | "humanity";
  source?: string;
  since?: string;
  limit?: number;
  offset?: number;
}): Promise<ArticleListResponse> {
  const searchParams = new URLSearchParams();
  if (params?.topic) searchParams.set("topic", params.topic);
  if (params?.source) searchParams.set("source", params.source);
  if (params?.since) searchParams.set("since", params.since);
  if (params?.limit) searchParams.set("limit", params.limit.toString());
  if (params?.offset) searchParams.set("offset", params.offset.toString());

  return fetchAPI<ArticleListResponse>(`/api/news?${searchParams.toString()}`);
}

export async function getAggregate(params?: {
  bucket_size?: "1m" | "5m" | "60m";
  topic?: "environment" | "politics" | "humanity";
  source?: string;
  since?: string;
}): Promise<AggregateResponse> {
  const searchParams = new URLSearchParams();
  if (params?.bucket_size) searchParams.set("bucket_size", params.bucket_size);
  if (params?.topic) searchParams.set("topic", params.topic);
  if (params?.source) searchParams.set("source", params.source);
  if (params?.since) searchParams.set("since", params.since);

  return fetchAPI<AggregateResponse>(`/api/aggregate?${searchParams.toString()}`);
}

export async function getAnomalies(params?: {
  topic?: "environment" | "politics" | "humanity";
  since?: string;
  bucket_size?: "1m" | "5m" | "60m";
  limit?: number;
}): Promise<AnomalyListResponse> {
  const searchParams = new URLSearchParams();
  if (params?.topic) searchParams.set("topic", params.topic);
  if (params?.since) searchParams.set("since", params.since);
  if (params?.bucket_size) searchParams.set("bucket_size", params.bucket_size);
  if (params?.limit) searchParams.set("limit", params.limit.toString());

  return fetchAPI<AnomalyListResponse>(`/api/anomalies?${searchParams.toString()}`);
}

export async function getSources(): Promise<SourceListResponse> {
  return fetchAPI<SourceListResponse>("/api/sources");
}

export function getStreamURL(): string {
  return `${API_BASE}/api/stream`;
}

