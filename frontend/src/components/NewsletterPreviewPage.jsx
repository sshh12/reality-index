import React, { useState, useEffect } from 'react'
import { useParams, useSearchParams } from 'react-router-dom'
import axios from 'axios'

const NewsletterPreviewPage = () => {
  const { id } = useParams()
  const [searchParams] = useSearchParams()
  const [newsletter, setNewsletter] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchNewsletter()
  }, [id])

  const fetchNewsletter = async () => {
    try {
      // If we have an ID, fetch specific newsletter
      if (id) {
        const response = await axios.get(`/api/newsletters/${id}`)
        setNewsletter(response.data)
      }
    } catch (err) {
      setError('Newsletter not found or failed to load.')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading newsletter...</p>
        </div>
      </div>
    )
  }

  if (error || !newsletter) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md w-full mx-4">
          <div className="bg-white rounded-lg shadow-lg p-8 text-center">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Newsletter Not Found</h2>
            <p className="text-gray-600 mb-6">{error}</p>
            <a href="/" className="btn-primary inline-block">
              Back to Homepage
            </a>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="flex-1">
              <h1 className="text-2xl font-semibold text-gray-900 mb-3">Newsletter Preview</h1>
              <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
                <div className="flex items-center gap-2">
                  <span>📅</span>
                  <span>{new Date(newsletter.sent_at).toLocaleDateString('en-US', { 
                    weekday: 'long',
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                  })}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span>📧</span>
                  <span>{newsletter.subscriber_count} subscribers</span>
                </div>
                <div className="flex items-center gap-2">
                  <span>🏷️</span>
                  <span>
                    {newsletter.topics.map(topic => 
                      topic.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')
                    ).join(' + ')}
                  </span>
                </div>
              </div>
            </div>
            <a 
              href="/" 
              className="btn-secondary flex-shrink-0 whitespace-nowrap"
            >
              ← Back to Subscribe
            </a>
          </div>
        </div>
      </div>

      {/* Newsletter Content */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <div 
            className="newsletter-content p-6 sm:p-8 lg:p-12"
            dangerouslySetInnerHTML={{ __html: newsletter.content_html }}
          />
        </div>
      </div>

      {/* Add global styles for newsletter content */}
      <style dangerouslySetInnerHTML={{__html: `
        .newsletter-content {
          font-family: Georgia, 'Times New Roman', serif;
          line-height: 1.6;
          color: #333;
        }
        
        .newsletter-content h1,
        .newsletter-content h2,
        .newsletter-content h3,
        .newsletter-content h4,
        .newsletter-content h5,
        .newsletter-content h6 {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif !important;
          font-weight: 600 !important;
        }
        
        .newsletter-content h1 {
          font-size: 2rem;
          margin-bottom: 1rem;
          border-bottom: 2px solid #3b82f6;
          padding-bottom: 0.5rem;
        }
        
        .newsletter-content h2 {
          font-size: 1.5rem;
          margin-top: 2rem;
          margin-bottom: 1rem;
          border-left: 4px solid #3b82f6;
          padding-left: 1rem;
        }
        
        .newsletter-content h3 {
          font-size: 1.25rem;
          margin-top: 1.5rem;
          margin-bottom: 0.75rem;
        }
        
        .newsletter-content strong {
          font-weight: 600 !important;
          color: #1f2937 !important;
        }
        
        .newsletter-content p {
          margin-bottom: 1rem;
        }
        
        .newsletter-content ul, .newsletter-content ol {
          margin-bottom: 1rem;
          padding-left: 1.5rem;
        }
        
        .newsletter-content li {
          margin-bottom: 0.25rem;
        }
        
        .newsletter-content a {
          color: #3b82f6;
          text-decoration: none;
        }
        
        .newsletter-content a:hover {
          text-decoration: underline;
        }
        
        .newsletter-content hr {
          border: none;
          border-top: 1px solid #e5e7eb;
          margin: 2rem 0;
        }
        
        .newsletter-content blockquote {
          border-left: 4px solid #e5e7eb;
          padding-left: 1rem;
          margin: 1rem 0;
          font-style: italic;
          color: #6b7280;
        }
      `}} />
    </div>
  )
}

export default NewsletterPreviewPage