// Keep the property names aligned with the FastAPI JSON response.
// These values mirror the enum in backend/app/schemas/application.py.
export type ApplicationStatus = 'Applied' | 'Interview' | 'Rejected' | 'Offer' | 'Withdrawn'

export interface Application {
  id: number
  company: string
  position: string
  status: ApplicationStatus
  application_date: string
  // The backend allows either optional field to be null in its JSON response.
  job_url: string | null
  notes: string | null
}

// Form controls use strings; the API utility converts blank optional fields to null.
export interface ApplicationFormData {
  company: string
  position: string
  status: ApplicationStatus
  application_date: string
  job_url: string
  notes: string
}
