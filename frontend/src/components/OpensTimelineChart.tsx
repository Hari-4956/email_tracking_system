import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { TimelinePoint } from '../types'
import { formatDate, formatNumber } from '../utils/format'
import { EmptyState } from './EmptyState'

interface OpensTimelineChartProps {
  data: TimelinePoint[]
}

function formatAxisDate(value: string): string {
  return formatDate(value)
}

export function OpensTimelineChart({ data }: OpensTimelineChartProps) {
  if (!data.length) {
    return (
      <EmptyState
        title="No open activity yet."
        description="Tracked opens will appear here once recipients open emails."
      />
    )
  }

  const chartHeight = data.length <= 2 ? 260 : 320

  return (
    <div className="chart-wrap" role="img" aria-label="Tracked opens over time">
      <ResponsiveContainer width="100%" height={chartHeight}>
        <LineChart data={data} margin={{ top: 12, right: 18, left: 4, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(15, 23, 42, 0.08)" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12, fill: '#64748b' }}
            tickFormatter={formatAxisDate}
            label={{ value: 'Date', position: 'insideBottom', offset: -2, fill: '#94a3b8', fontSize: 11 }}
          />
          <YAxis
            allowDecimals={false}
            tick={{ fontSize: 12, fill: '#64748b' }}
            label={{ value: 'Opens', angle: -90, position: 'insideLeft', fill: '#94a3b8', fontSize: 11 }}
            domain={[0, 'auto']}
          />
          <Tooltip
            formatter={(value) => [formatNumber(Number(value ?? 0)), 'Tracked opens']}
            labelFormatter={(label) => formatDate(String(label))}
            contentStyle={{
              borderRadius: 12,
              border: '1px solid rgba(15,23,42,0.08)',
              boxShadow: '0 10px 30px rgba(15,23,42,0.08)',
            }}
          />
          <Line
            type="monotone"
            dataKey="opens"
            name="Tracked opens"
            stroke="#0f766e"
            strokeWidth={2.75}
            dot={{ r: data.length <= 4 ? 4 : 3, fill: '#0f766e' }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
