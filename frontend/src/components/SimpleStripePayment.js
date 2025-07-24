import React, { useState, useEffect } from 'react';
import { loadStripe } from '@stripe/stripe-js';
import {
  Elements,
  PaymentElement,
  useStripe,
  useElements
} from '@stripe/react-stripe-js';

// Initialize Stripe with publishable key
const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY);

// Payment Form Component
const CheckoutForm = ({ clientSecret, onSuccess, onError }) => {
  const stripe = useStripe();
  const elements = useElements();
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    setIsLoading(true);
    setMessage(null);

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
      onSuccess?.();
    }

    setIsLoading(false);
  };

  return (
    <form onSubmit={handleSubmit} className="stripe-form">
      <PaymentElement />
      {message && <div className="payment-message">{message}</div>}
      <button 
        disabled={isLoading || !stripe || !elements} 
        className="stripe-submit-btn"
      >
        <span>
          {isLoading ? "Processing..." : "Pay now"}
        </span>
      </button>
    </form>
  );
};

// Main Payment Component
const SimpleStripePayment = ({ 
  amount, 
  currency = 'usd', 
  bundles = [], 
  workspaceName = '',
  onSuccess, 
  onError 
}) => {
  const [clientSecret, setClientSecret] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Create PaymentIntent as soon as the page loads
    const createPaymentIntent = async () => {
      try {
        setLoading(true);
        setError(null);

        const url = `${process.env.REACT_APP_BACKEND_URL}/api/create-payment-intent`;
        const authToken = localStorage.getItem('auth_token');
        console.log('Creating payment intent with URL:', url);
        console.log('Auth token:', authToken ? `${authToken.substring(0, 50)}...` : 'MISSING');
        console.log('Request data:', {
          amount: Math.round(amount * 100),
          currency,
          bundles,
          workspace_name: workspaceName
        });

        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
          },
          body: JSON.stringify({
            amount: Math.round(amount * 100), // Convert to cents
            currency,
            bundles,
            workspace_name: workspaceName,
            automatic_payment_methods: {
              enabled: true,
            },
          }),
        });

        if (!response.ok) {
          const errorText = await response.text();
          console.error(`Payment Intent Creation Failed:`, {
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
        } else {
          throw new Error('No client secret received');
        }
      } catch (err) {
        console.error('Error creating payment intent:', err);
        setError(err.message);
        onError?.(err);
      } finally {
        setLoading(false);
      }
    };

    if (amount > 0) {
      createPaymentIntent();
    }
  }, [amount, currency, bundles, workspaceName, onError]);

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

  const options = {
    clientSecret,
    appearance,
  };

  if (loading) {
    return (
      <div className="stripe-loading">
        <div className="loading-spinner"></div>
        <p>Setting up payment...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="stripe-error">
        <p>Error: {error}</p>
        <button onClick={() => window.location.reload()}>
          Try Again
        </button>
      </div>
    );
  }

  if (!clientSecret) {
    return (
      <div className="stripe-error">
        <p>Unable to initialize payment. Please try again.</p>
      </div>
    );
  }

  return (
    <div className="stripe-payment-container">
      <Elements options={options} stripe={stripePromise}>
        <CheckoutForm 
          clientSecret={clientSecret}
          onSuccess={onSuccess}
          onError={onError}
        />
      </Elements>
    </div>
  );
};

export default SimpleStripePayment;