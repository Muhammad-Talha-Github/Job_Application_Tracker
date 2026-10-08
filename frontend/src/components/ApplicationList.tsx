import type { Application } from '../types/application'
import { ApplicationCard } from './ApplicationCard'

interface ApplicationListProps {
  applications: Application[]
  onEdit: (application: Application) => void
  onDelete: (id: number) => void
  deletingId: number | null
}

export function ApplicationList({ applications, onEdit, onDelete, deletingId }: ApplicationListProps) {
  if (applications.length === 0) {
    return <div className="empty-state"><strong>No applications found</strong><span>Try another search or add an application.</span></div>
  }

  return (
    <div className="application-list">
      {applications.map((application) => (
        <ApplicationCard key={application.id} application={application} onEdit={onEdit} onDelete={onDelete} isDeleting={deletingId === application.id} />
      ))}
    </div>
  )
}
