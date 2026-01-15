import { useState, useEffect } from 'react'
import { Play, Loader2, CheckCircle, XCircle, Clock } from 'lucide-react'

function ScrapePanel({ sites, apiUrl, onScrapeComplete }) {
  const [selectedSites, setSelectedSites] = useState(['remoteok'])
  const [keyword, setKeyword] = useState('')
  const [location, setLocation] = useState('')
  const [scraping, setScraping] = useState(false)
  const [logs, setLogs] = useState([])
  const [message, setMessage] = useState(null)

  const fetchLogs = async () => {
    try {
      const res = await fetch(`${apiUrl}/api/scrape/logs`)
      const data = await res.json()
      setLogs(data.logs)
    } catch (error) {
      console.error('Error fetching logs:', error)
    }
  }

  useEffect(() => {
    fetchLogs()
    const interval = setInterval(fetchLogs, 5000)
    return () => clearInterval(interval)
  }, [])

  const toggleSite = (siteId) => {
    setSelectedSites(prev =>
      prev.includes(siteId)
        ? prev.filter(s => s !== siteId)
        : [...prev, siteId]
    )
  }

  const startScrape = async () => {
    if (selectedSites.length === 0) {
      setMessage({ type: 'error', text: 'Select at least one site' })
      return
    }

    setScraping(true)
    setMessage(null)

    try {
      const params = new URLSearchParams({
        sites: selectedSites.join(','),
        keyword,
        location
      })

      const res = await fetch(`${apiUrl}/api/scrape?${params}`, {
        method: 'POST'
      })

      if (res.ok) {
        setMessage({ type: 'success', text: 'Scraping started! Check logs below.' })
        fetchLogs()
        // Poll for completion
        setTimeout(() => {
          fetchLogs()
          onScrapeComplete()
        }, 5000)
      } else {
        const error = await res.json()
        setMessage({ type: 'error', text: error.detail || 'Scraping failed' })
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Connection error' })
    }

    setScraping(false)
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle size={16} className="text-green" />
      case 'failed':
        return <XCircle size={16} className="text-red" />
      case 'running':
        return <Loader2 size={16} className="spinning" />
      default:
        return <Clock size={16} className="text-yellow" />
    }
  }

  return (
    <div className="scrape-section">
      <div className="scrape-form">
        <h3>Start New Scrape</h3>

        <div className="form-group">
          <label>Select Sites</label>
          <div className="site-toggles">
            {sites.map(site => (
              <button
                key={site.id}
                className={`site-toggle ${selectedSites.includes(site.id) ? 'active' : ''}`}
                onClick={() => toggleSite(site.id)}
                disabled={site.requires_auth}
                title={site.requires_auth ? 'Requires authentication (configure in .env)' : ''}
              >
                {site.name}
                {site.requires_auth && <span className="auth-badge">Auth</span>}
              </button>
            ))}
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Keyword</label>
            <input
              type="text"
              placeholder="e.g., python, react, data engineer"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label>Location</label>
            <input
              type="text"
              placeholder="e.g., Madrid, Remote"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
            />
          </div>
        </div>

        {message && (
          <div className={`message ${message.type}`}>
            {message.text}
          </div>
        )}

        <button
          onClick={startScrape}
          disabled={scraping || selectedSites.length === 0}
          className="btn btn-primary btn-lg"
        >
          {scraping ? (
            <>
              <Loader2 size={18} className="spinning" />
              Scraping...
            </>
          ) : (
            <>
              <Play size={18} />
              Start Scraping
            </>
          )}
        </button>
      </div>

      <div className="scrape-logs">
        <h3>Recent Scrape Logs</h3>
        {logs.length === 0 ? (
          <p className="no-data">No scrape logs yet</p>
        ) : (
          <table className="logs-table">
            <thead>
              <tr>
                <th>Status</th>
                <th>Sites</th>
                <th>Keyword</th>
                <th>Jobs Found</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody>
              {logs.map(log => (
                <tr key={log.id}>
                  <td>{getStatusIcon(log.status)}</td>
                  <td>{log.sites}</td>
                  <td>{log.keyword || '-'}</td>
                  <td>{log.jobs_found}</td>
                  <td>{new Date(log.started_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

export default ScrapePanel
