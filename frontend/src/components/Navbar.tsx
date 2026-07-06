import { Link } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { GraduationCap, Moon, Sun } from "lucide-react";
import { useTheme } from "@/hooks/useTheme";

export function Navbar() {
  const { theme, toggle } = useTheme();
  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.4 }}
      className="sticky top-0 z-40 glass"
    >
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
        <Link to="/" className="flex min-w-0 items-center gap-3">
          <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl gradient-hero text-primary-foreground shadow-elegant">
            <GraduationCap className="h-5 w-5" />
          </div>
          <div className="min-w-0">
            <p className="truncate font-display text-sm font-bold sm:text-base">
              Government college of Engineering Dharmapuri
            </p>
            <p className="truncate text-[11px] text-muted-foreground">Attendance Portal</p>
          </div>
        </Link>
        <button
          onClick={toggle}
          aria-label="Toggle theme"
          className="grid h-10 w-10 shrink-0 place-items-center rounded-xl border border-border bg-card/60 text-foreground transition hover:bg-accent"
        >
          {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </button>
      </div>
    </motion.header>
  );
}
