export default function StatsCard({ title, value, icon, color }) {
  const colorClasses = {
    primary: 'bg-stone-100 text-stone-700',
    secondary: 'bg-stone-50 text-stone-600',
    accent: 'bg-amber-50 text-amber-700',
    green: 'bg-emerald-50 text-emerald-700',
  }

  return (
    <div className="bg-white rounded-lg border border-stone-100 p-6 hover:border-stone-300 transition-all duration-200">
      <div className="flex items-center">
        <div className={`flex-shrink-0 p-3 rounded-md ${colorClasses[color]}`}>
          {icon}
        </div>
        <div className="ml-5 w-0 flex-1">
          <dl>
            <dt className="text-sm font-medium text-stone-400 truncate uppercase tracking-wider">{title}</dt>
            <dd className="text-2xl font-light text-stone-800 mt-1">{value}</dd>
          </dl>
        </div>
      </div>
    </div>
  )
}
