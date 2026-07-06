import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { ArrowUpDown, Search } from "lucide-react";
import type { Subject } from "@/lib/mockData";
import { colorFor, percentage } from "@/lib/attendance";

type SortKey = "code" | "name" | "conducted" | "attended" | "percentage";

const badgeClass: Record<ReturnType<typeof colorFor>, string> = {
  success: "bg-[color:var(--color-success)]/15 text-[color:var(--color-success)] border-[color:var(--color-success)]/30",
  warning: "bg-[color:var(--color-warning)]/15 text-[color:var(--color-warning)] border-[color:var(--color-warning)]/30",
  destructive:
    "bg-destructive/15 text-destructive border-destructive/30",
};

export function SubjectTable({ subjects }: { subjects: Subject[] }) {
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState<{ key: SortKey; dir: "asc" | "desc" }>({
    key: "percentage",
    dir: "desc",
  });

  const rows = useMemo(() => {
    const filtered = subjects.filter(
      (s) =>
        s.name.toLowerCase().includes(query.toLowerCase()) ||
        s.code.toLowerCase().includes(query.toLowerCase()),
    );
    const withPct = filtered.map((s) => ({ ...s, percentage: percentage(s.attended, s.conducted) }));
    const dir = sort.dir === "asc" ? 1 : -1;
    return withPct.sort((a, b) => {
      const av = a[sort.key];
      const bv = b[sort.key];
      if (typeof av === "number" && typeof bv === "number") return (av - bv) * dir;
      return String(av).localeCompare(String(bv)) * dir;
    });
  }, [subjects, query, sort]);

  const toggleSort = (key: SortKey) =>
    setSort((prev) => ({ key, dir: prev.key === key && prev.dir === "desc" ? "asc" : "desc" }));

  const H = ({ k, label }: { k: SortKey; label: string }) => (
    <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground">
      <button onClick={() => toggleSort(k)} className="inline-flex items-center gap-1 hover:text-foreground">
        {label} <ArrowUpDown className="h-3 w-3 opacity-60" />
      </button>
    </th>
  );

  return (
    <div className="glass rounded-2xl p-4 sm:p-6">
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h3 className="font-display text-lg font-bold">Subject-wise Attendance</h3>
        <div className="relative w-full sm:w-64">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search subject…"
            className="w-full rounded-lg border border-border bg-background/60 py-2 pl-9 pr-3 text-sm outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full">
          <thead>
            <tr className="border-b border-border">
              <H k="code" label="Code" />
              <H k="name" label="Subject" />
              <H k="conducted" label="Conducted" />
              <H k="attended" label="Attended" />
              <H k="percentage" label="%" />
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-4 py-10 text-center text-sm text-muted-foreground">
                  No subjects match your search.
                </td>
              </tr>
            ) : (
              rows.map((s, i) => {
                const c = colorFor(s.percentage);
                return (
                  <motion.tr
                    key={s.code}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.04 }}
                    className="border-b border-border/50 last:border-0"
                  >
                    <td className="px-4 py-3 font-mono text-xs">{s.code}</td>
                    <td className="px-4 py-3 text-sm font-medium">{s.name}</td>
                    <td className="px-4 py-3 text-sm">{s.conducted}</td>
                    <td className="px-4 py-3 text-sm">{s.attended}</td>
                    <td className="px-4 py-3">
                      <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${badgeClass[c]}`}>
                        {s.percentage}%
                      </span>
                    </td>
                  </motion.tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
