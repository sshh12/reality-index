import React, { useState, useEffect } from 'react'
import axios from 'axios'

const HomePage = () => {
  const [email, setEmail] = useState('')
  const [selectedTopics, setSelectedTopics] = useState(['tech', 'ai'])
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')
  const [pastNewsletters, setPastNewsletters] = useState([])
  const [loadingNewsletters, setLoadingNewsletters] = useState(false)
  const [topics, setTopics] = useState([])
  const [loadingTopics, setLoadingTopics] = useState(true)

  // Load topics from API
  useEffect(() => {
    const fetchTopics = async () => {
      try {
        const response = await axios.get('/api/topics')
        const topicData = response.data.topics.map(key => ({
          id: key,
          label: response.data.display_names[key] || key,
          description: response.data.descriptions[key] || ''
        }))
        setTopics(topicData)
      } catch (error) {
        console.error('Failed to load topics:', error)
        // Fallback topics if API fails
        setTopics([
          { id: 'tech', label: 'Tech', description: 'Technology developments and trends' },
          { id: 'ai', label: 'AI', description: 'Artificial intelligence advances' }
        ])
      } finally {
        setLoadingTopics(false)
      }
    }
    
    fetchTopics()
  }, [])

  // Fetch past newsletters when topics change
  useEffect(() => {
    if (selectedTopics.length > 0) {
      fetchPastNewsletters()
    } else {
      setPastNewsletters([])
    }
  }, [selectedTopics])

  const fetchPastNewsletters = async () => {
    if (selectedTopics.length === 0) return

    setLoadingNewsletters(true)
    try {
      const topicsParam = selectedTopics.sort().join(',')
      const response = await axios.get(`/api/newsletters/preview?topics=${topicsParam}&limit=3`)
      setPastNewsletters(response.data.newsletters)
    } catch (err) {
      console.error('Failed to fetch past newsletters:', err)
      setPastNewsletters([])
    } finally {
      setLoadingNewsletters(false)
    }
  }

  const handleTopicChange = (topicId) => {
    setSelectedTopics(prev => 
      prev.includes(topicId) 
        ? prev.filter(id => id !== topicId)
        : [...prev, topicId]
    )
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!email || selectedTopics.length === 0) {
      setError('Please enter your email and select at least one topic.')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await axios.post('/api/subscribe', {
        email,
        topics: selectedTopics
      })

      setSuccess(true)
      setEmail('')
      setSelectedTopics([])
    } catch (err) {
      setError(err.response?.data?.detail || 'Subscription failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="max-w-md w-full mx-4">
          <div className="bg-white rounded-lg shadow-lg p-8 text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Welcome aboard!</h2>
            <p className="text-gray-600 mb-6">
              You've successfully subscribed to The Reality Index. You'll receive your first newsletter soon.
            </p>
            <button 
              onClick={() => setSuccess(false)}
              className="btn-secondary"
            >
              Subscribe Another Email
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="pt-16 pb-8">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-4">
            The Reality Index
          </h1>
          <div className="max-w-3xl mx-auto">
            <p className="text-xl md:text-2xl text-gray-600 mb-6">
              AI-Generated Prediction Market Newsletter
            </p>
            <div className="text-left space-y-3 text-gray-600">
              <div className="flex items-start">
                <span className="text-lg mr-3">💰</span>
                <p className="text-base">
                  <strong>Money talks louder than headlines</strong> – prediction markets reflect what people actually believe will happen, not just what they say
                </p>
              </div>
              <div className="flex items-start">
                <span className="text-lg mr-3">🎯</span>
                <p className="text-base">
                  <strong>Spot underreported stories</strong> before mainstream media catches on, and identify when popular narratives are overblown
                </p>
              </div>
              <div className="flex items-start">
                <span className="text-lg mr-3">🤖</span>
                <p className="text-base">
                  <strong>AI processes thousands of markets</strong> to find the most significant signals humans might miss in the noise
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-2xl mx-auto px-4 pb-16">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            Subscribe to Weekly Insights
          </h2>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email Input */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                className="input-field"
                required
              />
            </div>

            {/* Topic Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Choose Your Topics
              </label>
              <div className="space-y-3">
                {topics.map((topic) => (
                  <div key={topic.id} className="flex items-start">
                    <input
                      type="checkbox"
                      id={topic.id}
                      checked={selectedTopics.includes(topic.id)}
                      onChange={() => handleTopicChange(topic.id)}
                      className="checkbox-field mt-1"
                    />
                    <div className="ml-3">
                      <label htmlFor={topic.id} className="text-sm font-medium text-gray-900 cursor-pointer">
                        {topic.label}
                      </label>
                      <p className="text-sm text-gray-500">{topic.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Past Newsletters Preview */}
            {selectedTopics.length > 0 && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-blue-900 mb-3">
                  📧 Recent newsletters for {selectedTopics.map(topicId => {
                    const topic = topics.find(t => t.id === topicId)
                    return topic ? topic.label : topicId
                  }).join(' + ')}:
                </h4>
                
                {loadingNewsletters ? (
                  <div className="flex items-center justify-center py-4">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                    <span className="ml-2 text-sm text-blue-700">Loading past newsletters...</span>
                  </div>
                ) : pastNewsletters.length > 0 ? (
                  <div className="space-y-3">
                    {pastNewsletters.map((newsletter, index) => (
                      <div key={newsletter.id} className="bg-white rounded-md p-3 border border-blue-100">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h5 className="text-sm font-medium text-gray-900 mb-1">
                              {newsletter.title}
                            </h5>
                            <div className="flex items-center text-xs text-gray-500 space-x-3">
                              <span>
                                📅 {new Date(newsletter.sent_at).toLocaleDateString('en-US', { 
                                  month: 'short', 
                                  day: 'numeric', 
                                  year: 'numeric' 
                                })}
                              </span>
                              <span>
                                📧 {newsletter.subscriber_count} subscribers
                              </span>
                            </div>
                          </div>
                          <a
                            href={`/newsletter/${newsletter.id}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                          >
                            Preview ↗
                          </a>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-4">
                    <div className="text-3xl mb-2">📮</div>
                    <p className="text-sm text-blue-700">
                      No newsletters have been sent for this topic combination yet.
                    </p>
                    <p className="text-xs text-blue-600 mt-1">
                      Be among the first subscribers when we publish!
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Subscribing...' : 'Subscribe to Newsletter'}
            </button>
          </form>

          {/* Newsletter Info */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
              What you'll get:
            </h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-center">
                <svg className="w-4 h-4 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Weekly analysis powered by AI and prediction market data
              </li>
              <li className="flex items-center">
                <svg className="w-4 h-4 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Choose your topics from 8 categories of market insights
              </li>
              <li className="flex items-center">
                <svg className="w-4 h-4 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Unsubscribe anytime with one click
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Footer with GitHub Link */}
      <div className="max-w-2xl mx-auto px-4 pb-8">
        <div className="text-center">
          <p className="text-sm text-gray-500">
            Interested in the technical details? Check out the{' '}
            <a 
              href="https://github.com/sshh12/reality-index" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 underline"
            >
              source code on GitHub
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}

export default HomePage