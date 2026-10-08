import { useEffect, useMemo, useState } from 'react'
import { ApiError } from './api/http'
import { createApplication, deleteApplication as deleteApplicationRequest, getApplications, updateApplication } from './api/applications'
import { clearAccessToken, readAccessToken, saveAccessToken } from './auth/tokenStorage'
import { AuthPage } from './components/AuthPage'
import { ApplicationForm } from './components/ApplicationForm'
import { ApplicationFilters } from './components/ApplicationFilters'
import { ApplicationList } from './components/ApplicationList'
import type { Application, ApplicationFormData } from './types/application'
import './App.css'

function App() {
  // The token is saved locally so refreshing the page keeps the user signed in.
  const [token, setToken] = useState<string | null>(() => readAccessToken())
  // The API response is the source of truth; React state holds its current UI copy.
  const [applications, setApplications] = useState<Application[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [deletingId, setDeletingId] = useState<number | null>(null)
  const [apiError, setApiError] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('All')
  const [editingApplication, setEditingApplication] = useState<Application | null>(null)
  const [isFormOpen, setIsFormOpen] = useState(false)

  // Fetch the signed-in user's data whenever authentication changes.
  useEffect(() => {
    if (!token) {
      setApplications([])
      setIsLoading(false)
      return
    }

    let cancelled = false
    setIsLoading(true)
    setApiError(null)

    getApplications()
      .then((items) => { if (!cancelled) setApplications(items) })
      .catch((error: Error) => {
        if (cancelled) return
        if (error instanceof ApiError && error.status === 401) {
          clearAccessToken()
          setToken(null)
        } else {
          setApiError(error.message)
        }
      })
      .finally(() => { if (!cancelled) setIsLoading(false) })

    return () => { cancelled = true }
  }, [token])

  function handleAuthenticated(accessToken: string) {
    saveAccessToken(accessToken)
    setToken(accessToken)
  }

  function logOut() {
    // JWT logout here means deleting the browser's copy; the token expires server-side.
    clearAccessToken()
    setToken(null)
    setApplications([])
    setApiError(null)
  }

  // Derive the visible list from saved data; filtering never removes applications.
  const visibleApplications = useMemo(() => {
    const normalizedSearch = search.trim().toLowerCase()
    return applications.filter((application) => {
      const matchesSearch =
        application.company.toLowerCase().includes(normalizedSearch) ||
        application.position.toLowerCase().includes(normalizedSearch)
      const matchesStatus = statusFilter === 'All' || application.status === statusFilter
      return matchesSearch && matchesStatus
    })
  }, [applications, search, statusFilter])

  function openNewForm() {
    setApiError(null)
    setEditingApplication(null)
    setIsFormOpen(true)
  }

  async function saveApplication(formData: ApplicationFormData) {
    setApiError(null)
    setIsSaving(true)
    try {
      if (editingApplication) {
        // Use the server's updated response so React stays aligned with backend data.
        const updated = await updateApplication(editingApplication.id, formData)
        setApplications((current) => current.map((item) => item.id === updated.id ? updated : item))
      } else {
        const created = await createApplication(formData)
        setApplications((current) => [created, ...current])
      }
      setIsFormOpen(false)
      setEditingApplication(null)
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) logOut()
      else setApiError(error instanceof Error ? error.message : 'Could not save the application.')
    } finally {
      setIsSaving(false)
    }
  }

  async function removeApplication(id: number) {
    setApiError(null)
    setDeletingId(id)
    try {
      await deleteApplicationRequest(id)
      setApplications((current) => current.filter((item) => item.id !== id))
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) logOut()
      else setApiError(error instanceof Error ? error.message : 'Could not delete the application.')
    } finally {
      setDeletingId(null)
    }
  }

  const countFor = (status: string) =>
    applications.filter((application) => application.status === status).length

  if (!token) return <AuthPage onAuthenticated={handleAuthenticated} />

  return (
    <main className="page-shell">
      <header className="page-header">
        <div>
          <p className="eyebrow">YOUR CAREER, ORGANIZED</p>
          <h1>Job Application Tracker</h1>
          <p className="page-subtitle">Keep every opportunity moving forward.</p>
        </div>
        <div className="header-actions">
          <button className="button button-secondary" onClick={logOut}>Log out</button>
          <button className="button button-primary" onClick={openNewForm}>
            <span aria-hidden="true">+</span> Add Application
          </button>
        </div>
      </header>

      <section className="summary-grid" aria-label="Application summary">
        <SummaryCard label="Total applications" value={applications.length} accent="ink" />
        <SummaryCard label="Applied" value={countFor('Applied')} accent="blue" />
        <SummaryCard label="Interviews" value={countFor('Interview')} accent="purple" />
        <SummaryCard label="Offers" value={countFor('Offer')} accent="green" />
        <SummaryCard label="Rejected" value={countFor('Rejected')} accent="rose" />
      </section>

      <section className="applications-section">
        <div className="section-heading">
          <div><h2>Your applications</h2><p>{visibleApplications.length} opportunities in view</p></div>
        </div>
        <ApplicationFilters search={search} status={statusFilter} onSearchChange={setSearch} onStatusChange={setStatusFilter} />
        {apiError && !isFormOpen && <p className="api-error" role="alert">{apiError}</p>}
        {isLoading ? (
          <p className="loading-message" role="status">Loading applications...</p>
        ) : (
          <ApplicationList
            applications={visibleApplications}
            onEdit={(application) => { setApiError(null); setEditingApplication(application); setIsFormOpen(true) }}
            onDelete={removeApplication}
            deletingId={deletingId}
          />
        )}
      </section>

      {isFormOpen && (
        <div className="modal-backdrop">
          <ApplicationForm
            application={editingApplication}
            onSave={saveApplication}
            isSaving={isSaving}
            error={apiError}
            onCancel={() => { setIsFormOpen(false); setEditingApplication(null) }}
          />
        </div>
      )}
    </main>
  )
}

function SummaryCard({ label, value, accent }: { label: string; value: number; accent: string }) {
  return <article className={`summary-card summary-${accent}`}><p>{label}</p><strong>{value}</strong></article>
}

export default App
