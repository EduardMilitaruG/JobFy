import { useState, useEffect } from 'react'
import { Search, RefreshCw, Briefcase, Trash2 } from 'lucide-react'
import JobTable from './components/JobTable'
import StatsCharts from './components/StatsCharts'
import ScrapePanel from './components/ScrapePanel'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [jobs, setJobs] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [sourceFilter, setSourceFilter] = useState('')
  const [sites, setSites] = useState([])
  const [activeTab, setActiveTab] = useState('jobs')

  const fetchJobs = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (search) params.append('search', search)
      if (sourceFilter) params.append('source', sourceFilter)
      params.append('limit', '200')

      const res = await fetch(`${API_URL}/api/jobs?${params}`)
      const data = await res.json()
      setJobs(data.jobs)
    } catch (error) {
      console.error('Error fetching jobs:', error)
    }
    setLoading(false)
  }

  const fetchStats = async () => {
    try {
      const res = await fetch(`${API_URL}/api/stats`)
      const data = await res.json()
      setStats(data)
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  const fetchSites = async () => {
    try {
      const res = await fetch(`${API_URL}/api/sites`)
      const data = await res.json()
      setSites(data.sites)
    } catch (error) {
      console.error('Error fetching sites:', error)
    }
  }

  const deleteJob = async (id) => {
    try {
      await fetch(`${API_URL}/api/jobs/${id}`, { method: 'DELETE' })
      setJobs(jobs.filter(j => j.id !== id))
    } catch (error) {
      console.error('Error deleting job:', error)
    }
  }

  const clearAllJobs = async () => {
    if (!confirm('Are you sure you want to delete all jobs?')) return
    try {
      await fetch(`${API_URL}/api/jobs`, { method: 'DELETE' })
      setJobs([])
      fetchStats()
    } catch (error) {
      console.error('Error clearing jobs:', error)
    }
  }

  useEffect(() => {
    fetchJobs()
    fetchStats()
    fetchSites()
  }, [])

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchJobs()
    }, 300)
    return () => clearTimeout(timer)
  }, [search, sourceFilter])

  const refreshAll = () => {
    fetchJobs()
    fetchStats()
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <Briefcase size={28} />
            <h1>JobFy</h1>
          </div>
          <p className="tagline">Job Scraper Dashboard</p>
        </div>
      </header>

      <main className="main">
        <div className="tabs">
          <button
            className={`tab ${activeTab === 'jobs' ? 'active' : ''}`}
            onClick={() => setActiveTab('jobs')}
          >
            Jobs ({jobs.length})
          </button>
          <button
            className={`tab ${activeTab === 'stats' ? 'active' : ''}`}
            onClick={() => setActiveTab('stats')}
          >
            Statistics
          </button>
          <button
            className={`tab ${activeTab === 'scrape' ? 'active' : ''}`}
            onClick={() => setActiveTab('scrape')}
          >
            Scrape
          </button>
        </div>

        {activeTab === 'jobs' && (
          <div className="jobs-section">
            <div className="controls">
              <div className="search-box">
                <Search size={18} />
                <input
                  type="text"
                  placeholder="Search jobs, companies, skills..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
              </div>

              <select
                value={sourceFilter}
                onChange={(e) => setSourceFilter(e.target.value)}
                className="source-filter"
              >
                <option value="">All Sources</option>
                {stats?.by_source?.map(({ source }) => (
                  <option key={source} value={source}>{source}</option>
                ))}
              </select>

              <button onClick={refreshAll} className="btn btn-icon" title="Refresh">
                <RefreshCw size={18} />
              </button>

              <button onClick={clearAllJobs} className="btn btn-danger" title="Clear all">
                <Trash2 size={18} />
              </button>
            </div>

            <JobTable jobs={jobs} loading={loading} onDelete={deleteJob} />
          </div>
        )}

        {activeTab === 'stats' && (
          <StatsCharts stats={stats} />
        )}

        {activeTab === 'scrape' && (
          <ScrapePanel
            sites={sites}
            apiUrl={API_URL}
            onScrapeComplete={refreshAll}
          />
        )}
      </main>

      <footer className="footer">
        <p>JobFy - Multi-site Job Scraper</p>
      </footer>
    </div>
  )
}

export default App
