import { useState, type FormEvent } from 'react'
import { loginUser, registerUser } from '../api/auth'

interface AuthPageProps {
  onAuthenticated: (token: string) => void
}

export function AuthPage({ onAuthenticated }: AuthPageProps) {
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      if (mode === 'register') await registerUser(email, password)
      // Registration is followed by login so the user lands in their dashboard.
      const result = await loginUser(email, password)
      onAuthenticated(result.access_token)
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Could not sign in.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="auth-shell">
      <section className="auth-card">
        <p className="eyebrow">YOUR CAREER, ORGANIZED</p>
        <h1>{mode === 'login' ? 'Welcome back' : 'Create your account'}</h1>
        <p className="auth-subtitle">
          {mode === 'login' ? 'Sign in to view your applications.' : 'Start tracking your job search.'}
        </p>
        <form className="auth-form" onSubmit={handleSubmit}>
          <label className="form-field">
            <span>Email</span>
            <input
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@example.com"
            />
          </label>
          <label className="form-field">
            <span>Password{mode === 'register' && ' (at least 12 characters)'}</span>
            <input
              type="password"
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              minLength={mode === 'register' ? 12 : undefined}
              maxLength={128}
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </label>
          {error && <p className="api-error" role="alert">{error}</p>}
          <button className="button button-primary auth-submit" type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Please wait...' : mode === 'login' ? 'Sign in' : 'Create account'}
          </button>
        </form>
        <p className="auth-switch">
          {mode === 'login' ? 'New to the tracker?' : 'Already have an account?'}{' '}
          <button type="button" onClick={() => { setError(null); setMode(mode === 'login' ? 'register' : 'login') }}>
            {mode === 'login' ? 'Create an account' : 'Sign in'}
          </button>
        </p>
      </section>
    </main>
  )
}
