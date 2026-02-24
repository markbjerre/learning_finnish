export default function LoadingSpinner({ message = 'Loading...' }: { message?: string }) {
  return (
    <div
      className="min-h-screen flex items-center justify-center"
      style={{
        background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)',
      }}
    >
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 mb-4">
          <div className="w-12 h-12 border-4 border-slate-600 border-t-sky-500 rounded-full animate-spin"></div>
        </div>
        <p className="text-lg text-slate-300 font-medium">{message}</p>
      </div>
    </div>
  )
}
