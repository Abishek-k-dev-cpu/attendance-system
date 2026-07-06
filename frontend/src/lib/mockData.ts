export interface Subject {
  code: string;
  name: string;
  conducted: number;
  attended: number;
}

export interface Student {
  registerNumber: string;
  name: string;
  photo?: string;
  department: string;
  year: string;
  section: string;
  semester: string;
  lastUpdated: string;
  subjects: Subject[];
}

const SUBJECT_SETS: Record<string, Subject[]> = {
  cse: [
    { code: "CS3401", name: "Algorithms", conducted: 45, attended: 42 },
    { code: "CS3451", name: "Operating Systems", conducted: 42, attended: 35 },
    { code: "CS3491", name: "Artificial Intelligence & ML", conducted: 48, attended: 44 },
    { code: "CS3492", name: "Database Management Systems", conducted: 44, attended: 30 },
    { code: "CS3452", name: "Theory of Computation", conducted: 40, attended: 28 },
    { code: "GE3451", name: "Environmental Sciences", conducted: 30, attended: 27 },
  ],
  ece: [
    { code: "EC3401", name: "Networks and Security", conducted: 44, attended: 40 },
    { code: "EC3451", name: "Linear Integrated Circuits", conducted: 42, attended: 38 },
    { code: "EC3491", name: "Communication Systems", conducted: 46, attended: 32 },
    { code: "EC3492", name: "Digital Signal Processing", conducted: 40, attended: 36 },
    { code: "EC3452", name: "Electromagnetic Fields", conducted: 38, attended: 25 },
  ],
};

const STUDENTS: Record<string, Student> = {
  "21CS001": {
    registerNumber: "21CS001",
    name: "Aarav Sharma",
    department: "Computer Science & Engineering",
    year: "III",
    section: "A",
    semester: "6",
    lastUpdated: new Date().toISOString(),
    subjects: SUBJECT_SETS.cse,
  },
  "21CS042": {
    registerNumber: "21CS042",
    name: "Priya Nair",
    department: "Computer Science & Engineering",
    year: "III",
    section: "B",
    semester: "6",
    lastUpdated: new Date().toISOString(),
    subjects: SUBJECT_SETS.cse.map((s) => ({ ...s, attended: Math.max(20, s.attended - 5) })),
  },
  "22EC017": {
    registerNumber: "22EC017",
    name: "Rohan Verma",
    department: "Electronics & Communication",
    year: "II",
    section: "A",
    semester: "4",
    lastUpdated: new Date().toISOString(),
    subjects: SUBJECT_SETS.ece,
  },
};

export function findStudent(reg: string): Student | null {
  const key = reg.trim().toUpperCase();
  return STUDENTS[key] ?? null;
}

export const SAMPLE_REGISTERS = Object.keys(STUDENTS);
