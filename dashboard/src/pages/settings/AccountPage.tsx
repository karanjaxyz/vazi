import { useAuthStore } from '../../stores/auth';

export default function AccountPage() {
  const { user } = useAuthStore();

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="font-serif text-3xl mb-8">Account</h1>

      <div className="border border-border rounded-xl p-6 mb-6">
        <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wide mb-4">Profile</h2>
        <div className="space-y-3">
          <div>
            <span className="text-xs text-text-muted">Email</span>
            <p className="text-sm">{user?.email}</p>
          </div>
          <div>
            <span className="text-xs text-text-muted">User ID</span>
            <p className="text-sm font-mono text-text-secondary">{user?.uid}</p>
          </div>
        </div>
      </div>

      <div className="border border-border rounded-xl p-6">
        <h2 className="text-sm font-semibold text-text-secondary uppercase tracking-wide mb-4">Billing</h2>
        <p className="text-sm text-text-muted mb-4">Manage your subscription and payment method.</p>
        <a
          href="/settings/billing"
          className="inline-flex px-4 py-2.5 border border-border rounded-lg text-sm text-text-secondary hover:border-border-light hover:text-text transition-all"
        >
          Manage billing
        </a>
      </div>
    </div>
  );
}
