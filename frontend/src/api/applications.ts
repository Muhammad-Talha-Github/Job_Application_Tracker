import { apiRequest } from './http'
import type { Application, ApplicationFormData } from '../types/application'

function toRequestBody(data: ApplicationFormData) {
  // FastAPI allows these optional values to be null; blank form fields become null.
  return { ...data, job_url: data.job_url.trim() || null, notes: data.notes.trim() || null }
}

export function getApplications(): Promise<Application[]> {
  return apiRequest<Application[]>('/applications')
}

export function createApplication(data: ApplicationFormData): Promise<Application> {
  return apiRequest<Application>('/applications', { method: 'POST', body: JSON.stringify(toRequestBody(data)) })
}

export function updateApplication(id: number, data: ApplicationFormData): Promise<Application> {
  return apiRequest<Application>(`/applications/${id}`, { method: 'PUT', body: JSON.stringify(toRequestBody(data)) })
}

export function deleteApplication(id: number): Promise<void> {
  return apiRequest<void>(`/applications/${id}`, { method: 'DELETE' })
}
