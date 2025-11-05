import Link from "next/link";

export function Nav() {
  return (
    <nav className="border-b bg-card">
      <div className="max-w-7xl mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          <Link href="/" className="text-xl font-bold">
            PulseWatch
          </Link>
          <div className="flex gap-4">
            <Link href="/" className="hover:underline">
              Dashboard
            </Link>
            <Link href="/anomalies" className="hover:underline">
              Anomalies
            </Link>
            <Link href="/feed" className="hover:underline">
              Feed
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}

