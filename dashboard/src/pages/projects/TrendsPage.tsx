import { useParams } from 'react-router-dom';
import { useTrends } from '../../hooks/use-api';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';

export default function TrendsPage() {
  const { projectId } = useParams();
  const { data, isLoading } = useTrends(projectId!);

  if (isLoading) return <div className="p-8 text-text-muted text-sm">Loading...</div>;
  if (!data?.data.length) return <div className="p-8 text-text-muted text-sm">No data yet. Run a scan first.</div>;

  const chartData = data.data.map((d) => ({
    ...d,
    label: format(new Date(d.date), 'MMM d'),
  }));

  return (
    <div className="p-8">
      <h1 className="font-serif text-2xl mb-6">Trends</h1>

      <div className="border border-border rounded-xl p-6 mb-6">
        <h2 className="text-sm text-text-secondary font-medium mb-4">Mentions over time</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <XAxis
              dataKey="label"
              stroke="#645e50"
              fontSize={11}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              stroke="#645e50"
              fontSize={11}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip
              contentStyle={{
                background: '#18170f',
                border: '1px solid #2a2820',
                borderRadius: 8,
                fontSize: 12,
              }}
            />
            <Line
              type="monotone"
              dataKey="mention_count"
              stroke="#e8a634"
              strokeWidth={2}
              dot={false}
              name="Mentions"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="border border-border rounded-xl p-6">
        <h2 className="text-sm text-text-secondary font-medium mb-4">Sentiment trend</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <XAxis
              dataKey="label"
              stroke="#645e50"
              fontSize={11}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              stroke="#645e50"
              fontSize={11}
              tickLine={false}
              axisLine={false}
              domain={[0, 100]}
              unit="%"
            />
            <Tooltip
              contentStyle={{
                background: '#18170f',
                border: '1px solid #2a2820',
                borderRadius: 8,
                fontSize: 12,
              }}
            />
            <Line
              type="monotone"
              dataKey="sentiment_positive_pct"
              stroke="#7ec87e"
              strokeWidth={2}
              dot={false}
              name="Positive %"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
