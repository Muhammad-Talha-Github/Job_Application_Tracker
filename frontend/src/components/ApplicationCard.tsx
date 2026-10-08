import type { Application } from '../types/application'

interface ApplicationCardProps {
  application: Application
  onEdit: (application: Application) => void
  onDelete: (id: number) => void
  isDeleting: boolean
}

export function ApplicationCard({ application, onEdit, onDelete, isDeleting }: ApplicationCardProps) {
  const initials = application.company.slice(0, 1).toUpperCase()
  const formattedDate = new Date(`${application.application_date}T00:00:00`).toLocaleDateString('en', {
    year: 'numeric', month: 'short', day: 'numeric',
  })

  return (
    <article className="application-card">
      <div className="application-main">
        <div className="company-mark" aria-hidden="true">{initials}</div>
        <div className="application-copy">
          <h3>{application.company}</h3>
          <p>{application.position}</p>
          <div className="application-meta">
            <span>Applied {formattedDate}</span>
            {application.job_url && <><span aria-hidden="true">·</span><a href={application.job_url} target="_blank" rel="noreferrer">Job posting ↗</a></>}
          </div>
        </div>
      </div>
      <div className="application-actions">
        <span className={`status-badge status-${application.status.toLowerCase()}`}>{application.status}</span>
        <div>
          <button className="icon-button" disabled={isDeleting} onClick={() => onEdit(application)} aria-label={`Edit ${application.company} application`}>Edit</button>
          <button className="icon-button danger" disabled={isDeleting} onClick={() => onDelete(application.id)} aria-label={`Delete ${application.company} application`}>
            {isDeleting ? 'Deleting...' : 'Delete'}
          </button>
        </div>
      </div>
    </article>
  )
}
