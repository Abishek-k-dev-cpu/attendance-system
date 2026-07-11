declare global {
  interface Window {
    __ATTENDANCE_API_BASE__?: string;
  }
}

export function getApiBase(): string {
  if (typeof window !== "undefined" && window.__ATTENDANCE_API_BASE__) {
    return window.__ATTENDANCE_API_BASE__.replace(/\/$/, "");
  }

  return (import.meta.env.VITE_API_BASE ?? "").replace(/\/$/, "");
}
