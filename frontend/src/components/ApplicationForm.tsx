import { useState, type FormEvent, type ReactNode } from "react";
import type {
  Application,
  ApplicationFormData,
  ApplicationStatus,
} from "../types/application";

interface ApplicationFormProps {
  application: Application | null;
  onSave: (data: ApplicationFormData) => Promise<void> | void;
  onCancel: () => void;
  isSaving: boolean;
  error: string | null;
}

const statuses: ApplicationStatus[] = [
  "Applied",
  "Interview",
  "Rejected",
  "Offer",
  "Withdrawn",
];

export function ApplicationForm({
  application,
  onSave,
  onCancel,
  isSaving,
  error,
}: ApplicationFormProps) {
  // The form uses local state while the user is typing; the parent saves on submit.
  const [form, setForm] = useState<ApplicationFormData>({
    company: application?.company ?? "",
    position: application?.position ?? "",
    status: application?.status ?? "Applied",
    application_date:
      application?.application_date ?? new Date().toISOString().slice(0, 10),
    job_url: application?.job_url ?? "",
    notes: application?.notes ?? "",
  });

  function updateField<K extends keyof ApplicationFormData>(
    field: K,
    value: ApplicationFormData[K],
  ) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSave(form);
  }

  return (
    <form className="application-form" onSubmit={handleSubmit}>
      <div className="form-heading">
        <div>
          <h2>{application ? "Edit application" : "Add an application"}</h2>
          <p>Keep the details together for your next follow-up.</p>
        </div>
        <button
          type="button"
          className="close-button"
          onClick={onCancel}
          aria-label="Close form"
        >
          ×
        </button>
      </div>
      <div className="form-grid">
        <Field label="Company">
          <input
            required
            value={form.company}
            onChange={(event) => updateField("company", event.target.value)}
            placeholder="e.g. Systems Limited"
          />
        </Field>
        <Field label="Position">
          <input
            required
            value={form.position}
            onChange={(event) => updateField("position", event.target.value)}
            placeholder="e.g. Software Engineer"
          />
        </Field>
        <Field label="Status">
          <select
            value={form.status}
            onChange={(event) =>
              updateField("status", event.target.value as ApplicationStatus)
            }
          >
            {statuses.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Application date">
          <input
            required
            type="date"
            value={form.application_date}
            onChange={(event) =>
              updateField("application_date", event.target.value)
            }
          />
        </Field>
        <Field label="Job URL" fullWidth>
          <input
            type="url"
            value={form.job_url}
            onChange={(event) => updateField("job_url", event.target.value)}
            placeholder="https://example.com/jobs/123"
          />
        </Field>
        <Field label="Notes" fullWidth>
          <textarea
            value={form.notes}
            onChange={(event) => updateField("notes", event.target.value)}
            placeholder="Interview details, reminders, or follow-up notes..."
          />
        </Field>
      </div>
      {error && <p className="api-error" role="alert">{error}</p>}
      <div className="form-actions">
        <button
          type="button"
          className="button button-secondary"
          onClick={onCancel}
        >
          Cancel
        </button>
        <button type="submit" className="button button-primary" disabled={isSaving}>
          {isSaving ? "Saving..." : application ? "Save changes" : "Add application"}
        </button>
      </div>
    </form>
  );
}

function Field({
  label,
  fullWidth = false,
  children,
}: {
  label: string;
  fullWidth?: boolean;
  children: ReactNode;
}) {
  return (
    <label className={`form-field${fullWidth ? " full-width" : ""}`}>
      <span>{label}</span>
      {children}
    </label>
  );
}
