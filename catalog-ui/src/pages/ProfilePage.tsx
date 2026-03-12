import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function ProfilePage() {
  const { user, logout, updateProfile } = useAuth()
  const navigate = useNavigate()
  const [name, setName] = useState(user?.name ?? '')
  const [saving, setSaving] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState<string | null>(null)

  if (!user) {
    navigate('/login')
    return null
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    setError(null)
    setSuccess(false)
    try {
      await updateProfile(name)
      setSuccess(true)
    } catch {
      setError('Could not update profile')
    } finally {
      setSaving(false)
    }
  }

  function handleLogout() {
    logout()
    navigate('/')
  }

  return (
    <div className="max-w-md mx-auto mt-12">
      <h1 className="text-2xl font-bold mb-6">Your Profile</h1>

      <div className="bg-white border rounded-lg p-6 mb-4">
        <p className="text-sm text-gray-500 mb-1">Email</p>
        <p className="font-medium mb-4">{user.email}</p>
        <p className="text-sm text-gray-500 mb-1">Member since</p>
        <p className="font-medium">{new Date(user.created_at).toLocaleDateString()}</p>
      </div>

      <form onSubmit={handleSave} className="bg-white border rounded-lg p-6 space-y-4">
        <h2 className="font-semibold">Update name</h2>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Full name</label>
          <input
            type="text"
            required
            value={name}
            onChange={e => setName(e.target.value)}
            className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-400"
          />
        </div>

        {success && (
          <p className="text-green-600 text-sm">Profile updated successfully.</p>
        )}
        {error && (
          <p className="text-red-600 text-sm">{error}</p>
        )}

        <button
          type="submit"
          disabled={saving}
          className="w-full py-2.5 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 disabled:opacity-50"
        >
          {saving ? 'Saving…' : 'Save changes'}
        </button>
      </form>

      <button
        onClick={handleLogout}
        className="mt-4 w-full py-2.5 border border-red-300 text-red-600 rounded-lg hover:bg-red-50"
      >
        Sign out
      </button>
    </div>
  )
}
