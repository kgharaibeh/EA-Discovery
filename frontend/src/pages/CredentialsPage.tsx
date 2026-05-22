import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../api/client';
import type { Credential, CredentialCreate } from '../api/types';

export default function CredentialsPage() {
  const [showForm, setShowForm] = useState(false);
  const queryClient = useQueryClient();

  const { data: credentials = [], isLoading } = useQuery({
    queryKey: ['credentials'],
    queryFn: async () => {
      const { data } = await api.get<Credential[]>('/credentials');
      return data;
    },
  });

  const createMutation = useMutation({
    mutationFn: (cred: CredentialCreate) => api.post('/credentials', cred),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['credentials'] });
      setShowForm(false);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/credentials/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['credentials'] });
    },
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Credentials</h1>
        <button
          onClick={() => setShowForm(true)}
          className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700"
        >
          Add Credential
        </button>
      </div>

      {showForm && (
        <CredentialForm
          onSubmit={(cred) => createMutation.mutate(cred)}
          onCancel={() => setShowForm(false)}
          isSubmitting={createMutation.isPending}
        />
      )}

      {isLoading ? (
        <div className="text-center py-8 text-gray-500">Loading credentials...</div>
      ) : (
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Username</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {credentials.map((cred) => (
                <tr key={cred.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">{cred.name}</td>
                  <td className="px-6 py-4 text-sm text-gray-500 capitalize">{cred.credential_type}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{cred.username || '—'}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(cred.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button
                      onClick={() => deleteMutation.mutate(cred.id)}
                      className="text-sm text-red-600 hover:text-red-800"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
              {credentials.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-gray-500">
                    No credentials configured
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function CredentialForm({
  onSubmit,
  onCancel,
  isSubmitting,
}: {
  onSubmit: (cred: CredentialCreate) => void;
  onCancel: () => void;
  isSubmitting: boolean;
}) {
  const [form, setForm] = useState<CredentialCreate>({
    name: '',
    credential_type: 'ssh_password',
    username: '',
    password: '',
    description: '',
  });

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold mb-4">Add Credential</h2>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
          <input
            type="text"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            className="w-full border rounded-lg px-3 py-2 text-sm focus:ring-1 focus:ring-blue-500 focus:outline-none"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
          <select
            value={form.credential_type}
            onChange={(e) => setForm({ ...form, credential_type: e.target.value })}
            className="w-full border rounded-lg px-3 py-2 text-sm focus:ring-1 focus:ring-blue-500 focus:outline-none"
          >
            <option value="ssh_password">SSH Password</option>
            <option value="ssh_key">SSH Key</option>
            <option value="winrm">WinRM</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
          <input
            type="text"
            value={form.username}
            onChange={(e) => setForm({ ...form, username: e.target.value })}
            className="w-full border rounded-lg px-3 py-2 text-sm focus:ring-1 focus:ring-blue-500 focus:outline-none"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {form.credential_type === 'ssh_key' ? 'SSH Key' : 'Password'}
          </label>
          {form.credential_type === 'ssh_key' ? (
            <textarea
              value={form.ssh_key || ''}
              onChange={(e) => setForm({ ...form, ssh_key: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 text-sm focus:ring-1 focus:ring-blue-500 focus:outline-none"
              rows={3}
              placeholder="Paste SSH private key..."
            />
          ) : (
            <input
              type="password"
              value={form.password || ''}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 text-sm focus:ring-1 focus:ring-blue-500 focus:outline-none"
            />
          )}
        </div>
        <div className="col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <input
            type="text"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            className="w-full border rounded-lg px-3 py-2 text-sm focus:ring-1 focus:ring-blue-500 focus:outline-none"
          />
        </div>
      </div>
      <div className="flex gap-2 mt-4">
        <button
          onClick={() => onSubmit(form)}
          disabled={!form.name || isSubmitting}
          className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {isSubmitting ? 'Saving...' : 'Save'}
        </button>
        <button
          onClick={onCancel}
          className="px-4 py-2 border text-sm font-medium rounded-lg hover:bg-gray-50"
        >
          Cancel
        </button>
      </div>
    </div>
  );
}
