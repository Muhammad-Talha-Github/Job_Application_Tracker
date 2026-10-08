import type { Application } from '../types/application'

// Starter examples make the dashboard useful before an API is connected.
export const mockApplications: Application[] = [
  {
    id: 1,
    company: 'Systems Limited',
    position: 'AI Engineer',
    status: 'Interview',
    application_date: '2026-10-07',
    job_url: 'https://www.systemsltd.com/careers',
    notes: 'Technical interview scheduled for next week.',
  },
  {
    id: 2,
    company: 'Careem',
    position: 'Frontend Developer',
    status: 'Applied',
    application_date: '2026-10-03',
    job_url: 'https://careers.careem.com/',
    notes: 'Applied through the company careers page.',
  },
  {
    id: 3,
    company: 'Motive',
    position: 'Software Engineer',
    status: 'Offer',
    application_date: '2026-09-26',
    job_url: 'https://gomotive.com/careers/',
    notes: 'Reviewing the offer details.',
  },
  {
    id: 4,
    company: 'Jazz',
    position: 'Product Analyst',
    status: 'Rejected',
    application_date: '2026-09-20',
    job_url: 'https://jobs.jazz.com.pk/',
    notes: '',
  },
  {
    id: 5,
    company: '10Pearls',
    position: 'React Developer',
    status: 'Applied',
    application_date: '2026-09-16',
    job_url: 'https://10pearls.com/careers/',
    notes: 'Follow up if there is no response in two weeks.',
  },
]
