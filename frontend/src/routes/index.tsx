import { useState } from "react";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { AlertCircle, GraduationCap, Loader2, Search } from "lucide-react";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { fetchStudent } from "@/lib/api";
import { SAMPLE_REGISTERS } from "@/lib/mockData";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Attendance Portal — Government College of Engineering Dharmapuri" },
      {
        name: "description",
        content:
          "Check your attendance instantly. Enter your register number to view subject-wise attendance, charts, and download a PDF report.",
      },
      { property: "og:title", content: "Attendance Portal — Government College of Engineering Dharmapuri" },
      {
        property: "og:description",
        content: "Instant student attendance lookup with charts and PDF export.",
      },
    ],
  }),
  component: Home,
});

function Home() {
  const [reg, setReg] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reg.trim()) {
      setError("Please enter your register number.");
      return;
    }
    setError(null);
    setLoading(true);
    try {
      await fetchStudent(reg);
      navigate({ to: "/student/$regNo", params: { regNo: reg.trim().toUpperCase() } });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong. Try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen gradient-soft">
      <Navbar />
      <main className="relative overflow-hidden">
        <div className="pointer-events-none absolute inset-0 -z-10">
          <div className="absolute -left-32 top-10 h-96 w-96 rounded-full bg-primary/20 blur-3xl" />
          <div className="absolute -right-32 top-40 h-96 w-96 rounded-full bg-primary-glow/25 blur-3xl" />
        </div>

        <section className="mx-auto flex max-w-4xl flex-col items-center px-4 pb-16 pt-16 text-center sm:pt-24">
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="grid h-16 w-16 place-items-center rounded-2xl gradient-hero text-primary-foreground shadow-elegant"
          >
            <GraduationCap className="h-8 w-8" />
          </motion.div>

          <motion.h1
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.1 }}
            className="mt-6 font-display text-4xl font-bold sm:text-5xl md:text-6xl"
          >
            Attendance Portal
          </motion.h1>
          <motion.p
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="mt-4 max-w-xl text-base text-muted-foreground sm:text-lg"
          >
            Government College of Engineering Dharmapuri— check your attendance instantly. No login
            required.
          </motion.p>

          <motion.form
            onSubmit={submit}
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="glass mt-10 flex w-full max-w-xl flex-col gap-3 rounded-2xl p-3 sm:flex-row sm:items-center"
          >
            <div className="relative flex-1">
              <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <input
                value={reg}
                onChange={(e) => setReg(e.target.value)}
                placeholder="Enter Register Number"
                className="w-full rounded-xl border border-border bg-background/60 py-3 pl-11 pr-4 text-sm outline-none focus:ring-2 focus:ring-ring"
                autoFocus
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center justify-center gap-2 rounded-xl gradient-hero px-6 py-3 text-sm font-semibold text-primary-foreground shadow-elegant transition hover:scale-[1.02] disabled:opacity-70"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" /> Searching…
                </>
              ) : (
                <>Search</>
              )}
            </button>
          </motion.form>

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -6 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-4 flex items-center gap-2 rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-2 text-sm text-destructive"
            >
              <AlertCircle className="h-4 w-4" /> {error}
            </motion.div>
          )}

          <div className="mt-8 text-xs text-muted-foreground">
            {"\n"}
          </div>
        </section>

        <section className="mx-auto grid max-w-5xl gap-4 px-4 pb-16 sm:grid-cols-3 sm:px-6">
          {[
            { t: "Live tracking", d: "Attendance synced every evening from faculty portals." },
            { t: "Subject-wise view", d: "See exactly which class needs attention." },
            { t: "Download reports", d: "Export a printable PDF for reference." },
          ].map((f, i) => (
            <motion.div
              key={f.t}
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.4 + i * 0.08 }}
              className="glass rounded-2xl p-5"
            >
              <h3 className="font-display font-semibold">{f.t}</h3>
              <p className="mt-1 text-sm text-muted-foreground">{f.d}</p>
            </motion.div>
          ))}
        </section>
      </main>
      <Footer />
    </div>
  );
}
