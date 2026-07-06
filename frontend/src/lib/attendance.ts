import type { Subject } from "./mockData";

export function percentage(attended: number, conducted: number): number {
  if (!conducted) return 0;
  return Math.round((attended / conducted) * 1000) / 10;
}

export function colorFor(p: number): "success" | "warning" | "destructive" {
  if (p >= 90) return "success";
  if (p >= 75) return "warning";
  return "destructive";
}

export function summarize(subjects: Subject[]) {
  const conducted = subjects.reduce((a, s) => a + s.conducted, 0);
  const attended = subjects.reduce((a, s) => a + s.attended, 0);
  return {
    conducted,
    attended,
    absent: conducted - attended,
    percentage: percentage(attended, conducted),
  };
}
