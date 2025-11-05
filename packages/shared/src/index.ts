/** Shared types for PulseWatch */

export type Topic = "environment" | "politics" | "humanity";
export type SourceType = "rss" | "reddit_sub" | "reddit_user";
export type BucketSize = "1m" | "5m" | "60m";

export interface Article {
  id: number;
  source: string;
  source_type: string;
  title: string;
  url: string;
  summary: string | null;
  topic: Topic;
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
  bucket_size: BucketSize;
  topic: Topic;
  source: string | null;
  count: number;
}

export interface AggregateResponse {
  buckets: Count[];
  bucket_size: BucketSize;
  topic: Topic | null;
  source: string | null;
}

export interface Anomaly {
  id: number;
  bucket_start_utc: string;
  bucket_size: BucketSize;
  topic: Topic;
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
  type: SourceType;
  url_or_id: string;
  topic: Topic | null;
  enabled: boolean;
}

export interface SourceListResponse {
  items: Source[];
}

export interface StreamEvent {
  type: "count" | "anomaly" | "article";
  payload: Record<string, any>;
}

export interface HealthResponse {
  status: string;
  version: string;
  last_ingest_utc: string | null;
}

