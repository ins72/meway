import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const PaymentSuccessPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [status, setStatus] = useState('processing');
  const [message, setMessage] = useState('');
  const [workspaceInfo, setWorkspaceInfo] = useState(null);

  useEffect(() => {
    const verifyPayment = async () => {
      try {
        const paymentIntentId = searchParams.get('payment_intent');
        const paymentIntentClientSecret = searchParams.get('payment_intent_client_secret');

        if (!paymentIntentId) {
          setStatus('error');
          setMessage('No payment information found.');
          return;
        }

        console.log('Verifying payment:', paymentIntentId);

        // Confirm payment success with backend
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/payments/confirm-payment-success`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
          },
          body: JSON.stringify({
            payment_intent_id: paymentIntentId
          })
        });

        if (!response.ok) {
          throw new Error(`Payment verification failed: ${response.status}`);
        }

        const data = await response.json();
        
        if (data.success) {
          setStatus('success');
          setMessage('Payment successful! Your workspace is being created...');
          setWorkspaceInfo(data);

          // Redirect to workspace dashboard after a delay
          setTimeout(() => {
            if (data.redirect_url) {
              navigate(data.redirect_url);
            } else {
              navigate('/dashboard');
            }
          }, 3000);
        } else {
          throw new Error(data.error || 'Payment verification failed');
        }

      } catch (error) {
        console.error('Payment verification error:', error);
        setStatus('error');
        setMessage(error.message || 'Payment verification failed');
      }
    };

    verifyPayment();
  }, [searchParams, navigate]);

  const getStatusIcon = () => {
    switch (status) {
      case 'processing':
        return (
          <div className="status-icon processing">
            <div className="spinner"></div>
          </div>
        );
      case 'success':
        return <div className="status-icon success">✅</div>;
      case 'error':
        return <div className="status-icon error">❌</div>;
      default:
        return null;
    }
  };

  const getStatusTitle = () => {
    switch (status) {
      case 'processing':
        return 'Processing Payment...';
      case 'success':
        return 'Payment Successful!';
      case 'error':
        return 'Payment Error';
      default:
        return 'Payment Status';
    }
  };

  return (
    <div className="payment-success-page">
      <div className="payment-status-container">
        {getStatusIcon()}
        
        <h1 className="status-title">{getStatusTitle()}</h1>
        
        <p className="status-message">{message}</p>

        {workspaceInfo && status === 'success' && (
          <div className="workspace-info">
            <h3>Workspace Details</h3>
            <div className="info-grid">
              <div className="info-item">
                <span className="label">Workspace Name:</span>
                <span className="value">{workspaceInfo.workspace_name}</span>
              </div>
              <div className="info-item">
                <span className="label">Selected Bundles:</span>
                <span className="value">{workspaceInfo.bundles?.join(', ')}</span>
              </div>
              <div className="info-item">
                <span className="label">Status:</span>
                <span className="value status-active">Active</span>
              </div>
            </div>
          </div>
        )}

        {status === 'success' && (
          <div className="success-actions">
            <div className="redirect-info">
              <p>🚀 Redirecting to your workspace dashboard in a few seconds...</p>
            </div>
            <button 
              onClick={() => navigate(workspaceInfo?.redirect_url || '/dashboard')}
              className="go-to-dashboard-btn"
            >
              Go to Dashboard Now
            </button>
          </div>
        )}

        {status === 'error' && (
          <div className="error-actions">
            <button 
              onClick={() => navigate('/onboarding')}
              className="retry-btn"
            >
              Return to Onboarding
            </button>
            <button 
              onClick={() => navigate('/dashboard')}
              className="dashboard-btn"
            >
              Go to Dashboard
            </button>
          </div>
        )}

        <div className="payment-footer">
          <p className="security-note">
            🔒 Your payment was processed securely by Stripe
          </p>
          <p className="support-note">
            Need help? Contact support at support@mewayz.com
          </p>
        </div>
      </div>
    </div>
  );
};

export default PaymentSuccessPage;