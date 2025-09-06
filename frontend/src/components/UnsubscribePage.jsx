import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import axios from 'axios'

const UnsubscribePage = () => {
  const { token } = useParams()
  const [loading, setLoading] = useState(true)
  const [subscription, setSubscription] = useState(null)
  const [unsubscribed, setUnsubscribed] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchSubscriptionInfo()
  }, [token])

  const fetchSubscriptionInfo = async () => {
    try {
      const response = await axios.get(`/api/subscription/${token}`)
      setSubscription(response.data)
    } catch (err) {
      setError('Invalid unsubscribe link or subscription not found.')
    } finally {
      setLoading(false)
    }
  }

  const handleUnsubscribe = async () => {
    setLoading(true)
    try {
      await axios.delete(`/api/unsubscribe/${token}`)
      setUnsubscribed(true)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to unsubscribe. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full mx-4">
          <div className="bg-white rounded-lg shadow-lg p-8 text-center">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Error</h2>
            <p className="text-gray-600">{error}</p>
          </div>
        </div>
      </div>
    )
  }

  if (unsubscribed) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full mx-4">
          <div className="bg-white rounded-lg shadow-lg p-8 text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Unsubscribed Successfully</h2>
            <p className="text-gray-600 mb-6">
              You've been unsubscribed from The Reality Index newsletter. We're sorry to see you go!
            </p>
            <a 
              href="/"
              className="btn-primary inline-block"
            >
              Back to Homepage
            </a>
          </div>
        </div>
      </div>
    )
  }

  if (!subscription.active) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full mx-4">
          <div className="bg-white rounded-lg shadow-lg p-8 text-center">
            <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Already Unsubscribed</h2>
            <p className="text-gray-600 mb-2">
              This email address is already unsubscribed from our newsletter.
            </p>
            <p className="text-sm text-gray-500 mb-6">
              Email: {subscription.email}
            </p>
            <a 
              href="/"
              className="btn-primary inline-block"
            >
              Back to Homepage
            </a>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full mx-4">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="text-center mb-6">
            <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Unsubscribe from Newsletter</h2>
            <p className="text-gray-600">
              Are you sure you want to unsubscribe from The Reality Index newsletter?
            </p>
          </div>

          <div className="bg-gray-50 rounded-lg p-4 mb-6">
            <p className="text-sm text-gray-600 mb-2">
              <strong>Email:</strong> {subscription.email}
            </p>
            <p className="text-sm text-gray-600 mb-2">
              <strong>Subscribed Topics:</strong>
            </p>
            <div className="flex flex-wrap gap-2">
              {subscription.topics.map(topic => (
                <span key={topic} className="px-2 py-1 bg-primary-100 text-primary-800 text-xs rounded-full">
                  {topic === 'ai' ? 'AI & Tech' : topic.charAt(0).toUpperCase() + topic.slice(1)}
                </span>
              ))}
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Subscribed on: {new Date(subscription.created_at).toLocaleDateString()}
            </p>
          </div>

          <div className="flex space-x-4">
            <button
              onClick={handleUnsubscribe}
              className="flex-1 bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200"
            >
              Yes, Unsubscribe
            </button>
            <a
              href="/"
              className="flex-1 btn-secondary text-center"
            >
              Keep Subscription
            </a>
          </div>

          <p className="text-xs text-gray-500 text-center mt-4">
            You can always resubscribe later at our homepage.
          </p>
        </div>
      </div>
    </div>
  )
}

export default UnsubscribePage