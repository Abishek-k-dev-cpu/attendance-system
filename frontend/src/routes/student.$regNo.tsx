import { useEffect, useState } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  BookOpen,
  Calendar,
  CheckCircle2,
  Download,
  Frown,
  Printer,
  User,
  XCircle,
} from "lucide-react";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { DashboardSkeleton } from "@/components/Skeleton";
import { CircularProgress } from "@/components/CircularProgress";
import { SubjectTable } from "@/components/SubjectTable";
import { AttendanceCharts } from "@/components/AttendanceCharts";
import { fetchStudent } from "@/lib/api";
import type { Student } from "@/lib/mockData";
import { percentage, summarize } from "@/lib/attendance";

export const Route = createFileRoute("/student/$regNo")({
  head: ({ params }) => ({
    meta: [
      { title: `${params.regNo} — Attendance` },
      { name: "description", content: `Attendance dashboard for ${params.regNo}.` },
      { name: "robots", content: "noindex" },
    ],
  }),
  component: StudentDashboard,
});

function StudentDashboard() {
  const { regNo } = Route.useParams();
  const [student, setStudent] = useState<Student | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchStudent(regNo)
      .then((s) => !cancelled && setStudent(s))
      .catch((e) => !cancelled && setError(e instanceof Error ? e.message : "Failed to load"))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [regNo]);

  if (loading) {
    return (
      <div className="min-h-screen gradient-soft">
        <Navbar />
        <DashboardSkeleton />
      </div>
    );
  }

  if (error || !student) {
    return (
      <div className="min-h-screen gradient-soft">
        <Navbar />
        <div className="mx-auto flex max-w-xl flex-col items-center px-4 py-24 text-center">
          <div className="grid h-16 w-16 place-items-center rounded-2xl bg-destructive/10 text-destructive">
            <Frown className="h-8 w-8" />
          </div>
          <h1 className="mt-6 font-display text-2xl font-bold">No records found</h1>
          <p className="mt-2 text-sm text-muted-foreground">{error ?? "Data unavailable."}</p>
          <Link
            to="/"
            className="mt-6 inline-flex items-center gap-2 rounded-xl gradient-hero px-5 py-2.5 text-sm font-semibold text-primary-foreground shadow-elegant"
          >
            <ArrowLeft className="h-4 w-4" /> Back to search
          </Link>
        </div>
      </div>
    );
  }

  const summary = summarize(student.subjects);

  const downloadPdf = () => {
    const doc = new jsPDF();
    doc.setFontSize(16);
    doc.text("Attendance Report", 14, 18);
    doc.setFontSize(11);
    doc.text(`Name: ${student.name}`, 14, 28);
    doc.text(`Register No: ${student.registerNumber}`, 14, 34);
    doc.text(`Department: ${student.department}`, 14, 40);
    doc.text(`Year / Sec / Sem: ${student.year} / ${student.section} / ${student.semester}`, 14, 46);
    doc.text(
      `Overall: ${summary.percentage}%  |  Present: ${summary.attended} / ${summary.conducted}`,
      14,
      52,
    );

    autoTable(doc, {
      startY: 60,
      head: [["Code", "Subject", "Conducted", "Attended", "%"]],
      body: student.subjects.map((s) => [
        s.code,
        s.name,
        s.conducted,
        s.attended,
        `${percentage(s.attended, s.conducted)}%`,
      ]),
      styles: { fontSize: 10 },
      headStyles: { fillColor: [59, 105, 220] },
    });

    doc.save(`attendance-${student.registerNumber}.pdf`);
  };

  return (
    <div className="min-h-screen gradient-soft">
      <Navbar />
      <main className="mx-auto max-w-7xl space-y-6 px-4 py-8 sm:px-6">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <Link
            to="/"
            className="inline-flex w-fit items-center gap-2 text-sm text-muted-foreground hover:text-foreground"
          >
            <ArrowLeft className="h-4 w-4" /> Back to search
          </Link>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={downloadPdf}
              className="inline-flex items-center gap-2 rounded-xl border border-border bg-card/60 px-4 py-2 text-sm font-medium hover:bg-accent"
            >
              <Download className="h-4 w-4" /> Download PDF
            </button>
            <button
              onClick={() => window.print()}
              className="inline-flex items-center gap-2 rounded-xl border border-border bg-card/60 px-4 py-2 text-sm font-medium hover:bg-accent"
            >
              <Printer className="h-4 w-4" /> Print
            </button>
          </div>
        </div>

        {/* Profile + summary */}
        <motion.section
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid gap-6 lg:grid-cols-3"
        >
          <div className="glass rounded-2xl p-6 lg:col-span-2">
            <div className="grid grid-cols-[auto_minmax(0,1fr)] items-center gap-5">
              <div className="grid h-20 w-20 shrink-0 place-items-center rounded-2xl gradient-hero text-primary-foreground shadow-elegant">
                {student.photo ? (
                  <img
                    src={student.photo}
                    alt={student.name}
                    className="h-full w-full rounded-2xl object-cover"
                  />
                ) : (
                  <User className="h-9 w-9" />
                )}
              </div>
              <div className="min-w-0">
                <h1 className="truncate font-display text-2xl font-bold sm:text-3xl">
                  {student.name}
                </h1>
                <p className="mt-1 font-mono text-sm text-muted-foreground">
                  {student.registerNumber}
                </p>
              </div>
            </div>
            <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
              <InfoTile label="Department" value={student.department} />
              <InfoTile label="Year" value={student.year} />
              <InfoTile label="Section" value={student.section} />
              <InfoTile label="Semester" value={student.semester} />
            </div>
            <p className="mt-5 text-xs text-muted-foreground">
              <Calendar className="mr-1 inline h-3 w-3" />
              Last updated: {new Date(student.lastUpdated).toLocaleString()}
            </p>
          </div>

          <div className="glass flex flex-col items-center justify-center rounded-2xl p-6">
            <CircularProgress value={summary.percentage} />
            <div className="mt-6 grid w-full grid-cols-3 gap-2 text-center">
              <Stat icon={<BookOpen className="h-4 w-4" />} label="Total" value={summary.conducted} />
              <Stat
                icon={<CheckCircle2 className="h-4 w-4 text-[color:var(--color-success)]" />}
                label="Present"
                value={summary.attended}
              />
              <Stat
                icon={<XCircle className="h-4 w-4 text-destructive" />}
                label="Absent"
                value={summary.absent}
              />
            </div>
          </div>
        </motion.section>

        <AttendanceCharts subjects={student.subjects} />
        <SubjectTable subjects={student.subjects} />
      </main>
      <Footer />
    </div>
  );
}

function InfoTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-border/60 bg-background/40 p-3">
      <p className="text-[11px] uppercase tracking-wider text-muted-foreground">{label}</p>
      <p className="mt-1 truncate text-sm font-semibold">{value}</p>
    </div>
  );
}

function Stat({ icon, label, value }: { icon: React.ReactNode; label: string; value: number }) {
  return (
    <div className="rounded-xl border border-border/60 bg-background/40 p-3">
      <div className="flex items-center justify-center gap-1 text-xs text-muted-foreground">
        {icon} {label}
      </div>
      <p className="mt-1 font-display text-lg font-bold">{value}</p>
    </div>
  );
}
