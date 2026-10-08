import type { ApplicationStatus } from '../types/application'

interface ApplicationFiltersProps {
  search: string
  status: string
  onSearchChange: (value: string) => void
  onStatusChange: (value: string) => void
}

export function ApplicationFilters({ search, status, onSearchChange, onStatusChange }: ApplicationFiltersProps) {
  const statuses: ApplicationStatus[] = ['Applied', 'Interview', 'Rejected', 'Offer', 'Withdrawn']

  return (
    <div className="filters">
      <label className="search-field">
        <span aria-hidden="true">⌕</span>
        <input
          type="search"
          value={search}
          onChange={(event) => onSearchChange(event.target.value)}
          placeholder="Search by company or position"
          aria-label="Search applications by company or position"
        />
      </label>
      <label>
        <span className="visually-hidden">Filter by status</span>
        <select value={status} onChange={(event) => onStatusChange(event.target.value)}>
          <option value="All">All statuses</option>
          {statuses.map((item) => <option key={item} value={item}>{item}</option>)}
        </select>
      </label>
    </div>
  )
}
