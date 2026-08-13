import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { CampaignStats } from '../types'
import { formatNumber } from '../utils/format'
import { EmptyState } from './EmptyState'

interface StatusDistributionChartProps {
  stats: CampaignStats
}

const COLORS = {
  Pending: '#b45309',
  Sent: '#1d4ed8',
  Failed: '#b91c1c',
}

export function StatusDistributionChart({ stats }: StatusDistributionChartProps) {
  // send_status values only (not delivered_at / opened fields)
  const data = [
    { name: 'Pending', value: stats.pending },
    { name: 'Sent', value: stats.sent },
    { name: 'Failed', value: stats.failed },
  ]

  if (data.every((item) => item.value === 0)) {
    return (
      <EmptyState
        title="No send-status data yet"
        description="PENDING / SENT / FAILED counts appear from PostgreSQL send_status."
      />
    )
  }

  return (
    <div className="chart-wrap" role="img" aria-label="Send status distribution">
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={data} margin={{ top: 12, right: 16, left: 4, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(15, 23, 42, 0.08)" />
          <XAxis dataKey="name" tick={{ fontSize: 12, fill: '#64748b' }} />
          <YAxis allowDecimals={false} tick={{ fontSize: 12, fill: '#64748b' }} />
          <Tooltip
            formatter={(value) => [formatNumber(Number(value ?? 0)), 'Recipients']}
            contentStyle={{
              borderRadius: 12,
              border: '1px solid rgba(15,23,42,0.08)',
            }}
          />
          <Legend />
          <Bar dataKey="value" name="Recipients" radius={[8, 8, 0, 0]}>
            {data.map((entry) => (
              <Cell key={entry.name} fill={COLORS[entry.name as keyof typeof COLORS]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
