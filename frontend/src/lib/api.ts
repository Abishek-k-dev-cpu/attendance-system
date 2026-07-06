import axios from "axios";
import { findStudent, type Student } from "./mockData";

// In production, point this to your REST API base URL.
const API_BASE = import.meta.env.VITE_API_BASE ?? "";

export const api = axios.create({ baseURL: API_BASE, timeout: 8000 });

export async function fetchStudent(registerNumber: string): Promise<Student> {
  // If API is configured, use it. Otherwise fall back to mock data.
  if (API_BASE) {
    const { data } = await api.get<Student>(`/students/${encodeURIComponent(registerNumber)}`);
    return data;
  }
  await new Promise((r) => setTimeout(r, 900));
  const student = findStudent(registerNumber);
  if (!student) {
    throw new Error("Student not found. Please verify the register number and try again.");
  }
  return student;
}
