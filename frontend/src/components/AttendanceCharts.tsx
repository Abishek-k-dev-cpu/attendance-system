import { Bar, Pie } from "react-chartjs-2";
import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Tooltip,
} from "chart.js";
import type { Subject } from "@/lib/mockData";
import { percentage } from "@/lib/attendance";

ChartJS.register(ArcElement, BarElement, CategoryScale, LinearScale, Tooltip, Legend);

export function AttendanceCharts({ subjects }: { subjects: Subject[] }) {
  const totalConducted = subjects.reduce((a, s) => a + s.conducted, 0);
  const totalAttended = subjects.reduce((a, s) => a + s.attended, 0);
  const absent = totalConducted - totalAttended;

  const pieData = {
    labels: ["Present", "Absent"],
    datasets: [
      {
        data: [totalAttended, absent],
        backgroundColor: ["oklch(0.65 0.17 150)", "oklch(0.6 0.24 27)"],
        borderWidth: 0,
      },
    ],
  };

  const barData = {
    labels: subjects.map((s) => s.code),
    datasets: [
      {
        label: "Attendance %",
        data: subjects.map((s) => percentage(s.attended, s.conducted)),
        backgroundColor: subjects.map((s) => {
          const p = percentage(s.attended, s.conducted);
          if (p >= 90) return "oklch(0.65 0.17 150)";
          if (p >= 75) return "oklch(0.75 0.17 65)";
          return "oklch(0.6 0.24 27)";
        }),
        borderRadius: 8,
      },
    ],
  };

  return (
    <div className="grid gap-6 lg:grid-cols-5">
      <div className="glass rounded-2xl p-6 lg:col-span-2">
        <h3 className="mb-4 font-display text-lg font-bold">Present vs Absent</h3>
        <div className="mx-auto h-64 w-full max-w-xs">
          <Pie data={pieData} options={{ maintainAspectRatio: false, plugins: { legend: { position: "bottom" } } }} />
        </div>
      </div>
      <div className="glass rounded-2xl p-6 lg:col-span-3">
        <h3 className="mb-4 font-display text-lg font-bold">Subject-wise Percentage</h3>
        <div className="h-64 w-full">
          <Bar
            data={barData}
            options={{
              maintainAspectRatio: false,
              plugins: { legend: { display: false } },
              scales: { y: { beginAtZero: true, max: 100 } },
            }}
          />
        </div>
      </div>
    </div>
  );
}
