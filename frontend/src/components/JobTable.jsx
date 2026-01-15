import { Building2, MapPin, ExternalLink, Trash2, Tag } from 'lucide-react'

function JobTable({ jobs, loading, onDelete }) {
  if (loading) {
    return <div className="loading">Loading jobs...</div>
  }

  if (jobs.length === 0) {
    return (
      <div className="empty-state">
        <p>No jobs found. Start scraping to populate the database!</p>
      </div>
    )
  }

  return (
    <div className="job-table-container">
      <table className="job-table">
        <thead>
          <tr>
            <th>Job Title</th>
            <th>Company</th>
            <th>Location</th>
            <th>Tags</th>
            <th>Source</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {jobs.map((job) => (
            <tr key={job.id}>
              <td className="job-title">
                <a href={job.apply_link} target="_blank" rel="noopener noreferrer">
                  {job.job_title}
                </a>
              </td>
              <td>
                <span className="company">
                  <Building2 size={14} />
                  {job.company}
                </span>
              </td>
              <td>
                <span className="location">
                  <MapPin size={14} />
                  {job.location}
                </span>
              </td>
              <td className="tags-cell">
                {job.tags && job.tags.split(',').slice(0, 3).map((tag, i) => (
                  <span key={i} className="tag">{tag.trim()}</span>
                ))}
              </td>
              <td>
                <span className={`source-badge source-${job.source.toLowerCase().replace(/\s/g, '')}`}>
                  {job.source}
                </span>
              </td>
              <td className="actions">
                <a
                  href={job.apply_link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-sm"
                  title="Apply"
                >
                  <ExternalLink size={14} />
                </a>
                <button
                  onClick={() => onDelete(job.id)}
                  className="btn btn-sm btn-danger"
                  title="Delete"
                >
                  <Trash2 size={14} />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default JobTable
