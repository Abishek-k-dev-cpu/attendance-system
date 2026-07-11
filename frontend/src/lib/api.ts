import axios, { isAxiosError } from "axios";
import { getApiBase } from "./api-config";
import { findStudent, type Student } from "./mockData";

export const api = axios.create({ timeout: 15000 });

interface BackendSubjectAttendance {
  subject_code: string;
  subject_name: string;
  classes_conducted: number;
  classes_attended: number;
  percentage: number;
}

interface BackendStudent {
  register_number: string;
  name: string;
  photo?: string | null;
  department: string;
  year: string;
  section: string;
  semester: string;
  last_updated?: string | null;
  subject_wise_attendance: BackendSubjectAttendance[];
}

function toUiStudent(student: BackendStudent): Student {
  return {
    registerNumber: student.register_number,
    name: student.name,
    photo: student.photo ?? undefined,
    department: student.department,
    year: student.year,
    section: student.section,
    semester: student.semester,
    lastUpdated: student.last_updated ?? new Date().toISOString(),
    subjects: student.subject_wise_attendance.map((subject) => ({
      code: subject.subject_code,
      name: subject.subject_name,
      conducted: subject.classes_conducted,
      attended: subject.classes_attended,
    })),
  };
}

export async function fetchStudent(registerNumber: string): Promise<Student> {
  const apiBase = getApiBase();

  if (apiBase) {
    try {
      const { data } = await api.get<BackendStudent>(
        `${apiBase}/student/${encodeURIComponent(registerNumber.trim())}`,
      );
      return toUiStudent(data);
    } catch (error) {
      if (isAxiosError(error) && error.response?.status === 404) {
        throw new Error("Student not found. Please verify the register number and try again.");
      }
      if (isAxiosError(error) && error.response?.data?.detail) {
        const detail = error.response.data.detail;
        throw new Error(typeof detail === "string" ? detail : "Unable to fetch student record.");
      }
      throw new Error("Unable to connect to the attendance server. Please try again.");
    }
  }

  await new Promise((r) => setTimeout(r, 900));
  const student = findStudent(registerNumber);
  if (!student) {
    throw new Error(
      "Student not found. The attendance API is not configured on this site yet. Please contact the administrator.",
    );
  }
  return student;
}
