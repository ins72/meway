import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const PaymentSuccessPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [paymentStatus, setPaymentStatus] = useState('loading');
  const [paymentDetails, setPaymentDetails] = useState(null);

  useEffect(() => {
    const verifyPayment = async () => {
      try {
        const paymentIntentId = searchParams.get('payment_intent');
        const paymentIntentClientSecret = searchParams.get('payment_intent_client_secret');
        
        if (!paymentIntentId) {
          setPaymentStatus('error');
          return;
        }

        // Verify payment with backend
        const response = await fetch(
          `${process.env.REACT_APP_BACKEND_URL}/api/payment-intent/${paymentIntentId}`,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
            }
          }
        );

        if (response.ok) {
          const data = await response.json();
          setPaymentDetails(data);
          
          if (data.status === 'succeeded') {
            setPaymentStatus('success');
          } else {
            setPaymentStatus('processing');
          }
        } else {
          setPaymentStatus('error');
        }
      } catch (error) {
        console.error('Error verifying payment:', error);
        setPaymentStatus('error');
      }
    };

    verifyPayment();
  }, [searchParams]);

  const handleContinue = () => {
    // Navigate to onboarding completion or dashboard
    if (user?.onboarding_completed) {
      navigate('/dashboard');
    } else {
      navigate('/onboarding?step=5'); // Final step
    }
  };

  if (paymentStatus === 'loading') {
    return (
      <div className="payment-status-page">
        <div className="status-container">
          <div className="loading-spinner"></div>
          <h2>Verifying your payment...</h2>
          <p>Please wait while we confirm your payment.</p>
        </div>
      </div>
    );
  }

  if (paymentStatus === 'error') {
    return (
      <div className="payment-status-page">
        <div className="status-container error">
          <div className="status-icon">❌</div>
          <h2>Payment Verification Failed</h2>
          <p>We couldn't verify your payment. Please contact support if you were charged.</p>
          <button onClick={() => navigate('/onboarding')} className="btn btn-primary">
            Return to Setup
          </button>
        </div>
      </div>
    );
  }

  if (paymentStatus === 'processing') {
    return (
      <div className="payment-status-page">
        <div className="status-container processing">
          <div className="status-icon">⏳</div>
          <h2>Payment Processing</h2>
          <p>Your payment is being processed. This may take a few minutes.</p>
          <button onClick={() => window.location.reload()} className="btn btn-secondary">
            Refresh Status
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="payment-status-page">
      <div className="status-container success">
        <div className="status-icon">✅</div>
        <h2>Payment Successful!</h2>
        <p>Thank you for your payment. Your subscription is now active.</p>
        
        {paymentDetails && (
          <div className="payment-details">
            <h3>Payment Details</h3>
            <div className="detail-row">
              <span>Amount:</span>
              <span>${(paymentDetails.amount / 100).toFixed(2)} {paymentDetails.currency.toUpperCase()}</span>
            </div>
            <div className="detail-row">
              <span>Payment ID:</span>
              <span>{paymentDetails.id}</span>
            </div>
            {paymentDetails.metadata?.bundles && (
              <div className="detail-row">
                <span>Bundles:</span>
                <span>{paymentDetails.metadata.bundles}</span>
              </div>
            )}
          </div>
        )}
        
        <button onClick={handleContinue} className="btn btn-primary">
          Continue to Dashboard
        </button>
      </div>
    </div>
  );
};

export default PaymentSuccessPage;