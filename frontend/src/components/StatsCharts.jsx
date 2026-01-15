import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts'
import { Briefcase, Building2, MapPin, Tag } from 'lucide-react'

const COLORS = ['#6366f1', '#8b5cf6', '#a855f7', '#d946ef', '#ec4899', '#f43f5e']

function StatsCharts({ stats }) {
  if (!stats) {
    return <div className="loading">Loading statistics...</div>
  }

  return (
    <div className="stats-section">
      <div className="stats-grid">
        <div className="stat-card highlight">
          <Briefcase size={24} />
          <div className="stat-info">
            <span className="stat-value">{stats.total_jobs}</span>
            <span className="stat-label">Total Jobs</span>
          </div>
        </div>

        <div className="stat-card">
          <Building2 size={24} />
          <div className="stat-info">
            <span className="stat-value">{stats.by_company?.length || 0}</span>
            <span className="stat-label">Companies</span>
          </div>
        </div>

        <div className="stat-card">
          <MapPin size={24} />
          <div className="stat-info">
            <span className="stat-value">{stats.by_location?.length || 0}</span>
            <span className="stat-label">Locations</span>
          </div>
        </div>

        <div className="stat-card">
          <Tag size={24} />
          <div className="stat-info">
            <span className="stat-value">{stats.top_tags?.length || 0}</span>
            <span className="stat-label">Unique Tags</span>
          </div>
        </div>
      </div>

      <div className="charts-grid">
        {/* Jobs by Source - Pie Chart */}
        <div className="chart-card">
          <h3>Jobs by Source</h3>
          {stats.by_source?.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={stats.by_source}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ source, count, percent }) => `${source}: ${count}`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="count"
                  nameKey="source"
                >
                  {stats.by_source.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="no-data">No data available</p>
          )}
        </div>

        {/* Top Companies - Bar Chart */}
        <div className="chart-card">
          <h3>Top Companies</h3>
          {stats.by_company?.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={stats.by_company.slice(0, 8)} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis type="number" stroke="#9ca3af" />
                <YAxis
                  type="category"
                  dataKey="company"
                  width={120}
                  stroke="#9ca3af"
                  tick={{ fontSize: 12 }}
                />
                <Tooltip
                  contentStyle={{ background: '#1f2937', border: 'none', borderRadius: '8px' }}
                />
                <Bar dataKey="count" fill="#6366f1" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="no-data">No data available</p>
          )}
        </div>

        {/* Top Tags - Bar Chart */}
        <div className="chart-card wide">
          <h3>Most Requested Skills</h3>
          {stats.top_tags?.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={stats.top_tags.slice(0, 12)}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis
                  dataKey="tag"
                  stroke="#9ca3af"
                  tick={{ fontSize: 11 }}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis stroke="#9ca3af" />
                <Tooltip
                  contentStyle={{ background: '#1f2937', border: 'none', borderRadius: '8px' }}
                />
                <Bar dataKey="count" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="no-data">No data available</p>
          )}
        </div>

        {/* Top Locations - Bar Chart */}
        <div className="chart-card">
          <h3>Top Locations</h3>
          {stats.by_location?.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={stats.by_location.slice(0, 8)} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis type="number" stroke="#9ca3af" />
                <YAxis
                  type="category"
                  dataKey="location"
                  width={120}
                  stroke="#9ca3af"
                  tick={{ fontSize: 12 }}
                />
                <Tooltip
                  contentStyle={{ background: '#1f2937', border: 'none', borderRadius: '8px' }}
                />
                <Bar dataKey="count" fill="#a855f7" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="no-data">No data available</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default StatsCharts
