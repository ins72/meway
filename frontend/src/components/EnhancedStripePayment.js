import React, { useState, useEffect } from 'react';
import { loadStripe } from '@stripe/stripe-js';
import {
  Elements,
  PaymentElement,
  useStripe,
  useElements
} from '@stripe/react-stripe-js';
import { useNavigate } from 'react-router-dom';

// Initialize Stripe with publishable key
const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY);

// Enhanced Payment Form Component
const EnhancedPaymentForm = ({ clientSecret, onSuccess, onError, workspaceName, bundles }) => {
  const stripe = useStripe();
  const elements = useElements();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    setIsLoading(true);
    setMessage(null);

    // Confirm payment with automatic redirection handling
    const { error } = await stripe.confirmPayment({
      elements,
      confirmParams: {
        return_url: `${window.location.origin}/payment-success`,
      },
    });

    if (error) {
      if (error.type === "card_error" || error.type === "validation_error") {
        setMessage(error.message);
      } else {
        setMessage("An unexpected error occurred.");
      }
      onError?.(error);
    } else {
      // Payment succeeded - user will be redirected to return_url
      onSuccess?.();
    }

    setIsLoading(false);
  };

  return (
    <div className="enhanced-payment-form">
      <form onSubmit={handleSubmit}>
        <div className="payment-element-container">
          <PaymentElement 
            options={{
              layout: "tabs",
              defaultValues: {
                billingDetails: {
                  name: '',
                  email: ''
                }
              }
            }}
          />
        </div>
        
        {message && (
          <div className="payment-message error">
            {message}
          </div>
        )}

        <div className="payment-summary">
          <h4>Order Summary</h4>
          <div className="workspace-info">
            <p><strong>Workspace:</strong> {workspaceName}</p>
            <p><strong>Bundles:</strong> {bundles.join(', ')}</p>
          </div>
        </div>

        <button 
          disabled={isLoading || !stripe || !elements} 
          className="enhanced-payment-submit"
        >
          {isLoading ? (
            <span className="loading-text">
              <span className="spinner"></span>
              Processing Payment...
            </span>
          ) : (
            "Complete Payment & Create Workspace"
          )}
        </button>

        <div className="payment-security">
          <div className="security-badges">
            <span className="badge">🔒 SSL Secured</span>
            <span className="badge">💳 Stripe Protected</span>
            <span className="badge">✅ PCI Compliant</span>
          </div>
          <p className="security-text">
            Your payment information is secure and encrypted. 
            We never store your card details.
          </p>
        </div>
      </form>
    </div>
  );
};

// Main Enhanced Payment Component
const EnhancedStripePayment = ({ 
  amount, 
  currency = 'usd', 
  bundles = [], 
  workspaceName = '',
  onSuccess, 
  onError 
}) => {
  const [clientSecret, setClientSecret] = useState('');
  const [customerId, setCustomerId] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Create PaymentIntent with customer creation
    const createPaymentIntent = async () => {
      try {
        setLoading(true);
        setError(null);

        const url = `${process.env.REACT_APP_BACKEND_URL || window.location.origin}/api/payments/create-payment-intent`;
        const authToken = localStorage.getItem('auth_token');
        
        console.log('Creating enhanced payment intent with URL:', url);
        console.log('Auth token:', authToken ? 'present' : 'MISSING');
        console.log('Request data:', {
          amount: Math.round(amount * 100),
          currency,
          bundles,
          workspace_name: workspaceName,
          save_payment_method: true
        });

        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`
          },
          body: JSON.stringify({
            amount: Math.round(amount * 100), // Convert to cents
            currency,
            bundles,
            workspace_name: workspaceName,
            save_payment_method: true // Save payment method for future use
          }),
        });

        if (!response.ok) {
          const errorText = await response.text();
          console.error(`Enhanced Payment Intent Creation Failed:`, {
            status: response.status,
            statusText: response.statusText,
            url: response.url,
            errorText: errorText
          });
          throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
        }

        const data = await response.json();
        
        if (data.client_secret) {
          setClientSecret(data.client_secret);
          setCustomerId(data.customer_id);
          console.log('Enhanced payment intent created successfully:', data.payment_intent_id);
        } else {
          throw new Error('No client secret received from server');
        }
        
      } catch (err) {
        console.error('Enhanced payment intent creation error:', err);
        setError(`Payment setup failed: ${err.message}`);
        onError?.(err);
      } finally {
        setLoading(false);
      }
    };

    if (amount > 0) {
      createPaymentIntent();
    }
  }, [amount, currency, bundles, workspaceName, onError]);

  if (loading) {
    return (
      <div className="enhanced-payment-loading">
        <div className="loading-spinner"></div>
        <p>Setting up secure payment...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="enhanced-payment-error">
        <div className="error-icon">❌</div>
        <h3>Payment Setup Error</h3>
        <p>{error}</p>
        <button 
          onClick={() => window.location.reload()} 
          className="retry-button"
        >
          Try Again
        </button>
      </div>
    );
  }

  if (!clientSecret) {
    return (
      <div className="enhanced-payment-error">
        <div className="error-icon">⚠️</div>
        <h3>Payment Not Available</h3>
        <p>Unable to initialize payment. Please try again.</p>
      </div>
    );
  }

  const appearance = {
    theme: 'stripe',
    variables: {
      colorPrimary: '#6366f1',
      colorBackground: '#ffffff',
      colorText: '#1f2937',
      colorDanger: '#ef4444',
      fontFamily: 'Inter, system-ui, sans-serif',
      spacingUnit: '4px',
      borderRadius: '8px',
    },
  };

  return (
    <div className="enhanced-stripe-payment">
      <div className="payment-header">
        <h3>Complete Your Payment</h3>
        <p>Secure payment powered by Stripe</p>
      </div>
      
      <Elements 
        stripe={stripePromise} 
        options={{ clientSecret, appearance }}
      >
        <EnhancedPaymentForm
          clientSecret={clientSecret}
          onSuccess={onSuccess}
          onError={onError}
          workspaceName={workspaceName}
          bundles={bundles}
        />
      </Elements>
      
      <div className="customer-info">
        <p className="info-text">
          💡 Your payment method will be securely saved for future workspace purchases
        </p>
        {customerId && (
          <p className="customer-id">Customer ID: {customerId.substring(0, 20)}...</p>
        )}
      </div>
    </div>
  );
};

export default EnhancedStripePayment;